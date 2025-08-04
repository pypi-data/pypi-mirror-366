"""
EC-PeT Preprocessing Module
===========================

Comprehensive quality control and preprocessing routines for eddy-covariance data.
Implements quality checks following :cite:`vim_jaot97` (Vickers & Mahrt, 1997)
and extended tests from Mauder et al. (2013). Provides multiprocessing support
for efficient processing of large datasets.

The module performs:
    - Spike detection and removal
    - Data resolution and dropout analysis
    - Statistical moment analysis
    - Discontinuity detection using Haar wavelets
    - Stationarity tests
    - Lag correlation analysis
    - Instrument diagnostic filtering

@author: druee
"""
import io
import logging
import os
import warnings
from multiprocessing import Pool, Manager

import netCDF4 as nc
import numpy as np
import pandas as pd
from scipy import stats

from . import ecdb
from . import ecfile
from . import ecpack
from . import ecutils as ec

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
#
def getconf(conf, par, kind='float'):
    """
    Get configuration value from QC group with type validation.

    :param conf: Configuration object
    :type conf: object
    :param par: Parameter name to retrieve
    :type par: str
    :param kind: Expected data type, defaults to 'float'
    :type kind: str
    :return: Parameter value converted to specified type
    :rtype: type specified by kind parameter
    """
    val = conf.get(par, group=ec.qc_prefix, kind=kind)
    return val


# ----------------------------------------------------------------
#
def north_angle(conf):
    """
    Returns anemometer orientation relative to north.

    Determines the direction of the anemometer's north direction (phi) in degrees
    clockwise from north, and the coordinate system handedness.

    :param conf: Configuration object containing apparatus settings
    :type conf: object
    :return: Tuple of (phi, hand) where phi is orientation angle and hand is ±1 for handedness
    :rtype: tuple(float, float)
    :raises ValueError: If apparatus type is not a recognized anemometer

    :note: Zero degrees indicates anemometer x-axis aligned with geographic east.
           For right-handed systems, y-axis points north; for left-handed, south.

    :example: Campbell CSAT3: Direction from sensor heads to mounting node
              defines positive x direction. If device "points" west, heading is zero.
              Its handness is right.
    """
    # configuration for sonic anemometer type ("apparatus")
    qqtype = ec.code_ap(conf.get('QQType', group=ec.sonprefix, kind='int'))
    # "Yaw angle of apparatus relative to north"
    qqyaw = conf.get('QQYaw', group=ec.sonprefix, kind='float')
    # anemometer coordinate system handness (left or right)
    if qqtype in ['ApGenericSonic']:
        phi = qqyaw - 270
        # anemometer coordinate system handness (left or right)
        # from configuration
        hand = conf.get('QQExt8', group=ec.sonprefix, kind='float')
        hand = np.sign(hand) if hand != 0 else 1.
    elif qqtype in ['ApKaijoTR61', 'ApKaijoTR90']:
        phi = qqyaw
        hand = 1.  # right
    elif qqtype in ['ApGillSolent','ApCSATSonic', 'ApSon3Dcal']:
        phi = qqyaw - 270  # QQYaw = hdg to where device is open
        hand = 1.  # right
    else:
        raise ValueError('not an anemometer %s' % qqtype)

    return phi, hand


# ----------------------------------------------------------------
#
def mask_diag(conf, dat):
    """
    Remove flagged values based on instrument diagnostic flags.

    Applies quality masks for sonic anemometer and gas analyzer diagnostics.
    Sets values to NaN when instrument flags indicate problems.

    :param conf: Configuration object with diagnostic thresholds
    :type conf: object
    :param dat: DataFrame containing raw measurement data
    :type dat: pandas.DataFrame
    :return: DataFrame with flagged values masked as NaN
    :rtype: pandas.DataFrame

    :note: CSAT diagnostic uses bitmask; IRGA uses AGC threshold
           and flag bits:

           ```csatmask = b'1111000000000000'``` ! bits that must me lo
           ```irgamask = b'11110000': bits that must be hi
           ```agclimit = 70```


    """
    # get actual settings frpm config
    csatmask = getconf(conf, 'csatmask', kind='int')
    irgamask = getconf(conf, 'irgamask', kind='int')
    agclimit = getconf(conf, 'agclimit')
    #
    # CSAT3 (or other anemometer)
    mask = pd.Series(False, index=dat.index)
    for i in dat.index:
        # bad if one component or ts is nan or csat is flagged
        if (pd.isnull(dat['ux'][i]) or
                pd.isnull(dat['uy'][i]) or
                pd.isnull(dat['uz'][i])):
            mask[i] = True
        if ("diag_csat" in dat and
                (int(dat['diag_csat'][i]) & csatmask) > 0):
            mask[i] = True
    for k in ['ux', 'uy', 'uz', 'ts']:
        # OLD: dat[k].mask(mask, np.nan, inplace=True)
        # NEW: Use loc to avoid chained assignment
        dat.loc[mask, k] = np.nan
    #
    # LiCor Li-7xxx
    mask = pd.Series(False, index=dat.index)
    for i in dat.index:
        # calculate agc from quality byte
        if "diag_csat" in dat and not pd.isnull(dat['diag_irga'][i]):
            agc = float(int(dat['diag_irga'][i]) & 15) * 6.25
        else:
            agc = 1
        # bad if one gas is nan or agc is elevated or licor is flagged
        if (pd.isnull(dat['h2o'][i]) or
                pd.isnull(dat['co2'][i]) or
                (int(dat['diag_irga'][i]) & irgamask) != irgamask or
                agc > agclimit):
            mask[i] = True
    for k in ['h2o', 'co2', 'pres']:
        # OLD: dat[k].mask(mask, np.nan, inplace=True)
        # NEW: Use loc to avoid chained assignment
        dat.loc[mask, k] = np.nan

    return dat


# ----------------------------------------------------------------
# ----------------------------------------------------------------
#
# quality checks after Vickers & Mahrt (1997)
#
# ----------------------------------------------------------------
#
# quality check (a) in Vickers & Mahrt (1997)
# remove spikes from values series
#


