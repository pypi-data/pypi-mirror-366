# -*- coding: utf-8 -*-
"""
EC-PeT Configuration Management Module
======================================

Comprehensive configuration system for eddy-covariance processing workflows.
Provides hierarchical parameter management with validation, defaults handling,
file I/O operations, and type-safe parameter access. Supports both full and
reduced configuration formats for workflow flexibility.

Key Features:
    - Hierarchical parameter organization (group.parameter structure)
    - Type-safe parameter access with automatic conversion
    - Default configuration with user overrides
    - File pattern expansion for data discovery
    - Configuration validation and error correction
    - Minimized configuration export (non-default values only)

"""
import logging
import os
import re
import site
import sys

try:
    import importlib.resources as resources

    __haveimp__ = True
except:
    __haveimp__ = False

from ._version import __title__
from . import ecfile
from .ecutils import quote, str_to_bool, uncomment, unquote

logger = logging.getLogger(__name__)

home = os.path.expanduser("~")
package_name = __title__
cwd = os.getcwd()


class Config(object):
    """
    Configuration management class with hierarchical parameter organization.

    Provides type-safe parameter access, validation, and comparison with
    default values. Supports both full and reduced configuration modes
    for different workflow requirements.
    """
    _dict = {}

    def __init__(self, values=None, reduced=False):
        """
        Initialize configuration object with optional parameter values.

        :param values: Initial parameter values, defaults to None
        :type values: dict, optional
        :param reduced: Whether to use reduced mode (overrides only), defaults to False
        :type reduced: bool, optional
        """
        self._dict = {}
        if values is None:
            logger.debug('Config init from defaults')
            self._dict = defaults.copy()
        elif not isinstance(values, dict):
            logger.error('Config init values not of type dict')
            raise TypeError
        else:
            if not reduced:
                for k, v in defaults.items():
                    self._dict[k] = ''
            self._dict.update(values)
        self.changed = False

    def put(self, k, v):
        """
        Set parameter value with automatic formatting.

        :param k: Parameter key
        :type k: str
        :param v: Parameter value
        :type v: any
        """
        self._dict = _put(self._dict, k, v)

    def get(self, name, group='', kind=None, unlist=True, na=''):
        """
        Retrieve parameter value with type conversion and validation.

        :param name: Parameter name
        :type name: str
        :param group: Parameter group, defaults to ''
        :type group: str, optional
        :param kind: Type conversion ('str', 'int', 'float', 'bool'), defaults to None
        :type kind: str, optional
        :param unlist: Return scalar for single values, defaults to True
        :type unlist: bool, optional
        :param na: Value for missing parameters, defaults to ''
        :type na: any, optional
        :return: Parameter value with requested type conversion
        :rtype: any
        """
        return _get(self._dict, name, group, kind, unlist, na)

    def check(self):
        """
        Validate configuration parameters for completeness and consistency.

        :return: True if configuration is valid
        :rtype: bool
        """
        try:
            check_basic(self._dict)
        except ValueError:
            return False
        except Exception as e:
            raise e
        else:
            return True

    def is_default(self, name, group=''):
        """
        Check if parameter has default value.

        :param name: Parameter name
        :type name: str
        :param group: Parameter group, defaults to ''
        :type group: str, optional
        :return: True if parameter has default value
        :rtype: bool
        """
        k = tokenize(name, group)
        if self.get(k) == _get(defaults, k):
            return True
        else:
            return False

    def items(self):
        """Return iterator over configuration items."""
        return self._dict.items()

    def keys(self):
        """Return iterator over configuration keys."""
        return self._dict.keys()

    def to_dict(self):
        """Return configuration as dictionary."""
        return self._dict


class ConfigError(Exception):
    """Exception raised for configuration validation errors."""
    pass


# ----------------------------------------------------------------
#
# read config file that contains no sections
# (http://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/28563058#28563058)
#


def read_file(filename):
    """
    Read configuration file with group.key = value format.

    :param filename: Path to configuration file
    :type filename: str
    :return: Dictionary with configuration parameters
    :rtype: dict

    Parses configuration files using simple key=value syntax with
    dot notation for parameter groups and automatic comment removal.
    """
    logger.debug('parsing config file %s' % filename)
    if not os.path.exists(filename):
        logger.error('file not found: %s' % filename)
        raise FileNotFoundError
    with open(filename, 'r') as fid:
        content = fid.readlines()
    cd = {}
    for line in content:
        # remove comments
        lc = uncomment(line.strip())
        # detect non-empty lines by '='
        if '=' in lc:
            k, v = lc.split('=', 2)
            # put token -> value in dict
            # with any quotes, as in _dict
            cd[k.strip()] = v.strip()
    return cd


