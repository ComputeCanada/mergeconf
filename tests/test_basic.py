# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=unused-import,singleton-comparison
import os
import pytest
from tests.fixtures import (
  config, config_no_file, config_with_defaults, config_not_strict,
  config_strict, argparser, codename
)
import mergeconf

# ---------------------------------------------------------------------------
#                                                             helpers
# ---------------------------------------------------------------------------

codenameUC = codename.upper()

def envvarname(without_prefix):
  return f"{codenameUC}_{without_prefix.upper()}"

def clean_up_env():
  for key in os.environ:
    if key.startswith(codenameUC):
      del os.environ[key]

# ---------------------------------------------------------------------------
#                                                             tests
# ---------------------------------------------------------------------------

def test_no_config(config_no_file):
  """
  Tests we are able to parse an empty configuration, except it will fail on
  missing mandatory field ("shape").
  """
  with pytest.raises(mergeconf.exceptions.MissingConfiguration) as e:
    config_no_file.merge()
  print(e.value.missing)
  assert e.value.missing == "shape, section2.count"

def test_no_config_map(config_with_defaults):
  """
  Tests we are able to parse an empty configuration and get a map back.
  """
  config_with_defaults.merge()
  assert config_with_defaults['shape'] == 'triangle'
  assert config_with_defaults.shape == 'triangle'

  d = config_with_defaults.to_dict()
  print("Config as dict:")
  print(d)
  assert d == {
    'name': None,
    'colour': 'blue',
    'upsidedown': None,
    'rightsideup': True,
    'shape': 'triangle',
    'section2': {
      'count': 13,
      'z_index': 12,
      'ratio': None,
      'ferbs': '[1, 2, 3, 4]'
    }
  }

def test_config_only_env(config):
  """
  Tests we are able to parse a config defined only in the environment.
  """
  os.environ[envvarname("SHAPE")] = 'circle'
  os.environ[envvarname("UPSIDEDOWN")] = 'no'
  os.environ[envvarname("SECTION2_COUNT")] = '10'
  os.environ[envvarname("SECTION2_RATIO")] = '10.425'
  os.environ[envvarname("SECTION2_FUBAR")] = 'this does not even matter'
  config.merge()
  assert config['shape'] == 'circle'
  assert config['upsidedown'] == False
  assert config['rightsideup'] == True
  assert config['section2']['count'] == 10
  assert config['section2']['ratio'] == 10.425
  assert config.shape == 'circle'
  assert config.upsidedown == False
  assert config.rightsideup == True
  assert config.section2.count == 10
  assert config.section2.ratio == 10.425

  # clean up environment
  clean_up_env()

def test_config_only_file(config):
  """
  Tests we are able to correctly parse a config defined only in a file.
  """
  config.merge()
  assert config['shape'] == 'circle'
  assert config['upsidedown'] == False
  assert config['rightsideup'] == True
  assert config['section2']['count'] == 4
  assert config['section2']['ratio'] == 20.403

def test_config_file_and_env(config):
  """
  Tests we are able to correctly parse a config defined in both file and
  in the environment, with environment taking precedence.
  """
  os.environ[envvarname("SHAPE")] = 'triangle'
  os.environ[envvarname("UPSIDEDOWN")] = 'true'
  os.environ[envvarname("SECTION2_COUNT")] = '15'
  config.merge()
  assert config['shape'] == 'triangle'
  assert config['upsidedown'] == True
  assert config['rightsideup'] == True
  assert config['section2']['count'] == 15
  assert config['section2']['ratio'] == 20.403

  # clean up environment
  clean_up_env()

