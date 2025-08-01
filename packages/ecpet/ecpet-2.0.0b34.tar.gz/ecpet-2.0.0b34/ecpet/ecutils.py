# -*- coding: utf-8 -*-
"""
EC-PeT Utility Functions
========================

Core utility functions and constants for eddy-covariance data processing.
Provides physical constants, variable definitions, string manipulation,
atmospheric calculations, and progress reporting functionality.

"""


import logging
import warnings

import numpy as np

#
#  optional : inter-tread communication
#
try:
    #  from wx.lib.pubsub import pub
    from pubsub import pub
    have_com = True
except ImportError:
    pub = None
    have_com = False

logger = logging.getLogger(__name__)

#
# globals
#
#
# project stages:
stages = ['start', 'pre', 'plan', 'flux', 'post', 'out']
#
# slow variables
refvar = ['pp', 'tc', 'rh']
# corresponding config name stems
refstem = {'pp': 'Pref', 'rh': 'RelHum', 'tc': 'Tref'}
#
# fast variables
metvar = ['ux', 'uy', 'uz',
          'co2', 'h2o', 'ts',
          'pres', 'tcoup']
diavar = ['diag_csat',
          'diag_irga']
var = metvar+diavar
specvar = ['q', 'qco2']
ecvar = metvar+specvar
# corresponding flag name stems (metvar)
val = {'ux': 'ux_', 'uy': 'uy_', 'uz': 'uz_',
       'co2': 'co2', 'h2o': 'h2o', 'ts': 'ts_',
       'pres': 'prs', 'tcoup': 'tc_'}
# corresponding config name stems (var)
stem = {'ux': 'U', 'uy': 'V', 'uz': 'W',
        'co2': 'CO2', 'h2o': 'Humidity', 'ts': 'Tsonic',
        'pres': 'Press', 'tcoup': 'Tcouple',
        'diag_csat': 'diag', 'diag_irga': 'agc'}

#
# flux values ("physical quantities")
#
qpvar = ['rhoson', 'rhocoup',
         'meanw', 'vectwind', 'dirfrom'
         'hson', 'hcoup', 'ecov', 'ewebb', 'esum',
         'ustar', 'tausum',
         'fco2', 'fco2webb', 'fco2sum']
qpname = {'rhoson': 'RhoSon', 'rhocoup': 'RhoTc',
          'meanw': 'Wnorot', 'vectwind': 'U_vect', 'dirfrom': 'U_dir',
          'hson': 'HSonic', 'hcoup': 'HTc',
          'ecov': 'LvEcov', 'ewebb': 'LvEWebb', 'esum': 'SumLvE',
          'ustar': 'Ustar', 'tausum': 'Tau',
          'fco2': 'FCO2cov', 'fco2webb': 'FCO2Webb', 'fco2sum': 'SumFCO2'}
qpunit = {'rhoson': '[kg/m^3]', 'rhocoup': '[kg/m^3]',
          'meanw': '[m/s]', 'vectwind': '[m/s]', 'dirfrom': '[deg]',
          'hson': '[W/m^2]', 'hcoup': '[W/m^2]',
          'ecov': '[W/m^2]', 'ewebb': '[W/m^2]', 'esum': '[W/m^2]',
          'ustar': '[m/s]', 'tausum': '[N/m^2]',
          'fco2': '[kg/m^2/s]', 'fco2webb': '[kg/m^2/s]', 'fco2sum': '[kg/m^2/s]'}

# postprocessor variables
flx = ['tau', 'h_0', 'e_0', 'fc2']

# internal storage variable names and units
#
intvar = ['year', 'doy', 'hhmm', 'sec']+var
# units
intunit = {'year': '-', 'doy': '-', 'hhmm': '-', 'sec': '-',
           'ux': 'm/s', 'uy': 'm/s', 'uz': 'm/s',
           'co2': 'mg/m^3', 'h2o': 'g/m^3', 'ts': 'C',
           'pres': 'Press', 'tcoup': 'C',
           'diag_csat': '-', 'diag_irga': '-'}
