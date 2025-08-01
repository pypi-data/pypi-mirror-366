# -*- coding: utf-8 -*-
"""
EC-PeT Postprocessing Module
============================

Advanced quality control and flux calculation routines for eddy-covariance data.
Implements comprehensive postprocessing following established methodologies for
surface-atmosphere exchange measurements, including flux quality assessment,
meteorological variable derivation, and standardized output generation.

The module performs:
    - Derived meteorological variable calculations (potential temperature,
      Obukhov length, mixing ratios, density corrections)
    - Mean-value quality control tests following established protocols
    - Integral turbulence characteristic analysis (Foken & Wichura methods)
    - Stationarity assessment using multiple approaches
    - Wind sector exclusion and footprint analysis
    - Error threshold validation for flux measurements
    - Quality flag application with configurable rules
    - Flux interdependency assessment

"""

import datetime
import io
import logging
import os

import numpy as np
import pandas as pd

from . import ecutils as ec
from ._version import __release__ as version

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------

def derived_variables(intervals):
    """
    Calculate derived meteorological and flux variables.

    :param intervals: DataFrame with basic flux and meteorological measurements
    :type intervals: pandas.DataFrame
    :return: Updated DataFrame with derived variables
    :rtype: pandas.DataFrame

    :note: Calculates potential temperature, virtual potential temperature,
           Obukhov length, CO2 mixing ratios, and density corrections.
           Temperature selection based on 'whichtemp' indicator.
    """

    # copy fluxes to be quality controlled
    intervals['tau'] = intervals['tausum']
    intervals['dtau'] = intervals['dtausum']
    intervals['e_0'] = intervals['esum']
    intervals['de_0'] = intervals['desum']
    intervals['fc2'] = intervals['fco2sum']
    intervals['dfc2'] = intervals['dfco2sum']
    # and select temperature and flux by valid temperature
    tl = pd.Series(index=intervals.index, dtype='float64')
    intervals['h_0'] = np.nan
    intervals['dh_0'] = np.nan
    for i in intervals.index:
        if intervals.loc[i, 'whichtemp'] == ec.metvar.index('ts'):
            logger.insane('whichtemp = ts -> hson selected')
            tl[i] = intervals.loc[i, 'mean_ts']
            intervals.loc[i, 'h_0'] = intervals.loc[i, 'hson']
            intervals.loc[i, 'dh_0'] = intervals.loc[i, 'dhson']
# rho schon hier
            intervals['rho'] = intervals['rhoson']
        elif intervals[i, 'whichtemp'] == ec.metvar.index('tcoup'):
            logger.insane('whichtemp = tcoup -> hcoup selected')
            tl[i] = intervals.loc[i, 'mean_tcoup']
            intervals.loc[i, 'h_0'] = intervals.loc[i, 'hcoup']
            intervals.loc[i, 'dh_0'] = intervals.loc[i, 'dhcoup']
# rho schon hier
            intervals['rho'] = intervals['rhocoup']
        else:
            logger.critical('internal error: unknown whichtemp')
            raise ValueError

    # !derived variables
    #      IF (notnan(tl(nd)).AND.notnan(pp(nd))) THEN
    #        theta(nd)=tl(nd)*(pnull/pp(nd))**(r_l/cp)
    #      ELSE
    #        theta(nd) = nan
    #      END IF
    intervals['theta'] = tl*(ec.pnull/intervals['s_pp'])**(ec.r_l/ec.cp)
    # !             write (*,*)"Theta(nd) = ",Theta(nd)
    #      IF (notnan(tau(nd)).AND. notnan(u_st(nd)).AND.u_st(nd) /= 0.) THEN
    #        rho(nd)=tau(nd)/(u_st(nd)**2)
    #      ELSE
    #        rho(nd) = nan
    #      END IF
# warum nicht so???
#  intervals['rho']=intervals['s_pp']/(ec.r_l*tl)
# weil rhoson/rhocoup für feuchte Luft schon berechnet wurden
# und hie bekannt sind.
# aber wir kennen rho ja schon (so if ... whichtemp)

    # !             write (*,*)"rho(nd) = ",rho(nd)
    #      IF (notnan(theta(nd)).AND.notnan(q(nd))) THEN
    #        theta_v(nd)=theta(nd)*(1.+0.61*q(nd))
    #      ELSE
    #        theta_v(nd) = nan
    #      END IF
    intervals['theta_v'] = intervals['theta']*(1.+0.61*intervals['mean_q'])
    logger.insane('theta_v = {:f}'.format(intervals['theta_v'].mean()))
    # !             write (*,*)"Theta_v(nd) = ",Theta_v(nd)
    #      IF (notnan(theta(nd))) THEN
    #        a_theta=0.61*cp*theta(nd)/l_v
    #      ELSE
    #        a_theta = nan
    #      END IF
    intervals['a_theta'] = 0.61*ec.cp*intervals['theta']/ec.l_v
    logger.insane('a_theta = {:f}'.format(intervals['a_theta'].mean()))
    # !             write (*,*)"a_theta = ",a_theta
    #      IF (notnan(u_st(nd)).AND. notnan(theta_v(nd)).AND.  &
    #            notnan(h0(nd)).AND. notnan(a_theta).AND.  &
    #            notnan(e0(nd)).AND. notnan(rho(nd))) THEN
    # !             write (*,*)"L_st feucht",Theta_v(nd),notnan(Theta_v(nd))
    #        l_st(nd)=-(u_st(nd)**3*theta_v(nd))/  &
    #            (kappa*g*(h0(nd)+a_theta*e0(nd))/(rho(nd)*cp))
    #      ELSE IF (notnan(u_st(nd)).AND.&
    #        notnan(theta(nd)).AND. notnan(h0(nd)).AND.  &
    #            notnan(rho(nd))) THEN
    # !calculate Obukhov lenght for dry air if humidity measurement missing
    #        l_st(nd)=-(u_st(nd)**3*theta(nd))/  &
    #            ((kappa*g*(h0(nd)+0.07*0.))/(rho(nd)*cp))
    # !             write (*,*)"L_st trocken"
    #      ELSE
    #        l_st(nd) = nan
    # !             write (*,*)"L_st nix
    #      END IF
    # !             write (*,*)"L_st(nd) = ",L_st(nd)

    for i in intervals.index:
        if (np.isfinite(intervals.loc[i, 'ustar']) and
            np.isfinite(intervals.loc[i, 'theta_v']) and
            np.isfinite(intervals.loc[i, 'h_0']) and
            np.isfinite(intervals.loc[i, 'a_theta']) and
            np.isfinite(intervals.loc[i, 'e_0']) and
                np.isfinite(intervals.loc[i, 'rho'])):
            intervals.loc[i, 'lstar'] = (
                -(intervals.loc[i, 'ustar']**3*intervals.loc[i, 'theta_v']) /
                (ec.kappa*ec.g *
                 (intervals.loc[i, 'h_0'] +
                  intervals.loc[i, 'a_theta']*intervals.loc[i, 'e_0']) /
                 (intervals.loc[i, 'rho']*ec.cp)
                 )
            )
        elif (np.isfinite(intervals.loc[i, 'ustar']) and
              np.isfinite(intervals.loc[i, 'theta']) and
              np.isfinite(intervals.loc[i, 'h_0']) and
              np.isfinite(intervals.loc[i, 'rho'])):
            # calculate Obukhov lenght for dry air if humidity measurement missing
            intervals.loc[i, 'lstar'] = (
                -(intervals.loc[i, 'ustar']**3*intervals.loc[i, 'theta']) /
                (ec.kappa*ec.g *
                 (intervals.loc[i, 'h_0'] + 0.07 * 0.) /
                 (intervals.loc[i, 'rho']*ec.cp)
                 )
            )
        else:
            intervals.loc[i, 'lstar'] = np.nan
    logger.insane('lstar = {:f}'.format(intervals['lstar'].mean()))

    # !convert kg_m^-2_m^-1 to mumol_m^-2_s^-1
    #      IF (notnan(c0(nd))) THEN
    #        cn(nd)=1000000./0.044*c0(nd)
    #      ELSE
    #        cn(nd) = nan
    #      END IF
    #      IF (notnan(c0_err(nd))) THEN
    #        cn_err(nd)=(1000000./0.044)*c0_err(nd)
    #      END IF

    # convert kg_m^-2_m^-1 to mumol_m^-2_s^-1
    intervals['cn'] = 1000000./0.044*intervals['fco2sum']
    intervals['dcn'] = (1000000./0.044)*intervals['dfco2sum']
    logger.insane('cn = {:f}'.format(intervals['cn'].mean()))
    logger.insane('dcn = {:f}'.format(intervals['dcn'].mean()))

    # !convert kg_m^-3 to mumol/mol
    #      IF (notnan(cco2(nd)).AND. notnan(tl(nd)).AND.  &
    #            notnan(pp(nd))) THEN
    # !            M(co2)=44g/mol
    # !            n(co2)=rho(co2)/M(co2)
    # !            M(air)=28.96
    # !            R(air)=287.102
    # !            n(air)=rho(air)/M(air) = p/(RT*M) = p/T * 1/RM(air)
    # !            n(co2)/n(air)=[rho(co2)*T*R(air)*M(air)]/[M(co2)*p]
    #        molco2(nd)=(cco2(nd)*287.102*28.96*tl(nd))/(pp(nd)*44.01)
    #        molco2(nd)=molco2(nd)*1000000. ! mol/mol -> umol/mol
    #      ELSE
    #        molco2(nd) = nan
    #      END IF

    # convert kg_m^-3 to mol/mol
    intervals['molco2'] = (intervals['mean_co2']*287.102 *
                           28.96*tl)/(intervals['s_pp']*44.01)
    # mol/mol -> umol/mol
    intervals['molco2'] = intervals['molco2'] * 1000000.
    logger.insane('molco2 = {:f}'.format(intervals['molco2'].mean()))

    #      IF (notnan(cco2_err(nd)).AND. notnan(tl(nd)).AND.  &
    #            notnan(pp(nd))) THEN
    #        molco2_err(nd)=(cco2_err(nd)*287.102*28.96*tl(nd)) /(pp(nd)*44.01)
    #        molco2_err(nd)=molco2_err(nd)*1000000. ! mol/mol->umol/mol
    #      ELSE
    #        molco2_err(nd) = nan
    #      END IF

    # convert kg_m^-3 to mol/mol
    intervals['dmolco2'] = (intervals['dmean_co2'] *
                            287.102*28.96*tl) / (intervals['s_pp']*44.01)
    # mol/mol->umol/mol
    intervals['dmolco2'] = intervals['dmolco2']*1000000.
    logger.insane('dmolco2 = {:f}'.format(intervals['dmolco2'].mean()))

    return intervals

