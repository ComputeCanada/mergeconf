# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=W0621
"""
multiconf - support multiple configuration sources with order of precedence,
based on immediacy.  Currently: Default values are overridden by values read
from configuration file which in turn are overridden by values read from
environment variables.
"""
import os
import logging
import configparser
from multiconf import exceptions


class MultiConfValue:
  """
  Basic configuration item and base class for more complex types.
  """

  def __init__(self, key, value, mandatory=False, type=str):
    self._key = key
    self._mandatory = mandatory
    self._type = type

    if value is None:
      self._value = value
    else:
      self._value = self._type(value)

  @property
  def key(self):
    return self._key

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    if value is None:
      self._value = value
    else:
      self._value = self._type(value)


# pylint: disable=super-init-not-called
class MultiConfBoolean(MultiConfValue):
  """
  Configuration item where possible values are Boolean.
  """

  def __init__(self, key, value, mandatory=False):
    self._key = key
    self._mandatory = mandatory
    self._value = value

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    if value is None:
      self._value = value
    else:
      self._value = value.lower() in ['true', 'yes', '1']

class MultiConf():
  """
  Configuration class.  Initialized optionally with configuration items, then
  additional items may be added explicitly (and must be if they are mandatory,
  a specific type, etc.).  Once all items have been added the configuration is
  finalized with parse(), validation checks are performed, and the realized
  values can be extracted.
  """

  def __init__(self, codename, map=None):
    """
    Initializes MultiConf class.

    Args:
      codename (str): Simple string which is assumed to prefix any related
        environment variables associated with the configuration (along with an
        underscore as separator), in order to avoid collisions in the
        environment's namespace.  For example, for an `app_name` configuration
        key, with a codename `MYAPP`, the corresponding environment variable
        would be `MYAPP_APP_NAME`.
      map (dict): Configuration options which are neither mandatory nor of a
        specified type, specified as key, value pairs.
    """

    self._codename = codename
    self._mandatory = []
    if map:
      self._map = map
    else:
      self._map = {}

    for key, value in self._map.items():
      self.add(key, value)

  def _add(self, item, mandatory):
    self._map[item.key] = item

    # remember it's mandatory
    if mandatory:
      self._mandatory.append(item.key)

  def __getitem__(self, key):
    return self._map[key].value

  def add(self, key, value=None, mandatory=False, type=str):
    """
    Add a configuration item.

    Args:
      key (str): Name of configuration item
      value (whatever): Default value, None by default
      mandatory (boolean): Whether item is mandatory or not, defaults to
        False.
      type (type): Type of value
    """
    self._add(MultiConfValue(key, value, type=type), mandatory)

  def add_boolean(self, key, value=None, mandatory=False):
    """
    Add a configuration item of type Boolean.

    Args:
      key (str): Name of configuration item
      value (boolean): Default value, None by default
      mandatory (boolean): Whether item is mandatory or not, defaults to
        False.
    """
    self._add(MultiConfBoolean(key, value), mandatory)

  def parse(self, default_config_file=None):
    """
    Takes configuration definition and default configuration file and reads in
    configuration, overriding default values.  These are in turn overridden by
    corresponding variables found in the environment, if any.  Basic
    validations are performed.

    Args:
      default_config_file (str): Path to default configuration file.  This may
        be overridden if an alternative configuration file is specified in the
        environment.

    Returns:
      A dict of key-value configuration items.
    """

    # add this to any environment variable names
    envprefix = self._codename + '_'

    # get all environment variables starting with that prefix into dict with
    # prefix stripped from key
    envvars = {
      x[0].removeprefix(envprefix): x[1]
      for x in os.environ.items() if x[0].startswith(envprefix)
    }

    # get configuration file from environment, fall back to given
    config_file = envvars.get(envprefix + 'CONFIG', default_config_file)

    # if we have a config file, read into map
    if config_file:
      # get parser.  Turn interpolation off so '%' doesn't have to be escaped.
      config_from_file = configparser.ConfigParser(delimiters='=', interpolation=None)

      # read configuration
      config_from_file.read(config_file)

      # flag if configuration specified but not found
      if envprefix + 'CONFIG' in os.environ and not config_from_file:
        logging.error(
          "Configuration file '%s' specified but cannot be read",
          os.environ[envprefix + 'CONFIG']
        )

      # copy in anything from the configuration
      for section in config_from_file:

        # determine environment and config variable prefixes
        if section != 'DEFAULT':
          configprefix = section.upper() + '_'
        else:
          configprefix = ''

        # loop through configurations
        for key in config_from_file[section]:
          self._map[configprefix + key.upper()].value = config_from_file[section][key]

    # override with environment variables
    for (key, value) in envvars.items():
      if key in self._map:
        self._map[key].value = value
      else:
        logging.warning('Environment variable %s was set but is not used', envprefix + key)

    # test that mandatory value have been set
    unfulfilled = []
    for key in self._mandatory:
      if self._map[key].value is None:
        unfulfilled.append(key)
    if unfulfilled:
      raise exceptions.MissingConfiguration(unfulfilled)
