# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
import pytest
from multiconf import multiconf

# used to prefix environment variables
codename = 'test'

@pytest.fixture
def config():
  """
  Create a full configuration using all of the features.
  """

  # create multiconf object for configuration
  conf = multiconf.MultiConf('test')

  # add configuration items of various types
  conf.add('SECTION1_NAME')
  conf.add('SECTION1_COLOUR', value='black')
  conf.add('SECTION1_SHAPE', mandatory=True)
  conf.add_boolean('SECTION1_UPSIDEDOWN')

  return conf
