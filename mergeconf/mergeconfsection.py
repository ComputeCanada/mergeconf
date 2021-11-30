# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:

from mergeconf.mergeconfvalue import MergeConfValue

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
          self._items[key] = MergeConfValue(key, value)

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
    return self._sections.keys()

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
    item = MergeConfValue(key, value, type=type)

    default = self._items.get(item.key, None)
    if default and not item.value:
      item.value = default.value
    self._items[item.key] = item

    # remember it's mandatory
    if mandatory:
      self._mandatory.append(item.key)

  # TODO: this can be simplified to remove the if clause if/when `map` is no
  # longer permitted as a parameter to init()
  def add_section(self, name):
    if name in self._sections:
      return self._sections[name]
    section = MergeConfSection(name)
    self._sections[name] = section
    return section

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
