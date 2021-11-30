# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=W0621

from mergeconf import exceptions

# aliasing this allows the use of a parameter `type`, for which I can't find a
# reasonable replacement (like `klass` for `class`)
builtin_type = type

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

  def __init__(self, key, value=None, type=None):
    """
    Create a configuration item.

    Arguments:
      key: Configuration item's key.
      value: Current value
      type: Item data type.  Must be one of bool, int, float or str.  If not
        specified, will be autodetected.
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

    self._key = key
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
