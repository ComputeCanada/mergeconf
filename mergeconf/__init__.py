# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
"""
mergeconf - build a single configuration by merging multiple configuration
sources with order of precedence, based on immediacy.  Configurations can be
read from files (via ConfigParser), environment variables, and command-line
arguments (via ArgumentParser).  By default, configuration in files is
overridden by that in environment variables which in turn is overridden by
appropriate command-line arguments, but the library offers flexibility in
ordering.

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

### Adding command-line arguments

MergeConf can work with Python's built-in `argparse` package to handle
command-line arguments in addition to configuration files and environment
variables:

```
conf = mergeconf.MergeConf('myapp')

# use the `cli` parameter to indicate inclusion in command-line arguments, and
# use the `description` parameter so there's help text in the command usage
conf.add('name', description='Name of the thing', cli=True)
...

# set up argparse however you like
parser = argparse.ArgumentParser(prog='myapp')
parser.add_argument(...)
...

# now call MergeConf to configure the parser for indicated configurations
conf.config_argparser(parser)

# parse arguments
args = parser.parse_args()

# merge configuration
conf.merge(args)
```

### Generating sample configuration

MergeConf also provides a way to generate a sample configuration file using the
configuration item descriptions, types and default values.

```
print(conf.sample_config())
```

Produces something like:

```
# (str) Unique name for the thing
#name =

# (str) The shape of the thing
shape =

# (str) The colour of the thing
#colour = black

# (bool) Upside-downness of the thing
#upsidedown =

# (bool) Is this thing right-side-up
#rightsideup = True

[section1]
# (str) What level of fluffiness does this item exhibit
#fluff = light

# (int) It's hard to come up with examples
#density =

[section2]
# (int) How many of the thing
count =

# (float) The ratio of thing to thang
#ratio =
```

Note that:
* expected types are described in the comment and what follows is the description
* default values are provided in the commented-out assignment
* optional items are commented out
* mandatory items are not commented out (but blank)
"""

from .mergeconf import MergeConf
from .mergeconfsection import MergeConfSection
from .mergeconfitem import MergeConfItem
from . import exceptions