# ----------------------------------------------------------------

def qc_mean_run(conf, intervals):
    """
    Execute quality control tests on mean flux and meteorological values.

    :param conf: Configuration object with QC test parameters
    :type conf: object
    :param intervals: DataFrame with calculated mean values and fluxes
    :type intervals: pandas.DataFrame
    :return: Updated DataFrame with QC flags and quality measures
    :rtype: pandas.DataFrame

    :note: Implements tests including mean vertical wind check,
           integral turbulence characteristics, excluded sectors,
           footprint analysis, and excessive error detection.
    """

    disable = conf.get('QCdisable', kind='str')

    # flag2=0
    # !i. mean vertical wind
    #  IF (.NOT.disable(mnw)) THEN
    #    qm2(qmmnw,k)=ABS(wmean(k))
    #    IF (notnan(wmean(k))) THEN
    #      IF (ABS(wmean(k)) > wlimit1) THEN
    #        WRITE (tmpstr,*)'mean w: limit1 exeed at',(flxtime(1,j,k),j=1,3)
    #        CALL log_verbose(tmpstr)
    #        flag2(:,mnw,k)=1
    #      END IF
    #      IF (ABS(wmean(k)) > wlimit2) THEN
    #        WRITE (tmpstr,*)'mean w: limit2 exeed at',(flxtime(1,j,k),j=1,3)
    #        CALL log_verbose(tmpstr)
    #        flag2(:,mnw,k)=2
    #      END IF
    #    ELSE
    #      WRITE (tmpstr,*)'mean w: missing',(flxtime(1,j,k),j=1,3)
    #      CALL log_warning(tmpstr)
    #      flag2(:,mnw,k)=2
    #    END IF
    #  END IF

    # i. mean vertical wind
    if 'mnw' not in disable:
        flag = pd.Series(0, index=intervals.index)
        # get limits from confguration
        wlimit1 = conf.get('wlimit1', group='qcconf', kind='float')
        wlimit2 = conf.get('wlimit2', group='qcconf', kind='float')
        # calculate quality measure
        intervals['qmmnw'] = np.abs(intervals['mean_uz'])
        flag[intervals['qmmnw'] > wlimit1] = 1
        flag[intervals['qmmnw'] > wlimit2] = 2
    else:
        flag = pd.Series(np.nan, index=intervals.index)

    for ival in ec.metvar:
        fkey = '{:s}_{:s}'.format(ec.val[ival], 'mnw')
        intervals[fkey] = flag
    ec.progress_percent(30)

    # !ii. integr. turb. characteristics after Foken & Wichura
    #  IF (.NOT.disable(itc)) THEN
    #    f=2.*omega*SIN(lat*deg2rad)
    #    IF (notnan(h0(k)).AND. notnan(rho(k)).AND.rho(k) /= 0..AND.  &
    #          notnan(u_st(k)).AND.u_st(k) /= 0.) THEN
    #      t_st=h0(k)/(rho(k)*cp*u_st(k))
    #    ELSE
    #      t_st = nan
    #    END IF
    #    IF (notnan(e0(k)).AND. notnan(rho(k)).AND.rho(k) /= 0..AND.  &
    #          notnan(u_st(k)).AND.u_st(k) /= 0.) THEN
    #      q_st=e0(k)/(rho(k)*l_v*u_st(k))
    #    ELSE
    #      q_st = nan
    #    END IF
    # !          write (*,*)'qcitc',(z_m-d_0)/L_st(k),u_st(k),T_st,q_st
    #    DO ival=1,6
    #      itcm = nan
    #      itcc = nan
    #      IF (ival == ux) THEN
    # !            test u
    #        IF (notnan(sigma(ux,k)).AND.  &
    #              notnan(u_st(k)).AND.u_st(k) /= 0..AND.  &
    #              notnan(l_st(k)).AND.l_st(k) /= 0.) THEN
    #          itcm=sigma(ux,k)/u_st(k)
    #          itcc=itc_u((z_m-d_0)/l_st(k),u_st(k),f)
    #        ELSE
    #          itcm=nan
    #          itcc=nan
    #        END IF
    #      ELSE IF (ival == uz) THEN
    # !            test w
    #        IF (notnan(sigma(uz,k)).AND.  &
    #              notnan(u_st(k)).AND.u_st(k) /= 0..AND.  &
    #              notnan(l_st(k)).AND.l_st(k) /= 0.) THEN
    #          itcm=sigma(uz,k)/u_st(k)
    #          itcc=itc_w((z_m-d_0)/l_st(k),u_st(k),f)
    #        ELSE
    #          itcm=nan
    #          itcc=nan
    #        END IF
    #      ELSE IF (ival == h2o) THEN
    # !            test q
    #        IF (notnan(sigma(h2o,k)).AND. notnan(q_st).AND.q_st /= 0..AND.  &
    #              notnan(l_st(k)).AND.l_st(k) /= 0.) THEN
    #          itcm=ABS(sigma(h2o,k)/q_st)
    #          itcc=itc_t((z_m-d_0)/l_st(k))
    #        ELSE
    #          itcm=nan
    #          itcc=nan
    #        END IF
    #      ELSE IF (ival == ts) THEN
    # !            test t
    #        IF (notnan(sigma(ts,k)).AND. notnan(t_st).AND.t_st /= 0..AND.  &
    #              notnan(l_st(k)).AND.l_st(k) /= 0.) THEN
    #          IF (ABS(h0(k)) < itchmin) THEN
    # !               dont appply test if  if |H0| > 10 W/m^2
    #            itcm=1.
    #            itcc=1.
    #          ELSE
    #            itcm=ABS(sigma(ts,k)/t_st)
    #            itcc=itc_t((z_m-d_0)/l_st(k))
    #          END IF
    #        ELSE
    #          itcm=nan
    #          itcc=nan
    #        END IF
    #      ELSE
    # !            no test for v and co2
    #        itcm=1.
    #        itcc=1.
    #      END IF
    #      IF (notnan((itcc)).AND. notnan(itcm).AND.itcm /= 0) THEN
    #        ditc=ABS(itcc-itcm)/ABS(itcc)
    #        IF (ditc/=ditc) THEN
    #          WRITE (tmpstr,*) 'ITC unexplained nan in',val(ival)
    #          CALL log_verbose(tmpstr)
    #        END IF
    #      ELSE
    #        ditc = nan
    # !             write(*,*)'!!   explained nan:',val(ival),itcm,itcc
    #      END IF
    # !           if (ival.eq.ux.or.ival.eq.uz) then
    # !             write(*,*)'z_m',z_m,' d_0',d_0,' L_st(k)',L_st(k)
    # !             write(*,*)'z/L',(z_m-d_0)/L_st(k),' u*',u_st(k),' f',f
    # !           endif
    #      IF (ival == 1) THEN
    #        qm2(qmitu,k)=ditc
    #      ELSE IF (ival == 3) THEN
    #        qm2(qmitw,k)=ditc
    #      ELSE IF (ival == 5) THEN
    #        qm2(qmitq,k)=ditc
    #      ELSE IF (ival == 6) THEN
    #        qm2(qmitt,k)=ditc
    #      END IF
    # !            write (*,*)val(ival),sigma(ival,k),ditc
    #      IF (ditc > itclim1) THEN
    #        flag2(ival,itc,k)=1
    #      END IF
    #      IF (ditc > itclim2) THEN
    #        WRITE (tmpstr,*)'ITC: limit exeeded ',val(ival),ditc
    #        CALL log_verbose(tmpstr)
    #        flag2(ival,itc,k)=2
    #      ELSE IF (isnan(ditc)) THEN
    #        WRITE (tmpstr,*)'ITC: undefined ',val(ival)
    #        CALL log_verbose(tmpstr)
    #        flag2(ival,itc,k)=1
    #      END IF
    #    END DO
    #  END IF
    for ival in ec.metvar:
        fkey = '{:s}_{:s}'.format(ival, 'itc')
        intervals[fkey] = np.nan
    if 'itc' not in disable:
        # Position
        latlon = conf.get('InstLatLon', kind='float', na=None)
        if latlon is None:
            logger.warning('`InstLatLon` not configured, assuming 50N.')
            lanlon = [50.,np.nan]
        # height of (wind) measurement
        zm = conf.get('QQZ', group='SonCal', kind='float')
        # displacement height
        dh = conf.get('Displacement', kind='float', na=None)
        if dh is None:
            logger.warning('Displacement not configured, assuming zero.')
            dh = 0.
        # calculate Coriolis-parameter
        coriolis = 2.*ec.omega*np.sin(latlon[0]*ec.deg2rad)

        # get limits from confguration
        itclim1 = conf.get('itclim1', group='qcconf', kind='float')
        itclim2 = conf.get('itclim2', group='qcconf', kind='float')
        itchmin = conf.get('itchmin', group='qcconf', kind='float')

        # T star / temperature scaling
        intervals['tstar'] = intervals['h_0'] / \
            (intervals['rho']*ec.cp*intervals['ustar'])
        # convert Inf/-Inf to nan
        intervals.loc[~np.isfinite(intervals['tstar']), 'tstar'] = np.nan
        # q star / humidity scaling
        intervals['qstar'] = intervals['e_0'] / \
            (intervals['rho']*ec.l_v*intervals['ustar'])
        # convert Inf/-Inf to nan
        intervals.loc[~np.isfinite(intervals['qstar']), 'qstar'] = np.nan

        # calculate quality measure
        for ival in ec.metvar:
            if ival == 'ux':
                # test u
                itcm = intervals['std_ux']/intervals['ustar']
                itcc = np.vectorize(itc_u)(
                    (zm-dh)/intervals['lstar'], intervals['ustar'], coriolis)
            elif ival == 'uz':
                # test w
                itcm = intervals['std_uz']/intervals['ustar']
                itcc = np.vectorize(itc_w)(
                    (zm-dh)/intervals['lstar'], intervals['ustar'], coriolis)
            elif ival == 'co2':
                # test q
                itcm = np.abs(intervals['std_q']/intervals['qstar'])
                itcc = np.vectorize(itc_t)((zm-dh)/intervals['lstar'])
            elif ival == 'ts':
                # test t
                itcm = np.abs(intervals['std_ts']/intervals['tstar'])
                itcc = np.vectorize(itc_t)((zm-dh)/intervals['lstar'])
                # don't apply test if  if |H0| > 10 W/m^2
                itcm[np.abs(intervals['h_0']) < itchmin] = 1.
                itcc[np.abs(intervals['h_0']) < itchmin] = 1.
            else:
                # no test for v and co2
                itcm = pd.Series(1., index=intervals.index)
                itcc = pd.Series(1., index=intervals.index)

            ditc = np.abs(itcc-itcm)/np.abs(itcc)

            if ival == 'ux':
                intervals['qmitu'] = ditc
            elif ival == 'uz':
                intervals['qmitw'] = ditc
            elif ival == 'h2o':
                intervals['qmitq'] = ditc
            elif ival == 'ts':
                intervals['qmitt'] = ditc

            # set flags
            fkey = '{:s}_{:s}'.format(ec.val[ival], 'itc')
            intervals.loc[:, fkey] = 0
            intervals.loc[~np.isfinite(ditc), fkey] = 1
            intervals.loc[ditc > itclim1, fkey] = 1
            intervals.loc[ditc > itclim2, fkey] = 2

            ec.progress_percent(35+10*ec.metvar.index(ival)/len(ec.metvar))

    ec.progress_percent(50)

    # iii. excluded sector wind direction
    if 'exs' not in disable:
        flag = pd.Series(0, index=intervals.index)
        breaks = conf.get('ExcludeSector', kind='float', na=[])
        if len(breaks) > 0:
            # convert list into list of pairs
            if len(breaks) % 2 == 0:
                # https://stackoverflow.com/a/23286299
                it = iter(breaks)
                exclude = zip(it, it)
            else:
                logger.error(
                    'config value ExcludeSector must an even number of values')
                raise ValueError
            for ex in exclude:
                flag[(intervals['dirfrom'] > ex[0]) &
                     (intervals['dirfrom'] > ex[0])] = 2
    else:
        flag = pd.Series(np.nan, index=intervals.index)

    for ival in ec.metvar:
        fkey = '{:s}_{:s}'.format(ec.val[ival], 'exs')
        intervals[fkey] = flag

    ec.progress_percent(60)

    # iv. footprint model after Kormann & Meixner
    # ! IF (.NOT.disable(fkm)) THEN
    # !   IF (notnan(dd(k)).AND. notnan(ff(k)).AND.ff(k) > 0..AND.  &
    # !         notnan(sigma(uz,k)).AND.sigma(uz,k) > 0..AND.  &
    # !         notnan(u_st(k)).AND.u_st(k) > 0..AND. notnan(l_st(k))) THEN
    # !     CALL int_phi(nsrc,xp,yp,np,dd(k)  &
    # !         ,z_m-d_0,sigma(uz,k),ff(k),u_st(k),l_st(k) ,in(:,k),xmax(k))
    # !     qm2(qmfkf,k)=in(1,k)
    # !     qm2(qmfkx,k)=xmax(k)
    # !     IF (in(1,k) < minfoot) THEN
    # !       WRITE (*,*)'footprint (K&M) off source #1 area' ,in(1,k)
    # !       flag2(:,fkm,k)=2
    # !!             else
    # !!               write (*,*)'footprint (K&M) fraction:      '
    # !!      &               ,in
    # !     END IF
    # !   ELSE
    # !     qm2(qmfkf,k)=0.
    # !     qm2(qmfkx,k)=0.
    # !     WRITE (*,*)'footprint (K&M) indefinite'
    # !     flag2(:,fkm,k)=2
    # !   END IF
    # ! END IF
    if 'fkm' not in disable:
        flag = pd.Series(0, index=intervals.index)

        # ???
        intervals['qmfkf'] = 0.
        intervals['qmfkx'] = 0.
        logger.warning('footprint model not yet implemented !!')

    else:
        intervals['qmfkf'] = np.nan
        intervals['qmfkx'] = np.nan
        flag = pd.Series(np.nan, index=intervals.index)

    for ival in ec.metvar:
        fkey = '{:s}_{:s}'.format(ec.val[ival], 'fkm')
        intervals[fkey] = flag

    ec.progress_percent(80)

    # !iv. exessive error
    #  IF (.NOT.disable(exe)) THEN
    #    h0_errthr=SQRT(herrmin**2+(herrfac*h0(k))**2)
    #    e0_errthr=SQRT(eerrmin**2+(eerrfac*e0(k))**2)
    #    c0_errthr=SQRT(cerrmin**2+(cerrfac*c0(k))**2)
    #    tauerrthr=SQRT(terrmin**2+(terrfac*(rho(k)*u_st(k)**2))**2)
    #    tauerr=rho(k)*2.*u_st(k)*u_st_err(k)
    #    IF (h0_err(k) > h0_errthr) THEN
    #      WRITE (tmpstr,*)'exessive error in sensible heat flux:'  &
    #          ,h0_err(k)/ABS(h0(k))*100.,'%'
    #      CALL log_verbose(tmpstr)
    #      flag2(ts,exe,k)=2
    #    END IF
    #    IF (e0_err(k) > e0_errthr) THEN
    #      WRITE (tmpstr,*)'exessive error in   latent heat flux:'  &
    #          ,e0_err(k)/ABS(e0(k))*100.,'%'
    #      CALL log_verbose(tmpstr)
    #      flag2(h2o,exe,k)=2
    #    END IF
    #    IF (c0_err(k) > c0_errthr) THEN
    #      WRITE (tmpstr,*)'exessive error in           CO2 flux:'  &
    #          ,c0_err(k)/ABS(c0(k))*100.,'%'
    #      CALL log_verbose(tmpstr)
    #      flag2(co2,exe,k)=2
    #    END IF
    #    IF (tauerr > tauerrthr) THEN
    #      WRITE (tmpstr,*)'exessive error in      momentum flux:'  &
    #          ,tauerr/(rho(k)*u_st(k)**2)*100.,'%'
    #      CALL log_verbose(tmpstr)
    #      flag2(ux:uy,exe,k)=2
    #    END IF
    #  END IF
    if 'exe' not in disable:
        flag = pd.DataFrame(0, index=intervals.index, columns=ec.metvar)
        herrmin = conf.get('Herrmin', group='qcconf', kind='float')
        herrfac = conf.get('Herrfac', group='qcconf', kind='float')
        eerrmin = conf.get('Eerrmin', group='qcconf', kind='float')
        eerrfac = conf.get('Eerrfac', group='qcconf', kind='float')
        cerrmin = conf.get('Cerrmin', group='qcconf', kind='float')
        cerrfac = conf.get('Cerrfac', group='qcconf', kind='float')
        terrmin = conf.get('terrmin', group='qcconf', kind='float')
        terrfac = conf.get('terrfac', group='qcconf', kind='float')

        herrthr = np.sqrt(herrmin**2+(herrfac*intervals['h_0'])**2)
        eerrthr = np.sqrt(eerrmin**2+(eerrfac*intervals['e_0'])**2)
        cerrthr = np.sqrt(cerrmin**2+(cerrfac*intervals['fco2sum'])**2)
        terrthr = np.sqrt(
            terrmin**2+(terrfac*(intervals['rhoson']*intervals['ustar']**2))**2)
        tauerr = intervals['rhoson']*2.*intervals['ustar']*intervals['dustar']

        flag.loc[np.abs(intervals['dh_0']) > herrthr, 'ts'] = 2
        flag.loc[np.abs(intervals['e_0']) > eerrthr, 'h2o'] = 2
        flag.loc[np.abs(intervals['fco2sum']) > cerrthr, 'co2'] = 2
        flag.loc[tauerr > terrthr, ['ux', 'uy', 'uz']] = 2
    else:
        flag = pd.DataFrame(np.nan, index=intervals.index, columns=ec.metvar)
    for ival in ec.metvar:
        fkey = '{:s}_{:s}'.format(ec.val[ival], 'exe')
        intervals[fkey] = flag[ival]

    ec.progress_percent(90)

    return intervals