# noinspection GrazieInspection
def vmspike(conf, dat, dt):
    """
    Spike detection and removal following  Vickers & Mahrt.

    Quality check (a) from :cite:`vim_jaot97`. Iteratively identifies and
    removes spikes based on rolling standard deviation thresholds.

    :param conf: Configuration object with spike detection parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :param dt: Time step between measurements [s]
    :type dt: float
    :return: Tuple of (flags, quality_measures, despiked_data)
    :rtype: tuple(dict, dict, pandas.DataFrame)

    :note: Uses iterative approach with increasing thresholds over up to 10 iterations.
           Only removes short sequences of consecutive outliers as spikes.
    """
    logger.insane('vmspike')

    flags = {'_'.join([ec.val[x], 'spk']): 0 for x in ec.metvar}
    qms = {'_'.join([ec.val[x], 'qmspk']): np.nan for x in ec.metvar}
    n = ec.safe_len(dat)

    # copy dat to res, so dat remains unchanged
    res = dat.copy()

    l1 = getconf(conf, 'L1')
    wid = int(l1 / dt)
    limt = getconf(conf, 'spth')
    inc = getconf(conf, 'spin')
    cons = getconf(conf, 'spco')
    crit = getconf(conf, 'spcr')
    fill = getconf(conf, 'spfill')
    frac = np.nan

    for v in ec.metvar:
        logger.debug('[vmspike] despiking {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'spk'])
        qkey = '_'.join([ec.val[v], 'qmspk'])
        nospike = len(res.index)
        total_removed = 0
        if n < l1:
            logger.info('[vmspike] time series too short')
        else:
            # max. 10 Iterations
            for it in range(1, 11):
                if not (nospike > 0):
                    # stop iteration, if no spikes lest
                    break
                logger.insane('starting iteration #{:d}'.format(it))
                # increase thresh. with iteration
                trfac = (limt + inc * float(it))
                # cycle through values, initialize fast variance
                mean = pd.Series(res[v].rolling(wid, center=True).mean()
                                 ).interpolate(limit=int(wid / 2), limit_direction='both')
                stdv = pd.Series(res[v].rolling(wid, center=True).std()
                                 ).interpolate(limit=int(wid / 2), limit_direction='both')
                # flag values
                thresh = trfac * stdv
                # True -> 1, False -> 0
                spike = (np.abs(res[v] - mean) > thresh).astype(int)
                # count number of consecutive outliers
                concnt = 0
                for i in range(len(spike)):
                    if spike[i] > 0:
                        concnt = concnt + 1
                        spike[(i - concnt + 1):i + 1] = concnt
                    else:
                        concnt = 0

                # remove short sequences of outliers as spikes
                mask = (spike > 0) & (spike < cons)

                # store original nan values
                orgnan = res[v].isnull()
                # remove spike values
                res.loc[mask, v] = np.nan
                # fill, if desired:
                if fill != 0:
                    # replace spikes values by nan ant interpolate gaps
                    res[v] = res[v].interpolate(method='linear')
                    # restore original nan values
                    res.loc[orgnan, v] = np.nan
                # add up spikes  removed
                removed = sum(mask)
                total_removed += removed
                # spikes not removed in this pass
                nospike = sum(spike > 0) - removed
                frac = float(removed) / float(n)
                logger.insane(
                    'iteration #{:d} spikes removed: {:d}'.format(it, removed))
            qms[qkey] = float(total_removed) / float(n)

        if total_removed > int(float(n) * crit):
            flags[fkey] = 1
            logger.debug('[vmspike] numerous {:s} spikes : {:f}%'.format(
                v, round(frac * 100.)))
        if nospike > 0:
            flags[fkey] = 2
            logger.info('[vmspike] not all {:s} spikes removed'.format(v))

    return flags, qms, res


# ----------------------------------------------------------------
#
def ampres(conf, dat):
    """
    Amplitude resolution test following Vickers & Mahrt.

    Quality check (b) from :cite:`vim_jaot97`. Tests if data resolution
    is sufficient for flux calculations by examining distribution of values
    in bins.

    :param conf: Configuration object with resolution test parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Uses half-overlapping windows to test for empty bins in
           histogram.
           Pressure variables are typically skipped as they often
           fail without consequence.
    """
    wid = getconf(conf, 'widampres')
    maxempty = getconf(conf, 'mxem')
    nbin = 100

    logger.insane('ampres')
    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    for v in ec.metvar:
        logger.debug('[ampres] binning {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'res'])
        qkey = '_'.join([ec.val[v], 'qmebi'])
        if v == 'pres':
            # test fails most barometers without consequences
            # -> never test pres
            fracempty = 0
        elif n < wid:
            logger.info('[ampres] not enough data')
            fracempty = 0
        else:
            empty = []
            # half-overlapping windows
            # noinspection SpellCheckingInspection
            for i in np.arange(0, n - wid - 1, int(wid / 2), int):
                if sum(dat.loc[i:(i + wid - 1), v].notnull()) > 2:
                    # calculate bin range from mean and stdv and range of data
                    stdv = dat.loc[i:(i + wid - 1), v].std()
                    mean = dat.loc[i:(i + wid - 1), v].mean()
                    rmin = dat.loc[i:(i + wid - 1), v].min()
                    rmax = dat.loc[i:(i + wid - 1), v].max()
                    if rmax - rmin > 7. * stdv:
                        # upper limit for bin size
                        rmin = mean - 3.5 * stdv
                        rmax = mean + 3.5 * stdv
                    bins = np.linspace(rmin, rmax, nbin + 1)
                    if len(np.unique(bins)) < nbin + 1:
                        # avoid "ValueError: Bin edges must be unique"
                        # window width << numerical resolution of values:
                        # assume only center bin is populated
                        empty.append(nbin - 1)
                    else:
                        # classify data
                        try:
                            cnt = pd.cut(
                                dat.loc[i:(i + wid - 1), v],
                                bins).value_counts()
                        except ValueError:
                            cnt = [1 if x == nbin // 2 else 0
                                   for x in range(nbin)]
                        # count empty bins
                        empty.append(sum(cnt == 0))

                # print i,rmin,rmax,empty[-1]

            # do not fail series is emtpy
            if len(empty) == 0:
                maxem = 0
            # remember maximum value
            else:
                maxem = max(empty)
            # flag window as too low resolution if too many bins empty
            fracempty = float(maxem) / float(nbin)

        qms[qkey] = fracempty
        if fracempty > maxempty:
            logger.debug('[ampres] too many empty bins: {:f}%'.format(
                round(100. * fracempty)))
            flags[fkey] = 2
        else:
            logger.insane(
                '[ampres] fracempty {:f}%'.format((100. * fracempty)))

    return flags, qms


# ----------------------------------------------------------------
#
def dropout(conf, dat):
    """
    Dropout test for values "sticking" to certain values by Vickers & Mahrt.

    Quality check (c) from V:cite:`vim_jaot97`. Detects when data values
    remain constant for too long, indicating sensor problems.

    :param conf: Configuration object with dropout test parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Examines consecutive identical values in histogram bins across half-overlapping windows.
           Different thresholds applied for center bins vs. edge bins.
    """
    wid = getconf(conf, 'widdropout')
    con1 = getconf(conf, 'maxcon1')
    con2 = getconf(conf, 'maxcon2')
    nbin = 100
    mcon = np.nan

    logger.insane('dropout')
    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    if n < wid:
        logger.info('[dropout] not enough data')
        flags = {'_'.join([ec.val[v], 'drp']): 2 for v in ec.metvar}
        qms = {'_'.join([ec.val[v], 'qmcon']): 0 for v in ec.metvar}
    else:
        for v in ec.metvar:
            logger.debug('drp: binning {:s}'.format(v))
            fkey = '_'.join([ec.val[v], 'drp'])
            qkey = '_'.join([ec.val[v], 'qmcon'])
            if v == 'pres':
                # test fails most barometers without consequences
                # -> never test pres
                fail = False
                maxcon = 0
            else:
                fail = False
                con = []
                # half-overlapping windows
                for i in np.arange(0, n - wid - 1, int(wid / 2), int):
                    # noinspection SpellCheckingInspection
                    if sum(dat.loc[i:(i + wid - 1), v].notnull()) > 2:
                        # calculate bin range from mean and stdv and range of data
                        stdv = dat.loc[i:(i + wid - 1), v].std()
                        mean = dat.loc[i:(i + wid - 1), v].mean()
                        rmin = dat.loc[i:(i + wid - 1), v].min()
                        rmax = dat.loc[i:(i + wid - 1), v].max()
                        if rmax - rmin > 7. * stdv:
                            rmin = mean - 3.5 * stdv
                            rmax = mean + 3.5 * stdv
                        bins = np.linspace(rmin, rmax, nbin + 1)
                        if len(np.unique(bins)) < nbin + 1:
                            # avoid "ValueError: Bin edges must be unique"
                            # window width << numerical resolution of values:
                            # assume only center bin is populated
                            cb = np.array((nbin // 2) * [0] +
                                          [len(dat[v])] +
                                          (nbin - (nbin // 2)) * [0])
                        else:
                            # classify data
                            y = pd.cut(dat.loc[i:(i + wid - 1), v], bins)
                            # count continuous values
                            # https://stackoverflow.com/a/27626699
                            # noinspection PyUnresolvedReferences
                            cc = y.groupby((y != y.shift()).cumsum()
                                           ).cumcount() + 1
                            # find maximum in each class
                            cb = cc.groupby(y, observed=False).max()
                        # flag window as too low resolution if too many bins empty
                        per10 = int(0.1 * float(nbin))
                        per90 = int(0.9 * float(nbin))
                        if (np.max(cb[(per10 - 1):per90]) > int(con1 * float(wid)) or
                                np.max(cb[(per90 - 1):nbin]) > int(con2 * float(wid)) or
                                np.max(cb[0:per10]) > int(con2 * float(wid))):
                            fail = True
                        con.append(np.max(cb))

                # do not fail series is emtpy
                if len(con) == 0:
                    maxcon = 0
                # remember maximum value
                else:
                    maxcon = max(con)
                # flag window as too low resolution if too many bins empty
                mcon = float(maxcon) / float(wid)

            qms[qkey] = mcon
            if fail:
                logger.debug(
                    '[dropout] too many consecutive values: {:.0f}'.format(maxcon))
                flags[fkey] = 2
            else:
                logger.insane(
                    '[dropout] max. consecutive values {:.0f}'.format(maxcon))

    return flags, qms


# ----------------------------------------------------------------
#
def limit(conf, dat):
    """
    Absolute limits test following Vickers & Mahrt.

    Quality check (d) from vim_jaot97`. Checks if wind, temperature,
    and gas concentrations fall within physically reasonable ranges.

    :param conf: Configuration object with limit parameters
    :type conf: object
    :param dat: DataFrame containing measurement data with derived variables
    :type dat: pandas.DataFrame
    :return: Dictionary of quality flags by variable
    :rtype: dict

    :note: Tests horizontal wind speed, vertical wind speed, temperatures,
           specific humidity, and CO2 mixing ratio against configured limits.
    """
    logger.insane('limit')

    flags = {}
    n = ec.safe_len(dat)

    if n > 0:
        pn = ['limu', 'limw', 'limtl', 'limth',
              'limql', 'limqh', 'limcl', 'limch']
        pv = {x: getconf(conf, x) for x in pn}

        uh = np.sqrt(np.square(dat['ux']) + np.square(dat['uy']))
        if np.amax(uh) > pv['limu']:
            flags['ux'] = 2
            flags['uy'] = 2
            logger.debug('[limit] |v| > {:f} m/s'.format(pv['limu']))

        if np.amax(np.absolute(dat['uz'])) > pv['limw']:
            flags['uz'] = 2
            logger.debug('[limit] |w| > {:f} m/s'.format(pv['limw']))

        for tv in ['ts', 'tcoup']:
            if (np.amin(dat[tv]) < pv['limtl'] or
                    np.amax(dat[tv]) > pv['limth']):
                flags[tv] = 2
                logger.debug('[limit] {:s} outside [{:f},{:f}] C'.format(
                    ec.stem[tv], pv['limtl'], pv['limth']))

        if (np.amin(dat['q']) < pv['limql'] or
                np.amax(dat['q']) > pv['limqh']):
            flags['h2o'] = 2
            logger.debug(
                '[limit] q outside [{:f},{:f}] g/kg'.format(pv['limql'], pv['limqh']))

        if (np.amin(dat['ppm']) < pv['limcl'] or
                np.amax(dat['ppm']) > pv['limch']):
            flags['co2'] = 2
            logger.debug(
                '[limit] q outside [{:f},{:f}] umol/mol'.format(pv['limcl'], pv['limch']))

    return flags


# ----------------------------------------------------------------
#
def himom(conf, dat):
    """
    Higher moments test following Vickers & Mahrt (1997).

    Quality check (e) from :cite:`vim_jaot97`. Examines skewness and
    kurtosis of detrended data to detect unusual statistical distributions.

    :param conf: Configuration object with moment test parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Uses scipy's biased moments following Vickers & Mahrt methodology.
           Data is linearly detrended before moment calculation.
    """
    logger.insane('himom')

    flv = [1, 2]
    maxskew = [getconf(conf, 'maxskew_1'), getconf(conf, 'maxskew_2')]
    minkurt = [getconf(conf, 'minkurt_1'), getconf(conf, 'minkurt_2')]
    maxkurt = [getconf(conf, 'maxkurt_1'), getconf(conf, 'maxkurt_2')]

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    for v in ec.metvar:
        fkey = '_'.join([ec.val[v], 'mom'])
        skey = '_'.join([ec.val[v], 'qmskw'])
        kkey = '_'.join([ec.val[v], 'qmkrt'])

        #  use linear regression of non-nan values to eliminate trend

        # data=signal.detrend(dat[v],type='linear')
        #  does not cope with nan values.
        #  workaround: use linear regression and subtract it
        #  https://stackoverflow.com/a/44782130
        if n > 0:
            ok = np.array(~ np.isnan(dat[v]))
        else:
            ok = [False]

        if any(ok):
            nr = pd.Series(range(len(dat[v])))
            m, b, r_val, p_val, std_err = stats.linregress(nr[ok], dat[v][ok])
            data = dat[v][ok] - (m * nr[ok] + b)

            # use scipy functions because pandas only gives unbiased
            # skew/kurtosis whereas Vickers & Mahrt do not use
            # a bias correction and Pearson's kurtosis definition
            #
            # bias=True -> disables bias correction
            # fisher=True -> Fisher's definition (normal ==> 0.0)
            # fisher=False -> Pearson's definition is used (normal ==> 3.0).

            # nan_policy='omit'  only scipy >0.17

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore",
                    message=r".*Precision loss occurred "
                            r"in moment calculation.*" )
                res = stats.skew(data, bias=True)
            if isinstance(res, np.ma.masked_array):
                skew = float(res.data)
            else:
                skew = float(res)

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore",
                    message=r".*Precision loss occurred "
                            r"in moment calculation.*" )
                res = stats.kurtosis(data, fisher=False, bias=True)
            if isinstance(res, np.ma.masked_array):
                kurt = float(res.data)
            else:
                kurt = float(res)

        else:
            # if all dat ar nan, make moments nan, too
            skew = np.nan
            kurt = np.nan

        qms[skey] = skew
        qms[kkey] = kurt

        flags[fkey] = 0
        # flag skewness
        for i in range(2):
            if np.abs(skew) > maxskew[i]:
                flags[fkey] = max([flags[fkey], flv[i]])
        # flag kurtosis
        for i in range(2):
            if kurt > maxkurt[i] or kurt < minkurt[i]:
                flags[fkey] = max([flags[fkey], flv[i]])

        if flags[fkey] == 2:
            logger.debug('[himom] excessive moments: skew: {:F}, kurtosis: {:f}'.
                          format(skew, kurt))
        elif flags[fkey] == 1:
            logger.insane('[himom] higher moments: skew: {:F}, kurtosis: {:f}'.
                           format(skew, kurt))

    return flags, qms


# ----------------------------------------------------------------
#
def disco(conf, dat, dt):
    """
    Discontinuity detection using Haar wavelets after Vickers & Mahrt.

    Quality check (f) from :cite:`vim_jaot97`. Uses Haar transformation
    to detect sudden jumps or discontinuities in the data.

    :param conf: Configuration object with discontinuity test parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :param dt: Time step between measurements [s]
    :type dt: float
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Applies Haar wavelets and examines variance changes in sliding windows.
           Uses data standard deviation for normalization.
    """
    logger.insane('disco')

    l1 = getconf(conf, 'L1')
    wid = int((l1 / dt) / 2)  # half window width

    flags = {}
    qms = {}
    n = ec.safe_len(dat)
    stdv = np.nan

    for v in ec.metvar:
        fkey = '_'.join([ec.val[v], 'mom'])
        hkey = '_'.join([ec.val[v], 'qmtrs'])
        vkey = '_'.join([ec.val[v], 'qmvrn'])

        if n > 0:
            # statistics and range
            stdv = ec.allnanok(np.nanstd, dat[v].values)
            dmin = ec.allnanok(np.nanmin, dat[v].values)
            dmax = ec.allnanok(np.nanmax, dat[v].values)
            # determine scale
            scale = min([stdv, (dmax - dmin) / 4.])
        else:
            scale = 0

        if scale == 0:
            # max=min or stdev==0 -> unusual, but no spikes
            logger.info('[disco] zero scale in {:s}'.format(v))
            qms[hkey] = 0
            qms[vkey] = 0
            flags[fkey] = 0
        elif sum(dat[v].notnull()) <= 5:
            logger.info('[disco] too many nan data in {:s}'.format(v))
            qms[hkey] = 0
            qms[vkey] = 0
            flags[fkey] = 0

        else:
            # initialize quick haar transform
            wav = pd.Series([-1.] * wid + [1.] * wid)
            # do transform
            ht = np.convolve(dat[v], wav, mode='same') / (scale * float(wid))
            # convolve does zero padding at the ends; we don't want that
            ht[:wid] = np.nan
            ht[-wid:] = np.nan
            # remember maximum transform value
            hmax = ec.allnanok(np.nanmax, np.abs(ht))
            #
            # variances in the left ind right half window
            # By default,the result is set to the right edge of the window.
            varl = dat[v].rolling(wid, center=False).var()
            varr = varl.shift(-wid)
            # ratio variance, remember max value
            varrat = np.abs(varl - varr) / (stdv ** 2)
            varmax = ec.allnanok(np.nanmax, varrat.values)

            qms[hkey] = hmax
            qms[vkey] = varmax

            # flag record
            if hmax > 3.:
                flags[fkey] = 2
                logger.debug(
                    '[disco] {:s} Haar max. disontinuity {:f} > 3.'.format(v, hmax))
            if varmax > 3.:
                flags[fkey] = 2
                logger.debug(
                    '[disco] {:s} coherent variance change {:f} > 3.'.format(v, varmax))
            elif (hmax > 2.) or (varmax > 2.):
                flags[fkey] = 1
                logger.insane(
                    '[disco] {:s} elevated Haar or variance change ({:f}; {:f})'.format(v, hmax, varmax))
            else:
                flags[fkey] = 0

    return flags, qms


# ----------------------------------------------------------------

def nonstat(conf, dat):
    """
    Stationarity test for wind following Vickers & Mahrt.

    Quality check (g) from :cite:`vim_jaot97`. Tests stationarity by
    examining wind speed reduction and relative nonstationarity parameters.

    :param conf: Configuration object with stationarity test parameters
    :type conf: object
    :param dat: DataFrame containing wind measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Calculates mean wind vector, rotates to alongwind/crosswind coordinates,
           and examines linear trends as indicators of nonstationarity.
    """
    logger.insane('nonstat')

    n = ec.safe_len(dat)
    # min acceptable wind speed reduction (in 1)
    minred = getconf(conf, 'minred')
    maxrn = getconf(conf, 'maxrn')  # max acceptable wind speed change (in 1)

    if n > 0:
        # calculate mean wind vector  (opposite to wind direction!) and direction
        uxmean = ec.allnanok(np.nanmean, dat['ux'].values)
        uymean = ec.allnanok(np.nanmean, dat['uy'].values)
        hdmean = np.arctan2(uxmean, uymean) / ec.deg2rad

        # average instantaneous wind
        vh = np.sqrt(dat['ux'] ** 2 + dat['uy'] ** 2)
        uq = ec.allnanok(np.nanmean, vh.values)

        red = np.sqrt(uxmean ** 2 + uymean ** 2) / uq
        #  !       if (red.lt.minred) print *,'Speed reduction:',red

        #  calculate alongwind (uo) and crosswind (vo) to mean wind direction
        # ??? 180?
        rho = (180. - hdmean) * ec.deg2rad
        uo = dat['ux'] * np.sin(rho) - dat['uy'] * np.cos(rho)
        vo = dat['ux'] * np.cos(rho) + dat['uy'] * np.sin(rho)
    else:
        red = np.nan
        uo = np.nan
        vo = np.nan
        uq = np.nan

    # calculate alongwind relative nonstationarity
    if n > 1:
        # linear regression
        slope, offset = np.polyfit(np.arange(n), uo, deg=1)
        du = float(n) * slope
        # scale with wind speed average
        rnu = du / uq
    else:
        rnu = du = np.nan

    #  calculate crosswind relative nonstationarity
    if n > 1:
        # linear regression
        slope, offset = np.polyfit(np.arange(n), vo, deg=1)
        dv = float(n) * slope
        # scale with wind speed average
        rnv = dv / uq
    else:
        rnv = dv = np.nan

    # vector wind relative nonstationarity
    if n > 0 and uq != 0:
        rns = np.sqrt(du ** 2 + dv ** 2) / uq
    else:
        rns = np.nan

    if (red < minred or rnu > maxrn or
            rnv > maxrn or rns > maxrn):
        flag = 1
    else:
        flag = 0

    flags = {}
    qms = {}

    for v in ec.metvar:
        fkey = '_'.join([ec.val[v], 'nst'])
        qrkey = '_'.join([ec.val[v], 'qmred'])
        qukey = '_'.join([ec.val[v], 'qmrnu'])
        qvkey = '_'.join([ec.val[v], 'qmrnv'])
        qskey = '_'.join([ec.val[v], 'qmrns'])
        qms[qrkey] = red
        qms[qukey] = rnu
        qms[qvkey] = rnv
        qms[qskey] = rns
        if v == 'ux':
            flags[fkey] = flag
        #      qms[q1key]=rnu
        #      qms[q2key]=rns
        elif v == 'uy':
            flags[fkey] = flag
        #      qms[q1key]=rnv
        #      qms[q2key]=rns
        else:
            flags[fkey] = 0
    #      qms[q1key]=0.
    #      qms[q2key]=0.

    return flags, qms

# ----------------------------------------------------------------

def crosscorr(datax, datay, lag=0):
    """
     Calculate lag-N cross correlation between two time series.

     Quality check (h) from :cite:`vim_jaot97`. Tests if there is a hidden
     crosstalk between vertical wind and the other values.

     :param datax: First time series
     :type datax: pandas.Series
     :param datay: Second time series
     :type datay: pandas.Series
     :param lag: Lag in samples, defaults to 0
     :type lag: int
     :return: Cross correlation coefficient
     :rtype: float

     :note: Based on https://stackoverflow.com/a/37215839
     """
    return datax.corr(datay.shift(lag))


def lagcor(conf, dat, dt):
    """
    Lag correlation test following Vickers & Mahrt.

    Quality check (h) from :cite:`vim_jaot97`. Detects hidden lag
    between vertical wind and scalar measurements by examining cross-correlations.

    :param conf: Configuration object with lag test parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :param dt: Time step between measurements [s]
    :type dt: float
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Searches for maximum correlation at different lags to detect
           sensor synchronization problems or physical transport delays.
    """
    logger.insane('lagcor')

    n = ec.safe_len(dat)
    l2 = getconf(conf, 'L2')
    ll = int(l2 / dt)  # full window width
    limt = 0.10

    flags = {}
    qms = {}
    for v in ec.metvar:
        fkey = '_'.join([ec.val[v], 'lag'])
        qkey = '_'.join([ec.val[v], 'qmlag'])
        if n == 0 or v in ['uz', 'pres']:
            qms[qkey] = 0.
            flags[fkey] = 0
        else:
            # remember zero-lag correlation
            rnul = np.abs(crosscorr(dat[v], dat['uz'], 0))
            imax = 0
            if not np.isnan(rnul):
                rquit = rnul * (1. - limt)
                rmax = rnul
                # search positive lags
                lags = list(np.arange(1, ll, 1))
                for i in lags:
                    r = np.abs(crosscorr(dat[v], dat['uz'], int(i)))
                    if not np.isnan(r) and r > rmax:
                        rmax = r
                        imax = i
                    # speed up
                    elif r < rquit:
                        break
                # search negative lags
                lags = list(np.arange(-1, -ll, -1))
                for i in lags:
                    r = np.abs(crosscorr(dat[v], dat['uz'], int(i)))
                    if not np.isnan(r) and r > rmax:
                        rmax = r
                        imax = i
                    # speed up
                    elif r < rquit:
                        break
            else:
                rmax = 1.
                rnul = 1.
            # compute index and flag
            lcor = (rmax - rnul) / rnul
            qms[qkey] = lcor
            if lcor > 0.10:
                flags[fkey] = 2
                logger.debug(
                    '[lagcor] response ratio too large: {:f}'.format(lcor))
                logger.debug(
                    '[lagcor] best correlation at {:d} records shift'.format(imax))
            else:
                flags[fkey] = 0
                logger.insane(
                    '[lagcor] max response ratio: {:f}'.format(lcor))
                logger.insane(
                    '[lagcor] best correlation at {:d} records shift'.format(imax))

    return flags, qms


# ----------------------------------------------------------------
# ----------------------------------------------------------------
# quality checks after Mauder et al (2016)


# ----------------------------------------------------------------
#
def ratespike(conf, dat):
    """
    Spike detection based on change rate (Quality check 9).

    Extended quality test detecting spikes by examining rate of change
    between consecutive measurements.
    Inspired by :cite:`rgf_taac01`.

    :param conf: Configuration object with rate spike parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures, despiked_data)
    :rtype: tuple(dict, dict, pandas.DataFrame)

    :note: Uses forward differences to detect excessive change rates.
           Different thresholds applied per variable type.
    """

    logger.insane('ratepike')

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    # copy dat to res, so dat remains untouched
    res = dat.copy()

    fill = getconf(conf, 'spfill')
    mrate = {'ux': getconf(conf, 'chr_u'),
             'uy': getconf(conf, 'chr_u'),
             'uz': getconf(conf, 'chr_w'),
             'ts': getconf(conf, 'chr_t'),
             'tcoup': getconf(conf, 'chr_t'),
             'h2o': getconf(conf, 'chrh2o'),
             'co2': getconf(conf, 'chrco2'),
             'pres': np.nan}
    mxfrac = getconf(conf, 'chrcr')

    #
    # find spikes
    # C. Rebmann: only value after jump is spike
    # -> remove if forward difference too large
    #
    # for each variable explicitly:
    for v in ec.metvar:
        logger.debug('[ratespike] despiking {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'chr'])
        qmkey = '_'.join([ec.val[v], 'qmrat'])
        qfkey = '_'.join([ec.val[v], 'qmcsp'])

        # rate = forward difference (dfault axis= alon columns)
        # rate=np.abs(res[v].diff().shift(-1))
        # C. Rebmann: only value after jump is spike
        # => shift=0
        # i.e. rate stored at i equals change from i-1 -> i
        rate = np.abs(res[v].diff().shift(0))

        # store quality measure: max change rate
        qms[qmkey] = ec.allnanok(np.nanmax, rate.values)
        # mask : True where mrate is exceeded
        spike = (rate > mrate[v])
        # count values
        nspike = sum(spike)
        logger.insane(('[ratespike] max {:s} rate found: {:f}' +
                        '(limit: {:f})').format(v, rate.max(), mrate[v]))
        #
        # remove spikes
        #
        # store original nan values
        orgnan = res[v].isnull()
        # remove spike values
        res.loc[spike, v] = np.nan
        # fill, if desired:
        if fill != 0:
            # replace spikes values by nan ant interpolate gaps
            res[v] = res[v].interpolate(method='linear')
            # restore original nan values
            res.loc[orgnan, v] = np.nan
        # count spikes again:
        rate = np.abs(res[v].diff().shift(-1))
        remain = sum((rate > mrate[v]))

        # store quality measure: fraction of spikes
        if n > 1:
            frac = float(nspike) / float(n)
        else:
            frac = 0.

        qms[qfkey] = frac
        if frac > mxfrac:
            flags[fkey] = 1
            logger.debug('[ratespike] numerous {:s} spikes : {:f}%'.format(
                v, round(frac * 100.)))
        else:
            logger.insane(
                '[ratespike] {:s} spikes : {:f}%'.format(v, round(frac * 100.)))
        if remain > 0:
            flags[fkey] = 2
            logger.info('[ratespike]  not all spikes removed')

    return flags, qms, res


# ----------------------------------------------------------------
#
# quality check 10
# Spike detection based on MAD (median absolute deviation)
# based on the whole record (1 stdv approx 1.48 * 1 mad)
# returns despiked data
#


def derive(v, o):
    """
    Untility function to calculate derivative of time series if desired.

    :param v: Time series data
    :type v: pandas.Series
    :param o: Derivative order (0=none, 1=first, 2=second)
    :type o: int
    :return: Derivative time series or original data
    :rtype: pandas.Series

    :note: Uses centered differences for derivative calculation
    """
    # calculate derivative if desired
    if o == 0:
        # no derivative
        d = v
    elif o == 1:
        # 1st derivative (centered differences)
        d = v.diff(periods=2).shift(-1)
    elif o == 2:
        # 2nd derivative (centered differences)
        d = v.diff(periods=2).shift(-1).diff(periods=2).shift(-1)
    else:
        logger.info(
            '[madspike] illegal derivative {:d}; skipping test'.format(o))
        d = v * np.nan
    return d


def madspike(conf, dat):
    """
    Spike detection using Median Absolute Deviation (Quality check 10).

    Extended quality test using MAD for robust spike detection across
    the entire record :cite:`mcd_aafm13`.

    :param conf: Configuration object with MAD spike parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures, despiked_data)
    :rtype: tuple(dict, dict, pandas.DataFrame)

    :note: Uses MAD (:math:`\\approx 1.48 \\times`
           standard deviation for normal data) as robust
           measure of variability. Can operate on derivatives of the data.
    """
    logger.insane('madspike')

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    # copy dat to res, so dat remains untouched
    res = dat.copy()

    fill = getconf(conf, 'spfill')
    mader = getconf(conf, 'mader')
    madth = getconf(conf, 'madth')
    madcr = getconf(conf, 'madcr')

    # for each variable explicitly:
    for v in ec.metvar:
        logger.debug('mad: despiking {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'mad'])
        qkey = '_'.join([ec.val[v], 'qmmsp'])

        # derive, if wanted
        der = derive(res[v], mader)
        # calculate mad (along columns)
        # med=der.median(skipna=True)
        med = ec.allnanok(np.nanmedian, der.values)
        # pandas method .mad() is NOT MAD, but mean absolute deviation!
        # mad != der.mad(skipna=True)
        mad = ec.allnanok(np.nanmedian, np.abs(res[v].values - med))
        # find spikes
        spike = (np.abs(der - med) / mad > madth)
        nspike = sum(spike)
        #
        # remove spikes:
        # store original nan values
        orgnan = res[v].isnull()
        # remove spike values
        res.loc[spike, v] = np.nan
        # fill, if desired:
        if fill != 0:
            # replace spikes values by nan ant interpolate gaps
            res[v] = res[v].interpolate(method='linear')
            # restore original nan values
            res.loc[orgnan, v] = np.nan

        # count spikes again:
        der = derive(res[v], mader)
        med = der.median(skipna=True)
        # mad is deprecated since pandas 1.5.0, gone in 2.0.0
        # mad = der.mad(skipna=True)
        mad = (der - der.median(skipna=True)).abs().median()
        spike = (np.abs(der - med) / mad > madth)
        remain = sum(spike)

        # flag record
        if n > 1:
            frac = float(nspike) / float(n)
        else:
            frac = 0.
        # store quality measure: fraction of spikes
        qms[qkey] = frac
        if frac > madcr:
            flags[fkey] = 1
            logger.debug('[madspike] numerous {:s} spikes : {:f}%'.format(
                v, round(frac * 100.)))
        else:
            logger.insane(
                '[madspike] {:s} spikes : {:f}%'.format(v, round(frac * 100.)))
        if remain > 0:
            flags[fkey] = 2
            logger.info('[madspike]  not all spikes removed')

    return flags, qms, res


# ----------------------------------------------------------------

def fwstat(conf, dat):
    """
    Stationarity test following Foken & Wichura (Quality check 11).

    Extended stationarity test from cite:`fow_aafm96a`
    comparing covariances from subrecords
    with full record covariances.

    :param conf: Configuration object with F&W stationarity parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Divides record into subrecords and compares their mean covariance
           with the full-record covariance following Foken & Wichura methodology.
    """
    logger.insane('fwstat')

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    nsub = getconf(conf, 'fwsub', kind='int')
    mdif1 = getconf(conf, 'fwlim1')
    mdif2 = getconf(conf, 'fwlim2')

    # for each variable explicitly:
    for v in ec.metvar:
        logger.insane('fws: checking {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'fws'])
        qkey = '_'.join([ec.val[v], 'qmfwd'])

        if n > 0:
            ok = np.array(~ np.isnan(dat[v]))
        else:
            ok = [False]

        # noinspection SpellCheckingInspection
        if v in ['uz', 'pres'] or sum(ok) == 0:
            flags[fkey] = 0
            qms[qkey] = 0
        else:
            # determine the subrecords
            group = np.arange(n) // int(n / nsub)
            # calculate subrecord variances
            df = dat.loc[:, ['uz', v]].groupby(group).cov()
            covi = [df.loc[x, 'uz'][v] for x in df.index.levels[0]]
            # each covi entry is a 2x2 matrix of covariances!
            # select covariance uz`v`  as ['uz',v]
            com = ec.allnanok(np.nanmean, covi)
            # calculate full-record covariance (after F&w 1996, NOT F&et al.2004)
            coo = dat['uz'].cov(dat[v])
            # calculate difference
            diff = np.abs((com - coo) / coo)
            qms[qkey] = diff
            # flag if too large differnces
            if diff > mdif2:
                flags[fkey] = 2
                logger.info(
                    '[fwstat] difference {:s} too large :{:f}%'.format(v, 100. * diff))

            elif diff > mdif1:
                flags[fkey] = 1
                logger.debug(
                    '[fwstat] difference {:s} elevated  :{:f}%'.format(v, 100. * diff))
            else:
                flags[fkey] = 0
                logger.insane(
                    '[fwstat] difference {:s} normal    :{:f}%'.format(v, 100. * diff))

    return flags, qms


# ----------------------------------------------------------------------
#


def cotrend(conf, dat):
    """
    Stationarity test for trend influence (Quality check 12).

    Extended stationarity test comparing covariances of raw vs.
    detrended data to detect the influence of linear trends.
    Inspired by :cite:`gsg_bm10`

    :param conf: Configuration object with cotrend parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    Removes linear trends and compares covariances to assess
    whether trends significantly affect flux calculations.

    Parameters 1-4 can be used to estimate the pdf of data:

    .. math::

       p_\\mathrm{df}(x) =
       \\frac{\\Gamma(p) \\Gamma(q)}{\\Gamma(p+q)}
       \\frac{(x-x_\\mathrm{min})^{p-1} (x_\\mathrm{max}-x)^{q-1}}
       {(x_\\mathrm{max}-x_\\mathrm{min})^{p+q-1}}

    where:

    - :math:`\\Gamma` = the Gamma function
    - :math:`p` = param(1), :math:`q` = param(2)
    - :math:`x_\\mathrm{min}` = param(3), :math:`x_\\mathrm{max}` = param(4)

    :math:`x_\\mathrm{min}` and :math:`x_\\mathrm{max}` can also be used for
    comparison with the actual sample min and max of :math:`x`,
    or boundary-layer min & max.

    .. list-table:: Distribution Properties
       :header-rows: 1

       * - Distribution Type
         - r value
         - rootterm
       * - The lowest possible kurtosis
         - 0
         - >0
       * - Beta distribution
         - >0
         - >0
       * - Gaussian, beta/leptokurtic
         - 1/0
         - 1/0
       * - More leptokurtic than beta
         - <0
         - NaN
    """
    logger.insane('cotrend')

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    mxdiff = getconf(conf, 'cotlimit')

    # for each variable explicitly:
    for v in ec.metvar:
        logger.insane('mad: evaluating {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'cot'])
        qkey = '_'.join([ec.val[v], 'qmtrd'])
        # linear regressions
        try:
            slope, offset = np.polyfit(np.arange(n), dat['uz'],
                                       deg=1)
            residualsw = dat[v] - [slope * x + offset for x in np.arange(n)]
        except TypeError:
            residualsw = None
            logger.info('[cotrend]  not enough data: ' + v)

        if v not in ['co2', 'h2o', 'ts', 'tcoup'] or residualsw is None:
            flags[fkey] = 0
            qms[qkey] = 0
            residualsv = None
        else:
            # linear regressions => residuals = detrended data
            try:
                slope, offset = np.polyfit(np.arange(n), dat['uz'],
                                           deg=1)
                residualsv = dat['uz'] - [slope * x +
                                          offset for x in np.arange(n)]
            except TypeError:
                residualsv = None
                logger.info('[cotrend]  not enough data: ' + v)

        if residualsv is None:
            flags[fkey] = 0
            qms[qkey] = 0
        else:
            # calculate covariance detrended
            cov1 = pd.Series(residualsw).cov(pd.Series(residualsv))

            # calculate covariance not detrended
            cov2 = dat['uz'].cov(dat[v])

            # calculate difference
            diff = (cov2 - cov1) / cov2
            qms[qkey] = diff

            # flag if too many spikes
            if np.abs(diff) > mxdiff:
                flags[fkey] = 2
                logger.info(
                    '[cotrend] difference too large :{:f}'.format(100. * diff))
            else:
                flags[fkey] = 0
                logger.insane(
                    '[cotrend] relative difference  :{:f}'.format(100. * diff))

    return flags, qms


# ----------------------------------------------------------------
#
# quality check 13
# Stationarity Test after Foken & Wichura 1996
#
def beta(conf, dat):
    """
    Beta distribution analysis (Quality check 13).

    Extended statistical test comparing data distribution to beta distribution
    to assess departure from Gaussian behavior .
    Inspired by :cite:`gsg_bm10`

    :param conf: Configuration object with beta distribution parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Calculates beta distribution parameters from moments and flags
           data that is too leptokurtic or shows bimodal characteristics.
    """
    logger.insane('beta')

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    tol = getconf(conf, 'bettol')
    det = getconf(conf, 'betdet')

    # for each variable explicitly:
    for v in ec.metvar:
        logger.insane('bet: evaluating {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'bet'])
        qkey = '_'.join([ec.val[v], 'qmbdv'])  # dev
        key1 = '_'.join([ec.val[v], 'qmbpp'])  # param1
        key2 = '_'.join([ec.val[v], 'qmbpq'])  # param2
        key3 = '_'.join([ec.val[v], 'qmbpi'])  # param3
        key4 = '_'.join([ec.val[v], 'qmbpx'])  # param4

        if n > 0:
            ok = np.array(~ np.isnan(dat[v]))
        else:
            ok = [False]
        if sum(ok) <= 5:
            logger.info('[beta] too many nan data in {:s}'.format(v))
            dev = 0.
            param1 = 0.
            param2 = 0.
            param3 = 0.
            param4 = 0.
            flag = 0
        else:
            if det:
                #  linear regression of non-nan values to eliminate trend
                slope, offset = np.polyfit(np.arange(n)[ok], dat[v][ok],
                                           deg=1)
                data = dat[v][ok] - (np.arange(n)[ok] * slope + offset)
            else:
                # use data without detrending
                data = dat[v][ok].copy()

            # skewness, kurtosis
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore",
                    message=r".*Precision loss occurred "
                            r"in moment calculation.*" )
                skew = stats.skew(data, bias=True)
                kurt = stats.kurtosis(data, fisher=False, bias=True)

            # test criteria
            # if skew=0, dev indicates kurt deviation from Gaussian
            # else dev indicates deviation from borderline beta - gamma
            dev = kurt - (3. + 1.5 * skew)
            flag = 0
            if dev >= 0:
                # pdf more leptokurtic than a beta distribution
                # (limiting case at skew=0: Gaussian)
                # even more leptokurtic than user-defined tolerance?
                if dev > tol:
                    flag = 2
                    logger.info(
                        '[beta] {:s} too leptokurtic : {:f}'.format(v, dev))
                else:
                    logger.debug(
                        '[beta] {:s} leptokurtic : {:f}'.format(v, dev))
                    flag = 1
                param1 = np.nan
                param2 = np.nan
                param3 = np.nan
                param4 = np.nan
            else:
                # calculate parameters of beta distribution, if possible
                try:
                    r = 6. * (kurt - skew ** 2 - 1.) / (
                            6. + 3. * skew ** 2 - 2. * kurt)
                    denom = (r + 2.) ** 2 * skew ** 2 + 16. * (r + 1.)
                    if denom > 0:
                        rootterm = (r + 2.) * np.sqrt((skew ** 2) / denom)
                    else:
                        rootterm = np.nan
                    helpparam = [np.nan] * 2
                    helpparam[0] = r / 2. * (1. + rootterm)
                    helpparam[1] = r / 2. * (1. - rootterm)
                    if skew > 0:
                        param1 = np.min(helpparam)
                        param2 = np.max(helpparam)
                    else:
                        param1 = np.max(helpparam)
                        param2 = np.min(helpparam)

                    if (param1 * param2) == 0:
                        raise ZeroDivisionError

                    rang = np.sqrt((param1 + param2 + 1.) / (param1 * param2))
                    rang = rang * (np.sum(data ** 2) /
                                   float(len(data))) * (param1 + param2)
                    param3 = np.mean(data) - rang * param1 / (param1 + param2)
                    param4 = param3 + rang

                except ZeroDivisionError:
                    param1 = np.nan
                    param2 = np.nan
                    param3 = np.nan
                    param4 = np.nan
                    logger.debug(
                        '[beta] {:s} strangely distributed'.format(v))
                    flag = 2

                else:  # no exception occurred
                    if param1 < 1. and param2 < 1.:
                        # bimodal (U-shaped) beta distribution
                        # probably indicates jump in timeseries of data
                        flag = 2
                        logger.debug('[beta] bimodal distribution : {:f} {:f}'.format(
                            param1, param2))
                    elif param1 < 1. or param2 < 1.:
                        # J-shaped beta distribution:
                        # strongly non-gaussian but still may be ok
                        flag = 1
                    else:
                        # unimodal, similar-to-gaussian beta distribution
                        pass # keep flag = 0

        # store diagnostic data
        qms[qkey] = dev
        qms[key1] = param1
        qms[key2] = param2
        qms[key3] = param3
        qms[key4] = param4
        flags[fkey] = flag

    return flags, qms


# ----------------------------------------------------------------

def varstat(conf, dat, dt):
    """
    Variance stationarity test (Quality check 14).

    Extended test detecting discontinuities in variance using
    sliding windows.
    Inspired by :cite:`drh_bm07`

    :param conf: Configuration object with variance stationarity parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :param dt: Time step between measurements [s]
    :type dt: float
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Compares variances in adjacent windows to detect sudden changes
           in data variability that might indicate instrument problems.
    """
    logger.insane('varstat')

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    l1 = getconf(conf, 'L1')
    #  wid=int((l1/dt)/2) # half window width
    wid = int(l1 / dt)  # window width
    varlim = getconf(conf, 'vstlim')

    # for each variable explicitly:
    for v in ec.metvar:
        logger.insane('vst: evaluating {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'vst'])
        qkey = '_'.join([ec.val[v], 'qmvst'])  # dev

        if n == 0 or (sum(dat[v].notnull()) <= 5):
            logger.info('[varstat] too many nan data in {:s}'.format(v))
            flags[fkey] = 0
            qms[qkey] = 0
        else:
            stdv = ec.allnanok(np.nanstd, dat[v].values)
            #
            # variances in the left ind right half window
            # By default,the result is set to the right edge of the window.
            varl = dat[v].rolling(wid, center=False).var()
            varr = varl.shift(-wid)
            # ratio variance, remember max value
            if stdv != 0.:
                varrat = ec.allnanok(np.abs, varl - varr) / (stdv ** 2)
            else:
                varrat = np.nan
            varmax = ec.allnanok(np.nanmax, varrat)

            qms[qkey] = varmax

            # flag record
            if varmax > varlim:
                flags[fkey] = 2
                logger.info(
                    '[disco] {:s} excessive variance change {:f}'.format(v, varmax))
            else:
                flags[fkey] = 0
                logger.insane(
                    '[disco] {:s}       max. variance change {:f}'.format(v, varmax))

    return flags, qms


# ----------------------------------------------------------------

def fturb(conf, dat, dt):
    """
    Turbulent fraction test (Quality check 15).

    Extended test detecting intermittent turbulence by analyzing what fraction
    of the record contributes to most of the flux.
    Inspired by :cite:`drh_bm07`

    :param conf: Configuration object with turbulent fraction parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :param dt: Time step between measurements [s]
    :type dt: float
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Divides record into subrecords, sorts covariances by magnitude,
           and determines what fraction of subrecords contains 90% of total flux.
    """
    logger.insane('fturb')

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    lf = getconf(conf, 'Lf')  # subwindow width in s
    ll = int(lf / dt)  # subwindow width in records
    ftmin1 = getconf(conf, 'ftmin1')  # min turbulent fraction (soft flag)
    ftmin2 = getconf(conf, 'ftmin2')  # min turbulent fraction (hard flag)
    flrat = 0.90

    # check the subrecords
    nsub = n / ll
    if ll <= 0:
        logger.warning('[fturb]  subwindow too short')
        skip_test = True
    elif nsub <= 2:
        logger.info('[fturb]  not enough data')
        skip_test = True
    else:
        skip_test = False

    # for each variable explicitly:
    for v in ec.metvar:
        fkey = '_'.join([ec.val[v], 'ftu'])
        qkey = '_'.join([ec.val[v], 'qmftu'])
        if v in ['uz', 'pres'] or skip_test:
            flags[fkey] = 0
            qms[qkey] = 0
        else:
            logger.insane('ftu: evaluating {:s}'.format(v))

            #
            # calculate subrecord variances and their sum
            #
            # create two-column data frame and group it into subrecords
            aaa = pd.DataFrame({'w': dat['uz'], 'a': dat[v]})
            bbb = aaa.groupby(np.arange(n) // ll)
            # calculate covariance for each group (https://stackoverflow.com/a/39734585)
            covi = bbb.apply(lambda x: x['w'].cov(x['a']))
            covsum = ec.allnanok(np.nansum, covi.values)
            if covsum == 0:
                logger.info(
                    '[fturb] not enough covariances: {:s}'.format(v))
                continue
            #
            # sum subrecord covariances, starting with the largest amounts
            # and remember when 90% of full-record value are reached
            #
            # sort values in descending absolute value order
            covsort = np.sort(np.array(covi))[::-1]
            # cumulative sum and find last value where
            # cumulative sum is below threshold
            try:
                need = 1 + np.max(np.where(np.cumsum(covsort)
                                           < (flrat * covsum)))
            except ValueError:
                need = nsub
            #
            # calculate ratio
            ft = float(need) / float(nsub)
            frturb = min([1.0, ft / flrat])
            qms[qkey] = frturb
            #
            # flag if too large differences
            if frturb < ftmin2:
                flags[fkey] = 2
                logger.info(
                    '[fturb] {:s} turbulence too intermittent : {:.1f}%'.format(v, 100. * frturb))
            elif frturb < ftmin1:
                flags[fkey] = 1
                logger.debug(
                    '[fturb] {:s} elevated intermittent turb. : {:.1f}%'.format(v, 100. * frturb))
            else:
                flags[fkey] = 1
                logger.insane(
                    '[fturb] {:s} nominal intermittent turb. : {:.1f}%'.format(v, 100. * frturb))

    return flags, qms


# ----------------------------------------------------------------

def survive(conf, dat, ch):
    """
    Data survival fraction test (Quality check 16).

    Extended test examining what fraction of data survives all quality checks
    and corrections.

    :param conf: Configuration object with survival parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :param ch: DataFrame tracking which values were changed/removed
    :type ch: pandas.DataFrame
    :return: Tuple of (flags, quality_measures)
    :rtype: tuple(dict, dict)

    :note: Low survival rates indicate severe data quality problems or
           overly aggressive quality control settings.

    """
    logger.insane('survive')

    flags = {}
    qms = {}
    n = ec.safe_len(dat)

    msurv1 = getconf(conf, 'msurv1')  # minimum surviving data (soft flag)
    msurv2 = getconf(conf, 'msurv2')  # minimum surviving data (hard flag)

    # for each variable explicitly:
    for v in ec.metvar:
        logger.insane('srv: evaluating {:s}'.format(v))
        fkey = '_'.join([ec.val[v], 'srv'])
        qkey = '_'.join([ec.val[v], 'qmsrv'])

        if n > 0:
            surv = float(n - ch[v].sum()) / float(n)
        else:
            surv = np.nan

        qms[qkey] = surv
        if surv < msurv2:
            flags[fkey] = 2
            logger.info(
                '[survive] {:s} too few surviving data ({:f}%)'.format(v, surv * 100.))
        elif surv < msurv1:
            flags[fkey] = 1
            logger.debug(
                '[survive] {:s} reduced  surviving data ({:f}%)'.format(v, surv * 100.))
        else:
            flags[fkey] = 0
            logger.insane(
                '[survive] {:s} nominal  surviving data ({:f}%)'.format(v, surv * 100.))

    return flags, qms


# ----------------------------------------------------------------
#
# quality check 17

def docovmax(conf, dat, dt):
    """
    Lag correction by covariance maximization (Quality check 17).

    Extended lag correction finding optimal shift for maximum correlation,
    then correcting based on expected physical transport time.
    Inspired by :cite:`fow_aafm96a`

    :param conf: Configuration object with lag correction parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :param dt: Time step between measurements [s]
    :type dt: float
    :return: Tuple of (quality_measures, corrected_data)
    :rtype: tuple(dict, pandas.DataFrame)

    :note: Calculates expected lag from sensor separation and wind speed,
           compares to correlation-based lag, and applies correction.
    """
    logger.insane('docovmax')

    qms = {}
    n = ec.safe_len(dat)

    # copy dat to res, so dat remains untouched
    res = dat.copy()

    l2 = getconf(conf, 'L2')
    ll = int(l2 / dt)  # full window width
    limt = 0.10

    # anemometer position
    pn = ['QQX', 'QQY', 'QQZ']
    posson = [conf.get(x, group=ec.sonprefix, kind='float') for x in pn]
    # gas analyzer position(s)
    poshyg = [conf.get(x, group=ec.hygprefix, kind='float') for x in pn]
    posco2 = [conf.get(x, group=ec.co2prefix, kind='float') for x in pn]
    # thermocouple position
    postco = [conf.get(x, group=ec.coupprefix, kind='float') for x in pn]
    # anemometer north angle
    # (phi is where north of device coordinate system is pointing to,
    # clockwise from north)
    uphi,uhand = north_angle(conf)
    # x-axis heading
    # FIXME xyaw is not really needed
    xphi = 0.

    # for each variable explicitly:
    for v in ec.metvar:
        logger.insane('srv: evaluating {:s}'.format(v))
        # quality measure name
        qkey = '_'.join([ec.val[v], 'qmcmx'])
        # determine lag needed for maximum correlation
        if n == 0 or v in ['ux', 'uy', 'uz', 'ts', 'pres']:
            qms[qkey] = 0.
        else:
            # remember zero-lag correlation
            rnul = crosscorr(res[v], res['uz'], 0)
            imax = 0
            if not np.isnan(rnul):
                rquit = rnul * (1. - limt)
                # loop over all lags
                rmax = rnul
                lags = list(np.arange(1, ll, 1))
                for i in lags:
                    r = np.abs(crosscorr(dat[v], dat['uz'], int(i)))
                    if not np.isnan(r) and r > rmax:
                        rmax = r
                        imax = i
                    # speed up
                    elif r < rquit:
                        break
                # search negative lags
                lags = list(np.arange(-1, -ll, -1))
                for i in lags:
                    r = np.abs(crosscorr(dat[v], dat['uz'], int(i)))
                    if not np.isnan(r) and r > rmax:
                        rmax = r
                        imax = i
                    # speed up
                    elif r < rquit:
                        break
            else:
                rmax = 1.
                rnul = 1.
            # compute index of bet correlation and log it
            lcor = (rmax - rnul) / rnul
            # imax is opposite sign, compared to FORTRAN code!
            imax = -imax
            logger.insane('[lagcor] max response ratio: {:f}'.format(lcor))
            logger.insane(
                '[lagcor] at shift: {:d} records {:f} s'.format(imax, imax * dt))

            # compute expected lag due to wind
            #   mean wind in anemometer coordinates
            umean = ec.allnanok(np.nanmean, res['ux'])
            vmean = ec.allnanok(np.nanmean, res['uy'])
            #   mean wind in geographic coordinates
            #     uphi is clockwise angle between anemometer
            #     coordinates and geographic coordinates
            ugeo = (+ np.cos(uphi * ec.deg2rad) * umean
                    + np.sin(uphi * ec.deg2rad) * vmean * uhand)
            vgeo = (- np.sin(uphi * ec.deg2rad) * umean
                    + np.cos(uphi * ec.deg2rad) * vmean * uhand)
            #     sensor separation (anemometer to scalar)
            if v == 'h2o':
                posdat = poshyg
            elif v == 'co2':
                posdat = posco2
            elif v == 'tcoup':
                posdat = postco
            else:
                posdat = (np.nan, np.nan)
            dx = posdat[0] - posson[0]
            dy = posdat[1] - posson[1]
            #     sensor separation in geographic coordinates
            dxgeo = (+ np.cos(xphi * ec.deg2rad) * dx
                     + np.sin(xphi * ec.deg2rad) * dy)
            dygeo = (- np.sin(xphi * ec.deg2rad) * dx
                     + np.cos(xphi * ec.deg2rad) * dy)
            sep = np.sqrt(dxgeo ** 2 + dygeo ** 2)
            #     sensor separation direction unity vectors
            if sep != 0.:
                dxgeo = dxgeo / sep
                dygeo = dygeo / sep
            else:
                dxgeo = 0.
                dygeo = 0.
            #     scalar product is wind speed component along separation
            wsep = -ugeo * dxgeo - vgeo * dygeo
            if wsep != 0. and not pd.isnull(wsep) and not pd.isnull(sep):
                tsep = sep / wsep
            else:
                tsep = 0.
            isep = int(round(tsep / dt))
            #
            mgeo = np.sqrt(ugeo ** 2 + vgeo ** 2)
            dgeo = 180. + np.arctan2(ugeo, vgeo) / ec.deg2rad % 360.
            logger.insane(
                '[docovmax] mean wind: {:.1f} m/s from {:.1f} deg'.format(mgeo, dgeo))
            logger.insane(
                '[docovmax] mean wind along separation: {:.1f} m/s'.format(wsep))
            logger.insane(
                '[docovmax] corresponding shift: {:.3f} s or {:d} rec'.format(tsep, isep))
            #
            #  calculate  correction
            shift = imax - isep
            tshift = dt * float(shift)
            qms[qkey] = tshift
            logger.insane(
                '[docovmax] shift applied      : {:.3f} s or {:d} rec'.format(tshift, shift))
            #  apply correction
            if shift != 0:
                res.loc[:, v].shift(shift)

    return qms, res


# ----------------------------------------------------------------
# ----------------------------------------------------------------
#  end of quality checks worker routines follow below
# ----------------------------------------------------------------
# ----------------------------------------------------------------


# ----------------------------------------------------------------
#
def init_intervals(conf):
    """
    Initialize processing intervals from configuration dates.

    Expands start/end date definitions into individual averaging intervals
    based on the specified averaging period.

    :param conf: Configuration object with date and interval settings
    :type conf: object
    :return: DataFrame with interval start/end times
    :rtype: pandas.DataFrame

    :note: Creates intervals with right-closed boundaries for compatibility
           with standard eddy-covariance processing conventions.
    """
    db = conf.get('DateBegin', kind="str")
    de = conf.get('DateEnd', kind="str")
    date_begin = pd.to_datetime(db, utc=True)
    date_end = pd.to_datetime(de, utc=True)

    logger.debug('%s --%s' % (str(date_begin), str(date_end)))

    date_intv = '{:d}s'.format(
        int(ec.string_to_interval(conf.get('AvgInterval', kind='str'))))
    date_diff = pd.to_timedelta(date_intv)
    #
    try:
        # for pandas >=1.4
        ends = pd.date_range(start=date_begin, end=date_end, freq=date_intv,
                             tz='UTC', inclusive='right')
    except TypeError:
        # for pandas < 1.4
        ends = pd.date_range(start=date_begin, end=date_end, freq=date_intv,
                             tz='UTC', closed='right')
    begins = [x - date_diff for x in ends]

    r = pd.DataFrame(data={'begin': begins, 'end': ends}, index=ends)
    return r

# ----------------------------------------------------------------

def intervals_to_file(conf, intervals):
    """
    Write interval information to output file.

    Creates formatted output file with interval boundaries and metadata
    for subsequent processing steps.

    :param conf: Configuration object with output settings
    :type conf: object
    :param intervals: DataFrame containing interval data and results
    :type intervals: pandas.DataFrame

    :note: Output format compatible with EC-PACK interval file conventions.
    """
    #
    # get file name from config
    #
    interpath = conf.get('Parmdir')
    interbase = conf.get('InterName')
    intername = os.path.join(interpath, interbase)
    #
    # open file
    interfile = io.open(intername, 'w+')
    # write header
    interfile.write(u' doy1 h1 m1 doy2 h2 m2 q p_pa ncfile imedfile\n')
    #
    #
    for i in intervals.to_dict(orient='records'):
        fmt = '{:5d} {:02d} {:02d} {:5d} {:02d} {:02d} '
        fmt += '{:10.8f} {:8.1f} {:s} {:s}\n'
        line = fmt.format(
            i['begin'].dayofyear + i['begin'].year *
            1000, i['begin'].hour, i['begin'].minute,
            i['end'].dayofyear + i['end'].year *
            1000, i['end'].hour, i['end'].minute,
            i['s_rhov'], i['s_pp'],
            i['ncfile'], i['ncfile'].replace('.nc', '.imed')
        ).replace('nan', 'NaN')
        #    WRITE (intfid, '(2(i3.3,x,i2.2,x,i2.2,x)'//  &
        #        ',f10.8,x,f8.1,x,a,x,a)') doy(invarr(1,1),invarr(2,1),invarr(3,1)),  &
        #        invarr(4,1),invarr(5,1), doy(invarr(1,2),invarr(2,2),invarr(3,2)),  &
        #        invarr(4,2),invarr(5,2), s_qf(intv),s_pp(intv),  &
        #        trim(ofname(ofidx(intv)))//'.nc',trim(ofname(ofidx(intv)))//'.imed'
        interfile.write(str(line))

    interfile.close()


# ----------------------------------------------------------------
#
#  expand start date definitions to interval times
#  return dataframe
#


# noinspection GrazieInspection
def process_slow(conf, intervals, progress=100):
    """
    Process slow-response meteorological data.

    Retrieves and processes "slowe data", i.e.
    slowly-varying reference measurements
    (pressure, temperature, humidity) for use in quality control
    and flux calculations.

    :param conf: Configuration object with slow data settings
    :type conf: object
    :param intervals: DataFrame with processing intervals
    :type intervals: pandas.DataFrame
    :param progress: Progress reporting weight, defaults to 100
    :type progress: float
    :return: Updated intervals DataFrame with slow data
    :rtype: pandas.DataFrame

    :note: Resamples slow data to interval averages and calculates
           derived quantities like water vapor density from relative humidity.
    """
    #
    # construct names
    #
    # names of config tokens
    parnam = {x: ec.sccprefix + ec.refstem[x] + '_nam' for x in ec.refvar}
    # values of config tokens
    colnam = {x: conf.get(parnam[x], kind='str') for x in ec.refvar}
    #
    # get slow data
    #
    columns = list(filter(lambda x: len(x) != 0, colnam.values()))
    #    date_begin = dateutil.parser.parse(
    #        conf.get('DateBegin', kind='str')+':00 UTC')
    #    date_end = dateutil.parser.parse(conf.get('DateEnd', kind='str')+':00 UTC')
    date_begin = pd.to_datetime(conf.get('DateBegin', kind='str'), utc=True)
    date_end = pd.to_datetime(conf.get('DateEnd', kind='str'), utc=True)
    logger.debug('%s --%s' % (str(date_begin), str(date_end)))
    di = ecdb.retrieve_df('raw', 'slow', columns, date_begin, date_end)
    di.index = di['TIMESTAMP']
    ec.progress_increment(0.5 * progress)
    #
    # make averages (resample)
    #
    rule = '{:.0f}S'.format(ec.string_to_interval(
        conf.get('AvgInterval', kind='str')))
    logger.debug('resampling rule: {:s}'.format(rule))
    do = di.resample(rule=rule, closed='right',
                     origin=intervals.index[0]-pd.Timedelta(rule),
                     label='right').mean().reindex(intervals.index)
    ec.progress_increment(0.25 * progress)
    #
    # copy values to interval dataframe
    #
    intervals['s_pp'] = np.nan
    intervals['s_tc'] = np.nan
    intervals['s_qf'] = np.nan
    intervals['s_rhov'] = np.nan
    for v in ec.refvar:
        if len(colnam[v]) != 0:
            logger.debug('we got a reference column "%s"' % ec.refstem[v])
            if v == 'pp':
                intervals['s_pp'] = do[colnam[v]].values * 100.  # hPa -> Pa
            elif v == 'tc':
                intervals['s_tc'] = do[colnam[v]].values  # °C
            elif v == 'rh':
                est = (100. * 6.112 *
                       np.exp(17.62 * intervals['s_tc'] /
                              (243.12 + intervals['s_tc'])))  # Pa

                e = est * do[colnam[v]] / 100  # % -> Pa
                intervals['s_rhov'] = e / (ec.r_v *  # Pa -> kg m^{-3}
                                           (ec.Kelvin + intervals['s_tc']))

                intervals['s_qf'] = 0.622 * e / intervals['s_pp']  # Pa->1
            else:
                intervals[v] = do[colnam[v]].values
    ec.progress_increment(0.25 * progress)
    return intervals


#
#
#
def qc_raw_init(conf, interval, dat):
    """
    Initialize quality control by calculating derived variables.

    Converts raw measurements to derived quantities needed for quality
    control tests (specific humidity, CO2 mixing ratio, etc.).

    :param conf: Configuration object
    :type conf: object
    :param interval: Single interval data record
    :type interval: dict
    :param dat: DataFrame with raw measurement data
    :type dat: pandas.DataFrame
    :return: Updated interval record
    :rtype: dict

    :note: Handles missing pressure/temperature by interpolation or
           using reference values from slow measurements.
    """
    #
    # conversions
    #
    # fill nan values pressure
    if not dat['pres'].isnull().all():
        t_pp = dat['pres'].interpolate('linear') * 1000.  # kPa -> Pa
        logger.insane('using pressure: fast')
        if pd.isnull(interval['s_pp']):
            interval['s_pp'] = np.nanmean(dat['pres']) * 1000.  # kPa -> Pa
            logger.info('filling reference pressure: fast')
    elif not pd.isnull(interval['s_pp']):
        t_pp = pd.Series(interval['s_pp'], dat.index)  # Pa
        logger.insane('using pressure: slow')
    else:
        t_pp = pd.Series(np.nan, dat.index)
        logger.insane('using pressure: nan')
    #
    # fill nan values temperature
    if not dat['tcoup'].isnull().all():
        t_tc = dat['tcoup'].interpolate('linear')  # C
        logger.insane('using temperature: fast Thermometer')
    elif not dat['ts'].isnull().all():
        t_tc = dat['ts'].interpolate('linear')  # C
        logger.insane('using temperature: fast Sonic')
    elif not pd.isnull(interval['s_tc']):
        t_tc = pd.Series(interval['s_tc'], dat.index)  # Pa
        logger.insane('using temperature: slow')
    else:
        t_tc = pd.Series(np.nan, dat.index)
        logger.insane('using temperature: nan')
    #
    # dry air density
    rho = t_pp / (ec.r_l * (ec.Kelvin + t_tc))  # kg/m^3
    #
    # specific humidity
    dat['q'] = dat['h2o'] * 0.001 / rho  # mg/m^3   -> g/kg
    #
    # specific co2 concentration
    dat['ppm'] = (dat['co2'] / 44.) * 8.314 * (t_tc + 273.15) / (t_pp / 1000.)
    #  c02/44 in g, pres in kPa (pa/1000)=> ppm in 10^-6 aka umol/mol

    #
    # treat missing or scrambled diagnostics
    if len(conf.get(ec.fccprefix + ec.stem['diag_csat'] + '_nam')) == 0:
        #  pretend everything is normal
        dat['diag_csat'] = np.remainder(np.arange(len(dat.index)), 64)
    elif 'Campbell' in conf.get('Qflags', kind='str'):
        logger.info('expect CSAT diag to be scrambled by Campbell')
        if (dat['diag_csat'] <= 4096).all():
            #   move csat quality bits left
            dat['diag_csat'] = (dat['diag_csat'] * 4096 +
                                np.remainder(np.arange(len(dat.index)), 64))
        else:
            logger.critical('CSAT3 flags NOT scrambled by the' +
                             'example program, remove directive to unscramble')
            raise ValueError
    if len(conf.get(ec.fccprefix + ec.stem['diag_irga'] + '_nam')) == 0:
        # pretend everything is normal
        dat['diag_irga'] = 249
    elif 'noirga' in conf.get('Qflags', kind='str'):
        # pretend everything is normal
        dat['diag_irga'] = 249
        # flag unrealistic humidity values
        ratio = dat['q'] / interval['s_qf']
        dat.loc[(ratio < 0.75) | (ratio > 1.5), 'diag_irga'] = 0
        logger.info('mean q ratio {:f}, irga flagged {:f}'.format(
            np.mean(ratio), (dat.loc[:, 'diag_irga'] == 0).count()))
    return interval


def qc_raw_run(conf, interval, dat):
    """
    Execute comprehensive quality control test suite.

    Runs the complete set of quality control tests following :cite:`vim_jaot97`
    and extended tests, storing flags and quality measures.

    :param conf: Configuration object with QC parameters
    :type conf: object
    :param interval: Single interval data record
    :type interval: dict
    :param dat: DataFrame with measurement data
    :type dat: pandas.DataFrame
    :return: Tuple of (updated_interval, processed_data)
    :rtype: tuple(dict, pandas.DataFrame)

    :note: Tests are conditionally executed based on configuration settings.
           Data can be despiked using various methods (spk, chr, mad).
    """
    #
    # get config values
    #
    disable = conf.get('QCdisable', kind='str')
    despike = conf.get('Despiking', kind='str')

    desp = None
    #
    # create data frame of same dimension as dat
    # to record which values have changed
    ch = pd.DataFrame(False, columns=dat.columns, index=dat.index)

    # Quality checks:
    # letter mark tests after Vickers & Mahrt
    # numbers mark extended tests and corrections
    #
    # time between data points
    try:
        dt = (dat['TIMESTAMP'].iloc[-1] - dat['TIMESTAMP'].iloc[0]
              ).total_seconds() / float(len(dat.index))
    except (IndexError, ValueError):
        dt = 1. / conf.get('FREQ', 'Par', kind='float')
        logger.warning(
            'could not calculate frequency, using Par.FREQ instead.')
    #

    # d. Absolute limits
    if 'lim' not in disable:
        flags = limit(conf, dat)
        for k in flags:
            interval[k] = flags[k]

    # a. Spikes
    if 'spk' not in disable:
        flags, qms, dout = vmspike(conf, dat, dt)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]
        if despike == 'spk':
            desp = dout

    # 9. Spikes based on change rate
    if 'chr' not in disable:
        flags, qms, dout = ratespike(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]
        if despike == 'chr':
            desp = dout
            del dout

    # 10. Spikes based on median absolute deviation
    if 'mad' not in disable:
        flags, qms, dout = madspike(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]
        if despike == 'mad':
            desp = dout
            del dout

    # replace original data by despiked data of choice
    if despike in ['spk', 'chr', 'mad']:
        ch = (dat != desp)
        dat = desp

    # b. Amplitude Resolution
    if 'res' not in disable:
        flags, qms = ampres(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # c. Dropouts
    if 'drp' not in disable:
        flags, qms = dropout(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # e. Higher Moments
    if 'mom' not in disable:
        flags, qms = himom(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # 13. Higher moments compared to beta distribution
    if 'bet' not in disable:
        flags, qms = beta(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # h. Lag correlation
    if 'lag' not in disable:
        flags, qms = lagcor(conf, dat, dt)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # i. covariance maximization by lag correction
    if 'cmx' not in disable:
        qms, dat2 = docovmax(conf, dat, dt)
        for k in qms:
            interval[k] = qms[k]
        # track values that have changed
        ch = ch | (dat != dat2)
        dat = dat2
        del dat2

    # 16. Fraction of surviving data
    if 'srv' not in disable:
        flags, qms = survive(conf, dat, ch)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # f. Discontinuities
    if 'dis' not in disable:
        flags, qms = disco(conf, dat, dt)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # g. Nonstationarity
    if 'nst' not in disable:
        flags, qms = nonstat(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # 11. Stationarity following Foken & Wichura
    if 'fws' not in disable:
        flags, qms = fwstat(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # 12. Stationarity from flux by linear trend
    if 'cot' not in disable:
        flags, qms = cotrend(conf, dat)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # 14. Stationarity of variance
    if 'vst' not in disable:
        flags, qms = varstat(conf, dat, dt)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    # 15. turbulent fraction
    if 'ftu' not in disable:
        flags, qms = fturb(conf, dat, dt)
        for k in flags:
            interval[k] = flags[k]
        for k in qms:
            interval[k] = qms[k]

    return interval, dat


def dat_to_netcdf(conf, dat):
    """
    Write processed measurement data to NetCDF file.

    :param conf: Configuration object with output settings
    :type conf: object
    :param dat: DataFrame containing processed measurement data
    :type dat: pandas.DataFrame
    :return: Generated NetCDF filename or empty string if no data
    :rtype: str

    :note: Creates time variables and applies NaN replacement if configured
    """
    logger.insane('start writing to netcdf file')
    if len(dat.index) == 0:
        return ''  # i.e. no filename
    # read netcdf variable names from config
    varnamf = {x: conf.get(y, kind='str') for x, y in ec.intnamkey.items()}
    #
    # file name
    ncdfpath = conf.get('DatDir')
    # make directory if nonexistent (raise Error if a file of the same name exists)
    if not os.path.isdir(ncdfpath):
        os.makedirs(ncdfpath)
    timestr = dat.loc[0, 'TIMESTAMP'].strftime('%Y_%m_%d_%H%M')
    ncdfbase = 'ts_despiked_' + timestr + '.nc'
    ncdfname = os.path.join(ncdfpath, ncdfbase)
    #
    # provide new variable values
    #
    #  ncvar['time']=[(x-x.YearBegin) / pd.Timedelta('1 days') for x in dat['TIMESTAMP']]
    #  ncvar['time']=dat['TIMESTAMP']
    dat['year'] = [x.year for x in dat['TIMESTAMP']]
    dat['doy'] = [x.dayofyear for x in dat['TIMESTAMP']]
    dat['hhmm'] = [x.hour * 100 + x.minute for x in dat['TIMESTAMP']]
    dat['sec'] = [float(x.second) + float(x.nanosecond) *
                  1.E-06 for x in dat['TIMESTAMP']]
    dat['clock'] = [float(x.hour) * 1. + float(x.minute) / 60. +
                    float(x.second) / (60. * 60.) +
                    float(x.nanosecond) / (1000000. * 3600.) for x in dat['TIMESTAMP']]
    # replace nan by special value, if wanted
    try:
        outnan = conf.get(ec.qc_prefix + 'outnan', kind='float')
    except Exception:
        pass
    else:
        dat = dat.fillna(value=outnan)
        logger.info('nan replaced by {:f}'.format(outnan))
    #
    # open netcdf file
    #
    logger.debug('opening file {:s}'.format(ncdfname))
    ncfile = nc.Dataset(ncdfname, 'w')
    #
    # create variables
    #
    ncfile.createDimension('clock', len(dat.index))
    ncvar = {}
    for k, v in varnamf.items():
        # add only if variable is defined:
        if v != '':
            logger.insane('adding {:s} as variable "{:s}"'.format(k, v))
            # define variables: from name, type, dims
            # datatype 'f4' or 'f' (NC_FLOAT)
            ncvar[k] = ncfile.createVariable(v, 'f', dimensions='clock')
            # assign attribute values
            ncvar[k].setncattr('units', ec.intunit[k])
    # additional time variable, datatype 'f8' or 'd' (NC_DOUBLE)
    ncvar['time'] = ncfile.createVariable('clock', 'd', 'clock')
    #
    # put data into variables
    #
    for k, v in varnamf.items():
        # add only if variable is defined:
        if v != '':
            logger.insane('adding {:s} data'.format(k))
            ncfile.variables[v][:] = dat[k].values
    ncfile.variables['clock'][:] = dat['clock'].values
    #
    # close file
    #
    ncfile.close()

    logger.insane('done writing to netcdf file')
    return ncdfname


def dat_to_toa5(conf, dat):
    """
    Write processed measurement data to TOA5 format file.

    :param conf: Configuration object with output settings
    :type conf: object
    :param dat: DataFrame containing processed measurement data
    :type dat: pandas.DataFrame
    :return: Generated TOA5 filename
    :rtype: str

    :note: TOA5 is Campbell Scientific's table-oriented ASCII format
    """
    logger.insane('start writing to toa5 file')
    # read variable names from config
    varnamf = {x: conf.get(y, kind='str') for x, y in ec.intnamkey.items()}
    # replace nan by special value, if wanted
    try:
        outnan = conf.get(ec.qc_prefix + 'outnan', kind='float')
    except Exception:
        pass
    else:
        dat = dat.fillna(value=outnan)
        logger.info('nan replaced by {:f}'.format(outnan))
    #
    # collect toa5 header info
    #
    # read header line 1
    header = {'station_name': 'ts',
              'logger_name': '',
              'logger_serial': '',
              'logger_os': '',
              'logger_prog': '',
              'logger_sig': '',
              'table_name': 'despiked'}
    # read header line 2
    fields = ['TIMESTAMP', 'RECORD'] + [varnamf[x] for x in ec.var]
    header['column_count'] = len(fields)
    header['column_names'] = fields
    # read header line 3
    fields = ['TS', 'RN'] + [ec.intunit[x] for x in ec.var]
    header['column_units'] = fields
    # read header line 4
    fields = ['', ''] + [''] * len(ec.var)
    header['column_sampling'] = fields

    table_time = dat.loc[0, 'TIMESTAMP']
    table_date = table_time.strftime('%Y_%m_%d_%H%M')
    #
    # open file and write header
    #
    toa5base = ('TOA5' + '_' + header['station_name'] + '.' + header['table_name']
                + '_' + table_date + '.dat')
    toa5path = conf.get('DatDir')
    toa5name = os.path.join(toa5path, toa5base)

    logger.insane('writing header to toa5 file: ' + toa5name)
    ecfile.toa5_put_header(toa5name, header)

    # put data into file
    logger.insane('writing data   to toa5 file: ' + toa5name)
    rn = 0
    with io.open(toa5name, 'ab') as fid:
        for v in dat.to_dict(orient='rows'):
            rn += 1
            # format fixed (first two fields)
            fields = [ecfile.cs_style(v['TIMESTAMP'].strftime('%Y-%m-%d %H:%M:%S.%f')),
                      str(rn)]
            # format data fields
            fields += [ecfile.cs_style(v[x]) for x in ec.var]
            linesep = '\r\n'
            line = ','.join(fields) + linesep
            fid.write(line.encode('latin-1'))  # Encode to bytes

    logger.insane('done writing to toa5 file')
    return toa5name

# ----------------------------------------------------------------

def flags1_to_file(conf, intervals):
    """
    Write quality control flags and measures to output file.

    :param conf: Configuration object with output directory settings
    :type conf: object
    :param intervals: DataFrame containing interval results with flags
    :type intervals: pandas.DataFrame

    :note: Creates flags1.dat file with test flags and quality measures
    """
    #
    # get file name from config
    #
    flag1path = conf.get('OutDir')
    flag1base = 'flags1.dat'
    flag1name = os.path.join(flag1path, flag1base)
    #
    flag1file = io.open(flag1name, 'w+b')
    line = ('doy1 h1 m1 doy2 h2 m2 ' +
            ' '.join(['_'.join([ec.val[v], t]) for t in ec.tst for v in ec.metvar]) +
            ' ' +
            ' '.join(['_'.join([ec.val[v], q]) for q in ec.qmn for v in ec.metvar]) +
            '\n'
            )
    flag1file.write(line.encode())
    fmt = '{:5d} {:02d} {:02d} {:5d} {:02d} {:02d}'
    fmt += ' {:01d}' * (len(ec.metvar) * len(ec.tst))
    fmt += ' {:11.4g}' * (len(ec.metvar) * len(ec.qmn))
    fmt += '\n'
    for i in intervals.to_dict(orient='records'):
        try:
            line = fmt.format(
                *[i['begin'].dayofyear + (i['begin'].year % 100) * 1000, i['begin'].hour, i['begin'].minute,
                  i['end'].dayofyear + (i['end'].year % 100) * 1000, i['end'].hour, i['end'].minute] +
                 [ec.fint(i['_'.join([ec.val[v], t])]) for t in ec.tst for v in ec.metvar] +
                 [i['_'.join([ec.val[v], q])]
                  for q in ec.qmn for v in ec.metvar]
            ).replace('nan', 'NaN')
        except ValueError:
            if logger.getEffectiveLevel() < logger.DEBUG:
                for t in ec.tst:
                    for v in ec.metvar:
                        key = '_'.join([ec.val[v], t])
                        print(key)
                        print(i[key])
                        print(' {:11.4g}'.format(ec.fint(i[key])))
                for q in ec.qmn:
                    for v in ec.metvar:
                        key = '_'.join([ec.val[v], q])
                        print(key)
                        print(i[key])
                        print(' {:11.4g}'.format(i[key]))
            raise ValueError
        flag1file.write(line.encode())

    flag1file.close()

# ----------------------------------------------------------------

def process_fast_interval(args):
    """
    Process single interval of high-frequency measurement data.

    :param args: Tuple of (conf, interval, lock) for multiprocessing
    :type args: tuple
    :return: Updated interval record with QC results
    :rtype: dict

    :note: Retrieves raw data, applies QC tests, calibrates, and stores results.
           Designed for parallel execution with multiprocessing.
    """
    # Ensure custom logging is available in worker process
    from . import eclogger
    eclogger.ensure_logging_setup()
    #
    # unpack arguments
    conf, interval, lock = args
    #
    # print interval
    logger.info('process {:s} -- {:s}'.format(
        str(interval['begin']), str(interval['end'])))
    #
    # get columns
    parnam = {x: 'fastfmt.' + ec.stem[x] + '_nam' for x in ec.var}
    colnam = {x: conf.get(parnam[x], kind='str') for x in ec.var}

    #
    # get the data
    getcols = [colnam[x] for x in ec.var if not len(colnam[x]) == 0]
    dat = ecdb.retrieve_df('raw', 'fast',
                           columns=getcols,
                           tbegin=interval['begin'],
                           tend=interval['end'])
    logger.debug('got {:d} data'.format(len(dat.index)))
    #
    # rename columns to ec.var names
    logger.insane('got columns :' + ', '.join(dat.columns))
    dat.rename(columns={colnam[x]: x for x in ec.var if not len(colnam[x]) == 0},
               inplace=True)
    for x in ec.var:
        if x not in dat.columns:
            dat[x] = np.nan
    logger.insane('to columns :' + ', '.join(dat.columns))

    #
    # run qc tests
    interval = qc_raw_init(conf, interval, dat)
    dat = mask_diag(conf, dat)
    interval, dat = qc_raw_run(conf, interval, dat)

    #
    # write processed raw data
    pof = conf.get('PreOutFormat')
    if pof == 'NetCDF':
        ncfile = dat_to_netcdf(conf, dat.copy())
    elif pof == 'TOA5':
        ncfile = dat_to_toa5(conf, dat.copy())
    else:
        ncfile = ''
    interval['ncfile'] = os.path.basename(ncfile)

    #
    # calibrate and store mean values
    #
    # ??? should be done before QC but is done here for
    #     backward consistency
    #
    logger.debug('calibrating values')
    # C Apply gain and offset given in calibration file
    uncal = ecpack.convert(conf, dat)
    # C Do calibration i.e. do Device-specific corrections
    cal = ecpack.calibrat(conf, uncal, interval['s_pp'], tref=interval['s_tc'])
    #
    # add calibrated averages to intervals dataframe
    logger.debug('got calibrated values ' + ','.join(cal.columns))
    for v in cal.columns:
        if v not in ['TIMESTAMP', 'RECORD', 'diag_csat', 'diag_irga']:
            akey = '_'.join(['f', v])
            logger.insane('adding calibrated mean: ' + akey)
            interval[akey] = cal[v].mean(skipna=True)

    #
    # store processed & calibrated raw data
    #  pof=conf.get('PreOutFormat')
    #  if pof in ['NetCDF','TOA5']:
    #    pass
    #  else:
    with lock:
        # execute only once at a time to prevent race conditons
        ecdb.ingest_df(uncal, station_name='uncal', table_name='fast')
        ecdb.ingest_df(cal, station_name='calib', table_name='fast')

    # print interval
    logger.debug('done    {:s} -- {:s}'.format(
        str(interval['begin']), str(interval['end'])))
    return interval

# ----------------------------------------------------------------

def process_fast(conf, intervals, progress=100.):
    """
    Process all high-frequency measurement intervals with quality control.

    :param conf: Configuration object with processing parameters
    :type conf: object
    :param intervals: DataFrame with processing intervals
    :type intervals: pandas.DataFrame
    :param progress: Progress reporting weight, defaults to 100
    :type progress: float
    :return: Updated intervals DataFrame with QC results
    :rtype: pandas.DataFrame

    :note: Supports parallel processing using multiprocessing Pool.
           Number of processes controlled by conf['nproc'].
    """
    logger.debug('start processing "fast" data')
    with warnings.catch_warnings():
        warnings.filterwarnings(
            'ignore', message='DataFrame is highly fragmented')
        #
        # add columns for test flags
        #
        for v in ec.metvar:
            for t in ec.tst:
                nam = '_'.join([ec.val[v], t])
                intervals[nam] = 0.
        #
        # add columns for quality measures
        #
        for v in ec.metvar:
            for q in ec.qmn:
                nam = '_'.join([ec.val[v], q])
                intervals[nam] = np.nan
        #
        # add columns for quality measures
        #
        intervals['ncfile'] = ''
    #
    # define number of threads
    #
    nproc = conf.get('nproc', kind='int')

    logger.info('starting {:d} parallel processes'.format(nproc))
    if nproc == 0:
        pool = Pool(initializer=ecdb.init_worker_process, initargs=(ecdb.dbfile,))
    elif nproc > 1:
        pool = Pool(nproc, initializer=ecdb.init_worker_process, initargs=(ecdb.dbfile,))
    else:
        pool = None
    #
    # create the shared lock:
    # (https://stackoverflow.com/a/25558333)
    manager = Manager()
    lock = manager.Lock()
    #
    # progress per interval:
    int_progress = float(progress) / float(len(intervals.index))
    #
    # pack arguments and run thread(s)
    #
    args = [(conf, x, lock)
            for x in intervals.to_dict(orient='records')]
    if nproc == 1:
        #
        # execute serial
        results = []
        for a in args:
            result = process_fast_interval(a)
            ec.progress_increment(int_progress)
            if result is not None:
                results.append(result)
    else:
        # execute parallel
        results=[]
        for result in pool.imap(process_fast_interval, args):
            ec.progress_increment(int_progress)
            if result is not None:
                results.append(result)
    #
    # convert results into dataframe
    intervals_out = pd.DataFrame.from_records(results)

    logger.debug('done processing "fast" data')
    return intervals_out


# ----------------------------------------------------------------
#
#  preprocessor main routine
#


def preprocessor(conf):
    """
    Main preprocessing routine for eddy-covariance data.

    :param conf: Configuration object with all processing parameters
    :type conf: object
    :return: DataFrame with processed intervals and QC results
    :rtype: pandas.DataFrame

    :note: Orchestrates complete preprocessing workflow:
           - Initialize processing intervals
           - Process slow reference data
           - Process fast measurement data with QC
           - Generate output files
    """
    ec.progress_reset()
    logger.debug('start initializing interval data')
    intervals = init_intervals(conf)
    logger.debug('done initializing interval data')
    ec.progress_percent(5)

    logger.debug('start processing slow data')
    intervals = process_slow(conf, intervals, progress=5)
    logger.debug('done  processing slow data')

    logger.debug('start processing fast data')
    intervals = process_fast(conf, intervals, progress=90)
    logger.debug('done  processing fast data')

    #  dopf = conf.get('DateBegin')
    #  logger.insane('dopf: '+str(dopf))
    #  if not (dopf=='F' or dopf == False):
    #    intervals=planarfit(conf,intervals)

    pof = conf.get('PreOutFormat')
    logger.insane('pof: ' + str(pof))
    if pof == 'NetCDF' or pof == 'TOA5':
        intervals_to_file(conf, intervals)

    # flags1_to_file(conf, intervals)

    return intervals
