# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
import pytest
from mergeconf import mergeconf

# used to prefix environment variables
codename = 'test'

@pytest.fixture
def config():
  """
  Create a full configuration using all of the features.
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
  section2.add('count', type=int)
  section2.add('ratio', type=float)

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
  Create a full configuration and allow for unconfigured sections.
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