# ----------------------------------------------------------------

def apply_flags(conf, intervals):
    """
    Apply quality control flag rules to flux measurements.

    :param conf: Configuration object with flagging rules and thresholds
    :type conf: object
    :param intervals: DataFrame with QC test results and flags
    :type intervals: pandas.DataFrame
    :return: Updated DataFrame with final flux flags and deleted bad values
    :rtype: pandas.DataFrame

    :note: Uses configurable rules to combine individual test flags into
           final flux quality flags. Supports soft/hard flagging and
           flux interdependency rules.
    """

    # del=0
    # DO k=1,nd
    #  WRITE (tmpstr,*)'applying flags:',(flxtime(1,j,k),j=1,3)
    #  CALL log_info(tmpstr)
    #  DO iflx=1,nflx
    #    CALL log_verbose('... for flux:'//flx(iflx))
    # !test flag dependences
    #    tfn=0
    #    DO iv=1,nval
    #      DO it=1,ntst
    #        tfn=tfn+1
    #        tfnam(tfn)=val(iv)//'_'//tst(it)
    #        tfval(tfn)=flag1(iv,it,k)
    #      END DO
    #      DO it=1,npts
    #        tfn=tfn+1
    #        tfnam(tfn)=val(iv)//'_'//pts(it)
    #        tfval(tfn)=flag2(iv,it,k)
    #      END DO
    #    END DO
    #    CALL fapply (tfn,tfnam,tfval,frules(iflx),flag(iflx,k))

    flag = pd.DataFrame(0, index=intervals.index, columns=ec.flx)
    for f in ec.flx:
        frules = conf.get('flag_{:s}'.format(f), group='qcconf', kind='str')
        if any(len(x) < 7 for x in frules):
            logger.critical(
                'in flagrules: invalid test flag name in "{:s}"'.format(' '.join(frules)))
            raise ValueError
        testflagnames = [x[0:7] for x in frules]
