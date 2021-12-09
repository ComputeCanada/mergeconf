# Changelog

## v0.5.1 (2021-12-09) Support for prior command-line arguments

Added:

- Support for arguments configured directly in ArgumentParser object, outside
  of MergeConf.

## v0.5 (2021-12-04) Support for command-line arguments.

Added:

- Support for integration with Python's ArgumentParser library so that
  command-line arguments can be merged into configuration.

## v0.4 (2021-11-29) Significant overhaul.

Added:

- Configuration files may have items declared outside of sections.  This allows
  for simpler configurations or for configurations where defining a section
  header isn't appropriate.
- Configuration items may be accessed using dot notation, for example,
  `myconf.section.item` as well as by index notation.
- Can now iterate through sections.

Updated:

- Documentation includes examples.
- Everything in the MergeConf class.

## v0.3 (2021-05-10) Minor tweaks

Added:

- MissingConfigurationFile exception has `file` attribute for the missing
  filename.

## v0.2 (2021-04-13) First packaged release

First semi-mature release ready for use by the world.

Added:

- Support for specific types (int, float) as well as str and bool.
  Support for boolean values normalized to be consistent with other
  types.

Updated:

- Improved error handling.

## v0.1 (2020-12-22) First implementation.

* Reads from environment, configuration file