# ----------------------------------------------------------------


def write_file(filename, cd):
    """
    Write configuration parameters to file.

    :param filename: Output file path
    :type filename: str
    :param cd: Configuration dictionary to write
    :type cd: dict
    :return: Success flag
    :rtype: bool

    Creates configuration files with key=value format suitable for
    reading by read_file function.
    """
    logger.debug('writing config file %s' % filename)
    # write all values
    # with quotes, as in _dict
    with open(filename, 'w') as fid:
        for k, v in cd.items():
            if v is None:
                x = ''
            else:
                x = v
            fid.write('%s = %s\n' % (k, x))
    return True


# ----------------------------------------------------------------


def find_imagepath():
    """
    Locate GUI image resources in installation.

    :return: Path to image directory
    :rtype: str
    :raises EnvironmentError: If image directory not found

    Searches standard installation paths for GUI image resources
    using both modern and legacy package management approaches.
    """
    if __haveimp__:
        ref = resources.files(__title__) / 'images'
        with resources.as_file(ref) as p:
            pp = [p]
    else:
        pp = [os.path.join(sys.prefix, 'share', package_name, 'images')]+[
            os.path.join(x, package_name, 'images') for x in site.getsitepackages()]+[
            os.path.join(cwd, 'images')
        ]
    ip = None
    for p in pp:
        logger.debug('probing image path %s' % p)
        if ip is None and os.path.isdir(p):
            if os.path.isfile(os.path.join(p, 'gui-image_text.png')):
                logger.debug('probing image %s' %
                              os.path.join(p, 'gui-image_text.png'))
                logger.debug('images path found')
                ip = p
    if ip is None:
        raise EnvironmentError
    else:
        return ip


# ----------------------------------------------------------------

def default():
    """
    Locate default configuration file in installation.

    :return: Path to default configuration file
    :rtype: str
    :raises EnvironmentError: If default configuration not found

    Searches standard installation paths for default.conf using
    both modern package resources and legacy file system approaches.
    """
    if __haveimp__:
        ref = resources.files(__title__) / 'default.conf'
        with resources.as_file(ref) as p:
            dp = [p]
    else:
        exedir = os.path.abspath(os.path.dirname(sys.argv[0]))
        dp = [os.path.join(home, '.'+package_name),
              os.path.join(sys.prefix, 'share', package_name, 'default.conf')]+[
            os.path.join(x, package_name, 'default.conf') for x in site.getsitepackages()]+[
            os.path.join(exedir, 'default.conf')
        ]
    df = None
    for p in dp:
        logger.debug('probing defaults file %s' % p)
        if df is None and os.path.isfile(p):
            logger.debug('defaults file found')
            df = p
            break
    if df is None:
        raise EnvironmentError
    else:
        return df


# ----------------------------------------------------------------