#    testflagaction= [x[7:8] for x in frules]
#    testflagthresh= [x[8:9] for x in frules]
        if any(x not in intervals.columns for x in testflagnames):
            logger.critical('in flagrules: test flag name not found')
            raise ValueError
#    testflag = intervals.filter(items=testflagnames)

        # --- fapply ---
        # outf=0
        # DO WHILE (len_trim(str) > 0)
        #  str=adjustl(str)
        #  CALL log_debug('#'//trim(str)//'#')
        #  DO
        #    IF (str(1:1) == " ".OR.len_trim(str) == 0) EXIT
        #    i=-1
        #    DO j=1,nf
        #      IF (str(1:7) == fnam(j)) i=j
        #    END DO
        #    IF (i == -1) THEN
        #      CALL log_critical('ERROR: unknown condition in flagrules')
        #      STOP
        #    ELSE
        #    END IF
        #    ll=INDEX(str," ")
        #    IF (ll == 8) THEN
        #      action='u'
        #      thr=0
        #    ELSE IF (ll == 10) THEN
        #      action=str(8:8)
        #      READ (str(9:9),'(i1)') thr
        #    ELSE
        #      action='q'
        #      thr=0
        #    END IF
        #    WRITE (tmpstr,*)'fapply cond ',fnam(i),' action ',action ,' thr ',thr
        #    CALL log_verbose(tmpstr)
        #    select case (action)
        #    case ('u')
        #    outf=MAX(outf,fval(i))
        #    IF (fval(i) > 0) THEN
        #      WRITE (tmpstr,*)'... fapply uses      ',fnam(i),'=',fval(i)
        #      CALL log_info(tmpstr)
        #    END IF
        #    case ('i')
        #    IF (fval(i) >= thr) THEN
        #      outf=MIN(2,outf+1)
        #      WRITE (tmpstr,*)'... fapply increase  ',fnam(i),'=',fval(i)
        #      CALL log_info(tmpstr)
        #    END IF
        #    case ('s')
        #    IF (fval(i) >= thr) THEN
        #      outf=1
        #      WRITE (tmpstr,*)'... fapply soft flag ',fnam(i),'=',fval(i)
        #      CALL log_info(tmpstr)
        #    END IF
        #    case ('h')
        #    IF (fval(i) >= thr) THEN
        #      outf=2
        #      WRITE (tmpstr,*)'... fapply hard flag ',fnam(i),'=',fval(i)
        #      CALL log_info(tmpstr)
        #    END IF
        #    case default
        #    CALL log_critical('unknown action in fapply')
        #    STOP
        #  END select
        #  str=adjustl(str(ll:))
        # END DO
        # END DO
        # --- /fapply

        # --- fapply ---
        for k in intervals.index:
            outflag = 0
            for j in frules:
                tfname = j[0:7]
                tfvalue = int(intervals.loc[k, tfname])
                if len(j) == 7:
                    action = 'u'
                    thresh = 0
                elif len(j) == 9:
                    action = j[7:8]
                    thresh = int(float(j[8:9]))
                else:
                    action = 'q'
                    thresh = 0
                logger.insane('fapply cond {:s} action {:s} thresh {:d}'.format(
                    tfname, action, thresh))
                if action == 'u':
                    if tfvalue > outflag:
                        outflag = tfvalue
                        logger.insane(
                            '... fapply uses      {:s} = {:d}'.format(tfname, tfvalue))
                elif action == 'i':
                    if tfvalue >= thresh:
                        outflag = np.min([2, outflag+1])
                        logger.insane(
                            '... fapply increase  {:s} = {:d}'.format(tfname, tfvalue))
                elif action == 's':
                    if tfvalue >= thresh and outflag < 1:
                        outflag = 1
                        logger.insane(
                            '... fapply soft flag {:s} = {:d}'.format(tfname, tfvalue))
                elif action == 'h':
                    if tfvalue >= thresh and outflag < 2:
                        outflag = 2
                        logger.insane(
                            '... fapply hard flag {:s} = {:d}'.format(tfname, tfvalue))
                else:
                    logger.critical('unknown action in apply_flags')
                    raise ValueError

            flag.loc[k, f] = outflag
        # --- end of fapply
    # end of loop over fluxes

    # !flux flag interdependences
    # --- begin flinter
    #  flagtmp=flag(:,k)
    # INTEGER, INTENT (IN) :: nf,inpf(nf)
    # INTEGER, INTENT (OUT) :: outf(nf)
    # CHARACTER (LEN=3), INTENT(IN) :: ff(nf)
    # CHARACTER (LEN=*), INTENT(IN) ::  rstr
    #
    # INTEGER               :: i,j,o
    # CHARACTER (LEN=1)    ::  r
    # CHARACTER (LEN=2048) :: str
    # LOGICAL               :: yes
    #
    # outf=inpf
    # str=rstr
    # DO WHILE (len_trim(str) > 0)
    #  str=adjustl(str)
    #  CALL log_debug('#'//trim(str)//'#')
    #  o=-1
    #  DO j=1,nf
    #    IF (str(1:3) == ff(j)) o=j
    #  END DO
    #  IF (o == -1) THEN
    #    CALL log_critical('unknown target flux in FluxInter rules')
    #    STOP
    #  ELSE
    #  CALL log_debug('FluxInter target'//ff(o))
    #  END IF
    #  r=str(4:4)
    #  str=str(5:)
    #  IF (str(1:1) == " ") THEN
    #    CALL log_critical('missing condition in FluxInter rules')
    #    STOP
    #  END IF
    #  yes=.true.
    #  DO
    #    IF (str(1:1) == " ".OR.len_trim(str) == 0) EXIT
    #    i=-1
    #    DO j=1,nf
    #      IF (str(1:3) == ff(j)) i=j
    #    END DO
    #    IF (i == -1) THEN
    #      CALL log_critical('unknown condition in FluxInter rules')
    #      STOP
    #    ELSE
    #    CALL log_debug('FluxInter condition'//ff(i))
    #    END IF
    #    IF (inpf(i) >= 2.AND.yes) THEN
    #      yes=.true.
    #      CALL log_debug('                   ... yes')
    #    ELSE
    #      yes=.false.
    #      CALL log_debug('                   ... no')
    #    END IF
    #    str=str(4:)
    #  END DO
    #  IF (yes) THEN
    #    SELECT CASE (r)
    #      CASE ('d')
    #        outf(o)=2
    #        CALL log_verbose('... FluxInter mark bad '//ff(o))
    #      CASE ('i')
    #        outf(o)=MIN(2,outf(o)+1)
    #        CALL log_verbose('... FluxInter increase '//ff(o))
    #      CASE DEFAULT
    #        CALL log_critical('unknown action in FluxInter rules')
    #        STOP
    #    END SELECT
    #  END IF
    # END DO
    # END SUBROUTINE
    # --- end of flinter

    # flux flag interdependences
    # --- begin flinter
    flagtmp = flag.copy()
    irules = conf.get('interrule', group='qcconf', kind='str')
    for ir in irules:
        logger.insane('flux flag interdependence rule: {:s}'.format(ir))
        if (len(ir)-7) % 3 != 0:
            # minimum 7 chars, optionally added N * 3 chrs
            logger.critical('incomplete FluxInter rule: {:s}'.format(ir))
            raise ValueError
        else:
            ifff = ir[0:3]
            iact = ir[3:4]
            iccc = []
            # read ccc in 3-char blocks until end of string
            for c in range(4, len(ir), 3):
                iccc.append(ir[c:c+3])
        if ifff not in ec.flx:
            logger.critical(
                'unknown target flux in FluxInter rules: {:s}'.format(ifff))
            raise ValueError
        else:
            logger.insane('FluxInter target: {:s}'.format(ifff))
        if iact not in ['i', 'd']:
            logger.critical(
                'unknown target action in FluxInter rules: {:s}'.format(iact))
            raise ValueError
        else:
            logger.insane('FluxInter action: {:s}'.format(iact))
        for c in iccc:
            if c not in ec.flx:
                logger.critical(
                    'unknown condition action in FluxInter rules: {:s}'.format(c))
                raise ValueError
            else:
                logger.insane('FluxInter condition: {:s}'.format(c))

            for k in intervals.index:
                if flagtmp.loc[k, c] >= 2:
                    yes = True
                    logger.insane('                   ... yes')
                else:
                    yes = False
                    logger.insane('                   ... no')

                if yes:
                    if iact == 'd':
                        flag.loc[k, ifff] = 2
                        logger.debug(
                            '... FluxInter mark bad {:s}'.format(ifff))
                    elif iact == 'i':
                        flag.loc[k, ifff] = np.min([2, flag.loc[k, ifff]+1])
                        logger.debug(
                            '... FluxInter increase {:s}'.format(ifff))
                    else:
                        logger.critical('unknown action in FluxInter rules')
                        raise ValueError
            # end for k in intervals-index
        # end for c in iccc
    # end of for ir in interrules
    # --- end of flinter

    # !delete bad flux values
    #  IF (flag(flt,k) >= kill) THEN
    #    u_st(k) = nan
    #    u_st_err(k) = nan
    #    del(flt)=del(flt)+1
    #  END IF
    #  IF (flag(flh,k) >= kill) THEN
    #    h0(k) = nan
    #    h0_err(k) = nan
    #    del(flh)=del(flh)+1
    #  END IF
    #  IF (flag(fle,k) >= kill) THEN
    #    e0(k) = nan
    #    e0_err(k) = nan
    #    del(fle)=del(fle)+1
    #  END IF
    #  IF (flag(flc,k) >= kill) THEN
    #    c0(k) = nan
    #    c0_err(k) = nan
    #    cn(k) = nan
    #    cn_err(k) = nan
    #    del(flc)=del(flc)+1
    #  END IF
    # END DO

    # store flags
    for f in ec.flx:
        intervals['flag_'+f] = flag[f]

    # delete bad flux values
    kill = conf.get('kill', group='qcconf', kind='int')
    deleted = pd.Series(0, index=ec.flx)

    elim = flag['tau'].ge(kill)
    if any(elim):
        intervals.loc[elim, 'ustar'] = np.nan
        intervals.loc[elim, 'dustar'] = np.nan
        deleted['tau'] = sum(deleted)

    elim = flag['h_0'].ge(kill)
    if any(elim):
        intervals.loc[elim, 'h_0'] = np.nan
        intervals.loc[elim, 'dh_0'] = np.nan
        deleted['h_0'] = sum(deleted)

    elim = flag['e_0'].ge(kill)
    if any(elim):
        intervals.loc[elim, 'e_0'] = np.nan
        intervals.loc[elim, 'de_0'] = np.nan
        deleted['e_0'] = sum(deleted)

    elim = flag['fc2'].ge(kill)
    if any(elim):
        intervals.loc[elim, 'fc2'] = np.nan
        intervals.loc[elim, 'dfc2'] = np.nan
        intervals.loc[elim, 'cn'] = np.nan
        intervals.loc[elim, 'dcn'] = np.nan
        deleted['fc2'] = sum(deleted)

    return intervals

