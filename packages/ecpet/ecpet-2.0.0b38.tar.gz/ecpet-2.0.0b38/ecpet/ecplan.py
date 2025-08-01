# -*- coding: utf-8 -*-
"""
EC-PeT Planar Fit Module
========================

Planar fit tilt correction implementation for sonic anemometer data following
the methodology of Wilczak et al. (2001). Provides comprehensive coordinate
system correction to account for non-level instrument mounting and ensure
accurate flux measurements in eddy-covariance systems.

The module performs:
    - Planar fit angle calculation (alpha, beta, gamma)
    - 3×3 rotation matrix generation for coordinate transformation
    - Optional yaw correction for mean wind alignment
    - Temporal interval management for planar fit periods
    - Single-run vs. multi-run processing options
    - Vertical wind bias estimation and correction

"""

import io
import logging
import os
import warnings

import numpy as np
import pandas as pd

from . import ecutils as ec

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
#
# planarfit_angles
#
# C     Subroutine computes angles and untilt-matrix needed for
# C     tilt correction of Sonic data, using Planar Fit
# C     Method, as described in James M. Wilczak et al (2001), 'Sonic
# C     Anemometer tilt correction algorithms', Boundary Meteorology 99: 127:150
# C     References to formulae are to this article.
# C     The planar fit matrix is extended with an additional yaw-correction
# C     to turn the first coordinate into the direction of the mean wind
# C     over all runs. This extra rotation makes results from different
# C     eddy-covariance systems comparable.
# C     Furthermore, there is the option to determine a planar fit for
# C     a single run (using all individual samples within a run,
# C     rather than the mean velocities from a collection of runs as
# C     in the classic planar fit method).
#
# ec-pack name: EC_C_T01
#               EC_C_T02 (included)
#
# parameters:
#   dowbias: boolean
#     compute bias in mean vertical wind (False)
#     implies that the mean vertical wind over all
#     runs is assumed to be zero
#   singlerun: boolean
#     determine rotation for a single run
#   umean: pandas.dataframe(columns=['ux','uy','uz']
#     matrix of run mean velocity vectors
# returns:
#   apf: matrix(float(3,3))
#     the planar fit 3*3 untilt-matrix
#   alpha: np.float64
#     tiltangle alpha in degrees
#   beta: np.float64
#     tiltangle beta in degrees
#   gamma: np.float64
#     Fixed yaw-angle in degrees associated with mean over all runs
#   wbias: np.float64
#     The bias in the vertical velocity
#


def planarfit_interval(dowbias, singlerun, interval, pfvalid=0.,
                       progress=100):
    """
    Calculate planar fit tilt correction angles for sonic anemometer data.

    Computes tilt correction matrix using the Planar Fit Method following
    Wilczak et al. (2001). Includes optional yaw correction to align
    coordinate system with mean wind direction.

    :param dowbias: Whether to compute bias in mean vertical wind
    :type dowbias: bool
    :param singlerun: Use single run method (individual samples) vs classic method (run means)
    :type singlerun: bool
    :param interval: DataFrame containing wind velocity measurements
    :type interval: pandas.DataFrame
    :param pfvalid: Fraction of valid samples required to include
                    interval in planar fit. Defaults to 0 (include all).
    :type pfvalid: float
    :param progress: Progress reporting weight, defaults to 100
    :type progress: int
    :return: Dictionary with rotation matrix and angles
    :rtype: dict

    :note: Returns dict containing:
           - alpha, beta, gamma: tilt angles in degrees
           - wbias: vertical wind bias
           - apf_ij: 3x3 rotation matrix elements

    :raises numpy.linalg.LinAlgError: When planar fit matrix inversion fails
    """

    logger.insane('planarfit calculation started')
