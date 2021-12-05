# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=W0621
"""
Exceptions raised by MergeConf package.
"""

class MissingConfiguration(Exception):
  """
  Raised if mandatory configuration items are missing.

  Attributes:
    missing: string list of missing items in section-dot-key notation,
      separated by commas.
  """

  def __init__(self, missingvars):
    self._missing = missingvars

    description = f"Undefined mandatory variables: {missingvars}"
    super().__init__(description)

  @property
  def missing(self):
    return self._missing

class MissingConfigurationFile(Exception):
  """
  Raised if the specified configuration file is missing or otherwise
  unreadable.

  Attributes:
    file: the missing file
  """

  def __init__(self, file):
    self._file = file
    description = 'Configuration file missing or unreadable: {}'.format(file)
    super().__init__(description)

  @property
  def file(self):
    return self._file

class UnsupportedType(Exception):
  """
  Raised if a configuration item is added with an unsupported type.

  Attributes:
    type: the unsupported type
  """

  def __init__(self, type):
    self._type = type.__name__
    description = 'Unsupported type: {}'.format(self._type)
    super().__init__(description)

  @property
  def type(self):
    return self._type

class UndefinedSection(Exception):
  """
  Raised if a section is found that was not defined for the parser.

  Attributes:
    section: the section name
  """
  def __init__(self, section):
    self._section = section
    description = f"Unexpected section found: '{section}'"
    super().__init__(description)

  @property
  def section(self):
    return self._section

class UndefinedConfiguration(Exception):
  """
  Raised if a configuration item is found that was not defined for the parser.

  Attributes:
    section: the section name
    item: the item name
  """
  def __init__(self, section, item):
    self._section = section
    self._item = item
    description = f"Unexpected configuration item found: '{item}' in section '{section}'"
    super().__init__(description)

  @property
  def section(self):
    return self._section

  @property
  def item(self):
    return self._item

#class Deprecated(Exception):
#  """
#  Raised for hard deprecations where functionality has been removed and the
#  API is not available at all.
#
#  Attributes:
#    version: the last version in which this functionality is available.
#    message: further information to assist the user.
#  """
#  def __init__(self, version, message=None):
#    self._version = version
#    self._message = message
#    self._function = inspect.stack()[1].function
#    etc = f": {message}" if message else '.'
#    description = f"Deprecated API `{self._function}` last available in version {version}{etc}"
#    super().__init__(description)
#
#  @property
#  def function(self):
#    return self._function
#
#  @property
#  def version(self):
#    return self._version