intstem = stem.copy()
intstem.update({'hhmm': 'Hourmin', 'doy': 'Doy',
                'sec': 'sec', 'year': 'year'})
# build names of config tokens to read
intnamkey = {x: intstem[x]+'_var' for x in intvar}

#
# qc test ids
tst = ['spk', 'res', 'drp', 'lim', 'mom', 'dis', 'nst', 'lag',
       'chr', 'mad', 'fws', 'cot', 'bet', 'vst', 'ftu', 'srv', 'cmx']
pts = ['mnw', 'itc', 'exs', 'fkm', 'exe']
# qc test measurer ids
qmn = ['qmnan', 'qmspk', 'qmebi', 'qmcon', 'qmskw', 'qmkrt',
       'qmtrs', 'qmvrn', 'qmred', 'qmrnu', 'qmrnv',
       'qmrns', 'qmlag', 'qmcsp', 'qmrat', 'qmmsp', 'qmfwd',
       'qmtrd', 'qmbdv', 'qmbpp', 'qmbpq', 'qmbpi', 'qmbpx',
       'qmvst', 'qmftu', 'qmsrv', 'qmcmx']
q2n = ['qmmnw', 'qmitu', 'qmitw', 'qmitq', 'qmitt', 'qmfkf', 'qmfkx']
#
# config group name prefixes
sonprefix = 'SonCal.'
coupprefix = 'CoupCal.'
hygprefix = 'HygCal.'
co2prefix = 'Co2Cal.'
parprefix = 'par.'
qc_prefix = 'qcconf.'
sccprefix = 'slowfmt.'
fccprefix = 'fastfmt.'
#
# physical constants
Kelvin = 273.15      # Kelvin - Celsius offset
cp = 1004.         # specific heat of dry air (J/(kgK))
g = 9.81           # standard gravity (m/s²)
kappa = 0.4        # von-Karman constant
l_v = 2.50E6       # evaporation heat of water (J/kg)
pnull = 100000.     # potential temperature reference pressure (Pa)
r_l = 287.         # gas constant of dry air
r_v = 461.         # gas constant of water vapor
r_gas = 8314.      # Universal gas constant (J/kmol.K)
omega = 7.2921E-5  # earth rotation frequency (1/s)
FracO2 = 0.21      # fraction of O2 molecules in air (1)
M_O2 = 32.         # molecular weight of oxygen (g/mol)
M_air = 28.966     # molecular weight of dry air (g/mol)
M_vapour = 18.016  # molecular weight of water vapour (g/mol)

#
# mathematical constants
pi = 3.141592654
deg2rad = pi/180.
#
# other constants
GammaR = 403.      # gamma*R Constant in correction of sonic temperature
# for cross-wind (part of the Schooten correction)
# m^2 s^-2 K^-1
Epsilon = 1.E-30   # Infinitesimal small number

# ----------------------------------------------------------------
#
# Constants to characterize types of measurement apparatus, all starting
# with ''Ap''
#


def code_ap(i):
    """
    Convert apparatus code to descriptive string.

    :param i: Apparatus code number
    :type i: int
    :return: Descriptive string for the apparatus type
    :rtype: str
    """
    ap = ['Undefined',       #  0
          'ApCSATSonic',     #  1
          'ApTCouple',       #  2
          'ApCampKrypton',   #  3
          'ApPt100',         #  4
          'ApPsychro',       #  5
          'ApSon3Dcal',      #  6
          'ApMierijLyma',    #  7
          'ApLiCor7500',     #  8
          'ApKaijoTR90',     #  9
          'ApKaijoTR61',     # 10
          'ApGillSolent',    # 11
          'ApGenericSonic']  # 12
    i = int(i)
    if i not in range(len(ap)):
        i = 0
    logger.insane('code Ap {:d}: "{:s}"'.format(i, ap[i]))
    return ap[i]