#  print interval[['f_ux', 'f_uy', 'f_uz']]

    # mean winds
    mu, mv, mw = interval[['f_ux', 'f_uy', 'f_uz']].mean(axis=0)
    #
    # reject interval if not enough valid mean wind values
    m = ec.safe_len(interval)
    nanfrac = 1 - (interval[['f_ux', 'f_uy', 'f_uz']].count() / m)
    if any(nanfrac >= pfvalid):
        logger.warning(f"interval rejected: "
                       f"fraction of valid wind values too low: "
                       f" {interval['begin'].iloc[0]} -"
                       f" {interval['begin'].iloc[-1]}")
        alpha = beta = gamma = wbias = np.nan
        apf = pd.DataFrame(np.nan, index=range(3), columns=range(3))
    elif any([np.isnan(x) for x in [mu, mv, mw]]):
        logger.warning(f"interval rejected: "
                       f"mean wind is nan: "
                       f" {interval['begin'].iloc[0]} -"
                       f" {interval['begin'].iloc[-1]}")
        alpha = beta = gamma = wbias = np.nan
        apf = pd.DataFrame(np.nan, index=range(3), columns=range(3))
    else:

        # Make all sums of mean velocity components and of products of
        # mean velocity components in relation W.48
        muu = (interval['f_ux']*interval['f_ux']).mean()
        mvv = (interval['f_uy']*interval['f_uy']).mean()
        muv = (interval['f_ux']*interval['f_uy']).mean()
        muw = (interval['f_ux']*interval['f_uz']).mean()
        mvw = (interval['f_uy']*interval['f_uz']).mean()

    #  print('mu,mv,mw',mu,mv,mw)
    #  print('muu,muv,muw',muu,muv,muw)
    #  print('muv,mvv,mvw',muv,mvv,mvw)
    #  print('muw,mvw,mww',muw,mvw,np.nan)

        if not singlerun:
            # determine rotation for all runs
            logger.insane('determine rotation for all runs')
            if dowbias:
                # compute bias in mean vertical wind
                logger.insane('compute bias in mean vertical wind')
                # C
                # C Make matrix in relation W.48
                # C
                #          S(1,1) = 1.D0
                #          S(1,2) = umean(1)
                #          S(1,3) = umean(2)
                #          S(2,1) = umean(1)
                #          S(2,2) = uumean(1,1)
                #          S(2,3) = uumean(1,2)
                #          S(3,1) = umean(2)
                #          S(3,2) = uumean(1,2)
                #          S(3,3) = uumean(2,2)
                s = pd.DataFrame([[1.,  mu,  mv],
                                  [mu, muu, muv],
                                  [mv, muv, mvv]])
                # C
                # C Invert this matrix
                # C
                #          CALL EC_M_InvM(S,Sinv)
                sinv = pd.DataFrame(np.linalg.pinv(s.values), s.columns, s.index)
                # C
                # C Make RHS of relation W.48
                # C
                #          x(1) = umean(3)
                #          x(2) = uumean(1,3)
                #          x(3) = uumean(2,3)
                x = [mw, muw, mvw]
                # C
                # C Calculate coefficients b0, b1 and b2 in relation W.48
                # C
                #          CALL EC_M_MapVec(SInv,x,b(0))
                #
                # C SYNOPSIS
                # C     CALL EC_M_MapVec(a,x,y)
                # C FUNCTION
                # C     Calculates the image of "x" under the map "a"; y(i) = a(ij)x(j)
                b = sinv.dot(x)
                # C
                # C Find the bias in the vertical velocity via relation W.39
                # C
                #          WBias = b(0)
                wbias = b[0]
            else:
                logger.insane('do NOT compute bias in mean vertical wind')
                # C
                # C Make the sub-matrix of relation W.48 for a plane through origin
                # C
                #          SS2(1,1) = uumean(1,2)
                #          SS2(1,2) = uumean(2,2)
                #          SS2(2,1) = uumean(1,1)
                #          SS2(2,2) = uumean(2,1)
                ss2 = pd.DataFrame(data=[[muv, mvv],
                                         [muu, muv]])
                # C
                # C Invert this matrix
                # C
                #          CALL EC_M_InvM2(SS2,SS2inv)
                try:
                    ss2inv = pd.DataFrame(np.linalg.pinv(
                        ss2.values), ss2.columns, ss2.index)
                except np.linalg.LinAlgError:
                    logger.error('planar fit did not converge')
                    # set output b = [w, b1, b2] to nan
                    b = [0, np.nan, np.nan]
                else:
                    # C
                    # C Make RHS of relation W.48 for this submatrix
                    # C
                    #          x(1) = uumean(2,3)
                    #          x(2) = uumean(1,3)
                    x = [mvw, muw]
                    # C
                    # C Calculate coefficients b1 and b2 in relation W.48
                    # C
                    #          CALL EC_M_Map2Vec(SS2Inv,x,b(1))
                    b = [0]+ss2inv.dot(x).tolist()
                    # C
                    # C Assume that the calibration of the sonic is ok and has no bias in w
                    # C
                    #          WBias = 0.D0
                wbias = 0.
        else:
            logger.insane('apply Wilczak et al. (2001) code')
            # Wilczak et al. (2001) Appendix A: Matlab example code
            #    flen=length(u);
            #    su=sum(u);
            #    sv=sum(v);
            #    sw=sum(w);
            #    suv=sum(u v );
            #    suw=sum(u w );
            #    svw=sum(v ∗ w 0 );
            #    su2=sum(u ∗ u 0 );
            #    sv2=sum(v ∗ v 0
            flen = len(interval.index)
            su = interval['f_ux'].sum()
            sv = interval['f_uy'].sum()
            sw = interval['f_uz'].sum()
            suv = (interval['f_ux']*interval['f_uy']).sum()
            suw = (interval['f_ux']*interval['f_uz']).sum()
            svw = (interval['f_uy']*interval['f_uz']).sum()
            su2 = (interval['f_ux']*interval['f_ux']).sum()
            sv2 = (interval['f_uy']*interval['f_uy']).sum()
    #    print('su,sv,sw',su,sv,sw)
    #    print('su2,muv,muw',su2,suv,suw)
    #    print('suv,sv2,svw',suv,sv2,svw)
    #    print('suw,svw,sw2',suw,svw,np.nan)
            #    H=[flen su sv; su su2 suv; sv suv sv2]
            H = np.array([[flen,  su, sv],
                          [su, su2, suv],
                          [sv, suv, sv2]])

    #    print('H',H)
            #    g=[sw suw svw]
            g = np.array([sw, suw, svw])
    #    print('g',g)
            #    x=H\g
            # b=H.div(g)
            b = np.linalg.solve(H, g)
    #    print('b',b)
            wbias = b[0]

        logger.insane('planar fit coefs b1,b2 : '+str(b[0:2]))
        # C
        # C Construct the factors involved in the planar angles
        # C
        #      Sqrt1 = SQRT(b(2)*b(2)+1)
        #      Sqrt2 = SQRT(b(1)*b(1)+b(2)*b(2)+1)
        sqrt1 = np.sqrt(b[2]*b[2]+1.)
        sqrt2 = np.sqrt(b[1]*b[1]+b[2]*b[2]+1.)
        # C
        # C Planar tilt angles alpha and beta in relation W.44
        # C
        #      SinAlpha = -b(1)/Sqrt2
        #      CosAlpha = Sqrt1/Sqrt2
        #      SinBeta = b(2)/Sqrt1
        #      CosBeta = 1.D0/Sqrt1
        sinalpha = -b[1]/sqrt2
        cosalpha = sqrt1/sqrt2
        sinbeta = b[2]/sqrt1
        cosbeta = 1./sqrt1
    #  print('sinalpha',sinalpha)
    #  print('cosalpha',cosalpha)
    #  print('sinbeta',sinbeta)
    #  print('cosbeta',cosbeta)

        #
        #      Alpha = 180.D0/Pi*ATAN2(SinAlpha,CosAlpha)
        #      Beta = 180.D0/Pi*ATAN2(SinBeta,CosBeta)
        alpha = np.arctan2(sinalpha, cosalpha)/ec.deg2rad
        beta = np.arctan2(sinbeta, cosbeta)/ec.deg2rad
    #  print alpha,beta
        logger.insane('planar fit angles al,be : {:f},{:f}'.format(alpha, beta))
        # C
        # C Planar (un-)tilt matrix P from relation W.36
        # C
        #      Apf(1,1) = CosAlpha
        #      Apf(1,2) = SinAlpha*SinBeta
        #      Apf(1,3) = -SinAlpha*CosBeta
        #      Apf(2,1) = 0.D0
        #      Apf(2,2) = CosBeta
        #      Apf(2,3) = SinBeta
        #      Apf(3,1) = SinAlpha
        #      Apf(3,2) = -CosAlpha*SinBeta
        #      Apf(3,3) = CosAlpha*CosBeta
        apf = pd.DataFrame.from_records([[cosalpha, sinalpha*sinbeta, -sinalpha*cosbeta],
                                         [0.,          cosbeta,          sinbeta],
                                         [sinalpha, -cosalpha*sinbeta, cosalpha*cosbeta]])
    #  print('apf raw:',apf)
        # C
        # C Additional yaw-correction to align the first coordinate axis with
        # C the mean velocity over all runs according to relation W.45
        # C
        #      CALL EC_M_MapVec(Apf,mu,mu)
        (mu, mv, mw) = apf.dot((mu, mv, mw))
        #
        #      UHor = (umean(1)**2+umean(2)**2)**0.5D0
        #      SinGamma = umean(2)/UHor
        #      CosGamma = umean(1)/UHor
        #      Gamma = 180.D0*ACOS(CosGamma)/PI
        #      IF (SinGamma.LT.0.D0) Gamma = 360.D0-Gamma
        #      IF (Gamma.GT.180.D0) Gamma = Gamma-360.D0
        uhor = ec.amount((mu, mv))
    #  print('uhor:',uhor)
        singamma = mv/uhor
    #  print('singamma:',singamma)
        cosgamma = mu/uhor
    #  print('cosgamma:',cosgamma)
        gamma = np.arccos(cosgamma)/ec.deg2rad
    #  print('gamma raw:',gamma)
        if singamma < 0.:
            gamma = 360.-gamma
        if gamma > 180:
            gamma = gamma - 360.
    #  print('gamma raw:',gamma)
        logger.insane('planar fit angles gamma : {:g}'.format(gamma))

        #
        #      Yaw(1,1) = CosGamma
        #      Yaw(1,2) = SinGamma
        #      Yaw(1,3) = 0.D0
        #      Yaw(2,1) = -SinGamma
        #      Yaw(2,2) = CosGamma
        #      Yaw(2,3) = 0.D0
        #      Yaw(3,1) = 0.D0
        #      Yaw(3,2) = 0.D0
        #      Yaw(3,3) = 1.D0
        yaw = pd.DataFrame([[cosgamma, singamma, 0.],
                            [-singamma, cosgamma, 0.],
                            [0.,       0., 1.]],
                           index=range(3), columns=range(3))
        #
        #      CALL EC_M_MMul(Yaw,Apf,Apf)
        apf = yaw.dot(apf)

    # end of reject or not

    ad = {'apf_{:0d}{:0d}'.format(i+1, j+1): apf.to_dict('index')[i][j]
          for j in range(3) for i in range(3)}
    an = {'alpha': alpha, 'beta': beta, 'gamma': gamma, 'wbias': wbias}
    res = an.copy()
    res.update(ad)

    logger.insane('planarfit calculation done')
    ec.progress_increment(progress)
    return res