def test_config_missing_file(config):
  """
  Tests we handle a missing config file.
  """
  with pytest.raises(mergeconf.exceptions.MissingConfigurationFile) as e:
    config.merge_file('test2_missing.conf')
  assert e
  assert e.value.file == 'test2_missing.conf'

  # clean up environment
  clean_up_env()

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
  Tests a configuration initialized with defaults via a map and merging in
  a file.
  """
  config_with_defaults.merge_file('tests/test2.conf')
  assert config_with_defaults['shape'] == 'rectangle'
  assert config_with_defaults['colour'] == 'blue'
  assert config_with_defaults['upsidedown'] == False
  assert config_with_defaults['rightsideup'] == True
  assert config_with_defaults['section2']['count'] == 10
  assert config_with_defaults['section2']['ratio'] == 20.403
  assert config_with_defaults['section2']['z_index'] == 12

def test_add_with_defaults(config_with_defaults):
  """
  Tests a configuration initialized with defaults via a map.
  """
  section2 = config_with_defaults.add_section('section2')
  section2.add('feels', value='heavy')
  section2.add('width', value=10)
  section2.add('transparent', value=False)
  section2.add('ferbity', value=4.2)
  section2.add('ferbs', value=[1, 2, 3, 4])
  config_with_defaults.merge()

  # basically ensure none of the above become strings unless they already
  # are, or are an unsupported type
  assert config_with_defaults['section2']['feels'] == 'heavy'
  assert config_with_defaults['section2']['width'] == 10
  assert config_with_defaults['section2']['transparent'] == False
  assert config_with_defaults['section2']['ferbity'] == 4.2
  assert config_with_defaults['section2']['ferbs'] == '[1, 2, 3, 4]'
  assert config_with_defaults.section2.ferbs == '[1, 2, 3, 4]'

def test_iterate_values(config_with_defaults):
  """
  Tests iteration through a configuration.
  """
  config_with_defaults.merge_file('tests/test2.conf')
  print(config_with_defaults.to_dict())

  # iterate through main items
  it = iter(config_with_defaults)
  assert next(it)[0] == 'colour'
  assert next(it)[0] == 'shape'
  assert next(it)[0] == 'name'
  assert next(it)[0] == 'upsidedown'
  assert next(it)[0] == 'rightsideup'

  # iterate through sections
  for name in config_with_defaults.sections:
    assert name == 'section2'
    section = config_with_defaults[name]
    it = iter(section)
    assert next(it)[0] == 'count'
    assert next(it)[0] == 'z_index'
    assert next(it)[0] == 'ferbs'
    assert next(it)[0] == 'ratio'

def test_unconfigured_section_allowed(config_not_strict):
  """
  Tests that an unconfigured section is caught and an exception thrown.
  """
  config_not_strict.merge_file('tests/test3.conf')
  config_not_strict.validate()
  assert config_not_strict['section2']['snurf'] == 'garbage'
  assert config_not_strict['section3']['blarb'] == '32'
  assert config_not_strict['section3']['snarf'] == 'this is the way the world ends'

def test_unconfigured_item_not_allowed(config_strict):
  """
  Tests that an unconfigured configuration item is caught and an exception thrown.
  """
  with pytest.raises(mergeconf.exceptions.UndefinedConfiguration) as e:
    config_strict.merge_file('tests/test3.conf')
    config_strict.validate()
  assert e.value.section == 'section2'
  assert e.value.item == 'snurf'

def test_unconfigured_section_not_allowed(config_strict):
  """
  Tests that an unconfigured configuration section is caught and an exception thrown.
  """
  with pytest.raises(mergeconf.exceptions.UndefinedSection) as e:
    config_strict.merge_file('tests/test4.conf')
    config_strict.validate()
  assert e.value.section == 'section3'

#def test_deprecated_functionality(config):
#  """
#  Tests that attempted use of deprecated functionality results in an exception.
#  """
#  with pytest.raises(mergeconf.exceptions.Deprecated) as e:
#    config.add_boolean('thisshouldfail', True)
#  assert e.value.function == 'add_boolean'
#  assert e.value.version == '0.3'
#  with pytest.raises(mergeconf.exceptions.Deprecated) as e:
#    config.parse('fakefilename')
#  assert e.value.function == 'parse'
#  assert e.value.version == '0.3'

def test_garbage_item_by_index(config):
  """
  Tests that attempted access of undefined variable results in an exception.
  """
  config.merge()
  with pytest.raises(KeyError):
    print(config['whut'])

def test_garbage_item_by_attribute(config):
  """
  Tests that attempted access of undefined variable results in an exception.
  """
  config.merge()
  with pytest.raises(AttributeError):
    print(config.whut)

def test_map(config):
  """
  Tests the map() function by building a list of mandatory configuration
  items.
  """
  config.merge()

  def mandatories(sections, name, item):
    if item.mandatory:
      return f"{'.'.join(sections) + '.' if sections else ''}{name}"
    return None

  res = config.map(mandatories)
  print(res)
  assert res == ['shape', 'section2.count']

def test_args(config, argparser):
  """
  Tests that argument parsing is set up appropriately.
  """
  # configure argparser to support the designated config items in the fixture
  config.config_argparser(argparser)

  # now try interpreting some stuff
  args = argparser.parse_args(['--shape=square', '--upsidedown', '--section2-count=12'])
  assert argparser.format_usage() == \
    """usage: test [-h] [-c CONFIG] [-d] [-q] [--shape SHAPE] [--colour COLOUR]
            [--upsidedown] [--rightsideup] [--section1-fluff FLUFF]
            [--section2-count COUNT] [--section2-ratio RATIO]
"""
  config.merge(args)
  assert config.shape == 'square'
  assert config.section1.fluff == 'light'
  assert config.section2.count == 12
  assert config.upsidedown is True
  assert config.rightsideup is True

def test_sample_config(config):
  """
  Test that the sample configuration is generated correctly.
  """
  sample_config = config.sample_config()
  print("Sample configuration:\n\n```")
  print(sample_config)
  print("```")
  assert sample_config == \
"""# (str) Unique name for the thing
#name =

# (str) The shape of the thing
shape =

# (str) The colour of the thing
#colour = black

# (bool) Upside-downness of the thing
#upsidedown =

# (bool) Is this thing right-side-up
#rightsideup = True

[section1]
# (str) What level of fluffiness does this item exhibit
#fluff = light

# (int) It's hard to come up with examples
#density =

[section2]
# (int) How many of the thing
count =

# (float) The ratio of thing to thang
#ratio ="""
