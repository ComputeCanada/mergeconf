# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=unused-import,singleton-comparison
import os
import pytest
from tests.fixtures import config, codename
from multiconf import multiconf, exceptions

# ---------------------------------------------------------------------------
#                                                             helpers
# ---------------------------------------------------------------------------

def clean_up_env(codename):
  for key in os.environ:
    if key.startswith(codename):
      del os.environ[key]

# ---------------------------------------------------------------------------
#                                                             tests
# ---------------------------------------------------------------------------

def test_no_config(config):
  """
  Tests we are able to parse an empty configuration, except it will fail on
  missing mandatory fields.
  """
  with pytest.raises(exceptions.MissingConfiguration) as e:
    config.parse()
  assert e.value.missing == ['SECTION1_SHAPE']

def test_config_only_env(config):
  """
  Tests we are able to parse a config defined only in the environment.
  """
  os.environ[codename + "_SECTION1_SHAPE"] = 'circle'
  os.environ[codename + "_SECTION1_UPSIDEDOWN"] = 'no'
  os.environ[codename + "_SECTION2_COUNT"] = '10'
  os.environ[codename + "_SECTION2_RATIO"] = '10.425'
  os.environ[codename + "_SECTION2_FUBAR"] = 'this does not even matter'
  config.parse()
  assert config['SECTION1_SHAPE'] == 'circle'
  assert config['SECTION1_UPSIDEDOWN'] == False
  assert config['SECTION1_RIGHTSIDEUP'] == True
  assert config['SECTION2_COUNT'] == 10
  assert config['SECTION2_RATIO'] == 10.425

  # clean up environment
  clean_up_env(codename)

def test_config_only_file(config):
  """
  Tests we are able to correctly parse a config defined only in a file.
  """
  config.parse('tests/test1.conf')
  assert config['SECTION1_SHAPE'] == 'circle'
  assert config['SECTION1_UPSIDEDOWN'] == False
  assert config['SECTION1_RIGHTSIDEUP'] == True
  assert config['SECTION2_COUNT'] == 10
  assert config['SECTION2_RATIO'] == 20.403

def test_config_file_and_env(config):
  """
  Tests we are able to correctly parse a config defined in both file and
  in the environment, with environment taking precedence.
  """
  os.environ[codename + "_SECTION1_SHAPE"] = 'triangle'
  os.environ[codename + "_SECTION1_UPSIDEDOWN"] = 'true'
  os.environ[codename + "_SECTION2_COUNT"] = '15'
  config.parse('tests/test1.conf')
  assert config['SECTION1_SHAPE'] == 'triangle'
  assert config['SECTION1_UPSIDEDOWN'] == True
  assert config['SECTION1_RIGHTSIDEUP'] == True
  assert config['SECTION2_COUNT'] == 15
  assert config['SECTION2_RATIO'] == 20.403

  # clean up environment
  clean_up_env(codename)

def test_config_missing_file(config):
  """
  Tests we handle a missing config file.
  """
  os.environ[codename + "_CONFIG"] = 'test2_missing.conf'
  with pytest.raises(exceptions.MissingConfigurationFile) as e:
    config.parse('test2_missing.conf')
  assert e
