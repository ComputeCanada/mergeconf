# module `mergeconf`

mergeconf - build a single configuration by merging multiple configuration
sources with order of precedence, based on immediacy.  Configurations can be
read from files (via ConfigParser), environment variables, and command-line
arguments (via ArgumentParser).  By default, configuration in files is
overridden by that in environment variables which in turn is overridden by
appropriate command-line arguments, but the library offers flexibility in
ordering.

## Deprecation notice

v0.4 is a significant refactoring and includes API changes.  Clients will need
to be updated accordingly or pin their versions to v0.3.

* [module `mergeconf`](#module-mergeconf)
  * [class `MergeConf`](#class-MergeConf)
    * [function `__init__`](#function-__init__)
    * [function `__iter__`](#function-__iter__)
    * [function `add`](#function-add)
    * [function `add_boolean`](#function-add_boolean)
    * [function `add_section`](#function-add_section)
    * [function `config_argparser`](#function-config_argparser)
    * [function `map`](#function-map)
    * [function `merge`](#function-merge)
    * [function `merge_args`](#function-merge_args)
    * [function `merge_environment`](#function-merge_environment)
    * [function `merge_file`](#function-merge_file)
    * [function `missing_mandatory`](#function-missing_mandatory)
    * [function `parse`](#function-parse)
    * [function `sample_config`](#function-sample_config)
    * [property `sections`](#property-sections)
    * [function `to_dict`](#function-to_dict)
    * [function `validate`](#function-validate)
  * [module `mergeconf.exceptions`](#module-mergeconf.exceptions)
    * [class `Deprecated`](#class-Deprecated)
    * [class `MissingConfiguration`](#class-MissingConfiguration)
    * [class `MissingConfigurationFile`](#class-MissingConfigurationFile)
    * [class `UndefinedConfiguration`](#class-UndefinedConfiguration)
    * [class `UndefinedSection`](#class-UndefinedSection)
    * [class `UnsupportedType`](#class-UnsupportedType)

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

## class `MergeConf`

Configuration class.  Initialized optionally with configuration items, then
additional items may be added explicitly (and must be if they are mandatory,
a specific type, etc.).  Once all items have been added the configuration is
finalized with merge(), validation checks are performed, and the realized
values can be extracted.

This class inherits from the MergeConfSection class, which contains methods
to define configuration items and sections and examine the configuration.

### function `__init__`

Initializes MergeConf class.

Args:
  * `codename` (**str**): Simple string which is assumed to prefix any related
    environment variables associated with the configuration (along with an
    underscore as separator), in order to avoid collisions in the
    environment's namespace.  For example, for an `app_name` configuration
    key, with a codename `MYAPP`, the corresponding environment variable
    would be `MYAPP_APP_NAME`.
  * `files` (**str** or **list**): filename or list of filenames for configuration
    files.  Files are applied in order listed, and so should be listed from
    least to most important.
  * `map` (**dict**): Configuration options which are neither mandatory nor of a
    specified type, specified as key, value pairs.
  * `strict` (**boolean**): If true, unexpected configuration sections or items
    will cause an exception (`UndefinedSection` or `UndefinedConfiguration`,
    respectively).  If false, they will be added to the merged
    configuration.

Note: The `map` argument is probably to be deprecated and removed at a
  later date.  Its utility is limited and should be avoided.

### function `add`

Add a configuration item.

Args:
  * `key` (**str**): Name of configuration item
  * `value` (**whatever**): Default value, None by default
  * `type` (**type**): Type of value
  * `mandatory` (**boolean**): Whether item is mandatory or not, defaults to
    False.
  * `cli` (**boolean**): Whether item should be included in command-line arguments
  * `description` (**str**): Short descriptive text that may appear in usage text
    or sample configurations

Notes: Type detection is attempted if not specified.

### function `add_boolean`

_Deprecated._  Add a configuration item of type Boolean.

Args:
  * `key` (**str**): Name of configuration item
  * `value` (**boolean**): Default value, None by default
  * `mandatory` (**boolean**): Whether item is mandatory or not, defaults to
    False.

Note: This is deprecated; simply use `add` with `type=bool`.

### function `add_section`

Add a subsection to this section and return its object.

### function `config_argparser`

Configure ArgumentParser instance with designated configuration items.

This will run through all configuration items and add any defined as
appropriate for command-line arguments in the parser.  This method must
therefore be called before the ArgumentParser instance can be used.  The
client may configure any of its own arguments and other sections before
and/or after calling this method.

Arguments are configured with help text based on the configuration items'
descriptions, if available.  Boolean configuration items do not take
arguments but instead will set a value opposite of their default, or True
if not was defined.

args:
  argparser: ArgumentParser object to populate with appropriate items.

### function `map`

Apply the given function to every item in this section and recursively for
subsections.

Args:
  fn: Function taking (sections, name, MergeConfValue) and returning some
    value, or None.

Returns:
  List of values returned by function.  Values of None are not included.

### function `merge`

Takes configuration definition and any configuration files specified and
reads in configuration, overriding default values.  These are in turn
overridden by corresponding variables found in the environment, if any.
Basic validations are performed.

This is a convenience method to handle the typical configuration
hierarchy and process.  Clients may also call other `merge_*` methods in
any order, but should call `validate()` if so to ensure all mandatory
configurations are specified.

Args:
  args: Arguments processed by ArgumentParser.  Any matching appropriate
    are merged in after environment variables.

### function `merge_args`

Merge command-line arguments parsed by ArgumentParser.

Only configuration items identified with `cli=True` on creation
(in `add()`) will be considered.  See `config_argparser()` for adding the
arguments to an ArgumentParser object automatically.

Args:
  args: Arguments returned by parse_args().

### function `merge_environment`

Using configuration definition, reads in variables from the environment
matching the pattern `<codename>[_<section_name>]_<variable_name>`.  Any
variable found not matching a defined configuration item is returned in
a list: in this way variables outside the merged configuration context can
be handled, such as a variable specifying an alternative config file.

Returns:
  Map of environment variables matching the application codename.  The
  keys will be stripped of the codename prefix and will be converted to
  lowercase.

### function `merge_file`

Merge configuration defined in file.  File is expected to adhere to the
format defined by ConfigParser, with `=` used as the delimiter and
interpolation turned off.  In addition, unlike ConfigParser, config files
may include variables defined prior to any section header.

Args:
  * `config_file` (**str**): Path to config file.

### function `missing_mandatory`

Check that each mandatory item in this section and subsections has a
defined value.

Returns:
  List of fully qualified mandatory items without a defined value, in
  section-dot-item syntax.

### function `parse`

Deprecated.  See merge().

### function `sample_config`

Create a sample configuration.

This will be more informative if configuration items have been specified
with descriptions.

Returns:
  A string describing a sample configuration file.

Note:
  The sample configuration will have this format:

  ```
  # (str) this is the first item
  name =

  # (int) this is the second item which has a default value
  #count = 1

  [section1]
  # (bool) this item has no default
  #has_car =

  # (str) This is mandatory
  description =
  ```

### property `sections`

Provides list of section names.

### function `to_dict`

Return dictionary representation of configuration or section.

### function `validate`

Checks that mandatory items have been defined in configuration.  If not,
throws exception.  Client may also use `missing_mandatory()`.

Subclasses may add additional validation but should first call the parent
implementation as the test for mandatory items is primary.

## module `mergeconf.exceptions`

Exceptions raised by MergeConf package.

### class `Deprecated`

Raised for hard deprecations where functionality has been removed and the
API is not available at all.

Attributes:
  * `version`: the last version in which this functionality is available.
  * `message`: further information to assist the user.

### class `MissingConfiguration`

Raised if mandatory configuration items are missing.

Attributes:
  * `missing`: string list of missing items in section-dot-key notation,
    separated by commas.

### class `MissingConfigurationFile`

Raised if the specified configuration file is missing or otherwise
unreadable.

Attributes:
  * `file`: the missing file

### class `UndefinedConfiguration`

Raised if a configuration item is found that was not defined for the parser.

Attributes:
  * `section`: the section name
  * `item`: the item name

### class `UndefinedSection`

Raised if a section is found that was not defined for the parser.

Attributes:
  * `section`: the section name

### class `UnsupportedType`

Raised if a configuration item is added with an unsupported type.

Attributes:
  * `type`: the unsupported type
