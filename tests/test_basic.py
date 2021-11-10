# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=unused-import,singleton-comparison
import os
import pytest
from tests.fixtures import config, config_with_defaults, codename
import mergeconf

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
  with pytest.raises(mergeconf.exceptions.MissingConfiguration) as e:
    config.parse()
  assert e.value.missing == ['SECTION1_SHAPE']

def test_no_config_map(config_with_defaults):
  """
  Tests we are able to parse an empty configuration and get a map back.
  """
  config_with_defaults.parse()
  assert config_with_defaults['SECTION1_SHAPE'] == 'triangle'

  d = dict(config_with_defaults)
  print(d)
  assert d == {
    'SECTION1_NAME': None,
    'SECTION1_COLOUR': 'blue',
    'SECTION1_UPSIDEDOWN': None,
    'SECTION1_RIGHTSIDEUP': True,
    'SECTION1_SHAPE': 'triangle',
    'SECTION2_COUNT': 13,
    'SECTION2_Z_INDEX': 12,
    'SECTION2_RATIO': None,
    'SECTION2_FERBS': '[1, 2, 3, 4]'
  }

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
  with pytest.raises(mergeconf.exceptions.MissingConfigurationFile) as e:
    config.parse('test2_missing.conf')
  assert e
  assert e.value.file == 'test2_missing.conf'

def test_unsupported_type():
  """
  Tests the attempted use of an unsupported type throws an exception.
  """
  conf = mergeconf.MergeConf('test')
  with pytest.raises(mergeconf.exceptions.UnsupportedType) as e:
    conf.add('SECTION1_NAME', type=list)
  assert e.value.type == 'list'

def test_default_values(config_with_defaults):
  """
  Tests a configuration initialized with defaults via a map.
  """
  config_with_defaults.parse('tests/test2.conf')
  assert config_with_defaults['SECTION1_SHAPE'] == 'rectangle'
  assert config_with_defaults['SECTION1_COLOUR'] == 'blue'
  assert config_with_defaults['SECTION1_UPSIDEDOWN'] == False
  assert config_with_defaults['SECTION1_RIGHTSIDEUP'] == True
  assert config_with_defaults['SECTION2_COUNT'] == 10
  assert config_with_defaults['SECTION2_RATIO'] == 20.403
  assert config_with_defaults['SECTION2_Z_INDEX'] == 12

def test_add_with_defaults(config_with_defaults):
  """
  Tests a configuration initialized with defaults via a map.
  """
  config_with_defaults.add('SECTION2_FEELS', value='heavy')
  config_with_defaults.add('SECTION2_WIDTH', value=10)
  config_with_defaults.add('SECTION2_TRANSPARENT', value=False)
  config_with_defaults.add('SECTION2_FERBITY', value=4.2)
  config_with_defaults.add('SECTION2_FERBS', value=[1, 2, 3, 4])
  config_with_defaults.parse()

  # basically ensure none of the above become strings unless they already
  # are, or are an unsupported type
  assert config_with_defaults['SECTION2_FEELS'] == 'heavy'
  assert config_with_defaults['SECTION2_WIDTH'] == 10
  assert config_with_defaults['SECTION2_TRANSPARENT'] == False
  assert config_with_defaults['SECTION2_FERBITY'] == 4.2
  assert config_with_defaults['SECTION2_FERBS'] == '[1, 2, 3, 4]'