# ----------------------------------------------------------------

def planarfit_times(conf):
    """
    Generate time boundaries for planar fit calculation intervals.

    Creates interval boundaries based on configuration settings, handling
    various time units and edge cases for data period coverage.

    :param conf: Configuration object with planar fit interval settings
    :type conf: object
    :return: DataFrame with interval start and end times
    :rtype: pandas.DataFrame

    :note: Supports time units: S(econds), M(inutes), H(ours), D(ays), W(eeks).
           Automatically adjusts interval boundaries to ensure complete
           coverage of the data period.
    """
   #
    # processing interval
    #  date_begin=dateutil.parser.parse(conf.get('DateBegin',kind='str')+':00 UTC')
    #  date_end=dateutil.parser.parse(conf.get('DateEnd',kind='str')+':00 UTC')
    date_begin = pd.to_datetime(
        conf.get('DateBegin', kind='str'), utc=True)
    date_end = pd.to_datetime(conf.get('DateEnd', kind='str'), utc=True)
    #
    # is interval given as a number (assume unit days)
    intervalstr = conf.get('PlfitInterval', kind='str')
    try:
        v = float(intervalstr)
        u = 'D'
    except ValueError:
        v = float(intervalstr[:-1])
        u = intervalstr[-1:].upper()
    #
    # if value has a fraction (e.g. 0.5D -> 12H)
    if not v.is_integer():
        if u == 'W':
            v = round(v/7.)
            u = 'D'
        elif u == 'D':
            v = round(v/24.)
            u = 'H'
        elif u == 'H':
            v = round(v/60.)
            u = 'H'
        elif u == 'M':
            v = round(v/60.)
            u = 'H'
        elif u == 'S':
            v = round(v)
    #
    # if value actually representd a larger unit
    if u == 'S' and v % 60 == 0:
        v = v/60.
        u = 'M'
    if u == 'M' and v % 60 == 0:
        v = v/60.
        u = 'H'
    if u == 'H' and v % 24 == 0:
        v = v/24.
        u = 'D'
    if u == 'D' and v % 7 == 0:
        v = v/7.
        u = 'W'
    #
    freq = '{:d}{:s}'.format(int(v), u)
    delta = pd.to_timedelta(freq)
    logger.debug('planar fit interval: %s' % format(delta))
    #
    breaks = pd.date_range(date_begin, date_end, tz='UTC', freq=freq)
    if len(breaks) == 0:
        too_short = True
    else:
        too_short = False
    #
    # replace first/last value by start/end of processing interval
    # https://stackoverflow.com/a/44263575
    # ... start
    if (too_short or breaks[0] > date_begin + delta / 2):
        # if first break is inside data interval -> prepend data begin time
        breaks = pd.date_range(date_begin, tz='UTC',
                               periods=1).union(breaks)
        logger.debug('prepending a first planar fit interval at data begin')
    elif breaks[0] == date_begin:
        pass
    else:
        # if first break is before data interval begin -> replace by data begin time
        breaks = pd.date_range(date_begin, tz='UTC', periods=1).union(breaks[1:])
        logger.debug('nudging first planar fit interval end to data begin')
    # ... end
    if (too_short or breaks[-1] < date_end - delta / 2):
        # if last break is inside data interval -> append data end time
        breaks = breaks.union(
            pd.date_range(date_end, tz='UTC', periods=1))  #
        logger.debug('appending a last planar fit interval at data end')
    elif breaks[-1] == date_end:
        pass
    else:
        # if last break is after data interval end -> replace by data end time
        breaks = breaks[:-1].union(
            pd.date_range(date_end, tz='UTC', periods=1))
        logger.debug('nudging last planar fit interval end to data end')
    # make dataframe witch columns for start/end of each
    # planar fit interval
    pint = pd.DataFrame(data={'begin': breaks[:-1],
                              'end': breaks[1:]})

    logger.debug('planar fit interval boundaries:')
    for i in pint.to_dict('records'):
        logger.debug('{:s} -- {:s}'.format(
            i['begin'].strftime('%Y-%m-%d %H:%M'),
            i['end'].strftime('%Y-%m-%d %H:%M')))
    return pint

