# 

[[_TOC_]]

## Classes
    

###  MergeConf

<code>class <b>MergeConf</b>(codename, files=None, map=None, strict=True)</code>

  

  
Configuration class.  Initialized optionally with configuration items, then
additional items may be added explicitly (and must be if they are mandatory,
a specific type, etc.).  Once all items have been added the configuration is
finalized with merge(), validation checks are performed, and the realized
values can be extracted.

This class inherits from the MergeConfSection class, which contains methods
to define configuration items and sections and examine the configuration.

Initializes MergeConf class.
  

**Arguments**

* **`Note`**: The `map` argument is probably to be deprecated and removed at a
  later date.  Its utility is limited and should be avoided.
  

#### Ancestors
  * [MergeConfSection](docs/mergeconfsection.md#MergeConfSection)

  

---

####  <code>add_boolean(self, key, value=None, mandatory=False)</code>

  

  
_Deprecated._  Add a configuration item of type Boolean.
  

**Arguments**

* **`Note`**: This is deprecated; simply use `add` with `type=bool`.
  

  

---

####  <code>config_argparser(self, argparser)</code>

  

  
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
  

  

---

####  <code>map(self, fn)</code>

  

  
Apply the given function to every item in this section and recursively for
subsections.
  

**Arguments**

* **`fn`**: Function taking (sections, name, MergeConfValue) and returning some
    value, or None.

  
**Returns**

List of values returned by function.  Values of None are not included.

  

---

####  <code>merge(self, args=None)</code>

  

  
Takes configuration definition and any configuration files specified and
reads in configuration, overriding default values.  These are in turn
overridden by corresponding variables found in the environment, if any.
Basic validations are performed.

This is a convenience method to handle the typical configuration
hierarchy and process.  Clients may also call other `merge_*` methods in
any order, but should call `validate()` if so to ensure all mandatory
configurations are specified.
  

**Arguments**

* **`args`**: Arguments processed by ArgumentParser.  Any matching appropriate
    are merged in after environment variables.
  

  

---

####  <code>merge_args(self, args)</code>

  

  
Merge command-line arguments parsed by ArgumentParser.

Only configuration items identified with `cli=True` on creation
(in `add()`) will be considered.  See `config_argparser()` for adding the
arguments to an ArgumentParser object automatically.
  

**Arguments**

* **`args`**: Arguments returned by parse_args().
  

  

---

####  <code>merge_environment(self)</code>

  

  
Using configuration definition, reads in variables from the environment
matching the pattern `<codename>[_<section_name>]_<variable_name>`.  Any
variable found not matching a defined configuration item is returned in
a list: in this way variables outside the merged configuration context can
be handled, such as a variable specifying an alternative config file.
  

**Returns**

Map of environment variables matching the application codename.  The
keys will be stripped of the codename prefix and will be converted to
lowercase.

  

---

####  <code>merge_file(self, config_file)</code>

  

  
Merge configuration defined in file.  File is expected to adhere to the
format defined by ConfigParser, with `=` used as the delimiter and
interpolation turned off.  In addition, unlike ConfigParser, config files
may include variables defined prior to any section header.
  

  

---

####  <code>parse(self, *args, **kwargs)</code>

  

  
Deprecated.  See merge().
  

  

---

####  <code>sample_config(self)</code>

  

  
Create a sample configuration.

This will be more informative if configuration items have been specified
with descriptions.
  

**Returns**

A string describing a sample configuration file.

**Note**

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

  

---

####  <code>validate(self)</code>

  

  
Checks that mandatory items have been defined in configuration.  If not,
throws exception.  Client may also use `missing_mandatory()`.

Subclasses may add additional validation but should first call the parent
implementation as the test for mandatory items is primary.
  

      

---

---
Generated by [pdoc 0.9.2](https://pdoc3.github.io/pdoc).
