# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
"""
mergeconf - build a single configuration by merging multiple configuration
sources with order of precedence, based on immediacy.  Currently: Default
values are overridden by values read from configuration file which in turn are
overridden by values read from environment variables.
"""
from .mergeconf import MergeConf
