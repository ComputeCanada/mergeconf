# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=W0621
import os
import logging
from configparser import ConfigParser
from mergeconf import exceptions
from mergeconf.mergeconfvalue import MergeConfValue

# aliasing this allows the use of a parameter `type`, for which I can't find a
# reasonable replacement (like `klass` for `class`)
builtin_type = type

# deprecation apology message
deprecation_msg = """
This method is deprecated immediately.  I apologise for any inconvenience, but
I estimate uptake of this library to be in the low 1's and probably actually
just 1.  To continue using the API you're expecting, you can specify version
0.3 of the library but it was overhauled for better functionality and, I think,
a nicer API.
"""

# defined outside MergeConf and MergeConf is its own section (the default one)
class MergeConfSection():
  def __init__(self, name):
    self._name = name
    self._items = {}
    self._mandatory = []

  def __getitem__(self, key):
    return self._items[key].value

  def __getattr__(self, attr):
    return self.__getitem__(attr)

  def __iter__(self):
    for key, value in self._items.items():
      #if isinstance(value, dict):
      #  yield (key, dict)
      #else:
      yield (key, value.value)

  def add(self, key, value=None, mandatory=False, type=None):
    """
    Add a configuration item.

    Args:
      key (str): Name of configuration item
      value (whatever): Default value, None by default
      mandatory (boolean): Whether item is mandatory or not, defaults to
        False.
      type (type): Type of value

    Notes: Type detection is attempted if not specified
    """
    if type and type not in [bool, int, float, str]:
      raise exceptions.UnsupportedType(type)
    if not type:
      if value is None:
        type = str
      else:
        type = builtin_type(value)
        if type not in [bool, int, float, str]:
          type = str

    item = MergeConfValue(key, value, type=type)

    default = self._items.get(item.key, None)
    if default and not item.value:
      item.value = default.value
    self._items[item.key] = item

    # remember it's mandatory
    if mandatory:
      self._mandatory.append(item.key)


