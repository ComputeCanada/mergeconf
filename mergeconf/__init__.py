# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
"""
mergeconf - build a single configuration by merging multiple configuration
sources with order of precedence, based on immediacy.  Currently: Default
values are overridden by values read from configuration file which in turn are
overridden by values read from environment variables.

## Deprecation notice

v0.4 is a significant refactoring and includes API changes.  Clients will need
to be updated accordingly or pin their versions to v0.3.

## Examples

### Typical use

If the following is in `app.conf`:

```
shape = circle
upsidedown = false

[section2]
ratio = 20.403
count = 4
```

The following code could be used to set that up:

```
import mergeconf

conf = mergeconf.MergeConf('myapp', files='app.conf')
conf.add('name')
conf.add('shape', mandatory=True)
conf.add('colour', value='black')
conf.add('upsidedown', type=bool)
conf.add('rightsideup', type=bool, value=True)
section2 = conf.add_section('section2')
section2.add('count', type=int, mandatory=True)
section2.add('ratio', type=float)

# read file, override from environment, ensure mandatories are present
conf.merge()
```

Now to make use of the configuration:

```
# use attribute style access
print(f"Shape: {conf.shape}")

# including for sectioned configuration
print(f"Count: {conf.section2.count}")

# can also use array indices
print(f"Ratio: {conf['section2']['count']}")
```

### Handling atypical configuration hierarchy

In some cases it may be desirable to handle the merging yourself, such as if
you want a different hierarchy, such as environment configuration being
overridden by file-based configurations.

```
# not specifying file here
conf = mergeconf.MergeConf('myapp')
conf.add('name')
# other configuration items added, etc.
# ...

# now handle merge steps myself
conf.merge_file('app.conf')
conf.merge_environment()

# don't forget you have to validate when you're done
conf.validate()

# now ready to use
```
"""
from .mergeconf import MergeConf
from .mergeconfsection import MergeConfSection
from .mergeconfvalue import MergeConfValue
from . import exceptions
