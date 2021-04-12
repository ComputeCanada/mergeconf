# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=W0621


class MergeConfValue:
  """
  Basic configuration item and base class for more complex types.
  """
  def _set_value_appropriately(self, value):
    if value is None:
      self._value = value
    elif self._type == bool:
      if isinstance(value, bool):
        self._value = value
      else:
        self._value = value.lower() in ['true', 'yes', '1']
    else:
      self._value = self._type(value)

  def __init__(self, key, value=None, mandatory=False, type=str):
    self._key = key
    self._mandatory = mandatory
    self._type = type

    self._set_value_appropriately(value)

  @property
  def key(self):
    return self._key

  @property
  def value(self):
    return self._value

  @value.setter
  def value(self, value):
    self._set_value_appropriately(value)
