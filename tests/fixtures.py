# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
import argparse
import pytest
from mergeconf import mergeconf

# used to prefix environment variables
codename = 'test'

@pytest.fixture
def config_no_file():
  """
  Create a full configuration without specifying a configuration file.
  """

  # create mergeconf object for configuration
  conf = mergeconf.MergeConf('test')

  # add configuration items of various types
  conf.add('name')
  conf.add('shape', mandatory=True)
  conf.add('colour', value='black')
  #conf.add_boolean('upsidedown')
  #conf.add_boolean('rightsideup', value=True)
  conf.add('upsidedown', type=bool)
  conf.add('rightsideup', type=bool, value=True)
  section2 = conf.add_section('section2')
  section2.add('count', type=int, mandatory=True)
  section2.add('ratio', type=float)

  return conf

@pytest.fixture
def config():
  """
  Create a full configuration using all of the features.
  """

  # create mergeconf object for configuration
  conf = mergeconf.MergeConf('test', files='tests/test1.conf')

  # add configuration items of various types
  conf.add('name')
  conf.add('shape', mandatory=True, cli=True)
  conf.add('colour', value='black', cli=True)
  conf.add('upsidedown', type=bool, cli=True)
  conf.add('rightsideup', type=bool, value=True, cli=True)
  section2 = conf.add_section('section2')
  section2.add('count', type=int, mandatory=True, cli=True)
  section2.add('ratio', type=float, cli=True)

  return conf

@pytest.fixture
def config_with_defaults():
  """
  Create a full configuration including some defaults.
  """

  # set some basic defaults
  defaults = {
    'colour': 'blue',
    'shape': 'triangle',
    'section2': {
      'count': 13,
      'z_index': 12,
      'ferbs': [1, 2, 3, 4]
    }
  }

  # create mergeconf object for configuration
  conf = mergeconf.MergeConf('test', map=defaults)

  # add configuration items of various types
  conf.add('name')
  conf.add('shape', mandatory=True)
  conf.add('upsidedown', type=bool)
  conf.add('rightsideup', type=bool, value=True)
  section2 = conf.add_section('section2')
  section2.add('count', type=int)
  section2.add('ratio', type=float)

  return conf

@pytest.fixture
def config_not_strict():
  """
  Create a full configuration and allow for unconfigured sections.
  """

  # create mergeconf object for configuration
  conf = mergeconf.MergeConf('test', strict=False)

  # add configuration items of various types
  conf.add('name')
  conf.add('shape', mandatory=True)
  conf.add('upsidedown', type=bool)
  conf.add('rightsideup', type=bool, value=True)
  section2 = conf.add_section('section2')
  section2.add('count', type=int)
  section2.add('ratio', type=float)

  return conf

@pytest.fixture
def config_strict():
  """
  Create a full configuration and don't permit unconfigured sections.
  """

  # create mergeconf object for configuration
  conf = mergeconf.MergeConf('test', strict=True)

  # add configuration items of various types
  conf.add('name')
  conf.add('shape', mandatory=True)
  conf.add('upsidedown', type=bool)
  conf.add('rightsideup', type=bool, value=True)
  section2 = conf.add_section('section2')
  section2.add('count', type=int)
  section2.add('ratio', type=float)

  return conf

@pytest.fixture
def argparser():
  """
  Create a configuration with argparse enabled for command-line arguments.
  """
  # create argument parsing object
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-c", "--config", type=str,
                help="Configuration file",
                default=__file__ + ".conf")
  argparser.add_argument("-d", "--debug",
                help="Debug output",
                action='store_true')
  argparser.add_argument("-q", "--quiet",
                help="No output",
                action='store_true')
  return argparser
