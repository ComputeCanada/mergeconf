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
  conf.add('SECTION1_NAME')
  conf.add('SECTION1_COLOUR', value='black')
  conf.add('SECTION1_SHAPE', mandatory=True)
  conf.add_boolean('SECTION1_UPSIDEDOWN')
  conf.add_boolean('SECTION1_RIGHTSIDEUP', value=True)
  conf.add('SECTION2_COUNT', type=int)
  conf.add('SECTION2_RATIO', type=float)

  return conf

@pytest.fixture
def config_with_defaults():
  """
  Create a full configuration including some defaults.
  """

  # set some basic defaults
  defaults = {
    'SECTION1_COLOUR': 'blue',
    'SECTION1_SHAPE': 'triangle',
    'SECTION2_COUNT': 13,
    'SECTION2_Z_INDEX': 12,
    'SECTION2_FERBS': [1, 2, 3, 4]
  }

  # create mergeconf object for configuration
  conf = mergeconf.MergeConf('test', map=defaults)

  # add configuration items of various types
  conf.add('SECTION1_NAME')
  conf.add('SECTION1_SHAPE', mandatory=True)
  conf.add_boolean('SECTION1_UPSIDEDOWN')
  conf.add_boolean('SECTION1_RIGHTSIDEUP', value=True)
  conf.add('SECTION2_COUNT', type=int)
  conf.add('SECTION2_RATIO', type=float)

  return conf