class MergeConf(MergeConfSection):
  """
  Configuration class.  Initialized optionally with configuration items, then
  additional items may be added explicitly (and must be if they are mandatory,
  a specific type, etc.).  Once all items have been added the configuration is
  finalized with parse(), validation checks are performed, and the realized
  values can be extracted.
  """

  def __init__(self, codename, map=None, strict=True):
    """
    Initializes MergeConf class.

    Args:
      codename (str): Simple string which is assumed to prefix any related
        environment variables associated with the configuration (along with an
        underscore as separator), in order to avoid collisions in the
        environment's namespace.  For example, for an `app_name` configuration
        key, with a codename `MYAPP`, the corresponding environment variable
        would be `MYAPP_APP_NAME`.
      map (dict): Configuration options which are neither mandatory nor of a
        specified type, specified as key, value pairs.
      strict: If true, unexpected configuration sections or items will cause
        an exception (UndefinedSection or UndefinedConfiguration,
        respectively).  If false, they will be added to the merged
        configuration.

    Note: The `map` argument is probably to be deprecated and removed at a
      later date.  Its utility is limited and should be avoided.
    """
    super().__init__(None)

    self._codename = codename
    self._strict = strict

    # by default, for now, main section name is codename
    self._main = codename

    # config files to read
    self._files = []

    # sections map includes self
    self._sections = {
      None: self
    }

    if map:
      logging.warning("Support for `map` argument is deprecated and will " \
        "be removed.  Please use `add()` to add configuration options and " \
        "their specifications, including default values.")

      for sectionname, sectiondict in map.items():
        if sectionname not in self._sections:
          section = self.addsection(sectionname)
        else:
          section = self._sections[sectionname]
        for key, value in sectiondict.items():
          type = builtin_type(value)
          if type not in [bool, int, float, str]:
            type = str
          section.add(key, value, type=type)

  def sections(self):
    for sectionname, section in self._sections.items():
      yield sectionname, section

  def to_dict(self):
    return {
      sectionname: {
        key: value.value
        for key, value in section._items.items()
      }
      for sectionname, section in self._sections.items()
    }

  def __getitem__(self, key):
    if key in self._sections:
      return self._sections[key]
    return super().__getitem__(key)

  def __getattr__(self, attr):
    return self.__getitem__(attr)

  # pylint: disable=no-self-use
  def add_boolean(self, key, value=None, mandatory=False):
    """
    _Deprecated._  Add a configuration item of type Boolean.

    Args:
      key (str): Name of configuration item
      value (boolean): Default value, None by default
      mandatory (boolean): Whether item is mandatory or not, defaults to
        False.

    Note: This is deprecated; simply use `add` with `type=bool`.  This will be
      removed in a future release.
    """
    raise exceptions.Deprecated(version='0.3', message=deprecation_msg)

  def _merge_environment(self):
    """
    Using configuration definition, reads in variables from the environment
    matching the pattern `<codename>[_<section_name>]_<variable_name>`.  Any
    variable found not matching a defined configuration item is returned in
    a list: in this way variables outside the merged configuration context can
    be handled, such as a variable specifying an alternative config file.

    Returns:
      Map of environment variables matching the application codename but not
      matching defined configuration items.
    """
    # TODO: does not actually ONLY return those unmatched, maybe that's fine

    # add this to any environment variable names
    prefix = self._codename.upper() + '_'

    # get all environment variables starting with that prefix into dict with
    # prefix stripped from key
    envvars = {
      # in Python 3.9, `split(prefix, 1)[1]` can be replaced with
      # `removeprefix(prefix)`
      x[0].split(prefix, 1)[1]: x[1]
      for x in os.environ.items() if x[0].startswith(prefix)
    }

    # now map to sections and variables
    for sectionname, section in self._sections.items():
      if sectionname:
        prefix = sectionname.upper() + '_'
      else:
        prefix = ''
      for var in section._items:
        envvarname = f"{prefix}{var.upper()}"
        if envvarname in envvars:
          # overwrite existing value
          section._items[var].value = envvars[envvarname]

    return envvars

  # TODO: this can be simplified to remove the if clause if/when `map` is no
  # longer permitted as a parameter to init()
  def addsection(self, name):
    if name in self._sections:
      return self._sections[name]
    section = MergeConfSection(name)
    self._sections[name] = section
    return section

  def addfile(self, configfile):
    self._files.append(configfile)

  def parse(self, *args, **kwargs):
    """
    Deprecated.  See merge()
    """
    raise exceptions.Deprecated(version='0.3', message=deprecation_msg)

  def merge(self):
    """
    Takes configuration definition and any configuration files specified and
    reads in configuration, overriding default values.  These are in turn
    overridden by corresponding variables found in the environment, if any.
    Basic validations are performed.

    Returns:
      A dict of key-value configuration items.
    """

    # get configuration file from environment, fall back to given
    config_files = os.environ.get(
      f"{self._codename.upper()}_CONFIG",
      self._files
    )

    # if we have config files
    if config_files:
      # get parser.  Turn interpolation off so '%' doesn't have to be escaped.
      config_from_file = ConfigParser(delimiters='=', interpolation=None)

      # read configuration
      parsed_files = config_from_file.read(config_files)
      if not parsed_files:
        raise exceptions.MissingConfigurationFile(config_files)

      # read into stuffs
      for section in config_from_file.sections():
        if section == self._main:
          ref = self
        elif section not in self._sections:
          # unrecognized configuration section
          if self._strict:
            raise exceptions.UndefinedSection(section)
          logging.warning("Unexpected section in configuration: %s", section)
          ref = self.addsection(section)
        else:
          ref = self._sections[section]
        for option in config_from_file.options(section):
          if option not in ref._items:
            if self._strict:
              raise exceptions.UndefinedConfiguration(section, option)
            logging.warning("Unexpected configuration item in section %s: %s",
              section, option)
            ref.add(option, config_from_file[section][option])
          else:
            ref._items[option].value = config_from_file[section][option]

    # override with variables set in environment
    self._merge_environment()

    # test that mandatory value have been set
    unfulfilled = []
    for sectionname, section in self._sections.items():
      for key in section._mandatory:
        if section._items[key].value is None:
          unfulfilled.append((sectionname,key))
    if unfulfilled:
      raise exceptions.MissingConfiguration(unfulfilled)