# ----------------------------------------------------------------

def planarfit_to_file(conf, intervals):
    #
    # get file name from config
    #
    plfitpath = conf.get('Parmdir')
    plfitbase = conf.get('PlfName')
    plfitname = os.path.join(plfitpath, plfitbase)
    #
    # open file
    logger.debug('writing planarfit output to: {:s}'.format(plfitname))
    plfitfile = io.open(plfitname, 'w+')
    #
    #
    fmt = '{:8d} '*6+' '+'{:20.10f} '*13 + '\n'
    bla = ['apf_{:0d}{:0d}'.format(i+1, j+1)
           for j in range(3) for i in range(3)]
    for i in intervals.to_dict(orient='records'):
        line = fmt.format(
            i['begin'].dayofyear+i['begin'].year *
            1000, i['begin'].hour, i['begin'].minute,
            i['end'].dayofyear+i['end'].year *
            1000, i['end'].hour, i['end'].minute,
            i['alpha'], i['beta'], i['gamma'], i['wbias'],
            *[i[x] for x in bla]
        ).replace('nan', 'NaN')
#           Write(PlfFile,100) (StartTime(i),i=1,3),
#     &           (StopTime(i),i=1,3), Alpha, Beta, Gamma, WBias,
#     &           ((Apf(i,j),i=1,3),j=1,3)
# 100       FORMAT(6(I8,1X),1X,13(F20.10,1X))
        plfitfile.write(str(line))

    plfitfile.close()