# ----------------------------------------------------------------
# ----------------------------------------------------------------
#
#
# utility functions
#
# ----------------------------------------------------------------
#
# announce stage in gui progress dialog
#

global progress_state
progress_state = 0.

def progress_stage(stage):
    """
    Announce processing stage to GUI progress dialog.

    :param stage: Processing stage identifier
    :type stage: str
    """
    if have_com:
        pub.sendMessage('stage', msg=stage)
    logger.normal('[==== Entering stage: {:6s} ====]'.format(stage))

def progress_reset():
    """Reset progress to zero percent."""
    progress_percent(0.)

def progress_percent(perc):
    """
    Set absolute progress percentage.

    :param perc: Progress percentage (0-100)
    :type perc: float
    """
    global progress_state
    progress_state = perc
    if have_com:
        pub.sendMessage('progress', msg=perc)
    #else:
    logger.normal('[---- Stage progress: {:6.2f} ----]'.format(
        float(progress_state)))


def progress_pulse():
    """Send a pulse to indicate activity without specific progress."""
    if have_com:
        pub.sendMessage('pulse')


def progress_increment(perc):
    """
    Increment progress by specified percentage.

    :param perc: Percentage increment
    :type perc: float
    """
    global progress_state
    progress_state += perc
    if have_com:
        pub.sendMessage('increment', msg=perc)
    #else:
    logger.normal('[---- Stage progress: {:6.2f} ----]'.format(
        float(progress_state)))


def progress_info(txt):
    """
    Send informational message to progress dialog.

    :param txt: Information text
    :type txt: str
    """
    if have_com:
        pub.sendMessage('info', msg=txt)
    logger.normal('[---- progress info : {:6s} ----]'.format(txt))


def progress_done():
    """Mark current stage as completed."""
    global progress_state
    progress_state = 100.
    if have_com:
        pub.sendMessage('done')
    #else:
    logger.normal('[==== Stage finished. ====]')


def escape(string, chars=' ,'):
    """
    Escape special characters in string.

    :param string: String to escape
    :type string: str
    :param chars: Characters to escape, defaults to ' ,'
    :type chars: str
    :return: Escaped string
    :rtype: str
    """
    #    res = re.escape(string)
    res = ''
    for x in string:
        if x in chars:
            res += '\\'+x
        else:
            res += x
    return res


def unescape(string, chars=' ,'):
    """
    Remove escape characters from string.

    :param string: String to unescape
    :type string: str
    :param chars: Characters to unescape, defaults to ' ,'
    :type chars: str
    :return: Unescaped string
    :rtype: str
    """
    #    res = re.escape(string)
    inp = string
    res = ''
    while len(inp) > 0:
        #        print(inp)
        for c in chars:
            if inp.startswith('\\'+c):
                res += c
                inp = inp[2:]
                continue
        else:
            res += inp[0]
            inp = inp[1:]
    return res


def str_to_bool(string):
    """
    Convert string representation to boolean.

    :param string: String to convert
    :type string: str
    :return: Boolean value
    :rtype: bool
    """
    if (isinstance(string, (str, bytes)) and
            str(string).upper() in ['Y', 'YES', 'T', 'TRUE', '.TRUE.']):
        res = True
    elif (isinstance(string, (str, bytes)) and
          str(string).upper() in ['N', 'NO', 'F', 'FALSE', '.FALSE.']):
        res = False
    else:
        res = bool(int(float(string)))
    return res


def bool_to_str(x):
    """
    Convert boolean to string representation.

    :param x: Boolean value
    :type x: bool
    :return: String representation ('T' or 'F')
    :rtype: str
    :raises TypeError: If x is not boolean
    """
    if not isinstance(x, bool):
        logger.error('val %s is not bool' % x)
        raise TypeError
    if x:
        string = 'T'
    else:
        string = 'F'
    return string


