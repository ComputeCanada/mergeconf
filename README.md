# module `mergeconf`

mergeconf - build a single configuration by merging multiple configuration
sources with order of precedence, based on immediacy.  Currently: Default
values are overridden by values read from configuration file which in turn are
overridden by values read from environment variables.

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
    * [function `merge`](#function-merge)
    * [function `merge_environment`](#function-merge_environment)
    * [function `merge_file`](#function-merge_file)
    * [function `missing_mandatory`](#function-missing_mandatory)
    * [function `parse`](#function-parse)
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

conf = mergeconf.MergeConf(files='app.conf')
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
conf = mergeconf.MergeConf()
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

### function `__iter__`

Support iterating through configuration items.

### function `add`

Add a configuration item.

Args:
  * `key` (**str**): Name of configuration item
  * `value` (**whatever**): Default value, None by default
  * `mandatory` (**boolean**): Whether item is mandatory or not, defaults to
    False.
  * `type` (**type**): Type of value

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

### function `merge`

Takes configuration definition and any configuration files specified and
reads in configuration, overriding default values.  These are in turn
overridden by corresponding variables found in the environment, if any.
Basic validations are performed.

This is a convenience method to handle the typical configuration
hierarchy and process.  Clients may also call other `merge_*` methods in
any order, but should call `validate()` if so to ensure all mandatory
configurations are specified.

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