# ----------------------------------------------------------------

def planarfit(conf, intervals):
    """
    Main planar fit processing routine for eddy-covariance data.

    Orchestrates complete planar fit workflow including interval generation,
    angle calculation, and result distribution back to measurement intervals.

    :param conf: Configuration object with planar fit parameters
    :type conf: object
    :param intervals: DataFrame with averaged wind velocity measurements
    :type intervals: pandas.DataFrame
    :return: Updated DataFrame with planar fit angles and rotation matrices
    :rtype: pandas.DataFrame

    :note: Applies planar fit method following Wilczak et al. (2001) to
           correct for sonic anemometer tilt. Results are grouped by
           planar fit intervals and distributed to individual measurement periods.

           Workflow:
           - Generate planar fit time intervals
           - Group measurement intervals by planar fit periods
           - Calculate tilt angles for each planar fit interval
           - Distribute results back to measurement intervals
           - Write output files if configured
    """
    logger.insane('starting planarfit')
    ec.progress_reset()
    #
    # get planarfit intervals
    pint = planarfit_times(conf)
    ec.progress_percent(10.)

    #
    # apply planarfit intervals as grouping to averaging intervals
    #
    # add column
    intervals['plfitint'] = np.nan
    pint['plfitint'] = pint.index.values
    # evaluate times
    for ii, i in intervals.iterrows():
        for pi, p in pint.iterrows():
            #            print(i['begin'].tz, p['end'].tz)
            if i['begin'] < p['end'] and i['end'] >= p['begin']:
                intervals.loc[ii, 'plfitint'] = pi

    logger.insane('planar fit intervals:')
    for i in pint.to_dict('records'):
        logger.insane('{:s} - {:s}: {:d}'.format(
            i['begin'].strftime('%Y-%m-%d %H:%M'),
            i['end'].strftime('%Y-%m-%d %H:%M'),
            i['plfitint']))
    #
    # calculate planar fit for each planarfit interval
    plcalc = pd.Series()
    pfvalid = conf.get('PFValid', 'Par', kind='float', unlist=True, na=0.)
    try:
        # Try with include_groups first (pandas >= 1.5.0)
        plcalc = intervals.groupby(['plfitint'],
                                   include_groups=False).apply(
            lambda x: planarfit_interval(False, False, x, pfvalid, 85))
    except TypeError:
        # Fall back to old syntax with warning suppression (pandas < 1.5.0)
        logger.debug('falling back to syntax for pandas < 1.5.0')
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",
                                    message=".*grouping columns.*",
                                    category=FutureWarning)
            plcalc = intervals.groupby(['plfitint']).apply(
                lambda x: planarfit_interval(False, False, x, pfvalid, 85))
    # covert multi-index single column to multiple columns
    planang = pd.DataFrame.from_records(plcalc.values)

    # be verbose
    logger.info('fitted angles: (alpha,beta,gamma,wbias)')
    for p in planang.to_dict('records'):
        logger.info('               ({:.3f}, {:.3f}, {:.3f}, {:.3f})'.format(
            p['alpha'], p['beta'], p['gamma'], p['wbias']))
    #
    # distribute planar fit results back to each averaging interval
    #
    intervals = intervals.join(planang, on='plfitint')
    #
    # write output
    #
    planang = pd.merge(pint, planang, left_index=True, right_index=True)
    pof = conf.get('PreOutFormat')
    if pof == 'NetCDF' or pof == 'TOA5':
        #           Write(PlfFile,100) (StartTime(i),i=1,3),
        #     &           (StopTime(i),i=1,3), Alpha, Beta, Gamma, WBias,
        #     &           ((Apf(i,j),i=1,3),j=1,3)
        # 100       FORMAT(6(I8,1X),1X,13(F20.10,1X))
        planarfit_to_file(conf, planang)

    ec.progress_percent(100)

    logger.insane('finished planarfit')
    return intervals