# ----------------------------------------------------------------

def flags2_to_file(conf, intervals):
    """
    Write second-level quality flags to output file.

    :param conf: Configuration object with output directory settings
    :type conf: object
    :param intervals: DataFrame containing second-level QC flags
    :type intervals: pandas.DataFrame

    :note: Creates flags2.dat file with mean-value QC test results
           and quality measures for postprocessing analysis.
    """

    # OPEN(ff2fid,FILE=trim(opath)//'/'//trim(ff2name),STATUS="replace")
    # IF (nsrc <= 1) THEN
    #  srcstr =""
    # ELSE
    #  WRITE (srcstr,'(''SRC'',I2.2,999(X,''SRC'',I2.2))')(i,i=1,nsrc)
    # END IF
    # WRITE (ff2fid,'(999(x,a))') 'doy1 h1 m1 doy2 h2 m2',  &
    #    ((val(iv)//'_'//pts(ipts),iv=1,nval),ipts=1,npts), (q2n(iq2),iq2=1,nq2),  &
    #    trim(srcstr)
    # IF (nsrc <= 1) THEN
    #  WRITE (FMT,'(a,i3.3,a,i3.3,a,i3.3,a)') '(2(i3.3,x,i2.2,x,i2.2,x),'  &
    #      ,nval*npts,'(x,i1),' ,nq2,'(x,g11.4))'
    # ELSE
    #  WRITE (FMT,'(a,i3.3,a,i3.3,a,i3.3,a)') '(2(i3.3,x,i2.2,x,i2.2,x),'  &
    #      ,nval*npts,'(x,i1),' ,nq2,'(x,g11.4)'  &
    #      ,nsrc,'(x,g11.4))'
    # END IF
    # DO k=1,nd
    #  IF (nsrc <= 1) THEN
    #    WRITE(ff2fid,FMT) (flxtime(1,i,k),i=1,3),  &
    #        (flxtime(2,i,k),i=1,3), ((flag2(iv,ipts,k),iv=1,nval),ipts=1,npts),  &
    #        (qm2(iq2,k),iq2=1,nq2)
    #  ELSE
    #    WRITE(ff2fid,FMT) (flxtime(1,i,k),i=1,3),  &
    #        (flxtime(2,i,k),i=1,3), ((flag2(iv,ipts,k),iv=1,nval),ipts=1,npts),  &
    #        (qm2(iq2,k),iq2=1,nq2), (in(i,k),i=1,nsrc)
    #  END IF
    # END DO
    # CLOSE(ff2fid)

    #
    # get file name from config
    #
    flag2path = conf.get('OutDir')
    flag2base = 'flags2.dat'
    flag2name = os.path.join(flag2path, flag2base)
    #
    flag2file = io.open(flag2name, 'w+b')
    line = ('doy1 h1 m1 doy2 h2 m2 ' +
            ' '.join(['_'.join([ec.val[v], t]) for t in ec.pts for v in ec.metvar]) +
            ' '.join([q for q in ec.q2n]) +
            '\n'
            )
    flag2file.write(line.encode())
    fmt = '{:5d} {:02d} {:02d} {:5d} {:02d} {:02d}'
    fmt += ' {:01d}'*(len(ec.metvar)*len(ec.pts))
    fmt += ' {:11.4G}'*(1*len(ec.q2n))
    fmt += '\n'
    for i in intervals.to_dict(orient='records'):
        #            for t in ec.pts:
        #              for v in ec.metvar:
        #                print t,v,'_'.join([ec.val[v],t]),i['_'.join([ec.val[v],t])]
        #            for q in ec.q2n:
        #              for v in ec.metvar:
        #                print q,v,'_'.join([ec.val[v],q]),i['_'.join([ec.val[v],q])]
        #            print '==='
        try:
            line = fmt.format(
                *[i['begin'].dayofyear+(i['begin'].year % 100)*1000, i['begin'].hour, i['begin'].minute,
                  i['end'].dayofyear+(i['end'].year % 100)*1000, i['end'].hour, i['end'].minute] +
                [ec.fint(i['_'.join([ec.val[v], t])]) for t in ec.pts for v in ec.metvar] +
                [i[q] for q in ec.q2n]
            ).replace('nan', 'NaN')
        except ValueError:
            for t in ec.pts:
                for v in ec.metvar:
                    key = '_'.join([ec.val[v], t])
                    logger.debug(key, i[key])
                    logger.debug(' {:01d}'.format(ec.fint(i[key])))
            for q in ec.q2n:
                #               for v in ec.metvar:
                key = q
                logger.debug(key, i[key])
                logger.debug(' {:11.4G}'.format(i[key]))
            raise ValueError
        flag2file.write(line.encode())

    flag2file.close()

    return