def quote(string, always=False, required=False):
    """
    Conditionally quote string for safe output.

    :param string: String to quote
    :type string: str
    :param always: Always quote regardless of content, defaults to False
    :type always: bool
    :param required: Only quote if necessary for protection, defaults to False
    :type required: bool
    :return: Quoted or unquoted string
    :rtype: str
    :note: By default, numbers are not quoted, non-numeric strings are quoted
    """
    # convert None to empty string
    if string is None:
        string = ''
    # format known types
    elif isinstance(string, int):
        string = '{:d}'.format(string)
    elif isinstance(string, float):
        string = '{:f}'.format(string)
    elif isinstance(string, bool):
        string = bool_to_str(string)
    # format anything else using format()
    elif not isinstance(string, str):
        string = format(string)
    # test if we have a number string
    try:
        float(string)
    except ValueError:
        number = False
    else:
        number = True
    if escape(string) != string:
        special = True
    else:
        special = False
    if always or (not number and not required) or special:
        return '"'+string+'"'
    else:
        return string


def unquote(string):
    """
    Remove quotes around a string.

    :param string: String to unquote
    :type string: str
    :return: String without surrounding quotes
    :rtype: str
    """
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    elif string.startswith('\'') and string.endswith('\''):
        string = string[1:-1]
    return string


def uncomment(string):
    """
    Remove comments from string (everything after # or //).

    :param string: String to process
    :type string: str
    :return: String without comments
    :rtype: str
    """
    for sep in ['#', '//']:
        if sep in string:
            string = string.split(sep, 1)[0]
    return string


def isglob(string):
    """
    Check if string contains glob pattern characters.

    :param string: String to check
    :type string: str
    :return: True if string contains glob patterns
    :rtype: bool
    """
    if ('*' in string or
        '?' in string or
            ('[' in string and ']' in string)):
        return True
    else:
        return False


def sub_dict(somedict, somekeys, default=None):
    """
    Extract subset of dictionary with specified keys.

    :param somedict: Source dictionary
    :type somedict: dict
    :param somekeys: Keys to extract
    :type somekeys: list
    :param default: Default value for missing keys, defaults to None
    :type default: any
    :return: Dictionary with specified keys
    :rtype: dict
    """
    return dict([(k, somedict.get(k, default)) for k in somekeys])


def deg2dms(deg):
    """
    Convert degrees to degrees, minutes, seconds.

    :param deg: Decimal degrees
    :type deg: float
    :return: Tuple of (degrees, minutes, seconds)
    :rtype: tuple
    """
    m, s = divmod(deg*3600, 60)
    d, m = divmod(m, 60)
    return d, m, s


def dms2deg(d, m, s):
    """
    Convert degrees, minutes, seconds to decimal degrees.

    :param d: Degrees
    :type d: float
    :param m: Minutes
    :type m: float
    :param s: Seconds
    :type s: float
    :return: Decimal degrees
    :rtype: float
    """
    deg = float(d) + float(m)/60. + float(s)/3600.
    return deg


def getfields(line):
    """
    Split CSV (TOA5) line into fields.

    :param line: CSV line to split
    :type line: str
    :return: List of field values
    :rtype: list
    """
    #
    #  split line read from file into fields
    #
    line = str(line).replace('\n', '')
    fields = line.split(',')
    for i in range(0, len(fields)):
        fields[i] = fields[i].replace('"', '')
    return fields


