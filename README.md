# module `mergeconf`

mergeconf - build a single configuration by merging  multiple configuration
sources with order of precedence, based on immediacy.  Currently: Default
values are overridden by values read from configuration file which in turn are
overridden by values read from environment variables.

* [module `mergeconf`](#module-mergeconf)
  * [class `MergeConf`](#class-MergeConf)
    * [function `__init__`](#function-__init__)
    * [function `add`](#function-add)
    * [function `add_boolean`](#function-add_boolean)
    * [function `parse`](#function-parse)
  * [class `MergeConfValue`](#class-MergeConfValue)


## class `MergeConf`

Configuration class.  Initialized optionally with configuration items, then
additional items may be added explicitly (and must be if they are mandatory,
a specific type, etc.).  Once all items have been added the configuration is
finalized with parse(), validation checks are performed, and the realized
values can be extracted.

### function `__init__`

Initializes MergeConf class.

Args:
  * `codename` (**str**): Simple string which is assumed to prefix any related
    environment variables associated with the configuration (along with an
    underscore as separator), in order to avoid collisions in the
    environment's namespace.  For example, for an `app_name` configuration
    key, with a codename `MYAPP`, the corresponding environment variable
    would be `MYAPP_APP_NAME`.
  * `map` (**dict**): Configuration options which are neither mandatory nor of a
    specified type, specified as key, value pairs.

Note: The `map` argument is probably to be deprecated and removed at a
  later date.  Its utility is limited and should be avoided.

### function `add`

Add a configuration item.

Args:
  * `key` (**str**): Name of configuration item
  * `value` (**whatever**): Default value, None by default
  * `mandatory` (**boolean**): Whether item is mandatory or not, defaults to
    False.
  * `type` (**type**): Type of value

### function `add_boolean`

_Deprecated._  Add a configuration item of type Boolean.

Args:
  * `key` (**str**): Name of configuration item
  * `value` (**boolean**): Default value, None by default
  * `mandatory` (**boolean**): Whether item is mandatory or not, defaults to
    False.

Note: This is deprecated; simply use `add` with `type=bool`.  This will be
  removed in a future release.

### function `parse`

Takes configuration definition and default configuration file and reads in
configuration, overriding default values.  These are in turn overridden by
corresponding variables found in the environment, if any.  Basic
validations are performed.

Args:
  * `default_config_file` (**str**): Path to default configuration file.  This may
    be overridden if an alternative configuration file is specified in the
    environment.

Returns:
  A dict of key-value configuration items.

## class `MergeConfValue`

Basic configuration item and base class for more complex types.