# ----------------------------------------------------------------

def output_to_file(conf, intervals):
    """
    Write final quality-controlled flux data to output file.

    :param conf: Configuration object with output settings
    :type conf: object
    :param intervals: DataFrame with final QC results and flux values
    :type intervals: pandas.DataFrame

    :note: Generates main output file with quality-controlled fluxes,
           flags, and supporting meteorological variables in standardized format.
    """
    # filnam=trim(opath)//'/'//trim(outname)
    # OPEN(outfid,FILE=trim(filnam),STATUS="replace")
    # FMT='(2(I3,1X,2(I2,1X)),'// '4(3(G15.5:,1X)),'//  &
    #    '13(2(G15.5:,1X)))'
    # WRITE (outfid,'(a)') '# EC-FRAME version '//version//  &
    #    'generated '//timestr(time8())
    # WRITE (outfid,'(a)') 'DOY Hr Mn '//  &
    #    'DOY Hr Mn     '// 'UStar_qc        dUStar_qc       '//  &
    #    'UStar_flag      '// 'H_qc            dH_qc           '//  &
    #    'H_flag          '// 'LvE_qc          dLvE_qc         '//  &
    #    'LvE_flag        '// 'FCO2_qc         dFCO2           '//  &
    #    'FCO2_flag       '// 'FmolCO2_qc      dFmolCO2        '//  &
    #    'Dir             Mean(vectorU)   '// 'Thetason        Mean(q)         '//  &
    #    'CO2Mixr         dCO2Mixr        '// 'rho             LStar           '//  &
    #    'FPTarget        '// 'pres            '
    # WRITE (outfid,'(a)') '-   -  -  '//  &
    #    '-   -  -      '// '[m/s]           [m/s]           '//  &
    #    '[index]         '// '[W/m^2]         [W/m^2]         '//  &
    #    '[index]         '// '[W/m^2]         [W/m^2]         '//  &
    #    '[index]         '// '[kg/m^2]        [kg/m^2]        '//  &
    #    '[index]         '// '[umol/m^2]      [umol/m^2]      '//  &
    #    '[deg]           [m/s]           '// '[K]             [kg/kg]         '//  &
    #    '[umol/mol]      [umol/mol]      '// '[kg/m^3]        [m]             '//  &
    #    '[percent]       '// '[hPa]           '
    # DO k=1,nd
    #  outval=(/ u_st(k),u_st_err(k),REAL(flag(flt,k)),  &
    #           h0(k),h0_err(k),REAL(flag(flh,k)),  &
    #           e0(k),e0_err(k),REAL(flag(fle,k)),  &
    #           c0(k),c0_err(k),REAL(flag(flc,k)),  &
    #           cn(k),cn_err(k),  &
    #           dd(k),ff(k), theta(k),q(k),  &
    #           molco2(k),molco2_err(k), rho(k),l_st(k),  &
    #           in(1,k)*100., pp(k)/100.  &
    #      /)
    #  DO i=1,23
    #    IF (isnan(outval(i))) outval(i)=dummy
    #  END DO
    #  WRITE(outfid,FMT) (flxtime(1,i,k),i=1,3),  &
    #      (flxtime(2,i,k),i=1,3), outval(1:noutval)
    # END DO
    # CLOSE(outfid)
    # !    statistics
    # DO iflx=1,nflx
    #  WRITE (tmpstr,*)'flux '//flx(iflx)//  &
    #      ' eliminated:',100.*REAL(del(iflx))/REAL(nd),'%'
    #  CALL log_info(tmpstr)
    # END DO

    #
    # get file name from config
    #
    qcfluxpath = conf.get('Outdir')
    qcfluxbase = conf.get('QCOutName')
    qcfluxname = os.path.join(qcfluxpath, qcfluxbase)
    #
    qcfluxfile = io.open(qcfluxname, 'w+b')
    datestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = '# EC-PET version {:s} generated {:s}\n'.format(version, datestr)
    qcfluxfile.write(line.encode())

    line = ('DOY Hr Mn ' +
            'DOY Hr Mn     ' + 'UStar_qc        dUStar_qc       ' +
            'UStar_flag      ' + 'H_qc            dH_qc           ' +
            'H_flag          ' + 'LvE_qc          dLvE_qc         ' +
            'LvE_flag        ' + 'FCO2_qc         dFCO2           ' +
            'FCO2_flag       ' + 'FmolCO2_qc      dFmolCO2        ' +
            'Dir             Mean(vectorU)   ' + 'Thetason        Mean(q)         ' +
            'CO2Mixr         dCO2Mixr        ' + 'rho             LStar           ' +
            'FPTarget        ' + 'pres            ' +
            '\n')
    qcfluxfile.write(line.encode())

    line = ('-   -  -  ' +
            '-   -  -      ' + '[m/s]           [m/s]           ' +
            '[index]         ' + '[W/m^2]         [W/m^2]         ' +
            '[index]         ' + '[W/m^2]         [W/m^2]         ' +
            '[index]         ' + '[kg/m^2]        [kg/m^2]        ' +
            '[index]         ' + '[umol/m^2]      [umol/m^2]      ' +
            '[deg]           [m/s]           ' + '[K]             [kg/kg]         ' +
            '[umol/mol]      [umol/mol]      ' + '[kg/m^3]        [m]             ' +
            '[percent]       ' + '[hPa]           ' +
            '\n')
    qcfluxfile.write(line.encode())
    keys = ['ustar', 'dustar', 'flag_tau',
            'h_0', 'dh_0', 'flag_h_0',
            'e_0', 'de_0', 'flag_e_0',
            'fc2', 'dfc2', 'flag_fc2',
            'cn', 'dcn',
            'dirfrom', 'vectwind', 'theta', 'mean_q',
            'mean_qco2', 'std_qco2', 'rho', 'lstar',
            'qmfkf_out', 's_pp_out']
    fmt = '{:5d} {:02d} {:02d} {:5d} {:02d} {:02d}'
    fmt += ' {:15.5G}'*(len(keys))
    fmt += '\n'
    # flx=['tau','h_0','e_0','fc2']
    for i in intervals.to_dict(orient='records'):
        # convert just for output
        i['s_pp_out'] = i['s_pp']/100.
        i['qmfkf_out'] = i['qmfkf']*100.
        try:
            line = fmt.format(
                *[i['begin'].dayofyear+(i['begin'].year % 100)*1000, i['begin'].hour, i['begin'].minute,
                  i['end'].dayofyear+(i['end'].year % 100)*1000, i['end'].hour, i['end'].minute] +
                [i[k] for k in keys]
            ).replace('nan', 'NaN')
        except ValueError:
            line = 'oups'
        qcfluxfile.write(line.encode())

    qcfluxfile.close()

    return