def string_to_interval(string):
    """
    Convert string to time interval in seconds.

    :param string: Time interval string (e.g., '30m', '1h', '86400')
    :type string: str
    :return: Time interval in seconds
    :rtype: float
    :raises ValueError: If string format is invalid
    :note: Supported suffixes: s (seconds), m (minutes), h (hours), d (days), w (weeks)
    """
    suffix = ''
    try:
        interval = float(string)
    except ValueError:
        if string is None or len(string) <= 1:
            raise ValueError(
                'missing number in time interval string: %s' % string)
        else:
            suffix = string[-1]
            number = string[:-1]
        try:
            interval = float(number)
        except ValueError:
            raise ValueError(
                'incomprehensible time interval string: %s' % number)
    if suffix == '':
        # seconds (implicit)
        factor = 1
    elif suffix == 's':
        # seconds (explicit)
        factor = 1
    elif suffix == 'm':
        # minutes
        factor = 60
    elif suffix == 'h':
        # hours
        factor = 3600
    elif suffix == 'd':
        # days
        factor = 86400
    elif suffix == 'w':
        # weeks
        factor = 7*86400
    else:
        logger.insane('s', suffix)
        raise ValueError(
            'unkown time unit "%s" in time interval string: %s' % (suffix, string))
    return factor*interval


def amount(x):
    """
    Calculate magnitude (length) of a vector.

    :param x: 1-dimensional vector (list, tuple, np.array or DataFrame)
    :type x: array-like
    :return: Vector magnitude
    :rtype: float
    :raises TypeError: If argument doesn't coerce to vector
    """
    # concert argument to array
    try:
        x = np.array(x)
    except (TypeError, ValueError):
        logger.error('argument does not coerce to array')
        raise TypeError
    # check if argument is a vector
    if len(x.shape) != 1:
        logger.error('argument does not coerce to vector')
        raise TypeError
    # calculate amount
    return np.sqrt((x*x).sum())


def find_nearest(array, value):
    """
    Find nearest value in numpy array.

    :param array: Array to search
    :type array: numpy.ndarray
    :param value: Target value
    :type value: float
    :return: Nearest value in array
    :rtype: float
    """
    idx = (np.abs(array-value)).argmin()
    return array[idx]


def spechum(RhoV, T, P):
    """
    Calculate specific humidity of wet air.

    :param RhoV: Water vapor density [kg/m³]
    :type RhoV: float
    :param T: Temperature [K]
    :type T: float
    :param P: Pressure [Pa]
    :type P: float
    :return: Specific humidity [kg/kg]
    :rtype: float
    """
    if not (np.isnan(RhoV) or np.isnan(T) or np.isnan(P)):
        RhoWet = rhowet(RhoV, T, P)  # [kg/m^3]
        q = RhoV/RhoWet            # [kg/kg]
    else:
        q = np.nan
    return q


def specco2(RhoCO2, RhoV, T, P):
    """
    Calculate specific CO2 concentration of wet air.

    :param RhoCO2: CO2 density [kg/m³]
    :type RhoCO2: float
    :param RhoV: Water vapor density [kg/m³]
    :type RhoV: float
    :param T: Temperature [K]
    :type T: float
    :param P: Pressure [Pa]
    :type P: float
    :return: Specific CO2 concentration [kg/kg]
    :rtype: float
    """
    if not (np.isnan(RhoV) or np.isnan(RhoCO2) or np.isnan(T) or np.isnan(P)):
        RhoWet = rhowet(RhoV, T, P)       # [kg/m^3]
        qc = RhoCO2/RhoWet              # [kg/kg]
    else:
        qc = np.nan
    return qc


def rhodry(RhoV, T, P):
    """
    Calculate density of dry air component in wet air using Dalton's law.

    :param RhoV: Water vapor density [kg/m³]
    :type RhoV: float
    :param T: Temperature [K]
    :type T: float
    :param P: Pressure [Pa]
    :type P: float
    :return: Dry air density [kg/m³]
    :rtype: float
    :raises ValueError: If pressure or temperature units appear incorrect
    """
    if not (np.isnan(RhoV) or np.isnan(T) or np.isnan(P)):
        if P < 10000.:
            logger.error('P = {:f} seems to be not given in Pa'.format(P))
            raise ValueError
        if T < 150.:
            logger.error('T = {:f} seems to be not given in K'.format(T))
            raise ValueError
        r = P/(r_l*T) - RhoV*r_v/r_l	  # [kg m^{-3}]
    else:
        r = np.nan
    return r


