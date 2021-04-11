# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=unused-import
import os
import pytest
from tests.fixtures import config, codename
from multiconf import multiconf

def test_no_config(config):
  """
  Tests we are able to parse an empty configuration, except it will fail on
  missing mandatory fields.
  """
  with pytest.raises(multiconf.MissingConfiguration) as e:
    config.parse()
  assert e.value.missing == ['SECTION1_SHAPE']

def test_config_only_env(config):
  """
  Tests we are able to parse a config defined only in the environment.
  """
  varname = codename + "_SECTION1_SHAPE"
  os.environ[varname] = 'circle'
  config.parse()
  assert config['SECTION1_SHAPE'] == 'circle'