# ----------------------------------------------------------------------

def itc_u(zeta, ust, f):
    """
    Calculate integral turbulence characteristic for horizontal wind component.

    :param zeta: Stability parameter (z-d)/L
    :type zeta: float
    :param ust: Friction velocity [m/s]
    :type ust: float
    :param f: Coriolis parameter [s^-1]
    :type f: float
    :return: Integral turbulence characteristic for u-component
    :rtype: float

    :note: Combined Thomas (2001) & Foken (1997) formulation.
           Uses different expressions for unstable, neutral, and stable conditions.
    """

    # REAL FUNCTION itc_u(zeta,ust,f)
    # !Combined Thomas (2001) & Foken (1997), as in TK3
    # REAL, INTENT(IN) :: zeta,ust,f
    # REAL :: res
    # REAL :: zplus=1.0
    # IF (zeta < -0.2) THEN
    #  res=4.15*(-zeta)**(1./8.)
    # ELSE IF (zeta < 0.4) THEN
    #  res=0.44*LOG(zplus*f/ust)+6.3
    # ELSE
    #  res=2.7
    # END IF
    # itc_u=res
    # END FUNCTION

    # Combined Thomas (2001) & Foken (1997), as in TK3
    zplus = 1.0
    if zeta < -0.2:
        res = 4.15*(-zeta)**(1./8.)
    elif zeta < 0.4:
        res = 0.44*np.log(zplus*f/ust)+6.3
    else:
        res = 2.7
    return res

    # NOTE: code from publications
    #
    # !      real function itc_u(zeta,ust,f)
    # !c Thomas & Foken (2002)
    # !      real , intent(in) zeta,ust,f
    # !      real res
    # !      real zplus=1.0
    # !      if (zeta.lt.-3.0) then
    # !        res=nan
    # !      elseif (zeta.lt.-0.2) then
    # !        res=4.15*(-zeta)**(1./8.)
    # !      elseif (zeta.lt.0.4) then
    # !        res=0.44*log(zplus*f/ust)+6.3
    # !      else
    # !        res=nan
    # !      endif
    # !      itc_u=res
    # !      end function
    #
    # !      real function itc_u(zeta)
    # !c Foken & Wichura (1996), refered to as Foken (1991) but
    # !c NOT in Foken (1991)
    # !      real , intent(in) zeta
    # !      real res
    # !      if (zeta.lt.-1.) then
    # !        res=2.83*(-zeta)**(1./6.)
    # !      elseif (zeta.lt.-0.0625) then
    # !        res=2.83*(-zeta)**(1./8.)
    # !      elseif  (zeta.lt.0.) then
    # !        res=1.99
    # !      else
    # !        res=nan
    # !      endif
    # !      itc_u=res
    # !      end function
    # !