def rhowet(RhoV, T, P):
    """
    Calculate density of humid air.

    :param RhoV: Water vapor density [kg/m³]
    :type RhoV: float
    :param T: Temperature [K]
    :type T: float
    :param P: Pressure [Pa]
    :type P: float
    :return: Wet air density [kg/m³]
    :rtype: float
    """
    if not (np.isnan(RhoV) or np.isnan(T) or np.isnan(P)):
        r = rhodry(RhoV, T, P) + RhoV  # [kg m^{-3}]
    else:
        r = np.nan
    return r


def lvt(T):
    """
    Calculate latent heat of vaporization as function of temperature.

    :param T: Temperature [K]
    :type T: float
    :return: Latent heat of vaporization [J/kg]
    :rtype: float
    :note: Uses Henderson‐Sellers (1984) equation
    """
    #
    # Calculate the latent heat of vaporization
    # Inputs
    #       T  : temperature (K)
    # Returns
    #       latent heat of vaporization  (J/kg)
    #
    # Arnold Moene (EC-Pack) Source?
    # lv = (2501 - 2.375*(T-273.15))*1.0E3
    #
    # Henderson‐Sellers (1984) DOI: 10.1002/qj.49711046626
    #
    lv = 1.91846E6*(T/(T-33.91))**2
    #
    return lv


def cpt(T):
    """
    Calculate specific heat of dry air as function of temperature.

    :param T: Temperature [K]
    :type T: float
    :return: Specific heat of dry air [J/(kg·K)]
    :rtype: float
    :note: Uses :cite:`gar_92` equation A20
    """
    #
    # Calculate the specific heat of dry air
    # Inputs
    #     T  : temperature (K)
    # Returns
    #     specific heat of dry air (J/(kg*K))
    # Source
    #     equation (A20) in Garrat, J.R., 1992. 'The Atmospheric Boundary
    #     layer', Cambridge University Press
    c_p = 1005 + ((T - 250) ** 2.0) / 3364

    return c_p


def fint(x):
    """
    Convert flag value to integer, handling NaN values.

    :param x: Flag value as float
    :type x: float
    :return: Flag value as integer (-1 for NaN)
    :rtype: int
    :note: np.nan is converted to -1
    """
    if np.isfinite(x):
        i = int(x)
    else:
        i = -1
    return i


def allnanok(fun, arg):
    """
    Suppress numpy warnings for all-NaN operations.

    Suppresses RuntimeWarning "All-NaN axis encountered" when all values
    are NaN in numpy nan* function arguments.

    :param fun: numpy nan function (nanmin, nanmax, nanmean, etc.)
    :type fun: function
    :param arg: Array-like argument for the function
    :type arg: array-like
    :return: Function result
    :rtype: float
    :note: Returns np.nan silently for all-NaN arrays
    """
    # Convert to numpy array if needed
    arr = np.asarray(arg)

    # Pre-check for empty or all-NaN cases
    if arr.size == 0 or np.isnan(arr).all():
        return np.nan

    # If we get here, there's at least one valid value
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            res = fun(arr)
        except ValueError:
            res = np.nan
        except Exception as e:
            print(f"Error in allnanok: {type(arg)}")
            print(f"Argument: {arg}")
            raise e
    return res

def safe_len(arg):
    """
    Safely get length of DataFrame or array.

    :param arg: Object to inspect
    :type arg: any
    :return: Length if object has len attribute, otherwise 0
    :rtype: int
    """
    try:
        n = len(arg)
    except TypeError:
        logger.error('argument is has no len attribute')
        n = 0
    return n


def intersect_lists(list1: list, list2: list):
    """
    Find intersection of two lists preserving order from first list.

    :param list1: First list
    :type list1: list
    :param list2: Second list
    :type list2: list
    :return: Elements present in both lists, ordered as in list1
    :rtype: list
    """
    re = sorted(set(list1).intersection(set(list2)),
                key=lambda x: list1.index(x))
    return re