def check_basic(conf, correct=True):
    """
    Validate essential configuration parameters with optional correction.

    :param conf: Configuration dictionary to validate
    :type conf: dict
    :param correct: Whether to apply automatic corrections, defaults to True
    :type correct: bool, optional
    :return: Validated and optionally corrected configuration
    :rtype: dict
    :raises ConfigError: For invalid required parameters

    Validates required parameters for eddy-covariance processing including
    wind components, temperature sensors, and pressure measurements.
    """
    #
    # read column numbers into dict
    col_f = {}
    obj_f = re.compile(r'fastfmt\.(.*)_col')
    for k, v in conf.items():   # iter on both keys and values
        m = obj_f.match(k)
        if m:
            col_f[m.group(1)] = int(float(v))
    col_s = {}
    obj_s = re.compile(r'slowfmt\.(.*)_col')
    for k, v in conf.items():   # iter on both keys and values
        m = obj_s.match(k)
        if m:
            col_s[m.group(1)] = int(float(v))

    # raise if a required variable is missing:
    # ... 3D Wind
    if min(col_f['U'], col_f['V'], col_f['W']) <= 0:
        err = 'less than three columns specified for wind'
        logger.error(err)
        raise ConfigError(err)
    # ... any fast Temperature
    if max(col_f['Tsonic'], col_f['Tcouple']) <= 0:
        logger.debug(
            'Tsonic={:d}; Tcouple={:d}'.format(+col_f['Tsonic'], col_f['Tcouple']))
        err = 'no columns specified for temperature'
        logger.error(err)
        raise ConfigError(err)
    # ... any pressure
    if max(col_s['Pref'], col_f['Press']) <= 0:
        logger.debug(
            'Pref={:d}; Press={:d}'.format(+col_s['Pref'], col_f['Press']))
        err = 'no pressure column specified at all'
        logger.error(err)
        raise ConfigError(err)

    # consistency between Sensor Type ("absent") and (internal) netCDF variable
    # ... for Humidity
    if col_f['Humidity'] <= 0:
        logger.warning('no column specified for H2O')
        if correct and conf.get('Humidity_var') != '':
            conf.put('Humidity_var', '')
            logger.info('adjusted "Humidity_var" setting to ""')
    else:
        if correct and conf.get('Humidity_var') == '':
            conf.put('Humidity_var', defaults['Humidity_var'])
            logger.info('adjusted "Humidity_var" setting to "%s"' %
                         defaults['Humidity_var'])

    # ... for CO2
    if col_f['CO2'] <= 0:
        logger.warning('no column specified for CO2')
        if correct and conf.get('CO2_var') != '':
            conf.put('CO2_var', '')
            logger.info('adjusted "CO2_var" setting to ""')
    else:
        if correct and conf.get('CO2_var') == '':
            conf.put('CO2_var', defaults['CO2_var'])
            logger.info('adjusted "CO2_var" setting to "%s"' %
                         defaults['CO2_var'])

    # ... for TSonic
    if col_f['Tsonic'] <= 0:
        logger.info('no column specified for Tsonic')
        if correct and conf.get('Tsonic_var') != '':
            conf.put('Tsonic_var', '')
            logger.info('adjusted "Tsonic_var" setting to ""')
    else:
        if correct and conf.get('Tsonic_var') == '':
            conf.put('Tsonic_var', defaults['Tsonic_var'])
            logger.info('adjusted "Tsonic_var" setting to "%s"' %
                         defaults['Tsonic_var'])

    # ... for Tcouple
    if col_f['Tcouple'] <= 0:
        logger.info('no column specified for Tcouple')
        if correct and conf.get('Tcouple_var') != '':
            conf.put('Tcouple_var', '')
            logger.info('adjusted "Tcouple_var" setting to ""')
    else:
        if correct and conf.get('Tcouple_var') == '':
            conf.put('Tcouple_var', defaults['Tcouple_var'])
            logger.info('adjusted "Tcouple_var" setting to "%s"' %
                         defaults['Tcouple_var'])

    # warn if diagnostics are missing
    if col_f['diag'] <= 0:
        logger.warning('no column specified for Anemometer diganostics')
    if col_f['agc'] <= 0:
        logger.warning('no column specified for IRGA diganostics')

    return conf


# ----------------------------------------------------------------


def complete(arglist):
    """
    Create complete configuration from user parameters and defaults.

    :param arglist: User-provided configuration parameters
    :type arglist: dict or Config
    :return: Complete configuration with defaults applied
    :rtype: Config

    Merges user parameters with default values, discarding parameters
    not present in default configuration.
    """
    # convert arglist do Config Object:
    if isinstance(arglist, dict):
        conf = Config(arglist, reduced=True)
    elif isinstance(arglist, Config):
        conf = arglist
    else:
        raise ValueError('arglist must be either dict or Config')
    # create default Config Object:
    res = Config()
    # copy elements over
    for k in res.keys():
        if k in conf.keys():
            if not conf.is_default(k):
                res.put(k, conf.get(k))
                logger.debug('copying option value: %s: %s' %
                             (k, conf.get(k)))
            else:
                logger.debug('filling with default: %s' % k)
    return res


# ----------------------------------------------------------------
#
# replace all values in old config by values in arglist
# note: params in arglist that do not occur in old config are APPENDED
#


def apply(old, arglist):
    """
    Apply parameter changes to existing configuration.

    :param old: Original configuration dictionary
    :type old: dict
    :param arglist: Parameter updates to apply
    :type arglist: dict
    :return: Updated configuration
    :rtype: dict

    Updates existing configuration with new values, appending
    parameters not present in original configuration.
    """
    conf = old.copy()
    for i in arglist:
        if arglist[i] is not None:
            logger.debug('applying option: %s = %s' % (i, arglist[i]))
            conf[i] = arglist[i]
    return conf