# ----------------------------------------------------------------------

def itc_w(zeta, ust, f):
    """
    Calculate integral turbulence characteristic for vertical wind component.

    :param zeta: Stability parameter (z-d)/L
    :type zeta: float
    :param ust: Friction velocity [m/s]
    :type ust: float
    :param f: Coriolis parameter [s^-1]
    :type f: float
    :return: Integral turbulence characteristic for w-component
    :rtype: float

    :note: Combined Thomas (2001) & Foken (1997) formulation.
           Accounts for atmospheric stability effects on vertical wind variance.
    """
    # REAL FUNCTION itc_w(zeta,ust,f)
    # !Combined Thomas (2001) & Foken (1997), as in TK3
    # REAL, INTENT(IN) :: zeta,ust,f
    # REAL :: res
    # REAL :: zplus=1.0
    # IF (zeta < -0.2) THEN
    #  res=2.0*(-zeta)**(1./8.)
    # ELSE IF (zeta < 0.4) THEN
    #  res=0.21*LOG(zplus*f/ust)+3.1
    # ELSE
    #  res=1.3
    # END IF
    # itc_w=res
    # END FUNCTION

    # Combined Thomas (2001) & Foken (1997), as in TK3
    zplus = 1.0
    if zeta < -0.2:
        res = 2.0*(-zeta)**(1./8.)
    elif zeta < 0.4:
        res = 0.21*np.log(zplus*f/ust)+3.1
    else:
        res = 1.3
    return res

    # !NOTE: publication code
    # !
    # !      real function itc_w(zeta,ust,f)
    # !c Thomas & Foken (2002)
    # !      real , intent(in) zeta,ust,f
    # !      real res
    # !      real zplus=1.0
    # !      if (zeta.lt.-3.0) then
    # !        res=nan
    # !      elseif (zeta.lt.-0.2) then
    # !        res=1.30*(1.-2.*zeta)**(1./3.)
    # !      elseif (zeta.lt.0.4) then
    # !        res=0.21*log(zplus*f/ust)+3.1
    # !      else
    # !        res=nan
    # !      endif
    # !      itc_w=res
    # !      end function
    #
    # !      real function itc_w(zeta)
    # !c Foken (1991)
    # !c Foken & Wichura (1996), Table 4
    # !      real , intent(in) zeta
    # !      real res
    # !      if (zeta.lt.-1.) then
    # !        res=2.00*(-zeta)**(1./6.)
    # !      elseif (zeta.lt.-0.0625) then
    # !        res=2.00*(-zeta)**(1./8.)
    # !      elseif (zeta.lt.0.) then
    # !        res=1.41
    # !      else
    # !        res=nan
    # !      endif
    # !      itc_w=res
    # !      end function

# ----------------------------------------------------------------------

def itc_t(zeta):
    """
    Calculate integral turbulence characteristic for scalar quantities.

    :param zeta: Stability parameter (z-d)/L
    :type zeta: float
    :return: Integral turbulence characteristic for temperature/scalars
    :rtype: float

    :note: Thomas & Foken (2002) formulation for temperature and scalar
           variance scaling. Applied to both temperature and humidity.
    """
    # REAL FUNCTION itc_t(zeta)
    # !Thomas & Foken (2002)
    # !also as in TK3
    # REAL, INTENT(IN) :: zeta
    # REAL :: res
    # IF (zeta < -1.) THEN
    #  res=1.00*ABS(zeta)**(-1./3.)
    # ELSE IF (zeta < -0.0625) THEN
    #  res=1.00*ABS(zeta)**(-1./4.)
    # ELSE IF (zeta < 0.02) THEN
    #  res=0.50*ABS(zeta)**(-1./2.)
    # ELSE
    #  res=1.40*ABS(zeta)**(-1./4.)
    # END IF
    # itc_t=res
    # END FUNCTION

    # !Thomas & Foken (2002) also as in TK3
    if zeta < -1.:
        res = 1.00*np.abs(zeta)**(-1./3.)
    elif zeta < -0.0625:
        res = 1.00*np.abs(zeta)**(-1./4.)
    elif zeta < 0.02:
        res = 0.50*np.abs(zeta)**(-1./2.)
    else:
        res = 1.40*np.abs(zeta)**(-1./4.)
    return res

    # !      real function itc_t(zeta)
    # !c Foken (1991)
    # !c Foken & Wichura (1996) Table 4
    # !      real , intent(in) zeta
    # !      real res
    # !      if (zeta.lt.-1.) then
    # !        res=1.00*(-zeta)**(-1./3.)
    # !      elseif (zeta.lt.-0.0625) then
    # !        res=1.00*(-zeta)**(-1./4.)
    # !      elseif (zeta.lt.0.) then
    # !        res=0.50*(-zeta)**(-1./2.)
    # !      endif
    # !      itc_t=res
    # !      end function


# ----------------------------------------------------------------------

def postprocessor(conf, intervals):
    """
    Main postprocessing routine for eddy-covariance flux data.

    :param conf: Configuration object with all processing parameters
    :type conf: object
    :param intervals: DataFrame with preprocessed flux measurements
    :type intervals: pandas.DataFrame
    :return: DataFrame with final quality-controlled flux results
    :rtype: pandas.DataFrame

    :note: Orchestrates complete postprocessing workflow:
           - Calculate derived meteorological variables
           - Execute mean-value quality control tests
           - Apply flux quality flagging rules
           - Generate output files
    """

    logger.debug('posprocessor is calling derived variable calculation')
    intervals = derived_variables(intervals)
    logger.debug('posprocessor returned from derived variable calculation')
    ec.progress_percent(10)

    logger.debug('posprocessor is calling mean-value QC test')
    intervals = qc_mean_run(conf, intervals)
    logger.debug('posprocessor returned mean-value QC test')
    ec.progress_percent(90)

    logger.debug('posprocessor is calling flux flag application')
    intervals = apply_flags(conf, intervals)
    logger.debug('posprocessor returned flux flag application')
    ec.progress_percent(100)

#  flags2_to_file(conf,intervals)
#  output_to_file(conf,intervals)

    return intervals
