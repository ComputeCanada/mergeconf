# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=W0621

class MissingConfiguration(Exception):
  """
  Raised if mandatory configuration items are missing.

  Attributes:
    missing: list of missing variables' keys
  """

  def __init__(self, missingvars):
    self._missing = missingvars
    description = 'Undefined mandatory variables: {}'.format(', '.join(missingvars))
    super().__init__(description)

  @property
  def missing(self):
    return self._missing

class MissingConfigurationFile(Exception):
  """
  Raised if the specified configuration file is missing or otherwise
  unreadable.
  """

  def __init__(self):
    description = 'Configuration file missing or unreadable'
    super().__init__(description)

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