# ----------------------------------------------------------------


def reduce(conf):
    """
    Create reduced configuration containing only non-default parameters.

    :param conf: Complete configuration to reduce
    :type conf: Config
    :return: Reduced configuration with non-default values only
    :rtype: Config

    Extracts only parameters that differ from default values,
    useful for creating minimal configuration files.
    """
    #
    # find parameters with non-default values
    #
    values = {}
    for k, v in conf.items():
        if conf.is_default(k):
            logger.info('reducing   option %s [%s]' % (k, defaults[k]))
        else:
            logger.info('extracting option %s: %s [%s]' % (
                k, v, defaults[k]))
            values[k] = v
    changed = Config(values, reduced=True)
    return changed


# ----------------------------------------------------------------
#
# replaces glob patterns in configuration by list of filenames
#


def unglob(conf):
    """
    Expand file patterns in configuration to actual file lists.

    :param conf: Configuration with file patterns
    :type conf: Config
    :return: Configuration with expanded file lists
    :rtype: Config

    Resolves glob patterns in RawFastData and RawSlowData parameters
    to actual file lists, validating directory existence.
    """
    #
    # shorthands:
    RawDir = conf.get('RawDir')
    RawFastData = conf.get('RawFastData', unlist=False)
    RawSlowData = conf.get('RawSlowData', unlist=False)

    #
    # test if RawDir exists
    logger.debug('got RawDir string "%s"' % RawDir)
    if RawDir == '':
        RawDir = '.'
    if not os.path.isdir(RawDir):
        logger.critical('data directory not found: %s' % RawDir)
        quit()
    else:
        logger.info('data directory found: %s' % RawDir)

    #
    # create fast-data file list (expand patterns)
    list_fast = []
    for x in RawFastData:
        list_fast += ecfile.find(RawDir, x)
    # quit if nothing is found
    if len(list_fast) == 0:
        logger.critical('no fast-data files found')
        quit()
    else:
        logger.info('found %i fast-data files' % len(list_fast))
    conf.put('RawFastData', list_fast)
    logger.debug('RawFastData = {}'.format(list_fast))

    #
    # create slow-data file list (expand patterns)
    if RawSlowData == ['']:
        list_slow = list_fast
        logger.info('using fast-data files as slow-data files)')
    else:
        list_slow = []
        for x in RawSlowData:
            list_slow += ecfile.find(RawDir, x)
    # quit if nothing is found
    if len(list_slow) == 0:
        logger.critical('no slow-data files found')
        quit()
    else:
        logger.info('found %i slow data files' % len(list_slow))
    conf.put('RawSlowData', list_slow)
    logger.debug('RawSlowData = {}'.format(list_slow))

    return conf


# ----------------------------------------------------------------

def write(conf, filename=None, full=False):
    """
    Write configuration to file with optional minimization.

    :param conf: Configuration to write
    :type conf: Config
    :param filename: Output file path (auto-generated if None), defaults to None
    :type filename: str, optional
    :param full: Write complete configuration vs. changes only, defaults to False
    :type full: bool, optional
    :return: Success flag
    :rtype: bool

    Creates configuration files with either complete parameters (full=True)
    or only non-default values (full=False) for workflow documentation.
    """
    if filename is None:
        try:
            x = conf.get('ConfName')
        except:
            filename = defaults['ConfName']
        else:
            filename = x
    #
    # write full or minimized config ?
    #
    if full is True:
        # complete returns Config object -> to_dict
        c = complete(conf).to_dict()
    elif full is False:
        # reduce returns dict -> keep it
        c = reduce(conf)
    else:
        raise TypeError('parameter "full" must be True or False')
    write_file(filename, c)

    return True
    # ----------------------------------------------------------------


def tokenize(name, group=''):
    """
    Generate configuration token from parameter name and group.

    :param name: Parameter name
    :type name: str
    :param group: Parameter group (optional trailing dot allowed), defaults to ''
    :type group: str, optional
    :return: Configuration token
    :rtype: str
    :raises KeyError: If token not found in default configuration

    Creates dot-notation tokens (e.g., 'Par.DoTilt') with case-insensitive
    matching against default configuration parameters.
    """
    if not isinstance(group, str):
        logger.error(
            'group name must be type str but is {:s}'.format(type(group)))
        raise TypeError
    if not isinstance(name, str):
        logger.error(
            'parameter name must be type str but is {:s}'.format(type(group)))
        raise TypeError
    if group == '':
        token = name
    elif group.endswith('.'):
        token = group+name
    else:
        token = '.'.join([group, name])
    for k, v in defaults.items():
        if token.upper() == k.upper():
            token = k
            break
    else:
        # if for loop was not broken, i.e. token not found:
        logger.error('not in configuration: {:s}'.format(token))
        raise KeyError
    return token


