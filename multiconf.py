# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=W0621

import os
import logging
import configparser


class MissingConfiguration(Exception):
  """
  Raised if mandatory configuration items are missing.
  """

class MultiConfValue:

  def __init__(self, key, value, mandatory=False):
    self._key = key
    self._value = value
    self._mandatory = mandatory

  @property
  def key(self):
    return self._key

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    self._value = value

class MultiConfBoolean(MultiConfValue):

  @property
  def value(self):
    if isinstance(self._value, bool):
      return self._value
    return self._value.lower() in ['true', 'yes', '1']

class MultiConf:

  def __init__(self, codename, map=None):
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

  def add(self, key, value=None, mandatory=False):
    self._add(MultiConfValue(key, value), mandatory)

  def add_boolean(self, key, value=None, mandatory=False):
    self._add(MultiConfBoolean(key, value), mandatory)

  def parse(self, default_config_file):

    # add this to any environment variable names
    envprefix = self._codename + '_'

    # get configuration file from or environment
    config_file = os.environ.get(envprefix + 'CONFIG', default_config_file)

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
    for key in self._map.keys():
      envvar = envprefix + key.upper()
      if envvar in os.environ:
        self._map[key].value = os.environ[envvar]

    # test that mandatory value have been set
    unfulfilled = []
    for key in self._mandatory:
      if not self._map[key].value:
        unfulfilled.append(key)
    if unfulfilled:
      raise MissingConfiguration(unfulfilled)

    return self._map
