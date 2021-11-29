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
  def __init__(self, name, map=None):
    self._name = name
    self._items = {}
    self._mandatory = []
    self._sections = {}

    if map:
      for key, value in map.items():
        if isinstance(value, dict):
          self._sections[key] = MergeConfSection(key, map=value)
        else:
          type = builtin_type(value)
          if type not in [bool, int, float, str]:
            type = str
          print(f"Adding to section {name}: {key} = {value} with type {type}")
          self._items[key] = MergeConfValue(key, value, type=type)

  def __getitem__(self, key):
    if key in self._items:
      return self._items[key].value
    if key in self._sections:
      return self._sections[key]
    raise KeyError

  def __getattr__(self, attr):
    if attr in self._items:
      return self._items[attr].value
    if attr in self._sections:
      return self._sections[attr]
    raise AttributeError

  def __iter__(self):
    for key, item in self._items.items():
      yield (key, item.value)

  # get items for this section
  # then for each subsection, check if any variables start with the section
  # name and if so, strip the subsection name from them and send them to
  # section._merge_env
  # given envvars: list of variables with section prefix already stripped
  #
  def _merge_env(self, envvars):

    # get any variable names for this section
    for name, item in self._items.items():
      if name in envvars:
        item.value = envvars[name]

    # see if any subsection has variables
    for sectionname, section in self._sections.items():
      prefix = sectionname + '_'
      sectionvars = {
        # TODO(3.9): replace `split(prefix, 1)[1]` with `removeprefix(prefix)`
        x[0].split(prefix, 1)[1]: x[1]
        for x in envvars.items() if x[0].startswith(prefix)
      }
      if sectionvars:
        section._merge_env(sectionvars)

  def to_dict(self):
    # TODO(3.9): use union
    # return {
    #   key: item.value for key, item in self._items.items()
    # } | {
    #   name: section.to_dict() for name, section in self._sections.items()
    # }
    d = { key: item.value for key, item in self._items.items() }
    d.update(
      { name: section.to_dict() for name, section in self._sections.items() }
    )
    return d

  @property
  def sections(self):
    for name, section in self._sections.items():
      yield (name, section)

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
    # TODO: move this logic to MergeConfValue
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
      print(f"Adding  mandatory variable {item.key}")
      self._mandatory.append(item.key)

  # TODO: this can be simplified to remove the if clause if/when `map` is no
  # longer permitted as a parameter to init()
  def add_section(self, name):
    if name in self._sections:
      return self._sections[name]
    section = MergeConfSection(name)
    self._sections[name] = section
    return section

  #@property
  #def sections(self):
  #  return self._sections

  def missing_mandatory(self):
    """
    Check that each mandatory item in this section has a defined value, and
    each subsection as well.

    Returns:
      List of fully qualified mandatory items without a defined value, in
      section-dot-item syntax.
    """
    missing = []

    # check items
    for key in self._mandatory:
      if self._items[key].value is None:
        missing.append(key)

    # check subsections
    for sectionname, section in self._sections.items():
      ss_missing = section.missing_mandatory()
      # TODO: This is a pylint bug.  It applies to `sectionname`, but that
      # should be locked in for each iteration of the enclosing for loop.
      # see https://vald-phoenix.github.io/pylint-errors/plerr/errors/variables/W0640.html
      # pylint: disable=cell-var-from-loop
      if ss_missing:
        missing.extend(map(lambda i: f"{sectionname}.{i}", ss_missing))

    return missing or None

class MergeConf(MergeConfSection):
  """
  Configuration class.  Initialized optionally with configuration items, then
  additional items may be added explicitly (and must be if they are mandatory,
  a specific type, etc.).  Once all items have been added the configuration is
  finalized with parse(), validation checks are performed, and the realized
  values can be extracted.
  """

  def __init__(self, codename, files=None, map=None, strict=True):
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
    super().__init__(None, map=map)

    self._codename = codename
    self._files = files
    self._strict = strict

    # main section name transparently added.  ConfigParser requires all items
    # to be contained in a section; this supports simpler configurations and
    # avoids having to create a "main" or "app" section explicitly if not
    # desired.
    self._main = '__app__'

    # config files to read
    self._files = []

    if map:
      logging.warning("Support for `map` argument is deprecated and will " \
        "be removed.  Please use `add()` to add configuration options and " \
        "their specifications, including default values.")

  def merge_environment(self):
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
    # key stripped of prefix and made lowercase
    envvars = {
      # TODO(3.9): replace `split(prefix, 1)[1]` with `removeprefix(prefix)`
      x[0].split(prefix, 1)[1].lower(): x[1]
      for x in os.environ.items() if x[0].startswith(prefix)
    }

    self._merge_env(envvars)

    return envvars

  def merge_file(self, config_file):
    """
    Merge configuration defined in ConfigParser-format file.
    """
    config = ConfigParser(delimiters='=', interpolation=None)

    # read configuration into string so we can prepend a pretend main section.
    # See definition of self._main for explanation.
    try:
      with open(config_file) as f:
        config_content = f"[{self._main}]\n{f.read()}"
    except FileNotFoundError:
      # TODO: disable this globally?
      # pylint: disable=raise-missing-from
      raise exceptions.MissingConfigurationFile(config_file)

    # read configuration
    config.read_string(config_content, source=config_file)

    # read into stuffs
    for section in config.sections():
      if section == self._main:
        ref = self
      elif section not in self._sections:
        # unrecognized configuration section
        if self._strict:
          raise exceptions.UndefinedSection(section)
        logging.warning("Unexpected section in configuration: %s", section)
        ref = self.add_section(section)
      else:
        ref = self._sections[section]
      for option in config.options(section):
        if option not in ref._items:
          if self._strict:
            raise exceptions.UndefinedConfiguration(section, option)
          logging.warning("Unexpected configuration item in section %s: %s",
            section, option)
          ref.add(option, config[section][option])
        else:
          ref._items[option].value = config[section][option]

  def validate(self):
    """
    Checks that mandatory items have been defined in configuration.  If not,
    throws exception.  Client may also use `missing_mandatory()`.

    Subclasses may add additional validation but should first call the parent
    implementation as the test for mandatory items is primary.
    """
    # TODO(3.8): use walrus operator
    # if unfulfilled := self.missing_mandatory():
    unfulfilled = self.missing_mandatory()
    if unfulfilled:
      raise exceptions.MissingConfiguration(', '.join(unfulfilled))

  # pylint: disable=no-self-use
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

    # if we have config files, merge into config
    for config_file in config_files:
      self.merge_file(config_file)

    # override with variables set in environment
    self.merge_environment()

    # test that mandatory values have been set
    self.validate()