#
# get a configuration value by group + name
#


def _get(conf, name, group='', kind=None, unlist=True, na=''):
    """
    Retrieve configuration value with type conversion and validation.

    :param conf: Configuration dictionary
    :type conf: dict
    :param name: Parameter name
    :type name: str
    :param group: Parameter group, defaults to ''
    :type group: str, optional
    :param kind: Type conversion ('str', 'int', 'float', 'bool'), defaults to None
    :type kind: str, optional
    :param unlist: Return scalar for single values, defaults to True
    :type unlist: bool, optional
    :param na: Value for empty parameters, defaults to ''
    :type na: any, optional
    :return: Configuration value with type conversion
    :rtype: any

    Internal function providing type-safe parameter access with automatic
    list handling and quote processing.
    """
    if not isinstance(conf, dict):
        logger.error('conf name must be type dict but is %s' %
                      format(type(group)))
        raise TypeError
    token = tokenize(name, group)
    for k, v in conf.items():
        if token.upper() == k.upper():
            string = v
            break
    else:
        # if for loop was not broken, i.e. token not found:
        logger.error('not in configuration: {:s}'.format(token))
        raise KeyError
    # split multiple values:
    if isinstance(string, (str, bytes)):
        # NOT aware of quotes:
        # field=val.split()
        # THIS is aware of quotes:
        # https://bytes.com/topic/python/answers/44243-quote-aware-string-splitting
        regex = re.compile(r'''
            '.*?' | # single quoted substring
            ".*?" | # double quoted substring
            \S+     # all the rest
            ''', re.VERBOSE)
        field = [unquote(x) for x in regex.findall(string)]
        ##
    elif isinstance(string, list):
        field = [unquote(x) if isinstance(
            x, (str, bytes)) else x for x in string]
    else:
        logger.error('config value {} type is not list or str but {}'.format(
            token, type(string)))
        raise TypeError
#    field=[string]
    n = len(field)
    logger.insane('token %s returned %i fields: %s ' % (token, n, str(field)))
    if n > 0:
        if kind == 'float':
            try:
                val = [float(x) if x != '' else na for x in field]
            except:
                logger.error('value of token {:s} is no float'.format(token))
                raise ValueError
        elif kind == 'int':
            try:
                val = [int(float(x)) if x != '' else na for x in field]
            except:
                logger.error('value of token {:s} is no number'.format(token))
                raise ValueError
        elif kind == 'bool':
            try:
                val = [str_to_bool(x) if x != '' else na for x in field]
            except:
                logger.error('value of token {:s} is no bool'.format(token))
                raise ValueError
        elif kind == 'str' or kind is None:
            val = field
        else:
            raise ValueError('unknown kind: "%s"' % kind)
#      val=[unquote(x) for x in field]

        #
        # return single value as scalar, not list
        if unlist and hasattr(val, "__len__") and len(val) == 1:
            val = val[0]
    else:
        if unlist:
            val = na
        else:
            val = []
    logger.insane('get {}: {}'.format(token, val))
    return val


def _put(conf, name, value, group='', kind=None, unlist=True):
    """
    Store configuration value with proper formatting and quoting.

    :param conf: Configuration dictionary
    :type conf: dict
    :param name: Parameter name
    :type name: str
    :param value: Parameter value to store
    :type value: any
    :param group: Parameter group, defaults to ''
    :type group: str, optional
    :param kind: Type specification (unused), defaults to None
    :type kind: str, optional
    :param unlist: List handling flag (unused), defaults to True
    :type unlist: bool, optional
    :return: Updated configuration dictionary
    :rtype: dict

    Internal function for storing parameters with automatic quote handling
    for complex values and list serialization.
    """
    if not isinstance(conf, dict):
        logger.error(
            'conf name must be type dict but is {:s}'.format(type(group)))
        raise TypeError
    token = tokenize(name, group)
    # join multiple values:
    if isinstance(value, (list, tuple)):
        line = ' '.join([quote(x) for x in value])
    else:
        line = quote(value)
    #
    conf[token] = line
    return conf


# ----------------------------------------------------------------
#
defaults = read_file(default())
