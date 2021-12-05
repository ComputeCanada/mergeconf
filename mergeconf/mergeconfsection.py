# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:

from mergeconf.mergeconfitem import MergeConfItem

class MergeConfSection():
  def __init__(self, name, map=None):
    self._name = name
    self._items = {}
    self._sections = {}

    if map:
      for key, value in map.items():
        if isinstance(value, dict):
          self._sections[key] = MergeConfSection(key, map=value)
        else:
          self._items[key] = MergeConfItem(key, value)

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
    """
    Support iterating through configuration items.
    """
    for key, item in self._items.items():
      yield (key, item.value)

  # Given a list of variables with section prefix already stripped, find
  # variables defined in environment that match configuration items, and
  # assign their values to the items.  Then for each subsection, strip the
  # section prefix from any variables and call recursively on te section.
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
    """
    Return dictionary representation of configuration or section.
    """
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
    """
    Return list of sections.
    """
    return self._sections.keys()

  def add(self, key, value=None, type=None, mandatory=False, cli=False,
      description=None):
    """
    Add a configuration item.

    Args:
      key (str): Name of configuration item
      value (whatever): Default value, None by default
      type (type): Type of value
      mandatory (boolean): Whether item is mandatory or not, defaults to
        False.
      cli (boolean): Whether item should be included in command-line arguments
      description (str): Short descriptive text that may appear in usage text
        or sample configurations

    Notes: Type detection is attempted if not specified.
    """
    item = MergeConfItem(key, value, type=type, mandatory=mandatory,
      cli=cli, description=description)

    default = self._items.get(item.key, None)
    if default and not item.value:
      item.value = default.value
    self._items[item.key] = item

  def add_section(self, name):
    """
    Add a subsection to this section and return its object.
    """
    if name in self._sections:
      return self._sections[name]
    section = MergeConfSection(name)
    self._sections[name] = section
    return section

  def missing_mandatory(self):
    """
    Check that each mandatory item in this section and subsections has a
    defined value.

    Returns:
      List of fully qualified mandatory items without a defined value, in
      section-dot-item syntax.
    """
    def mandatories(sections, name, item):
      if item.mandatory and item.value is None:
        return f"{'.'.join(sections) + '.' if sections else ''}{name}"
      return None

    return self.map(mandatories) or None

  def _map(self, fn, sections):
    """
    Apply the given function to every item in this section and descend into
    subsections.

    Args:
      fn: Function taking (sections, name, MergeConfItem) and returning some
        value, or None.
      sections: list of sections built as a trail of breadcrumbs during
        recursion.

    Returns:
      List of values returned by function.  Values of None are not included.
    """
    results = []

    # apply to items
    for key, item in self._items.items():
      el = fn(sections, key, item)
      if el:
        results.append(fn(sections, key, item))

    # descend into subsections
    for name, section in self._sections.items():
      results.extend(section._map(fn, sections + [name]))

    return results

  def _sample_config(self):

    sample = []

    for name, item in self._items.items():
      typestr = f"({item.type.__name__}) " if item.type is not None else ''
      sample.append(f"# {typestr}{item.description or ''}")

      if item.value:
        sample.append(f"#{name} = {item.value}")
      elif item.mandatory:
        sample.append(f"{name} =")
      else:
        sample.append(f"#{name} =")

      sample.append("")

    for name, section in self._sections.items():
      sample.append(f"[{name}]")
      sample.extend(section._sample_config())

    return sample
