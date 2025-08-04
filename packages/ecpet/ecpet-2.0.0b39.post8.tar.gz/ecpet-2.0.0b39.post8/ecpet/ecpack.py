# -*- coding: utf-8 -*-
"""
EC-PeT Core Processing Module
=============================

Comprehensive eddy-covariance flux calculation engine implementing the complete
processing chain from raw measurements to final surface exchange fluxes.
Provides instrument calibration, coordinate transformations, atmospheric corrections,
and flux calculations following established micrometeorological principles and
best practices for eddy-covariance methodology.

The module performs:
    - Multi-sensor calibration (sonic anemometers, gas analyzers, thermocouples)
    - Statistical analysis with uncertainty quantification
    - Coordinate system transformations and tilt corrections
    - Atmospheric density and frequency response corrections
    - Surface flux calculations with error propagation
    - Quality assessment and data validation

"""
import datetime
import io
import logging
import os
from multiprocessing import Pool

import numpy as np
import pandas as pd

from . import ecdb
from . import ecutils as ec
from ._version import __release__ as version

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------
#


def averag(df):
    """
    Calculate mean values, covariances, and their tolerances from
    calibrated time series.

    :param df: DataFrame containing calibrated measurement samples
    :type df: pandas.DataFrame
    :return: Tuple of (means, tolerance_means, covariances,
      tolerance_covariances, independent_samples_means,
      independent_samples_covariances)
    :rtype: tuple

    Estimates tolerances as 2 * sigma / sqrt(N_independent) where
    N_independent is estimated from sign changes in fluctuations.
    Only uses samples with valid data.

    Name in ECPACK: EC_M_Averag
    """

    tolcov = pd.DataFrame(np.nan, index=ec.ecvar, columns=ec.ecvar)
    cindep = pd.DataFrame(np.nan, index=ec.ecvar, columns=ec.ecvar)
    if ec.safe_len(df) == 0:
        means = tolmean = mindep = pd.Series({x: np.nan for x in ec.ecvar})
        covs = tolcov = cindep = pd.DataFrame(
            np.nan, index=ec.ecvar, columns=ec.ecvar)
    else:
        # C
        # C Initialise the arrays
        # C
        #      DO i=1,NMax
        #        RawMean(i) = 0.D0
        #        Mean(i) = 0.D0
        #        TolMean(i) = 0.D0
        #        Mok(i) = 0
        #        DO j=1,NMax
        #          Cov(i,j) = 0.D0
        #          TolCov(i,j) = 0.D0
        #          Cok(i,j) = 0
        #        ENDDO
        #      ENDDO

        # select numeric columns
        # numcols = df.select_dtypes(include=[np.number])
        numcols = pd.DataFrame(index=df.index)
        for x in ec.ecvar:
            if x in df.columns:
                numcols[x] = df[x]
            else:
                numcols[x] = np.nan

        # C
        # C Find a rough estimate for the mean
        # C
        #      DO i=1,M
        #        DO j=1,N
        #          IF (.NOT.Flag(j,i)) THEN
        #            Mok(j) = Mok(j) + 1
        #            RawMean(j) = RawMean(j) + x(j,i)
        #          ENDIF
        #        ENDDO
        #      ENDDO
        #
        #      DO j=1,N
        #        IF (Mok(j).GT.0) RawMean(j) = RawMean(j)/DBLE(Mok(j))
        #      ENDDO
        # C
        # C Find final estimates for mean
        # C
        #      DO i=1,M
        #        DO j=1,N
        #          IF (.NOT.Flag(j,i)) THEN
        #            Mean(j) = Mean(j) + (x(j,i) - RawMean(j))
        #          ENDIF
        #        ENDDO
        #      ENDDO
        #
        #      DO j=1,N
        #        IF (Mok(j).GT.0) THEN
        #          Mean(j) = Mean(j)/DBLE(Mok(j))
        #          Mean(j) = Mean(j) + RawMean(j)
        #        ELSE
        #          Mean(j) = DUMMY
        #        ENDIF
        #      ENDDO
        means = numcols.mean(skipna=True)

        # C
        # C Find (co-)variances and from them the tolerances of the mean
        # C
        #      DO j=1,N
        #        NChange(j,j) = 0
        #        NMin(j,j) = 0
        #        NPlus(j,j) = 0
        #        PrevPrime(j) = 0
        #      ENDDO
        #
        #      DO i=1,M
        #        DO j=1,N
        #          IF (.NOT.Flag(j,i)) THEN
        #            xPrime(j) = x(j,i) - Mean(j)
        #            IF (xPrime(j).LT.0.D0) NMin(j,j) = NMin(j,j)+1
        #            IF (xPrime(j).GT.0.D0) NPlus(j,j) = NPlus(j,j)+1
        #            IF (i.GT.1) THEN
        #              IF (PrevPrime(j)*xPrime(j).LE.0.D0)
        #     &                NChange(j,j) = NChange(j,j) + 1
        #            ENDIF
        #            PrevPrime(j) = xPrime(j)
        #          ENDIF
        #        ENDDO
        #
        #
        #        DO j=1,N
        #          DO k=j,N
        #            IF (.NOT.(Flag(j,i).OR.Flag(k,i))) THEN
        #              Cok(j,k) = Cok(j,k) + 1
        #              Cov(j,k) = Cov(j,k) + xPrime(j)*xPrime(k)
        #            ENDIF
        #          ENDDO
        #        ENDDO
        #      ENDDO
        #
        #      DO j=1,N
        #        DO k=j,N
        #          IF (Cok(j,k).GT.0) THEN
        #             Cov(j,k) = Cov(j,k)/DBLE(Cok(j,k))
        #          ELSE
        #             Cov(j,k) = DUMMY
        #          ENDIF
        #        ENDDO
        #      ENDDO
        #
        #      DO j=1,N
        #        DO k=1,N
        #          IF (k.LT.j) Cov(j,k) = Cov(k,j)
        #        ENDDO
        #      ENDDO
        #
        #      DO j=1,N
        #        PSwap = 2.D0*DBLE(NMin(j,j))*DBLE(NPlus(j,j))/
        #     &    DBLE(NMin(j,j) + NPlus(j,j))**2.D0
        #        MIndep(j) = INT(DBLE(NChange(j,j))/PSwap) - 1
        #        MIndep(j) = MAX(MIndep(j),1)
        #        IF (Cok(j,j).GT.0.AND.MIndep(j).NE.0.AND.
        #     &      Cov(j,j).NE.DUMMY.AND.Cov(j,j).GE.0.D0) THEN
        #           TolMean(j) = 2.D0*(Cov(j,j)/DBLE(MIndep(j)))**0.5D0
        #        ELSE
        #           TolMean(j) = DUMMY
        #        ENDIF
        #      ENDDO

        # substract mean from each column (except text cols)
        prime = numcols.copy()
        for c in prime:
            try:
                # prime.loc[:,c] = prime.loc[:,c]  - prime[c].mean()
                # faster:
                prime.loc[:, c] = prime.loc[:, c] - means[c]
            except TypeError:
                pass
        # count sign changes
        nminus = {c: sum(np.sign(prime[c]) < 0) for c in prime.columns}
        nplus = {c: sum(np.sign(prime[c]) > 0) for c in prime.columns}
        nchange = {c: sum(prime[c].ffill()*prime[c].ffill().shift(-1) <= 0)
                   for c in prime.columns}
        ntot = len(prime.index)
        # ist ok:   https://github.com/pandas-dev/pandas/issues/16837
        covs = prime.cov()
        # .cov() is normalized by N-1 -> orginal ECPACK: by N
        covs = covs * (ntot-1) / ntot
        pswap = {}
        mindep = {}
        tolmean = {}
        for c in numcols.columns:
            if (nminus[c]+nplus[c]) != 0:
                pswap[c] = 2.*nminus[c]*nplus[c] / (nminus[c]+nplus[c])**2
            else:
                pswap[c] = np.nan
            if pswap[c] not in [0., np.nan]:
                mindep[c] = np.max([int(nchange[c]/pswap[c]) - 1, 1])
            else:
                mindep[c] = np.nan
            if mindep[c] not in [0., np.nan]:
                tolmean[c] = 2.*np.sqrt(covs.loc[c, c]/mindep[c])
            else:
                tolmean[c] = np.nan
        # C
        # C Find tolerances for (co-)variances
        # C
        #      DO i=1,M
        #        DO j=1,N
        #          IF (.NOT.Flag(j,i)) THEN
        #            xPrime(j) = x(j,i) - Mean(j)
        #          ENDIF
        #        ENDDO
        #        DO j=1,N
        #          DO k=j,N
        #            IF (.NOT.(Flag(j,i).OR.Flag(k,i))) THEN
        #              dTolCov(j,k)=xPrime(j)*xPrime(k)-Cov(j,k)
        #              TolCov(j,k)=TolCov(j,k)+dTolCov(j,k)**2
        #            ENDIF
        #          ENDDO
        #        ENDDO
        #      ENDDO
        #
        #      DO j=1,N
        #        DO k=j,N
        # C
        # C Here we estimate the number of independent contributions to the
        # C covariance by counting the least number of independent contributions
        # C to either of the factors.
        # C
        #             CIndep(j,k) = MIN(MIndep(j),MIndep(k))
        # C
        # C Calculate the standard deviation of the instantaneous contributions
        # C to the covariances.
        # C
        #          IF (Cok(j,k).GT.0.AND.TolCov(j,k).GE.0
        #     &        .AND.CIndep(j,k).GE.0) THEN
        #             TolCov(j,k)=TolCov(j,k)/DBLE(Cok(j,k))
        #             TolCov(j,k) = TolCov(j,k)/DBLE(CIndep(j,k))
        # C
        # C Tolerance is defined as 2*sigma, where sigma is standard deviation
        # C
        #             TolCov(j,k) = 2.D0*TolCov(j,k)**0.5D0
        #          ELSE
        #             CIndep(j,k) = 0
        #             TolCov(j,k) = DUMMY
        #          ENDIF
        #        ENDDO
        #      ENDDO
        for i in numcols.columns:
            for j in numcols.columns:
                # C Calculate the standard deviation of the instantaneous contributions
                # C to the covariances.
                tolcov.loc[i, j] = ec.allnanok(np.nanmean,
                                               (prime[i]*prime[j]-covs.loc[i, j])**2)
                # C Here we estimate the number of independent contributions to the
                # C covariance by counting the least number of independent contributions
                # C to either of the factors.
                cindep.loc[i, j] = ec.allnanok(
                    np.nanmin, [mindep[i], mindep[j]])
                # C Tolerance is defined as 2*sigma, where sigma is standard deviation
                if cindep.loc[i, j] != 0.:
                    tolcov.loc[i, j] = 2. * \
                        np.sqrt(tolcov.loc[i, j]/cindep.loc[i, j])
                else:
                    tolcov.loc[i, j] = np.nan

    return means, tolmean, covs, tolcov, mindep, cindep

# ----------------------------------------------------------------
#


def calibrat(conf, dat, pres, cormean=None, badtc=False, tref=np.nan):
    """
    Apply instrument-specific calibrations to raw measurement data.

    :param conf: Configuration object with calibration parameters
    :type conf: object
    :param dat: DataFrame containing raw measurement data
    :type dat: pandas.DataFrame
    :param pres: Atmospheric pressure [Pa]
    :type pres: float
    :param cormean: Correction terms for calibrated quantities, defaults to None
    :type cormean: dict, optional
    :param badtc: Flag indicating bad thermocouple, defaults to False
    :type badtc: bool, optional
    :param tref: Reference temperature [K], defaults to np.nan
    :type tref: float, optional
    :return: DataFrame with calibrated measurement data
    :rtype: pandas.DataFrame

    Applies sonic anemometer calibration, coordinate rotations,
       Schotanus corrections, and sensor-specific polynomial calibrations.
       Calculates derived quantities like specific humidity and CO2 mixing
       ratios.

    Name in ECPACK: Calibrat
    """
    # create copy so we can modify it without altering the
    # function parameter value (dat)
    # in EC-Pack a second field (error) contains a mask
    # that marks invalid data, here we set values is raw to np.nan,
    # instead
    if cormean is None:
        cormean = {x: 0. for x in ec.var}
    raw = dat.copy()

    # exit if no data
    if ec.safe_len(raw) == 0:
        try:
            raw['qco2'] = raw['co2']
        except KeyError:
            pass
        return raw

    # output defaults to input values (i.e. no calibration needed)
    sample = raw.copy()
    # --------------------------------------------------------------
    #  calibrate the sonic anemometer

    # get type of anemometer
    SonicType = ec.code_ap(conf.get('QQType', group='SonCal', kind='int'))

    # C
    # C If this is a wind tunnel calibrated sonic,
    # C we can apply the KNMI calibrations
    # C
    #         IF (CalSonic(QQType) .EQ. ApSon3Dcal) THEN
    #            WDum = Sample(W)
    #            CALL EC_C_Scal(CalSonic,
    #     &                  UDUM, VDUM, WDum,
    #     &                  ERROR(U), ERROR(V), ERROR(W))
    #            Sample(W) = WDum
    #         ENDIF
    if SonicType == 'ApSon3Dcal':
        res = scal(conf, raw)
        for c in res.columns:
            sample[c] = res[c].copy()
        del res

    #         IF (Have_Uncal(QUDiagnost)) THEN
    #            DIAG_WORD = INT(RawSampl(QUDiagnost)/4096)
    #            IF ((Error(U).OR.Error(V).OR.Error(W)).OR.
    #     &          (DIAG_WORD.NE.0.D0)) THEN
    #               Error(U) = (.TRUE.)
    #               Error(V) = (.TRUE.)
    #               Error(W) = (.TRUE.)
    #               Error(TSonic) = (.TRUE.)
    #            ENDIF
    DIAG_WORD = np.trunc(raw['diag_csat']/4096)

    #
    # evaluate diagnostic variable
    #
    # C This is the construction when we have a diagnostic variable
    for i in raw.index:
        if not np.isnan(DIAG_WORD[i]):
            if DIAG_WORD[i] != 0:
                raw.loc[i, 'ux'] = np.nan
                raw.loc[i, 'uy'] = np.nan
                raw.loc[i, 'uz'] = np.nan
                raw.loc[i, 'ts'] = np.nan
        else:
            # C This is the construction when we do not have a diagnostic variable
            #   IF ((Error(U).OR.Error(V)).OR.Error(W)) THEN
            #     Error(U) = (.TRUE.)
            #     Error(V) = (.TRUE.)
            #     Error(W) = (.TRUE.)
            #   ENDIF
            if (pd.isnull(raw.loc[i, 'ux']) or
                pd.isnull(raw.loc[i, 'uy']) or
                    pd.isnull(raw.loc[i, 'uz'])):
                raw.loc[i, 'ux'] = np.nan
                raw.loc[i, 'uy'] = np.nan
                raw.loc[i, 'uz'] = np.nan
# FIXME muesste nicht auch:     raw.loc[i,'ts']=np.nan

    #  IF (.NOT.((Error(U).OR.Error(V)).OR.Error(W))) THEN
    # statement moved into each of the following block
#      if not ( raw.loc[i,'ux'].isnull() or
#               raw.loc[i,'uy'].isnull() or
#               raw.loc[i,'uz'].isnull() ):
#
    # C
    # C Rotate velocity according to angle of setups north relative real north
    # C Rotation angle as given in calibration file should be taken negative
    # C
    # C Sonic takes flow that blows into the sonic as positive. To get
    # C the wind speed with wind to north as positive substract 180 degrees:
    # C
    # C Generic sonic
    # C
    #           IF (CalSonic(QQType) .EQ. ApGenericSonic) THEN
    if SonicType == 'ApGenericSonic':
        # C CalSonic(QQExt8) contains handedness: > 0: righthanded, < 0 left handed
        # C CalSonic(QQExt9) contains extra rotation (in degrees)
        # C
        #               IF (CalSonic(QQExt8) .GE. 0) THEN
        #                      SonDir=-1
        #               ELSE
        #                      SonDir=1
        #               ENDIF
        SonDir = -1. * np.sign(conf.get('QQExt8', group='SonCal', kind='int'))
        #
        # rotate by QQYaw:
        #               Hook = PI*(-CalSonic(QQYaw)+180)/180.D0
        #               Sample(U) =  COS(Hook)*UDum + SIN(Hook)*(SonDir*VDum)
        #               Sample(V) = -SIN(Hook)*UDum + COS(Hook)*(SonDir*VDum)
        Hook = (-conf.get('QQYaw', group='SonCal', kid='float')+180.)*ec.deg2rad
        sample['ux'] = np.cos(Hook)*raw['ux'] + np.sin(Hook)*SonDir*raw['uy']
        sample['uy'] = -np.sin(Hook)*raw['ux'] + np.cos(Hook)*SonDir*raw['uy']
        del Hook
        #
        #               Hook = CalSonic(QQExt9) * PI/180.D0
        #               UDum  =  Sample(U) ! U [m/s]
        #               VDum  =  Sample(V) ! V [m/s]
        #               Sample(U) =  COS(Hook)*UDum + SIN(Hook)*VDum
        #               Sample(V) = -SIN(Hook)*UDum + COS(Hook)*VDum
        Hook = conf.get('QQExt9', group='SonCal', kind='float') * ec.deg2rad
        UDum = sample['ux']
        VDum = sample['uy']
        sample['ux'] = np.cos(Hook)*UDum + np.sin(Hook)*VDum
        sample['uy'] = -np.sin(Hook)*UDum + np.cos(Hook)*VDum
        del (Hook, UDum, VDum)
    else:
        # C
        # C Apparently V is defined other way around (explains -VDum)
        # C
        #              Hook = PI*(-CalSonic(QQYaw)+180)/180.D0
        #              Sample(U) =  COS(Hook)*UDum + SIN(Hook)*(-VDum)
        #              Sample(V) = -SIN(Hook)*UDum + COS(Hook)*(-VDum)
        Hook = (-conf.get('QQYaw', group='SonCal', kind='float')+180.)*ec.deg2rad
        sample['ux'] = np.cos(Hook)*raw['ux'] + np.sin(Hook)*(-raw['uy'])
        sample['uy'] = -np.sin(Hook)*raw['ux'] + np.cos(Hook)*(-raw['uy'])
        del Hook
        # C
        # C Kaijos have different coordinate system: extra 90 degree rotation
        # C
        #              IF ((CalSonic(QQType) .EQ. ApKaijoTR90) .OR.
        #     &            (CalSonic(QQType) .EQ. ApKaijoTR61)) THEN
        #                  Hook = -90.D0 * PI/180.D0
        #                  UDum  =  Sample(U) ! U [m/s]
        #                  VDum  =  Sample(V) ! V [m/s]
        #                  Sample(U) =  COS(Hook)*UDum + SIN(Hook)*VDum
        #                  Sample(V) = -SIN(Hook)*UDum + COS(Hook)*VDum
        if SonicType in ['ApKaijoTR90', 'ApKaijoTR61']:

            Hook = -90. * ec.deg2rad
            UDum = sample['ux']  # u (m/s)
            VDum = sample['uy']  # v (m/s)
            sample['ux'] = np.cos(Hook)*UDum + np.sin(Hook)*VDum
            sample['uy'] = -np.sin(Hook)*UDum + np.cos(Hook)*VDum
            del (Hook, UDum, VDum)

    # C Take care that we have a sonic temperature (either directly, or
    # C from the sonic speed of sound
    #           IF (Have_Uncal(QUTSonic)) THEN
    #             Sample(TSonic) = RawSampl(QUTSonic) + Kelvin
    #           ELSE IF (Have_Uncal(QUSSpeed)) THEN
    #             Sample(TSonic) = EC_Ph_SS2Ts(RawSampl(QUSSpeed))
    #           ENDIF
    raw['ts'] = raw['ts'] + ec.Kelvin
    # C
    # C Here the Schotanus et al. correction for sensitivity of the sonic for
    # C lateral velocity is applied directly to the raw data. This is only
    # C half of the Schotanus-correction. Humidity-correction comes later.
    # C
    # C Only in the spring of 2004 we found out that CSAT3 does this side-wind
    # C correction online (see CSAT  manual, page 1, section 2, 3rd sentence).
    #           IF (CalSonic(QQType) .EQ. ApGillSolent) THEN
    #           Sample(TSonic) = Sample(TSonic) +
    #     &         ((3./4.)*(Sample(U)**2 + Sample(V)**2) +
    #     &          (1./2.)* Sample(W)**2
    #     &         )/GammaR
    #           ELSE IF (CalSonic(QQType) .EQ. ApGenericSonic) THEN
    #           Sample(TSonic) = Sample(TSonic) +
    #     &         (CalSonic(QQExt5)*Sample(U)**2 + CalSonic(QQExt6)*Sample(V)**2 +
    #     &          CalSonic(QQExt7)*Sample(W)**2
    #     &         )/GammaR
    #           ELSE IF (CalSonic(QQType) .NE. ApCSATsonic) THEN
    #             Sample(TSonic) = Sample(TSonic)
    #     &         + (Sample(U)**2 + Sample(V)**2)/GammaR
    #           ENDIF
    if SonicType == 'ApGillSolent':
        sample['ts'] = (raw['ts'] +
                        ((3./4.)*(sample['ux']**2 + sample['uy']**2) +
                         (1./2.) * sample['uz']**2
                         )/ec.GammaR)
    elif SonicType == 'ApGenericSonic':
        sample['ts'] = (raw['ts'] +
                        (conf.get('QQExt5', group='SonCal', kid='float')*sample['ux']**2 +
                         conf.get('QQExt6', group='SonCal', kid='float')*sample['uy']**2 +
                         conf.get('QQExt7', group='SonCal',
                                  kid='float')*sample['uw']**2
                         )/ec.GammaR)
    elif SonicType != 'ApCSATsonic':
        sample['ts'] = (raw['ts'] +
                        (sample['ux']**2 + sample['uy']**2)/ec.GammaR)
    else:
        sample['ts'] = raw['ts']

    sample['ts'] = sample['ts'] + cormean['ts']
    #
    # EC-Pack makes all values invalid, if any wind is invalid
    for i in sample.index:
        if (np.isnan(raw.loc[i, 'ux']) or
            np.isnan(raw.loc[i, 'uy']) or
                np.isnan(raw.loc[i, 'uz'])):
            sample.loc[i, 'ux'] = np.nan
            sample.loc[i, 'uy'] = np.nan
            sample.loc[i, 'uz'] = np.nan
            sample.loc[i, 'ts'] = np.nan

    # --------------------------------------------------------------
    #  Calibrate thermocouple

    function_type = conf.get('QQFunc', group='CoupCal')
    if function_type == 1 and not tref.isnull():
        logger.insane('Tcoup function type 1 (NormPoly)')
        # C
        # C This is calibration according to Campbells P14 instruction
        # C      T =  Calibration(voltage +
        # C                       inverse calibration(reference temperature))
        # C Reference temperature is supposed to be in Celcius !!
        # C
        #            DO i=0,NINT(CalTherm(QQOrder))
        #              c(i) = CalTherm(QQC0+i)
        #            ENDDO
        #            Dum = RawSampl(QUTref)
        #            Error(TCouple) =
        #     &           ((DUM .GT.(MaxT))
        #     &             .OR. (DUM .LT.(MinT)))
        #            IF (.NOT. Error(TCouple)) THEN
        #               UPLIMIT = (DUM + 3.0D0 - CalTherm(QQC0))/CalTherm(QQC1)
        #               DNLIMIT = (DUM - 3.0D0 - CalTherm(QQC0))/CalTherm(QQC1)
        #               ESTIM = (Dum - CalTherm(QQC0))/CalTherm(QQC1)
        #               RELERROR = 1D-4
        #               ABSERROR = 0.001D0/CalTherm(QQC1)
        #               DUMORDER = NINT(CalTherm(QQOrder))
        #               DUMTYP = NINT(CalTherm(QQFunc))
        #               CALL DFZERO(DUMFUNC, DNLIMIT, UPLIMIT, ESTIM, RELERROR,
        #     &                    ABSERROR, IFLG)
        #               IF (IFLG .GT. 3) THEN
        # 	                ERROR(TCouple) = .TRUE.
        # 	            ENDIF

        #               Sample(Tcouple) = Kelvin +
        #     &             EC_M_BaseF(DNLIMIT + RawSampl(QUTcouple),
        #     &              NINT(CalTherm(QQFunc)),
        #     &              NINT(CalTherm(QQOrder)),c)
        Order = conf.get('QQOrder', group='CoupCal')
        QQC = [conf.get('QQC{:1d}'.format(x), group='CoupCal')
               for x in range(6)]
        for i in sample.index:
            # copy coefs
            polyeq = QQC
            # setup polynomial equation tref = qqc_i*x^i as 0 = Poly()
            polyeq[0] = polyeq[0] - tref
            # calculate linear approximation
            estim = polyeq[0]/polyeq[1]
            # solve eqn
            roots = np.roots(polyeq[0:Order])
            # discard complex solutions
            realr = roots[~np.iscomplex(roots)]
            # if the are real solutions choose most probable one
            if len(realr) > 0:
                invref = ec.find_nearest(realr, estim)
                sample.loc[i, 'Tcouple'] = np.polyval(
                    QQC, raw.loc[i, 'Tcouple'] + invref) + ec.Kelvin
            else:
                sample.loc[i, 'Tcouple'] = np.nan

    elif function_type == 2 and not tref.isnull():
        logger.critical('Tcoup function type 2 (LogPoly) not implemented')
        raise ValueError

    else:
        logger.insane(
            'Tcoup function type 0 (None) or no reference temperature')
        # C
        # C Suppose that sample is already temperature (now in Kelvin, Sept. 18, 2002!)
        # C
        #             Sample(TCouple) = RawSampl(QUTCouple) + Kelvin
        sample['tcoup'] = raw['tcoup'] + ec.Kelvin

    sample['tcoup'] = sample['tcoup'] + cormean['tcoup']

    # --------------------------------------------------------------
    #  Calibrate hygrometer

    # C
    # C Add an optional correction to the krypton's humidity to compensate for
    # C drift in the hygrometer (e.g. dirt). Compensation may be provided by
    # C the difference between the mean humidity by a (slow) psychrometer's
    # C output and the mean of the humidity estimated by the hygrometer.
    # C
    # C Note that cormean is set ec_gene and is only non-zero if DoCrmean flag has been
    # C set (which only happens on the second call to calibrat, and is only implemented
    # C for hygrometers (and CO2), not necessarily only Kryptons (during BLLAST (2011) we found
    # C out that LiCor 7500 can also have short term drift problems.
    # C
    #      IF (HAVE_UNCAL(QUHumidity)) THEN
    #         Dum = RawSampl(QUHumidity)
    #         IF (Dum .GE. Epsilon) THEN
    # FIXME why this epsilon thing?
    #            DO i=0,NINT(CalHyg(QQOrder))
    #              c(i) = CalHyg(QQC0+i)
    #            ENDDO
    function_type = conf.get('QQFunc', group='HygCal')
    if function_type == 1:
        logger.insane('h2o function type 1 (NormPoly)')
        Order = conf.get('QQOrder', group='HygCal')
        QQC = [conf.get('QQC{:1d}'.format(x), group='HygCal')
               for x in range(Order)]
        #            Sample(Humidity) = cormean(Humidity) +
        #     &         EC_M_BaseF(Dum,NINT(CalHyg(QQFunc)),
        #     &           NINT(CalHyg(QQOrder)),c)
        sample['h2o'] = cormean['h2o'] + np.polyval(QQC, raw['h2o'])
    elif function_type == 2:
        logger.critical('h2o function type 2 (LogPoly) not implemented')
        raise ValueError

    else:
        logger.insane(
            'h2o function type 0 (None) or no reference temperature')
        sample['h2o'] = raw['h2o']
    # C
    # C Calculate specific humidity associated with this absolute humidity
    # C
    #            IF (.NOT.Error(Humidity)) THEN
    #              IF (.NOT.BadTc) THEN
    #                IF (.NOT.Error(TCouple)) THEN
    #                  Sample(SpecHum)=EC_PH_Q(Sample(Humidity),
    #     &                                Sample(TCouple),P)
    #                ELSE IF (.NOT.Error(TSonic)) THEN
    #                  TsCorr = EC_C_Schot3(Sample(TSonic),
    #     &                                Sample(Humidity), P)
    #                  Sample(SpecHum)=EC_PH_Q(Sample(Humidity),
    #     &                                TsCorr,P)
    #                ELSE
    #                  Error(SpecHum) = (.TRUE.)
    #                ENDIF
    #              ELSE
    #                IF (.NOT.Error(TSonic)) THEN
    #                  TsCorr = EC_C_Schot3(Sample(TSonic),
    #     &                                Sample(Humidity), P)
    #                  Sample(SpecHum)=EC_PH_Q(Sample(Humidity),
    #     &                                TsCorr,P)
    #                ELSE
    #                  Error(SpecHum) = (.TRUE.)
    #                ENDIF
    #              ENDIF
    if not badtc and not np.all(np.isnan(sample['tcoup'])):
        sample['q'] = sample.apply(
            lambda x, p=pres: ec.spechum(x['h2o'], x['tcoup'], p), axis=1)
    else:
        sample['TsCorr'] = sample.apply(
            lambda x: schotanus3(x['ts'], x['h2o'], pres), axis=1)
        sample['q'] = sample.apply(lambda x, p=pres: ec.spechum(
            x['h2o'], x['TsCorr'], p), axis=1)
        sample = sample.drop(['TsCorr'], axis=1)

    # --------------------------------------------------------------
    #  Calibrate  CO2 sample
    # C
    #      IF (HAVE_UNCAL(QUCO2)) THEN
    #         DO i=0,INT(CalCO2(QQOrder))
    #              c(i) = CalCO2(QQC0+i)
    #         ENDDO
    #      Sample(CO2) = CorMean(CO2) +
    #     &         EC_M_BaseF(RawSampl(QUCO2),NINT(CalCO2(QQFunc)),
    #     &           NINT(CalCO2(QQOrder)),c)
    #         Error(CO2) = ((Sample(CO2).GT.MaxRhoCO2)
    #     &          .OR. (Sample(CO2).LT.MinRhoCO2))
    function_type = conf.get('QQFunc', group='Co2Cal')
    if function_type == 1:
        logger.insane('co2 function type 1 (NormPoly)')
        Order = conf.get('QQOrder', group='Co2Cal')
        QQC = [conf.get('QQC{:1d}'.format(x), group='Co2Cal')
               for x in range(Order)]
        #            Sample(Humidity) = CorMean(Humidity) +
        #     &         EC_M_BaseF(Dum,NINT(CalHyg(QQFunc)),
        #     &           NINT(CalHyg(QQOrder)),c)
        sample['co2'] = cormean['co2'] + np.polyval(QQC, raw['co2'])
    elif function_type == 2:
        logger.critical('co2 function type 2 (LogPoly) not implemented')
        raise ValueError

    else:
        logger.insane(
            'co2 function type 0 (None) or no reference temperature')
        sample['co2'] = raw['co2']
    # C
    # C Calculate specific CO2 associated with this absolute CO2 concentration
    # C
    #         IF (.NOT.Error(CO2)) THEN
    #              IF (.NOT.BadTc) THEN
    #                IF (.NOT.Error(TCouple) .AND.
    #     &              .NOT.Error(Humidity)) THEN
    #                  Sample(SpecCO2)=EC_PH_QCO2(
    #     &                                Sample(CO2),
    #     &                                Sample(Humidity),
    #     &                                Sample(TCouple),P)
    #                ELSE IF (.NOT.Error(TSonic) .AND.
    #     &                   .NOT.Error(Humidity)) THEN
    #                  TsCorr = EC_C_Schot3(Sample(TSonic),
    #     &                                Sample(Humidity), P)
    #                  Sample(SpecCO2)=EC_PH_QCO2(
    #     &                                Sample(CO2),
    #     &                                Sample(Humidity),
    #     &                                TsCorr,P)
    #                  Error(SpecCO2) = .FALSE.
    #                ELSE
    #                  Error(SpecCO2) = (.TRUE.)
    #                ENDIF
    #              ELSE
    #                IF (.NOT.Error(TSonic) .AND.
    #     &              .NOT.Error(Humidity)) THEN
    #                  TsCorr = EC_C_Schot3(Sample(TSonic),
    #     &                                Sample(Humidity), P)
    #                  Sample(SpecCO2)=EC_PH_QCO2(
    #     &                                Sample(CO2),
    #     &                                Sample(Humidity),
    #     &                                TsCorr,P)
    #                  Error(SpecCO2) = .FALSE.
    #                ELSE
    #                  Error(SpecCO2) = (.TRUE.)
    #                ENDIF
    #              ENDIF
    #         ENDIF
    if not badtc and not np.all(np.isnan(sample['tcoup'])):
        #    sample['qco2']=ec.specco2(sample['co2'],sample['h2o'],sample['tcoup'],pres)
        sample['qco2'] = sample.apply(lambda x: ec.specco2(
            x['co2'], x['h2o'], x['tcoup'], pres), axis=1)
    else:
        sample['TsCorr'] = sample.apply(
            lambda x: schotanus3(x['ts'], x['h2o'], pres), axis=1)
        sample['qco2'] = sample.apply(lambda x: ec.specco2(
            x['co2'], x['h2o'], x['TsCorr'], pres), axis=1)
        sample = sample.drop(['TsCorr'], axis=1)

    return sample


# ----------------------------------------------------------------
#
def convert(conf, dat):
    """
    Apply gain and offset corrections for unit conversion.

    :param conf: Configuration object with gain/offset parameters
    :type conf: object
    :param dat: DataFrame containing measurement data
    :type dat: pandas.DataFrame
    :return: DataFrame with converted data including time delays
    :rtype: pandas.DataFrame

    Applies mapping x → (x/Gain) + Offset and
    time delays specified
    in configuration. Delays converted from milliseconds to sample counts.

    """
    if ec.safe_len(dat) == 0:
        return dat

    Delay = {x: 0. for x in ec.metvar}
    Gain = {x: 1. for x in ec.metvar}
    Offset = {x: 0. for x in ec.metvar}

    #      Delay(QUU)        = NINT(CalSonic(QQDelay)*
    #     &                         0.001D0*ExpVar(QEFreq))
    #      Delay(QUV)        = NINT(CalSonic(QQDelay)*
    #     &                         0.001D0*ExpVar(QEFreq))
    #      Delay(QUW)        = NINT(CalSonic(QQDelay)*
    #     &                         0.001D0*ExpVar(QEFreq))
    #      Delay(QUHumidity) = NINT(CalHyg(QQDelay)*
    #     &                         0.001D0*ExpVar(QEFreq))
    #      Delay(QUTcouple)  = NINT(CalTherm(QQDelay)*
    #     &                         0.001D0*ExpVar(QEFreq))
    #      Delay(QUTsonic)   = NINT(CalSonic(QQDelay)*
    #     &                         0.001D0*ExpVar(QEFreq))
    #      Delay(QUCO2)      = NINT(CalCO2(QQDelay)*
    #     &                         0.001D0*ExpVar(QEFreq))
    Delay['ux'] = conf.get('QQDelay', group='SonCal', kind='float')
    Delay['uy'] = conf.get('QQDelay', group='SonCal', kind='float')
    Delay['uz'] = conf.get('QQDelay', group='SonCal', kind='float')
    Delay['ts'] = conf.get('QQDelay', group='SonCal', kind='float')
    Delay['h2o'] = conf.get('QQDelay', group='HygCal', kind='float')
    Delay['co2'] = conf.get('QQDelay', group='Co2Cal', kind='float')
    Delay['tcoup'] = conf.get('QQDelay', group='CoupCal', kind='float')
    # convert delay from milliseconds to number-of-records
    QEFreq = conf.get('Freq', group='Par', kind='float')
    Delay = {k: round(v*float(QEFreq)*0.001) for k, v in Delay.items()}

    #      Gain(QUU)        = CalSonic(QQGain)
    #      Gain(QUV)        = CalSonic(QQGain)
    #      Gain(QUW)        = CalSonic(QQGain)
    #      Gain(QUHumidity) = CalHyg(QQGain)
    #      Gain(QUTcouple)  = CalTherm(QQGain)
    #      Gain(QUTsonic)   = CalSonic(QQGain)
    #      Gain(QUCO2)      = CalCO2(QQGain)
    #
    #      Offset(QUU)        = CalSonic(QQOffset)
    #      Offset(QUV)        = CalSonic(QQOffset)
    #      Offset(QUW)        = CalSonic(QQOffset)
    #      Offset(QUHumidity) = CalHyg(QQOffset)
    #      Offset(QUTcouple)  = CalTherm(QQOffset)
    #      Offset(QUTsonic)   = CalSonic(QQOffset)
    #      Offset(QUCO2)      = CalCO2(QQOffset)
    Gain['ux'] = conf.get('QQGain', group='SonCal', kind='float')
    Gain['uy'] = conf.get('QQGain', group='SonCal', kind='float')
    Gain['uz'] = conf.get('QQGain', group='SonCal', kind='float')
    Gain['ts'] = conf.get('QQGain', group='SonCal', kind='float')
    Gain['h2o'] = conf.get('QQGain', group='HygCal', kind='float')
    Gain['co2'] = conf.get('QQGain', group='Co2Cal', kind='float')
    Gain['tcoup'] = conf.get('QQGain', group='CoupCal', kind='float')

    Offset['ux'] = conf.get('QQOffset', group='SonCal', kind='float')
    Offset['uy'] = conf.get('QQOffset', group='SonCal', kind='float')
    Offset['uz'] = conf.get('QQOffset', group='SonCal', kind='float')
    Offset['ts'] = conf.get('QQOffset', group='SonCal', kind='float')
    Offset['h2o'] = conf.get('QQOffset', group='HygCal', kind='float')
    Offset['co2'] = conf.get('QQOffset', group='Co2Cal', kind='float')
    Offset['tcoup'] = conf.get('QQOffset', group='CoupCal', kind='float')

    for c in ec.metvar:
        dat[c] = dat.apply(lambda x: x[c]/Gain[c] +
                           Offset[c], axis=1).shift(Delay[c])

    return dat

# -----------------------------------------------------------------------
#


def detrend(x):
    """
    Construct linearly detrended dataset while preserving mean values.

    :param x: DataFrame or Series with measurement samples
    :type x: pandas.DataFrame or pandas.Series
    :return: Detrended data with original mean added back
    :rtype: pandas.DataFrame or pandas.Series

    Uses linear regression to remove trends while handling NaN values.
           Preserves data structure (DataFrame vs Series) of input.
    """
    logger.insane('detrending')
    if isinstance(x, pd.DataFrame):
        # normal input
        pass
    elif isinstance(x, pd.Series):
        # convert Series in one-column DataFrame
        x = pd.DataFrame(x)
    else:
        logger.error('argument must be pandas DataFrame or Series')
        raise TypeError
    #  use linear regression of non-nan values to eliminate trend
    # data=signal.detrend(dat[v],type='linear')
    #  does not cope with nan values.
    #  workaroud: use linear regresion ans sbstract ist
    #  https://stackoverflow.com/a/44782130
    o = x.copy()
    for c in x.columns:
        if x[c].dtype == np.number:
            ok = np.array(np.isfinite(x[c]))
            nr = np.array(range(len(x.index)))
            # m, b, r_val, p_val, std_err = stats.linregress(nr[ok],x[[c]][ok])
            y = x[c][ok]
            A = np.array([nr[ok], np.ones(len(y))])
            try:
                (m, b) = np.linalg.lstsq(A.T, y)[0]
            except np.linalg.LinAlgError:
                o[c] = x[c]
            else:
                o[c] = (x[c] - (m*nr + b)) + x[c].mean(skipna=True)

    # if there's only one column, return a Series
    if len(o.columns) == 1:
        o = o[o.columns[0]]

    return o

# -----------------------------------------------------------------------
#


def crosscorr(datax, datay, lag=0):
    """
    Calculate lag-N cross correlation between two time series.

    :param datax: First time series
    :type datax: pandas.Series
    :param datay: Second time series
    :type datay: pandas.Series
    :param lag: Time lag in samples, defaults to 0
    :type lag: int, optional
    :return: Cross correlation coefficient
    :rtype: float

    Based on pandas correlation with lag shifting.
           Used for sensor synchronization analysis.
    """
    return datax.corr(datay.shift(lag))

# -----------------------------------------------------------------------
#


def errfisi(val):
    """
    Calculate covariance error matrix using Finkelstein-Sims method.

    :param val: DataFrame with calibrated measurement samples
    :type val: pandas.DataFrame
    :return: Covariance error matrix
    :rtype: pandas.DataFrame

    Uses FFT-based high-pass filtering and correlation analysis.
           Provides alternative error estimation to traditional methods.
           Returns NaN matrix if insufficient data (< 8 samples).
    """
    if ec.safe_len(val) < 8:
        sigma = pd.DataFrame(np.nan, index=ec.ecvar, columns=ec.ecvar)
        logger.debug('skipped, too few data')
    else:
        #
        # select only numeric values
        # spl = val.select_dtypes(include=[np.number])
        spl = val[ec.intersect_lists(ec.ecvar, val.columns)]
        #
        # C     linear interpolate data gaps
        spl = spl.interpolate(method='linear', axis=0, limit_direction='both')
        logger.debug('... filled gaps')
        #
        # C     Calculate Fourier Transforms of all quantities
        #      to remove trend
        flen = (len(spl.index))//2 + 1
        f = pd.DataFrame(np.nan, columns=spl.columns, index=range(flen))
        for c in spl.columns:
            f[c] = np.fft.rfft(spl[c])
        #
        # C     High-pass Filter (set first three frequence zero)
        f.loc[0:3, :] = 0.
        #
        #     inverse FFT to reconstruct detrended time series
        rlen = len(spl.index)-len(spl.index) % 2
        rf = pd.DataFrame(np.nan, columns=spl.columns,
                          index=spl.index[range(rlen)])
        for c in spl.columns:
            rf[c] = np.fft.irfft(f[c])
        logger.debug('... removed means')

        # covariance error:
        # create empty array
        sigma = pd.DataFrame(np.nan, columns=ec.ecvar, index=ec.ecvar)
        # short hands for length
        n = len(rf.index)
        # nicht noetig mit np.correlate(...'same'):
        # m = n//2
        # we need just the autocovariances except for these:
        only = ['ux', 'uy', 'uz', 'ts', 'tcoup', 'h2o', 'co2']
        # keep the impatient user informed (count sigmas to calculate):
        nsig = len(only)*len(only)+len(spl.columns)-len(only)
        isig = 0
        ccf = dict()
        for x in spl.columns:
            # ccf[x]=(np.correlate(rf[x],rf[x],'full')/float(n))[n-m-1:n+m-1]
            # ist das gleiche wie
            ccf[x] = (np.correlate(rf[x], rf[x], 'same')/float(n))
        for x in spl.columns:
            for y in spl.columns:
                if (x in only and y in only) or x == y:
                    if np.isfinite(sigma.loc[y, x]):
                        sigma.loc[x, y] = sigma.loc[y, x]
                    else:
                        # inspired by statsmodel's ccovf
                        # (http://www.statsmodels.org/devel/_modules/statsmodels/tsa/stattools.html#ccovf)      sum=0.
                        # this was the fastest for long time series:
                        # ccxx=(np.correlate(rf[x],rf[x],'full')/(n))[n-m-1:n+m-1]
                        # ccyy=(np.correlate(rf[y],rf[y],'full')/(n))[n-m-1:n+m-1]
                        #
                        ccxx = ccf[x]
                        ccyy = ccf[y]
                        if x == y:
                            ccxy = ccf[x]
                        else:
                            # ccxy=(np.correlate(rf[x],rf[y],'full')/float(n))[n-m-1:n+m-1]
                            # ist das gleiche wie:
                            ccxy = (np.correlate(
                                rf[x], rf[y], 'same')/float(n))
                        # ccyx=(np.correlate(rf[y],rf[x],'full')/float(n))[n-m-1:n+m-1]
                        # ist das gleiche wie:
                        # ccyx=(np.correlate(rf[y],rf[x],'same')/float(n))
                        # faster:
                        ccyx = ccxy[::-1]
                        #
                        sigma.loc[x, y] = np.sqrt(
                            (sum(ccxx*ccyy)+sum(ccxy*ccyx)) / float(n))

                    # keep the impatient user informed:
                    isig += 1
                    logger.debug('... sigma {:d}/{:d}'.format(isig, nsig))

        logger.debug('... done')

    return sigma

# -----------------------------------------------------------------------
#


def freqcorr(conf, Means, Covs, TolCov, WhichTemp):
    """
    Calculate frequency response corrections for sensor and path effects.

    :param conf: Configuration object with sensor parameters
    :type conf: object
    :param Means: Mean values of measured quantities
    :type Means: pandas.Series
    :param Covs: Covariance matrix of fluctuations
    :type Covs: pandas.DataFrame
    :param TolCov: Tolerance matrix for covariances
    :type TolCov: pandas.DataFrame
    :param WhichTemp: Temperature variable to use (`ts` or `tcoup`)
    :type WhichTemp: str
    :return: Tuple of (corrected_covariances, corrected_tolerances)
    :rtype: tuple

    Corrects for sensor response, path averaging, separation effects,
    and signal processing. Based on :cite:`moo_bm86` and others.
    Only corrects variances and covariances involving vertical velocity.

    See also
      - :cite:`phi_ajop63`
      - :cite:`lek_bm92`

    """
    WXT = None
    #
    # C
    # C-- Declarations of constants ----------------------------------------
    # C

    #        NSTA   = -5.0D0    ! [?] start frequency numerical integration
    #        NEND   = LOG10(0.5*ExpVar(QEFreq)) ! [?] end frequency numerical integration
    #        NumINT = 39        ! [1] number of intervals
    #        TAUV   = 0.0D0     ! [?] Low pass filter time constant
    #        TauD   = 0.0D0     ! [?] interval length for running mean

    #      TAUT = CalTherm(QQTime)/
    #     &  (1.D0+4.9D0*(CalTherm(QQTime)**0.5D0*Mean(U))**0.45D0)
    #      LF   = (NEND-NSTA)/DBLE(NumINT-1)    ! Interval width num. integr.
    #      C    = 1.D0/(LOG(10.D0)*LF/3.D0)     ! Constant of integration, eq.1
    #      LF   = 10.D0**LF
    #      N    = 10.D0**NSTA
    #      DO I=1,NNMAX
    #         DO J=1,NNMAX
    #            INTTS(I,J)=0.D0
    #         ENDDO
    #      ENDDO

    QEFreq = conf.get('FREQ', group='Par', kind='float')
    TcTime = conf.get('QQTime', group='CoupCal', kind='float')

    NSTA = -5.0      # start frequency numerical integration
    NEND = np.log10(0.5*QEFreq)  # end frequency numerical integration
    NumInt = 39        # number of intervals
    TAUV = 0.0       # Low pass filter time constant
    TauD = 0.0       # interval length for running mean

    TAUT = TcTime/(1.+4.9*(TcTime**0.5 * Means['ux'])**0.45)
    LF = (NEND-NSTA)/(NumInt-1)    # Interval width num. integr.
    C = 1./(np.log(10.)*LF/3.)    # Constant of integration, eq.1
    LF = 10.**LF
    N = 10.**NSTA

    INTTS = pd.DataFrame(0., columns=Covs.columns, index=Covs.columns)

    # C Make scales for obukhov length calculation
    #      Ustar = (Cov(U,W)**2.D0 + Cov(V,W)**2.D0)**0.25D0
    #      Tstar = -Cov(W, WhichTemp)/Ustar
    Ustar = (Covs.loc['ux', 'uz']**2 + Covs.loc['uy', 'uz']**2)**0.25
    Tstar = -Covs.loc['uz', WhichTemp]/Ustar

    # C Take care of situation when we don't have a hygrometer
    #      IF (INT(CalHyg(QQType)) .NE. INT(DUMMY)) THEN
    #         Qstar = -Cov(W, SpecHum)/Ustar
    #      ELSE
    #         Qstar = 0
    #      ENDIF
    #      ZL = CalSonic(QQZ)/EC_Ph_Obukhov(Ustar, Tstar, Qstar,
    #     &                                 Mean(WhichTemp))

    HygType = conf.get('QQType', group='HygCal', kind='int')
    if HygType is not None:
        Qstar = -Covs.loc['uz', 'q']/Ustar
    else:
        Qstar = 0
    HygZ = conf.get('QQZ', group='HygCal', kind='float')
    ZL = HygZ/obukhov(Ustar, Tstar, Qstar, Means[WhichTemp])

    # C Initialize ATT etc
    #      ATT=0.0961D0
    #      AWW=0.838D0
    #      AUU=0.2D0*AWW
    #      AWT=0.284D0
    #      AUW=0.124D0
    #      BTT=3.124D0/ATT**0.667D0
    #      BWW=3.124D0/AWW**0.667D0
    #      BUU=3.124D0/AUU**0.667D0
    #      BWT=2.34D0/AWT**1.1D0
    #      BUW=2.34D0/AUW**1.1D0
    #      XI   = 0.0D0
    #      ZETA = (0.001D0*CalSonic(QQZ))**1.667D0
    #      CW   = 0.7285D0+1.4115D0*XI
    #      CU   = 9.546D0+1.235D0*XI/(ZETA**0.4D0)

    ATT = 0.0961
    AWW = 0.838
    AUU = 0.2*AWW
    AWT = 0.284
    AUW = 0.124
    BTT = 3.124/ATT**0.667
    BWW = 3.124/AWW**0.667
    BUU = 3.124/AUU**0.667
    BWT = 2.34/AWT**1.1
    BUW = 2.34/AUW**1.1
    XI = 0.0
    SonicZ = conf.get('QQZ', group='SonCal', kind='float')
    ZETA = (0.001*SonicZ)**1.667
    CW = 0.7285+1.4115*XI
    CU = 9.546+1.235*XI/(ZETA**0.4)

    #
    #      IF(ZL.GE.0.D0) THEN
    # C
    # C-- Stable spectral and co-spectral function factors, eq. 20b, 21b
    # C
    #        ATT=0.0961D0+0.644D0*ZL**0.6D0
    #        AWW=0.838D0+1.172D0*ZL
    #        AUU=0.2D0*AWW
    #        AWT=0.284D0*(1.D0+6.4D0*ZL)**0.75D0
    #        AUW=0.124D0*(1.D0+7.9D0*ZL)**0.75D0
    #        BTT=3.124D0/ATT**0.667D0
    #        BWW=3.124D0/AWW**0.667D0
    #        BUU=3.124D0/AUU**0.667D0
    #        BWT=2.34D0/AWT**1.1D0
    #        BUW=2.34D0/AUW**1.1D0
    #      ELSE

    if ZL >= 0.:
        # C
        # C-- Stable spectral and co-spectral function factors, eq. 20b, 21b
        # C
        ATT = 0.0961 + 0.644 * ZL**0.6
        AWW = 0.838 + 1.172 * ZL
        AUU = 0.2 * AWW
        AWT = 0.284 * (1. + 6.4 * ZL)**0.75
        AUW = 0.124 * (1. + 7.9 * ZL)**0.75
        BTT = 3.124 / ATT**0.667
        BWW = 3.124 / AWW**0.667
        BUU = 3.124 / AUU**0.667
        BWT = 2.34 / AWT**1.1
        BUW = 2.34 / AUW**1.1
    else:
        # C
        # C-- Unstable spectral and co-spectral function factors, eq. 23 -----
        # C
        #        XI   = (-ZL)**0.667D0
        #        ZETA = (0.001D0*CalSonic(QQZ))**1.667D0
        #        CW   = 0.7285D0+1.4115D0*XI
        #        CU   = 9.546D0+1.235D0*XI/(ZETA**0.4D0)
        #      END IF
        XI = (-ZL)**0.667
        ZETA = (0.001 * SonicZ)**1.667
        CW = 0.7285 + 1.4115 * XI
        CU = 9.546 + 1.235 * XI/(ZETA**0.4)

    # C
    # C-- Start Simpson's rule numerical integration -----------------------
    # C     From -5 to log(5) in NumInt steps
    # C
    #      I3=0
    #      DO I1=1,INT(0.5*(NumInt+1))
    #        DO I2=2,4,2
    #          I3=I3+1
    #          IF (I3.GT.NumInt) GOTO 200
    #          I4=I2
    #          IF (I3.EQ.1)  I4=I4-1
    #          IF (I3.EQ.NumInt) I4=I4-1

    ii = []
    for I1 in range(1, int(0.5*(NumInt+1))+1):
        for I2 in [2, 4]:
            ii.append((I1, I2))

    for I3 in range(ec.allnanok(np.nanmin, [len(ii), NumInt])):
        I1, I2 = ii[I3]
        if I3 in [1, NumInt]:
            I4 = I2-1
        else:
            I4 = I2

        # C
        # C-- Skip integration if frequency exceeds Nyquist frequency ------
        # C
        #          IF (N.GT.(0.5D0*NS)) GOTO 999

        if N > (0.5 * QEFreq):
            #
            # break statement cuses the else clause of the for-I3 loop
            # to be NOT executed
            #
            break

        # C
        # C-- ELECTRONIC / DIGITAL FILTERS !!
        # C-- Auto Regressive Moving Average filter response gain, eq. 19 --
        # C   Does nothing if TauD is set to zero (as above)
        # C
        #          GAIND=1.0D0
        #          X=2.0D0*PI*N*TAUD
        #          IF (X.LT.6.D0 .AND. X.GT.0.0D0) GAIND=X*X/(1.0D0+X*X)

        GAIND = 1.0
        X = 2.0*ec.pi*N*TauD
        if 6. > X > 0.:
            GAIND = X*X / (1.+X*X)

        # C
        # C-- Butterworth filter frequency response gain, eq. 5 ------------
        # C   Does nothing if TauV is set to zero (as above)
        # C
        #          GAINV = 1.0D0
        #          GAINV=(2.0D0*PI*N*TAUV)**2.0D0
        #          GAINV=1.0D0+GAINV*GAINV

        GAINV = (2.0*ec.pi*N*TAUV)**2
        GAINV = 1.0 + GAINV*GAINV

        # C
        # C-- Data aquisition co-spectral transfer function, eq. 15 (b=3) --
        # C   The documentation claims that this is not needed if one is
        # C   interested in spectrally integrated quantities
        # C         TRANA=1.0D0+(N/(NS-N))**3.0D0
        #          TRANA=1.0D0

        TRANA = 1.0

        # C
        # C-- LUW THERMOCOUPLE TEMPERATURE !!
        # C-- Thermocouple frequency response gain, eq. 2 ------------------
        # C
        #          GAINT1=1.0D0+(2.0D0*PI*N*TAUT)**2.0D0

        GAINT1 = 1.0 + (2.*ec.pi*N*TAUT)**2

        # C
        # C-- Thermocouple spatial averaging transfer function, eq. 7 ------
        # C
        #          TRANT1=1.0D0       !spatial averaging negligible

        # spatial averaging negligible
        TRANT1 = 1.

        # C
        # C-- W-T lateral separation transfer function, eq. 11 -------------
        # C
        #          TRANWT1=1.0D0
        #          SEP = SQRT((CalTherm(QQX)-CalSonic(QQX))**2 +
        #     &               (CalTherm(QQY)-CalSonic(QQY))**2 +
        #     &               (CalTherm(QQZ)-CalSonic(QQZ))**2)
        #          X=N/Mean(U)*SEP
        #          IF (X.GT.0.01D0) TRANWT1=EXP(-9.9D0*X**1.5D0)

        TRANWT1 = 1.
        ThermX = conf.get('QQX', group='CoupCal', kind='float')
        ThermY = conf.get('QQY', group='CoupCal', kind='float')
        ThermZ = conf.get('QQZ', group='CoupCal', kind='float')
        SonicX = conf.get('QQX', group='SonCal', kind='float')
        SonicY = conf.get('QQY', group='SonCal', kind='float')
        SEP = np.sqrt((ThermX-SonicX)**2 +
                      (ThermY-SonicY)**2 +
                      (ThermZ-SonicZ)**2)
        X = N/Means['ux']*SEP
        if X > 0.:
            TRANWT1 = np.exp(-9.9 * X**1.5)

        # C
        # C-- SOLENT SONIC TEMPERATURE !!
        # C-- Sonic temperature frequency response gain, eq. 2 -------------
        # C
        #          GAINT2=1.0D0       !sonic temperature gain negligible

        # sonic temperature gain negligible
        GAINT2 = 1.0

        # C
        # C-- Sonic temperature spatial averaging transfer function, eq.7 --
        # C
        #          TRANT2=1.0D0
        #          X=2.0D0*PI*N/Mean(U)*CalSonic(QQExt4)
        #          IF (X.GT.0.02D0)
        #     &        TRANT2=(3.0D0+EXP(-X)-4.0D0*(1.0D0-EXP(-X))/X)/X

        TRANT2 = 1.0
        # [m] path length sonic T
        SonicPathT = conf.get('QQExt4', group='SonCal', kind='float')
        X = 2.0 * ec.pi*N/Means['ux']*SonicPathT
        if X > 0.:
            TRANT2 = (3. + np.exp(-X) - 4.*(1.-np.exp(-X))/X)/X

        # C
        # C-- W-T lateral separation transfer function, eq. 11 -------------
        # C
        #          TRANWT2=1.0D0       !there is no lateral separation

        # there is no lateral separation
        TRANWT2 = 1.0

        # C
        # C-- SOLENT SONIC HORIZONTAL WINDSPEED !!
        # C-- UV-sensor frequency response gain, eq. 2 ---------------------
        # C
        #          GAINUV=1.0D0       !sonic UV windspeed gain negligible

        # sonic UV windspeed gain negligible
        GAINUV = 1.0

        # C
        # C-- UV-sensor spatial averaging transfer function, eq. 7 ---------
        # C
        #          TRANUV=1.0D0
        #          X=2.0D0*PI*N/Mean(U)*CalSonic(QQPath)
        #          IF (X.GT.0.02D0)
        #     &          TRANUV=(3.0D0+EXP(-X)-4.0D0*(1.0D0-EXP(-X))/X)/X

        TRANUV = 1.0
        SonicPathW = conf.get('QQPath', group='SonCal', kind='float')
        X = 2.0 * ec.pi * N/Means['ux'] * SonicPathW
        if X > 0.02:
            TRANUV = (3. + np.exp(-X) - 4.0*(1.0-np.exp(-X))/X)/X

        # C
        # C-- W-UV lateral separation transfer function, eq. 11 ------------
        # C
        #          TRANWUV=1.0D0
        #          X = N/Mean(U)*CalSonic(QQExt3)
        #          IF (X .GT.0.01D0) TRANWUV = EXP(-9.9D0*X**1.5D0)

        TRANWUV = 1.0
        # [m] distance w-u
        SonicDistUW = conf.get('QQExt3', group='SonCal', kind='float')
        X = N/Means['ux']*SonicDistUW
        if X > 0.01:
            TRANWUV = np.exp(-9.9 * X**1.5)

        # C
        # C-- SOLENT SONIC VERTICAL WINDSPEED !!
        # C-- W-sensor frequency response gain, eq. 2 ----------------------
        # C
        #          GAINW=1.0D0        !sonic W windspeed gain neglectible

        # sonic W windspeed gain neglectible
        GAINW = 1.0

        # C
        # C-- W-sensor spatial averaging transfer function, eq. 9 ----------
        # C
        #          TRANW=1.0D0
        #          X=2.0D0*PI*N/Mean(U)*CalSonic(QQPath)
        #          IF (X.GT.0.04D0)
        #     &       TRANW=(1.0D0+(EXP(-X)-3.D0*(1.0D0-EXP(-X))/X)/2.0D0)*4.0D0/X

        TRANW = 1.0
        X = 2.0 * ec.pi * N/Means['ux'] * SonicPathW
        if X > 0.04:
            TRANW = (1. + (np.exp(-X) - 3.*(1.-np.exp(-X))/X)/2.0) * 4.0/X

        # C
        # C-- LYMANN-ALPHA OPEN PATH HYGROMETER !!
        # C-- hygrometer frequency response gain, eq. 2 ------------
        # C
        #          GAINQ1=1.0D0        !hygrometer gain neglectible

        # hygrometer gain neglectible
        GAINQ1 = 1.0

        # C
        # C-- lymann-alpha spatial averaging transfer function, eq.7 ------------
        # C
        #          TRANQ1=1.0D0
        #          X=2.0D0*PI*N/Mean(U)*CalHyg(QQPath)
        #          IF (X.GT.0.02D0)
        #     &           TRANQ1=(3.0D0+EXP(-X)-4.0D0*(1.0D0-EXP(-X))/X)/X

        TRANQ1 = 1.0
        HygPath = conf.get('QQPath', group='HygCal', kind='float')
        X = 2.0 * ec.pi * N/Means['ux'] * HygPath
        if X > 0.02:
            TRANQ1 = (3.0 + np.exp(-X) - 4.0*(1.0-np.exp(-X))/X)/X

        # C
        # C-- W-Q lateral separation transfer function, eq. 11 -------------
        # C
        #          TRANWQ1=1.0D0
        #          SEP = SQRT((CalHyg(QQX)-CalSonic(QQX))**2 +
        #     &               (CalHyg(QQY)-CalSonic(QQY))**2 +
        #     &               (CalHyg(QQZ)-CalSonic(QQZ))**2)
        #          X=N/Mean(U)*SEP
        #          IF (X.GT.0.01D0) TRANWQ1=EXP(-9.9D0*X**1.5D0)

        HygX = conf.get('QQX', group='HygCal', kind='float')
        HygY = conf.get('QQY', group='HygCal', kind='float')
        HygZ = conf.get('QQZ', group='HygCal', kind='float')

        TRANWQ1 = 1.0
        SEP = np.sqrt((HygX-SonicX)**2 +
                      (HygY-SonicY)**2 +
                      (HygZ-SonicZ)**2)
        X = N/Means['ux']*SEP
        if X > 0.01:
            TRANWQ1 = np.exp(-9.9 * X**1.5)

        # C
        # C-- CO2 sensor !!
        # C-- CO2 sensor frequency response gain, eq. 2 ------------
        # C
        #          GAINCO21=1.0D0         !CO2 sensor gain neglectible

        # CO2 sensor gain neglectible
        GAINCO21 = 1.0

        # C
        # C-- CO2 sensor spatial averaging transfer function, eq.7 ------------
        # C
        #          TRANCO21=1.0D0
        #          X=2.D0*PI*N/Mean(U)*CalCO2(QQPath)
        #          IF (X.GT.0.02D0) THEN
        #            TRANCO21=(3.0D0+EXP(-X)-4.0D0*(1.0D0-EXP(-X))/X)/X
        #          ENDIF

        Co2Path = conf.get('QQPath', group='Co2Cal', kind='float')
        TRANCO21 = 1.0
        X = 2. * ec.pi * N/Means['ux'] * Co2Path
        if X > 0.02:
            TRANCO21 = (3.0 + np.exp(-X) - 4.0*(1.0-np.exp(-X))/X)/X

        # C
        # C-- W-CO2 lateral separation transfer function, eq. 11 -------------
        # C
        #          TRANWCO21=1.0D0
        #          SEP = SQRT((CalCO2(QQX)-CalSonic(QQX))**2 +
        #     &               (CalCO2(QQY)-CalSonic(QQY))**2 +
        #     &               (CalCO2(QQZ)-CalSonic(QQZ))**2)
        #          X=N/Mean(U)*SEP
        #          IF (X.GT.0.01D0) TRANWCO21=EXP(-9.9D0*X**1.5D0)

        Co2X = conf.get('QQX', group='Co2Cal', kind='float')
        Co2Y = conf.get('QQY', group='Co2Cal', kind='float')
        Co2Z = conf.get('QQZ', group='Co2Cal', kind='float')

        TRANWCO21 = 1.0
        SEP = np.sqrt((Co2X-SonicX)**2 +
                      (Co2Y-SonicY)**2 +
                      (Co2Z-SonicZ)**2)
        X = N/Means['ux'] * SEP
        if X > 0.01:
            TRANWCO21 = np.exp(-9.9 * X**1.5)

        # C
        # C-- Composite transfer functions, eq. 28 -------------------------
        # C
        #          DO I=1,NNMAX
        #             DO J=1,NNMAX
        #                  G(I,J) = 0.0D0
        #             ENDDO
        #          ENDDO
        #
        #          G(U,U)= TRANUV / GAINUV    !UU
        #          G(V,V)= TRANUV / GAINUV    !VV
        #          G(W,W)= TRANW  / GAINW    !WW
        #          G(TCouple, Tcouple) = TRANT1 / GAINT1    !TTth
        #          G(TSonic,TSonic)= TRANT2 / GAINT2    !TTso
        #          G(SpecHum,SpecHum)= TRANQ1 / GAINQ1    !QQ
        #          G(Humidity,Humidity)= TRANQ1 / GAINQ1    !rhov rhov
        #          G(CO2,CO2)= TRANCO21 / GAINCO21    !CO2
        #          G(SpecCO2,SpecCO2)= TRANCO21 / GAINCO21    !CO2
        #          G(U,W) = TRANWUV * SQRT (G(U,U) * G(W,W))    !WU
        #          G(W,U) = G(U,W)
        #          G(V,W) = TRANWUV * SQRT (G(V,V) * G(W,W))    !WV
        #          G(W,V) = G(V,W)
        #          G(W,TCouple) = TRANWT1 *
        #     &                   SQRT (G(W,W) * G(TCouple,TCouple))      !WTth
        #          G(TCouple,W) = G(W,TCouple)
        #          G(W,TSonic) = TRANWT2 * SQRT (G(W,W) * G(TSonic,TSonic))    !WTso
        #          G(TSonic,W) = G(W,TSonic)
        #          G(W,Humidity) = TRANWQ1 *
        #     &                   SQRT (G(W,W) * G(Humidity,Humidity))         !WQkr
        #          G(Humidity,W) = G(W,Humidity)
        #          G(W,SpecHum) = TRANWQ1 *
        #     &                   SQRT (G(W,W) * G(Humidity,Humidity))         !WQkr
        #          G(SpecHum,W) = G(W,SpecHum)
        #          G(W,CO2) = TRANWCO21 *
        #     &                   SQRT (G(W,W) * G(CO2,CO2))                   !WCO2
        #          G(CO2,W) = G(W,CO2)
        #          G(W,SpecCO2) = TRANWCO21 *
        #     &                   SQRT (G(W,W) * G(CO2,CO2))                  ! WqCO2
        #          G(SpecCO2,W) = G(W,SpecCO2)
        #          DO I=1,NNMax
        #             DO J=1,NNMax
        #                  G(I,J) = G(I,J)*TRANA*GAINV*GAIND
        #             ENDDO
        #          ENDDO

        G = pd.DataFrame(0., columns=Covs.columns, index=Covs.index)

        G.loc['ux', 'ux'] = TRANUV / GAINUV  # UU
        G.loc['uy', 'uy'] = TRANUV / GAINUV  # VV
        G.loc['uz', 'uz'] = TRANW / GAINW   # WW
        G.loc['tcoup', 'tcoup'] = TRANT1 / GAINT1  # TTth
        G.loc['ts', 'ts'] = TRANT2 / GAINT2  # TTso
        G.loc['q', 'q'] = TRANQ1 / GAINQ1  # QQ
        G.loc['h2o', 'h2o'] = TRANQ1 / GAINQ1  # rhov rhov
        G.loc['co2', 'co2'] = TRANCO21 / GAINCO21  # CO2
        G.loc['qco2', 'qco2'] = TRANCO21 / GAINCO21  # CO2
        G.loc['ux', 'uz'] = TRANWUV * \
            np.sqrt(G.loc['ux', 'ux'] * G.loc['uz', 'uz'])  # WU
        G.loc['uz', 'ux'] = G.loc['ux', 'uz']
        G.loc['uy', 'uz'] = TRANWUV * \
            np.sqrt(G.loc['uy', 'uy'] * G.loc['uz', 'uz'])  # WV
        G.loc['uz', 'uy'] = G.loc['uy', 'uz']
        G.loc['uz', 'tcoup'] = TRANWT1 * \
            np.sqrt(G.loc['uz', 'uz'] * G.loc['tcoup', 'tcoup'])  # WTth
        G.loc['tcoup', 'uz'] = G.loc['uz', 'tcoup']
        G.loc['uz', 'ts'] = TRANWT2 * \
            np.sqrt(G.loc['uz', 'uz'] * G.loc['ts', 'ts'])  # WTso
        G.loc['ts', 'uz'] = G.loc['uz', 'ts']
        G.loc['uz', 'h2o'] = TRANWQ1 * \
            np.sqrt(G.loc['uz', 'uz'] * G.loc['h2o', 'h2o'])  # WQkr
        G.loc['h2o', 'uz'] = G.loc['uz', 'h2o']
        G.loc['uz', 'q'] = TRANWQ1 * \
            np.sqrt(G.loc['uz', 'uz'] * G.loc['h2o', 'h2o'])  # WQkr
        G.loc['q', 'uz'] = G.loc['uz', 'q']
        G.loc['uz', 'co2'] = TRANWCO21 * \
            np.sqrt(G.loc['uz', 'uz'] * G.loc['co2', 'co2'])  # WCO2
        G.loc['co2', 'uz'] = G.loc['uz', 'co2']
        G.loc['uz', 'qco2'] = TRANWCO21 * \
            np.sqrt(G.loc['uz', 'uz'] * G.loc['co2', 'co2']
                    )                  # WqCO2
        G.loc['qco2', 'uz'] = G.loc['uz', 'qco2']

        G = G * TRANA * GAINV * GAIND

        #
        #          F=N/Mean(U)*CalSonic(QQZ)
        #          IF (ZL.LT.0.0D00) THEN

        F = N/Means['ux']*SonicZ

        if ZL < 0.:
            # C
            # C-- Unstable normalised spectral and co-spectral forms ---------
            # C
            #            UU=210.0D0*F/(1.0D0+33.0D0*F)**1.667D0                    !eq. 23
            #            UU=UU+F*XI/(ZETA+2.2D0*F**1.667D0)
            #            UU=UU/CU
            #            WW=16.0D0*F*XI/(1.0D0+17.0D0*F)**1.667D0                 !eq. 22
            #            WW=WW+F/(1.0D0+5.3D0*F**1.667D0)
            #            WW=WW/CW
            #            TT=14.94D0*F/(1.0D0+24.0D0*F)**1.667D0                  !eq. 24
            #            IF (F.GE.0.15D0) TT=6.827D0*F/(1.0D0+12.5D0*F)**1.667D0
            #            WT=12.92D0*F/(1.0D0+26.7D0*F)**1.375D0                  !eq. 25
            #            IF (F.GE.0.54D0) WT=4.378D0*F/(1.0D0+3.8D0*F)**2.4D0
            #            UW=20.78D0*F/(1.0D0+31.0D0*F)**1.575D0                  !eq. 26
            #            IF (F.GE.0.24D0) UW=12.66D0*F/(1.0D0+9.6D0*F)**2.4D0
            #          ELSE

            UU = 210.0 * F/(1.0 + 33.0*F)**1.667                   # eq. 23
            UU = UU + F*XI/(ZETA + 2.2*F**1.667)
            UU = UU/CU
            WW = 16.0 * F*XI/(1.0 + 17.0*F)**1.667                 # eq. 22
            WW = WW + F/(1.0 + 5.3*F**1.667)
            WW = WW/CW
            TT = 14.94 * F/(1.0 + 24.0*F)**1.667                   # eq. 24
            if F >= 0.15:
                TT = 6.827 * F/(1.0 + 12.5 * F)**1.667
            WT = 12.92 * F/(1.0 + 26.7*F)**1.375                   # eq. 25
            if F >= 0.54:
                WT = 4.378 * F/(1.0 + 3.8*F)**2.4
            UW = 20.78 * F/(1.0 + 31.0*F)**1.575                   # eq. 26
            if F >= 0.24:
                UW = 12.66 * F/(1.0 + 9.6*F)**2.4

        else:
            # C
            # C-- Stable normalised spectral and co-spectral forms, eq. 20a --
            # C
            #            UU=F/(AUU+BUU*F**1.667D0)
            #            WW=F/(AWW+BWW*F**1.667D0)
            #            TT=F/(ATT+BTT*F**1.667D0)
            #            WT=F/(AWT+BWT*F**2.1D0)
            #            UW=F/(AUW+BUW*F**2.1D0)
            #          ENDIF

            UU = F/(AUU+BUU*F**1.667)
            WW = F/(AWW+BWW*F**1.667)
            TT = F/(ATT+BTT*F**1.667)
            WT = F/(AWT+BWT*F**2.1)
            UW = F/(AUW+BUW*F**2.1)

        # C
        # C-- Integral of co-spectral transfer function * atm. co-spectrum -
        # C
        #          INTTS(U,U)  = INTTS(U,U) + I4*G(U,U) *UU  !UU
        #          INTTS(V,V)  = INTTS(V,V) + I4*G(V,V) *UU  !VV
        #          INTTS(W,W)  = INTTS(W,W) + I4*G(W,W) *WW  !WW
        #          INTTS(TCouple,TCouple)  =
        #     &           INTTS(TCouple,TCouple) + I4*G(TCouple,TCouple)*TT !TTth
        #          INTTS(TSonic,TSonic)  =
        #     &           INTTS(TSonic,TSonic) + I4*G(TSonic,TSonic) *TT ! TTso
        #          INTTS(Humidity,Humidity)  =
        #     &           INTTS(Humidity,Humidity) + I4*G(Humidity,Humidity) *TT  !QQkr
        #          INTTS(CO2,CO2)  =
        #     &           INTTS(CO2,CO2) + I4*G(CO2,CO2) *TT  !CO2 CO2
        #          INTTS(U,W)  = INTTS(U,W) + I4*G(U,W) *UW   !WU
        #          INTTS(W,U) = INTTS(U,W)
        #          INTTS(V,W)  = INTTS(V,W) + I4*G(V,W)*UW   !WV
        #          INTTS(W,V) = INTTS(V,W)
        #          INTTS(W,TCouple) = INTTS(W,TCouple) + I4*G(W,TCouple)*WT   !WTth
        #          INTTS(TCouple,W) = INTTS(W,TCouple)
        #          INTTS(W,TSonic) = INTTS(W,TSonic) + I4*G(W,TSonic)*WT   !WTso
        #          INTTS(TSonic,W) = INTTS(W,TSonic)
        #          INTTS(W,Humidity) = INTTS(W,Humidity) + I4*G(W,Humidity)*WT  !WQkr
        #          INTTS(Humidity,W) = INTTS(W,Humidity)
        #          INTTS(W,CO2) = INTTS(W,CO2) + I4*G(W,CO2)*WT  !WQCO2
        #          INTTS(CO2,W) = INTTS(W,CO2)

        INTTS.loc['ux', 'ux'] = INTTS.loc['ux', 'ux'] + \
            I4*G.loc['ux', 'ux'] * UU  # UU
        INTTS.loc['uy', 'uy'] = INTTS.loc['uy', 'uy'] + \
            I4*G.loc['uy', 'uy'] * UU  # VV
        INTTS.loc['uz', 'uz'] = INTTS.loc['uz', 'uz'] + \
            I4*G.loc['uz', 'uz'] * WW  # WW
        INTTS.loc['tcoup', 'tcoup'] = INTTS.loc['tcoup', 'tcoup'] + \
            I4*G.loc['tcoup', 'tcoup']*TT  # TTth
        INTTS.loc['ts', 'ts'] = INTTS.loc['ts', 'ts'] + \
            I4*G.loc['ts', 'ts'] * TT  # TTso
        INTTS.loc['h2o', 'h2o'] = INTTS.loc['h2o', 'h2o'] + \
            I4*G.loc['h2o', 'h2o'] * TT  # QQkr
        INTTS.loc['co2', 'co2'] = INTTS.loc['co2', 'co2'] + \
            I4*G.loc['co2', 'co2'] * TT  # CO2 CO2
        INTTS.loc['ux', 'uz'] = INTTS.loc['ux', 'uz'] + \
            I4*G.loc['ux', 'uz'] * UW   # WU
        INTTS.loc['uz', 'ux'] = INTTS.loc['ux', 'uz']
        INTTS.loc['uy', 'uz'] = INTTS.loc['uy', 'uz'] + \
            I4*G.loc['uy', 'uz']*UW   # WV
        INTTS.loc['uz', 'uy'] = INTTS.loc['uy', 'uz']
        INTTS.loc['uz', 'tcoup'] = INTTS.loc['uz', 'tcoup'] + \
            I4*G.loc['uz', 'tcoup']*WT   # WTth
        INTTS.loc['tcoup', 'uz'] = INTTS.loc['uz', 'tcoup']
        INTTS.loc['uz', 'ts'] = INTTS.loc['uz', 'ts'] + \
            I4*G.loc['uz', 'ts']*WT   # WTso
        INTTS.loc['ts', 'uz'] = INTTS.loc['uz', 'ts']
        INTTS.loc['uz', 'h2o'] = INTTS.loc['uz', 'h2o'] + \
            I4*G.loc['uz', 'h2o']*WT  # WQkr
        INTTS.loc['h2o', 'uz'] = INTTS.loc['uz', 'h2o']
        INTTS.loc['uz', 'co2'] = INTTS.loc['uz', 'co2'] + \
            I4*G.loc['uz', 'co2']*WT  # WQCO2
        INTTS.loc['co2', 'uz'] = INTTS.loc['uz', 'co2']

        #
        # C
        # C-- Increase frequency by interval width -------------------------
        # C
        #          N=N*LF

        N = N*LF

        #        ENDDO
        #      ENDDO
        #
        # 200  CONTINUE

        # The else clause executes when the loop completes normally.
        # This means that the loop did not encounter any break.
        #
        #

        #
        # in FORTRAN this is done implicitply by the declaration
        WXT = pd.DataFrame(np.nan, columns=Covs.columns, index=Covs.columns)

    else:
        #
        # C
        # C-- Final flux loss correction factors !! ----------------------------
        # C
        #
        #      DO I=1,NSize
        #        DO J=1,NSize
        #           WXT(I,J) = 1.0D0
        #        ENDDO
        #      ENDDO
        #

        WXT = pd.DataFrame(1., columns=Covs.columns, index=Covs.columns)

    # continue here if for I3 loop was left by break command

    # 999   CONTINUE

    #      WXT(U,U) = C/INTTS(U,U)              !UU
    #      WXT(V,V) = C/INTTS(V,V)              !VV
    #      WXT(U,V) = WXT(U,U)                  !UV
    #      WXT(V,U) = WXT(U,V)                  !VU
    #      WXT(W,W) = C/INTTS(W,W)              !WW
    #      WXT(W,U) = C/INTTS(U,W)              !WU
    #      WXT(U,W) = WXT(W,U)
    #      WXT(W,V) = C/INTTS(V,W)              !WV
    #      WXT(V,W) = WXT(W,V)
    #
    #      WXT(W,TSonic) = C/INTTS(W,TSonic)    !WTso
    #      WXT(TSonic,W) = WXT(W,TSonic)
    #      WXT(TSonic,TSonic) = C/INTTS(TSonic,TSonic)  !TTso
    #
    #      WXT(W,TCouple) = C/INTTS(W,TCouple)  !WTth
    #      WXT(TCouple,W) = WXT(W,TCouple)
    #      WXT(TCouple,TCouple) = C/INTTS(TCouple,TCouple)    !TTth
    #
    #      WXT(W,Humidity) = C/INTTS(W,Humidity)   !WQly
    #      WXT(Humidity,W) = WXT(W,Humidity)
    #      WXT(Humidity,Humidity) = C/INTTS(Humidity,Humidity)  !QQly
    #
    #      WXT(W,SpecHum)       = WXT(W,Humidity)
    #      WXT(SpecHum,W)       = WXT(Humidity,W)
    #      WXT(SpecHum,SpecHum) = WXT(Humidity,Humidity)
    #
    #      WXT(W,CO2) = C/INTTS(W,CO2)       ! W rhoCO2
    #      WXT(CO2,W) = WXT(W,CO2)
    #      WXT(CO2,CO2) = C/INTTS(CO2,CO2)  ! rhoCO2^2
    #
    #      WXT(W,SpecCO2)       = WXT(W,CO2)
    #      WXT(SpecCO2,W)       = WXT(CO2,W)
    #      WXT(SpecCO2,SpecCO2) = WXT(CO2,CO2)

    WXT.loc['ux', 'ux'] = C/INTTS.loc['ux', 'ux']              # UU
    WXT.loc['uy', 'uy'] = C/INTTS.loc['uy', 'uy']              # VV
    WXT.loc['ux', 'uy'] = WXT.loc['ux', 'ux']                  # UV
    WXT.loc['uy', 'ux'] = WXT.loc['ux', 'uy']                  # VU
    WXT.loc['uz', 'uz'] = C/INTTS.loc['uz', 'uz']              # WW
    WXT.loc['uz', 'ux'] = C/INTTS.loc['ux', 'uz']              # WU
    WXT.loc['ux', 'uz'] = WXT.loc['uz', 'ux']
    WXT.loc['uz', 'uy'] = C/INTTS.loc['uy', 'uz']              # WV
    WXT.loc['uy', 'uz'] = WXT.loc['uz', 'uy']

    WXT.loc['uz', 'ts'] = C/INTTS.loc['uz', 'ts']              # WTso
    WXT.loc['ts', 'uz'] = WXT.loc['uz', 'ts']
    WXT.loc['ts', 'ts'] = C/INTTS.loc['ts', 'ts']              # TTso

    WXT.loc['uz', 'tcoup'] = C/INTTS.loc['uz', 'tcoup']        # WTth
    WXT.loc['tcoup', 'uz'] = WXT.loc['uz', 'tcoup']
    WXT.loc['tcoup', 'tcoup'] = C/INTTS.loc['tcoup', 'tcoup']  # TTth

    WXT.loc['uz', 'h2o'] = C/INTTS.loc['uz', 'h2o']            # WQly
    WXT.loc['h2o', 'uz'] = WXT.loc['uz', 'h2o']
    WXT.loc['h2o', 'h2o'] = C/INTTS.loc['h2o', 'h2o']          # QQly

    WXT.loc['uz', 'q'] = WXT.loc['uz', 'h2o']
    WXT.loc['q', 'uz'] = WXT.loc['h2o', 'uz']
    WXT.loc['q', 'q'] = WXT.loc['h2o', 'h2o']

    WXT.loc['uz', 'co2'] = C/INTTS.loc['uz', 'co2']            # W rhoCO2
    WXT.loc['co2', 'uz'] = WXT.loc['uz', 'co2']
    WXT.loc['co2', 'co2'] = C/INTTS.loc['co2', 'co2']          # rhoCO2^2

    WXT.loc['uz', 'qco2'] = WXT.loc['uz', 'co2']
    WXT.loc['qco2', 'uz'] = WXT.loc['co2', 'uz']
    WXT.loc['qco2', 'qco2'] = WXT.loc['co2', 'co2']

    #      DO i=1,NSize
    #        DO j=1,NSize
    #          IF ((WXT(i,j).GE.Lower).AND.(WXT(i,j).LE.Upper)
    #     &        .AND.COV(i,j).NE.DUMMY.AND.TOLCOV(i,j).NE.DUMMY) THEN
    #            Cov(i,j) = Cov(i,j)*WXT(i,j)
    # C
    # C The tolerance is augmented by half the amount added by frequency-
    # C response correction.
    # C
    #            TolCov(i,j) = SQRT(TolCov(i,j)**2.D0+
    #     &         (0.5D0*Cov(i,j)*(WXT(i,j)-1.D0))**2.D0)
    #          ENDIF
    #        ENDDO
    #      ENDDO

    Lower = conf.get('LLimit', group='Par', kind='float')
    Upper = conf.get('ULimit', group='Par', kind='float')
    OCovs = Covs.copy()
    OTolCov = TolCov.copy()
    for i in Covs.index:
        for j in Covs.columns:
            if ((WXT.loc[i, j] >= Lower) and (WXT.loc[i, j] <= Upper)
                and np.isfinite(Covs.loc[i, j])
                    and np.isfinite(TolCov.loc[i, j])):
                OCovs.loc[i, j] = Covs.loc[i, j]*WXT.loc[i, j]
                # C
                # C The tolerance is augmented by half
                # C the amount added by frequency-
                # C response correction.
                # C
                OTolCov.loc[i, j] = np.sqrt(
                    TolCov.loc[i, j]**2 + (0.5*OCovs.loc[i, j]*(WXT.loc[i, j]-1.))**2)

    return OCovs, OTolCov

# ----------------------------------------------------------------
#


def mapmtx(a, b):
    """
    Calculate matrix-vector product y = A·b for coordinate transformations.

    :param a: Transformation matrix
    :type a: pandas.DataFrame
    :param b: Vector or matrix to be transformed
    :type b: pandas.DataFrame
    :return: Transformed vector/matrix
    :rtype: pandas.DataFrame

    Applies transformation to each row using matrix multiplication.
           Used extensively in coordinate system rotations.

    Name in ECPACK: EC_M_MapMtx
    """
    return b.apply(lambda x: np.array(a).dot(x), axis=1, raw=True)


# ----------------------------------------------------------------
#
def flux(means, tolmean, covs, tolcov, badtc, p, webvel, diryaw):
    """
    Calculate surface fluxes from mean values and covariances.

    :param means: Mean values of all variables
    :type means: pandas.Series
    :param tolmean: Tolerances in mean values
    :type tolmean: pandas.Series
    :param covs: Covariance matrix of all variables
    :type covs: pandas.DataFrame
    :param tolcov: Tolerances in covariances
    :type tolcov: pandas.DataFrame
    :param badtc: Flag for corrupt thermocouple temperature
    :type badtc: bool
    :param p: Atmospheric pressure [Pa]
    :type p: float
    :param webvel: Webb correction velocity [m/s]
    :type webvel: float
    :param diryaw: Yaw rotation angle [degrees]
    :type diryaw: float
    :return: Tuple of (physical_quantities, uncertainties)
    :rtype: tuple

    Calculates friction velocity, sensible/latent heat fluxes,
           CO2 fluxes, wind statistics, and their uncertainties.
           Handles both sonic and thermocouple temperature options.

    Name in ECPACK: EC_Ph_Flux
    """
    # C
    # C Air density (sonic T)
    # C
    #      IF ((Mean(Humidity) .NE. DUMMY) .AND.
    #     &    (Mean(TSonic) .NE. DUMMY)) THEN
    #        QPhys(QPRhoSon) = EC_Ph_RhoWet(Mean(Humidity),Mean(TSonic),p)
    #        dQPhys(QPRhoSon) = DUMMY
    #      ELSE
    #        QPhys(QPRhoSon) = DUMMY
    #        dQPhys(QPRhoSon) = DUMMY
    #      ENDIF

    qphys = {k: np.nan for k in ec.qpvar}
    dqphys = {k: np.nan for k in ec.qpvar}

    if np.isfinite(means['h2o']) and np.isfinite(means['ts']):
        qphys['rhoson'] = ec.rhowet(means['h2o'], means['ts'], p)
        dqphys['rhoson'] = np.nan
    else:
        qphys['rhoson'] = np.nan
        dqphys['rhoson'] = np.nan

    # C
    # C Air density (couple T)
    # C
    #      IF ((.NOT. BadTC) .AND.
    #     &    (Mean(Humidity) .NE. DUMMY) .AND.
    #     &    (Mean(TCouple) .NE. DUMMY)) THEN
    #        QPhys(QPRhoTC) = EC_Ph_RhoWet(Mean(Humidity),Mean(TCouple),p)
    #        dQPhys(QPRhoTC) = DUMMY
    #      ELSE
    #        QPhys(QPRhoTC) = DUMMY
    #        dQPhys(QPRhoTC) = DUMMY
    #      ENDIF

    if ((not badtc) and
            np.isfinite(means['h2o']) and np.isfinite(means['tcoup'])):
        qphys['rhocoup'] = ec.rhowet(means['h2o'], means['tcoup'], p)
        dqphys['rhocoup'] = np.nan
    else:
        qphys['rhocoup'] = np.nan
        dqphys['rhocoup'] = np.nan

    # C
    # C Sensible heat flux [W m^{-2}]
    # C
    #      IF (.NOT. BadTC) THEN
    #        Cp = EC_Ph_Cp(Mean(TCouple))
    #      ELSE
    #        Cp = EC_Ph_Cp(Mean(TSonic))
    #      ENDIF
    #
    #      IF ((Mean(Humidity) .NE. DUMMY) .AND.
    #     &    (Mean(TSonic) .NE. DUMMY) .AND.
    #     &    (Cov(W,TSonic) .NE. DUMMY)) THEN
    #        RhoSon = QPhys(QPRhoSon)
    #        QPhys(QPHSonic) = Cp*RhoSon*Cov(W,TSonic)
    #        dQPhys(QPHSonic) = Cp*RhoSon*TolCov(W,TSonic)
    #      ELSE
    #        QPhys(QPHSonic) = DUMMY
    #        dQPhys(QPHSonic) = DUMMY
    #      ENDIF
    #
    #      IF ((.NOT. BadTC) .AND.
    #     &    (Mean(Humidity) .NE. DUMMY) .AND.
    #     &    (Mean(TCouple) .NE. DUMMY) .AND.
    #     &    (Cov(W,TCouple) .NE. DUMMY)) THEN
    #        RhoTc = QPhys(QPRhoTC)
    #        QPhys(QPHTc) = Cp*RhoTc*Cov(W,TCouple)
    #        dQPhys(QPHTc) = Cp*RhoTc*TolCov(W,TCouple)
    #      ELSE
    #        QPhys(QPHTc) = DUMMY
    #        dQPhys(QPHTc) = DUMMY
    #      ENDIF

    if not badtc:
        cp = ec.cpt(means['tcoup'])
    else:
        cp = ec.cpt(means['ts'])

    if (np.isfinite(means['h2o']) and np.isfinite(means['ts'])
            and np.isfinite(covs.loc['uz', 'ts'])):
        qphys['hson'] = cp*qphys['rhoson']*covs.loc['uz', 'ts']
        dqphys['hson'] = cp*qphys['rhoson']*tolcov.loc['uz', 'ts']
    else:
        qphys['hson'] = np.nan
        dqphys['hson'] = np.nan

    if ((not badtc) and
        np.isfinite(means['h2o']) and np.isfinite(means['tcoup'])
            and np.isfinite(covs.loc['uz', 'tcoup'])):
        qphys['hcoup'] = cp*qphys['rhoson']*covs.loc['uz', 'tcoup']
        dqphys['hcoup'] = cp*qphys['rhoson']*tolcov.loc['uz', 'tcoup']
    else:
        qphys['hcoup'] = np.nan
        dqphys['hcoup'] = np.nan

    # C
    # C Latent heat flux [W m^{-2}]
    # C
    #      IF (.NOT. BadTC) THEN
    #        Lv = EC_Ph_Lv(Mean(TCouple))
    #      ELSE
    #        Lv = EC_Ph_Lv(Mean(TSonic))
    #      ENDIF
    #
    #      IF (Cov(W, Humidity) .NE. DUMMY) THEN
    #        QPhys(QPLvE) = Lv*Cov(W,Humidity)
    #        dQPhys(QPLvE) = Lv*TolCov(W,Humidity)
    #      ELSE
    #        QPhys(QPLvE) = DUMMY
    #        dQPhys(QPLvE) = DUMMY
    #      ENDIF
    #
    #      IF ((WebVel .NE. DUMMY) .AND.
    #     &    (Mean(Humidity) .NE. DUMMY).AND.
    #     &    (TolMean(Humidity) .NE. DUMMY)) THEN
    #           Qphys(QPLvEWebb) = Lv*WebVel*Mean(Humidity)
    #         Frac1 = 0.D0
    #         Frac2 = ABS(TolMean(Humidity)/Mean(Humidity))
    #
    #         dQPhys(QPLvEWebb) = QPhys(QPLvEWebb)*
    #     &                    (Frac1**2.D0+Frac2**2.D0)**0.5D0
    #      ELSE
    #        QPhys(QPLvEWebb) = DUMMY
    #        dQPhys(QPLvEWebb) = DUMMY
    #      ENDIF

    if not badtc:
        l_v = ec.lvt(means['tcoup'])
    else:
        l_v = ec.lvt(means['ts'])

    if np.isfinite(covs.loc['uz', 'h2o']):
        qphys['ecov'] = l_v*covs.loc['uz', 'h2o']
        dqphys['ecov'] = l_v*tolcov.loc['uz', 'h2o']
    else:
        qphys['ecov'] = np.nan
        dqphys['ecov'] = np.nan

    if (np.isfinite(webvel) and
        np.isfinite(means['h2o']) and
            np.isfinite(tolmean['h2o'])):
        qphys['ewebb'] = l_v*webvel*means['h2o']
        frac1 = 0.
        frac2 = np.abs(tolmean['h2o']/means['h2o'])
        dqphys['ewebb'] = qphys['ewebb'] * np.sqrt(frac1**2 + frac2**2)
    else:
        qphys['ewebb'] = np.nan
        dqphys['ewebb'] = np.nan

    #      IF ((QPhys(QPLvE) .NE. DUMMY) .AND.
    #     &    (QPhys(QPLvEWebb) .NE. DUMMY)) THEN
    #      	   QPhys(QPSumLvE) = QPhys(QPLvE) + QPhys(QPLvEWebb)
    #           dQPhys(QPSumLvE) =  SQRT(dQPhys(QPLvE)**2.D0 +
    #     &                        dQPhys(QPLvEWebb)**2.D0)
    #      ELSE
    #          QPhys(QPSumLvE) = DUMMY
    #          dQPhys(QPSumLvE) = DUMMY
    #      ENDIF

    if (np.isfinite(qphys['ecov']) and
            np.isfinite(qphys['ewebb'])):
        qphys['esum'] = qphys['ecov'] + qphys['ewebb']
        dqphys['esum'] = np.sqrt(dqphys['ecov']**2 + dqphys['ewebb']**2)
    else:
        qphys['esum'] = np.nan
        dqphys['esum'] = np.nan

    # C
    # C Friction velocity (vector sum of two components
    # C
    #      IF (.NOT. ((COV(W,U) .EQ. DUMMY) .AND.
    #     &           (COV(W,V) .EQ. DUMMY))) THEN
    #        QPhys(QPUStar) = SQRT(SQRT(Cov(W,U)**2+Cov(W,V)**2))
    #        IF (.NOT.BadTc) THEN
    #          RhoSon = QPhys(QPRhoSon)
    #          RhoTc = QPhys(QPRhoTc)
    #          QPhys(QPTau) = 0.5D0*(RhoSon+RhoTc)*
    #     &                         (ABS(QPhys(QPUStar)))**2.D0
    #        ELSE
    #          RhoSon = QPhys(QPRhoSon)
    #          QPhys(QPTau) = RhoSon*(ABS(QPHys(QPUStar)))**2.D0
    #        ENDIF
    #        IF (QPhys(QPUStar) .NE. 0.D0) THEN
    #          dQPhys(QPUStar) = (0.25D0*(2D0*TolCov(W,U)*ABS(COV(W,U)) +
    #     &                               2D0*TolCov(W,V)*ABS(COV(W,V)))/
    #     &                  QPhys(QPUStar)**4D0)*
    #     &                  QPhys(QPUStar)
    #          dQPhys(QPTau) = (2D0*dQPhys(QPUstar)/QPhys(QPUstar))*
    #     &             QPhys(QPTau)
    #        ELSE
    #          dQPhys(QPUstar) = DUMMY
    #          dQPhys(QPTau) = DUMMY
    #        ENDIF
    #      ELSE
    #        QPhys(QPUstar) = DUMMY
    #        dQPhys(QPUstar) = DUMMY
    #        QPhys(QPTau) = DUMMY
    #        dQPhys(QPTau) = DUMMY
    #      ENDIF

    if (np.isfinite(covs.loc['uz', 'ux']) and
            np.isfinite(covs.loc['uz', 'uy'])):
        qphys['ustar'] = np.sqrt(
            np.sqrt(covs.loc['uz', 'ux']**2 + covs.loc['uz', 'uy']**2))
        if not badtc:
            qphys['tausum'] = (qphys['rhoson']+qphys['rhocoup']
                               )/2. * qphys['ustar']**2
        else:
            qphys['tausum'] = qphys['rhoson'] * qphys['ustar']**2

        if qphys['ustar'] != 0.:
            dqphys['ustar'] = ((0.25 * (2. * tolcov.loc['uz', 'ux'] * np.abs(covs.loc['uz', 'ux'])
                                        + 2. * tolcov.loc['uz', 'uy'] * np.abs(covs.loc['uz', 'uy']))
                                / qphys['ustar']**4)
                               * qphys['ustar'])
            dqphys['tausum'] = (2. * dqphys['ustar'] /
                                qphys['ustar'])*qphys['tausum']
        else:
            dqphys['ustar'] = np.nan
            dqphys['tausum'] = np.nan
    else:
        qphys['ustar'] = np.nan
        qphys['tausum'] = np.nan
        dqphys['ustar'] = np.nan
        dqphys['tausum'] = np.nan

    # C
    # C CO2 flux [kg m^{-2} s^{-1}]
    # C
    #      IF (COV(W,CO2) .NE. DUMMY) THEN
    #        QPhys(QPFCO2) = Cov(W,CO2)
    #        dQPhys(QPFCO2) = TolCov(W,CO2)
    #      ELSE
    #        QPhys(QPFCO2) = DUMMY
    #        dQPhys(QPFCO2) = DUMMY
    #      ENDIF
    #      IF ((WebVel .NE. DUMMY) .AND.
    #     &    (Mean(CO2) .NE. DUMMY)) THEN
    #           QPhys(QPFCO2Webb) = WebVel*Mean(CO2)
    # C Frac1 is set to zero, assuming no error in W (else error in
    # C Webb term would be enormous
    #           Frac1 = 0.D0
    #           Frac2 = ABS(TolMean(CO2)/Mean(CO2))
    #
    #           dQPhys(QPFCO2Webb) =
    #     &          QPhys(QPFCO2Webb)*(Frac1**2.D0+Frac2**2.D0)**0.5D0
    #      ELSE
    #        QPhys(QPFCO2Webb) = DUMMY
    #        dQPhys(QPFCO2Webb) = DUMMY
    #      ENDIF
    #      IF ((QPhys(QPFCO2) .NE. DUMMY) .AND.
    #     &    (QPhys(QPFCO2Webb) .NE. DUMMY)) THEN
    #      	   QPhys(QPSumFCO2) = QPhys(QPFCO2) + QPhys(QPFCO2Webb)
    #           dQPhys(QPSumFCO2) =  SQRT(dQPhys(QPFCO2)**2.D0 +
    #     &                      dQPhys(QPFCO2Webb)**2.D0)
    #      ELSE
    #          QPhys(QPSumFCO2) = DUMMY
    #          dQPhys(QPSumFCO2) = DUMMY

    if np.isfinite(covs.loc['uz', 'co2']):
        qphys['fco2'] = covs.loc['uz', 'co2']
        dqphys['fco2'] = tolcov.loc['uz', 'co2']
    else:
        qphys['fco2'] = np.nan
        dqphys['fco2'] = np.nan

    if (np.isfinite(webvel) and
            np.isfinite(means['co2'])):
        qphys['fco2webb'] = webvel * means['co2']
        # C Frac1 is set to zero, assuming no error in W (else error in
        # C Webb term would be enormous
        frac1 = 0.
        frac2 = np.abs(tolmean['co2']/means['co2'])
        dqphys['fco2webb'] = qphys['fco2webb'] * np.sqrt(frac1**2 + frac2**2)
    else:
        qphys['fco2webb'] = np.nan
        dqphys['fco2webb'] = np.nan

    if (np.isfinite(qphys['fco2']) and
            np.isfinite(qphys['fco2webb'])):
        qphys['fco2sum'] = qphys['fco2'] + qphys['fco2webb']
        dqphys['fco2sum'] = np.sqrt(dqphys['fco2']**2 + dqphys['fco2webb']**2)
    else:
        qphys['fco2sum'] = np.nan
        dqphys['fco2sum'] = np.nan

    # C
    # C Vector wind
    # C
    #      IF ((Mean(U) .NE. DUMMY) .AND.
    #     &    (Mean(V) .NE. DUMMY)) THEN
    #        QPhys(QPVectWind) = SQRT(Mean(U)**2D0+Mean(V)**2D0)
    #        dQPhys(QPVectWind) = 0.5D0 * (TolMean(U)*ABS(Mean(U)) +
    #     &                       TolMean(V)*ABS(Mean(V)))
    #      ELSE
    #        QPhys(QPVectWind) = DUMMY
    #        dQPhys(QPVectWind) = DUMMY
    #      ENDIF

    if (np.isfinite(means['ux']) and
            np.isfinite(means['uy'])):
        qphys['vectwind'] = np.sqrt(means['ux']**2 + means['uy']**2)
        dqphys['vectwind'] = 0.5 * (tolmean['ux']*np.abs(means['ux'])
                                    + tolmean['uy']*np.abs(means['uy']))
    else:
        qphys['vectwind'] = np.nan
        dqphys['vectwind'] = np.nan

    # C
    # C Wind direction
    # C
    #      IF ((Mean(U) .NE. DUMMY) .AND.
    #     &    (Mean(V) .NE. DUMMY) .AND.
    #     &    (DirYaw .NE. DUMMY)) THEN
    #
    #         IF (DirYaw.GE.180.D0) THEN
    #             QPhys(QPDirFrom) = DirYaw - 180.D0
    #         ELSE
    #             QPhys(QPDirFrom) = DirYaw + 180.D0
    #         ENDIF
    #         QPhys(QPDirFrom) = QPhys(QPDirFrom)
    #     &                  - ATAN2(Mean(V), -Mean(U))*180/PI
    #         IF (QPhys(QPDirFrom) .LT. 0) THEN
    #            QPhys(QPDirFrom) = QPhys(QPDirFrom) + 360.0D0
    #         ENDIF
    #         IF (QPhys(QPDirFrom) .GT. 360.D0) THEN
    #            QPhys(QPDirFrom) = QPhys(QPDirFrom) - 360.0D0
    #         ENDIF
    #
    #         LocalDir = ATAN2(Mean(U), Mean(V))
    #         dQPhys(QPDirFrom) = 2.D0*180.D0*ATAN(
    #     &              SQRT(Cos(LocalDir)*Cov(V,V)+
    #     &                   SIN(LocalDir)*Cov(U,U))/QPhys(QPVectWind))/Pi
    #      ELSE
    #         QPhys(QPDirFrom) = DUMMY
    #         dQPhys(QPDirFrom) = DUMMY
    #      ENDIF

    if (np.isfinite(means['ux']) and
        np.isfinite(means['uy']) and
            np.isfinite(diryaw)):
        if diryaw >= 180.:
            qphys['dirfrom'] = diryaw - 180.
        else:
            qphys['dirfrom'] = diryaw + 180.

        qphys['dirfrom'] = (qphys['dirfrom']
                            - np.arctan2(means['uy'], -means['ux'])/ec.deg2rad
                            ) % 360.

        localdir = np.arctan2(means['ux'], means['uy'])
        dqphys['dirfrom'] = 2.*np.arctan(
            np.sqrt(
                np.cos(localdir)*covs.loc['uy', 'uy'] +
                np.sin(localdir)*covs.loc['ux', 'ux']
            )/qphys['vectwind']
        )/ec.deg2rad
    else:
        qphys['dirfrom'] = np.nan
        dqphys['dirfrom'] = np.nan

    return qphys, dqphys

# ----------------------------------------------------------------
#


def obukhov(Ustar, Tstar, Qstar, MeanT):
    """
    Calculate Obukhov length including water vapor buoyancy effects.

    :param Ustar: Friction velocity [m/s]
    :type Ustar: float
    :param Tstar: Temperature scale [K]
    :type Tstar: float
    :param Qstar: Humidity scale [kg/kg]
    :type Qstar: float
    :param MeanT: Mean temperature [K]
    :type MeanT: float
    :return: Obukhov length [m]
    :rtype: float

    Uses standard Monin-Obukhov similarity theory formulation
           with humidity correction for buoyancy effects.

    name in ECPACK: EC_Ph_Obukhov
    """
    L = (MeanT/(ec.kappa*ec.g)) * Ustar**2/(Tstar + 0.61*MeanT*Qstar)
    return L


# ----------------------------------------------------------------
#
def oxygen(MeanT, Covin, P, HygType, WhichTemp):
    """
    Correct hygrometer measurements for oxygen absorption effects.

    :param MeanT: Mean temperature [K]
    :type MeanT: float
    :param Covin: Input covariance matrix
    :type Covin: pandas.DataFrame
    :param P: Atmospheric pressure [Pa]
    :type P: float
    :param HygType: Hygrometer type code
    :type HygType: str
    :param WhichTemp: Temperature variable used
    :type WhichTemp: str
    :return: Corrected covariance matrix
    :rtype: pandas.DataFrame

    Applies corrections for KH20, Lyman-alpha, and LiCor hygrometers.
           LiCor IR hygrometers are not sensitive to oxygen.

    Names in ECPACK: EC_C_Oxygen1 and EC_C_Oxygen2
    """

    # C Intialize GenKo eand GenKw
    #      GenKo = 0.0D0
    #      GenKw = 1.0D0
    #      IF (HygType .EQ. ApCampKrypton) THEN
    #          GenKo = KoK
    #          GenKw = KwK
    #      ELSE IF (HygType .EQ. ApMierijLyma) THEN
    #          GenKo = KoLa
    #          GenKw = KwLa
    #      ELSE IF (HygType .EQ. ApLiCor7500) THEN
    #          GenKo = 0.0D0
    #          GenKw = 1.0D0SpecHum
    #      ENDIF

    # Intialize GenKo eand GenKw
    GenKo = 0.0
    GenKw = 1.0
    if HygType == 'ApCampKrypton':
        GenKo = 0.0038              # [m^{3} g^{-1} cm^{-1}]
        GenKw = 0.143               # [m^{3} g^{-1} cm^{-1}]
    if HygType == 'ApMierijLyma':
        GenKo = 0.001085            # [m^{3} g^{-1} cm^{-1}]
        GenKw = 0.09125             # [m^{3} g^{-1} cm^{-1}]
    if HygType == 'ApLiCor7500':
        GenKo = 0.0
        GenKw = 1.0

    #      OXC = FracO2*MO2*P*GenKo/(RGas*MeanT**2.D0*GenKw)
    #
    #      DO i = 1,N
    #        Factor(i) = 1.D0 + OXC*Cov(i,WhichTemp)/Cov(i,Humidity)
    #        IF ((i.EQ.Humidity).OR.(i.EQ.SpecHum))
    #     &       Factor(i) = Factor(i)**2.D0
    #      ENDDO

    # fraction of O2 molecules in air
    oxc = ec.FracO2*ec.M_O2*P*GenKo/(ec.r_gas * MeanT**2 * GenKw)

    factor = {}
    for v in ec.ecvar:
        factor[v] = (1. + oxc*Covin.loc[v, WhichTemp]/Covin.loc[v, 'h2o'])
        if v == 'h2o' or v == 'q':
            factor[v] = factor[v]**2

    #      REAL*8 Cov(NMax,NMax),Factor(NMax)
    #      DO i = 1,N
    #        Cov(i,Humidity) = Factor(i)*Cov(i,Humidity)
    #        Cov(i,SpecHum ) = Factor(i)*Cov(i,SpecHum )
    #        Cov(Humidity,i) = Cov(i,Humidity)
    #        Cov(SpecHum ,i) = Cov(i,SpecHum )
    #      ENDDO

    Covs = Covin.copy()
    for v in ec.ecvar:
        Covs.loc[v, 'h2o'] = factor[v]*Covs.loc[v, 'h2o']
        Covs.loc[v, 'q'] = factor[v]*Covs.loc[v, 'q']
        Covs.loc['h2o', v] = Covs.loc[v, 'h2o']
        Covs.loc['q', v] = Covs.loc[v, 'q']

    return Covs

# ----------------------------------------------------------------
#


def scal(conf, raw):
    """
    Apply wind tunnel calibration to sonic anemometer data.

    :param conf: Configuration object with calibration coefficients
    :type conf: object
    :param raw: DataFrame with raw sonic measurements
    :type raw: pandas.DataFrame
    :return: DataFrame with calibrated sonic data
    :rtype: pandas.DataFrame

    The method is based on a wind tunnel calibration of the sonic
    The real velocity components can be derived from the
    measured components and the real azimuth (:math:`\\varphi`)
    and elevation angle (:math:`\\theta`).
    But the latter are not known and have to be determined
    iteratively from the measured components. The relationship
    between the real components and the measured components is:

    .. math::

        U_\\mathrm{real} &= \\frac{U_\\mathrm{meas}}
                               {U_{C1}\\left(1 - 0.5 \\left(
                               (\\varphi + (\\theta/0.5236) \\cdot U_{C2})
                               \\cdot
                               (1 - U_{C3} \\cdot |\\theta/0.5236|)\\right)^2
                               \\right)}

        V_\\mathrm{real} &= V_\\mathrm{meas} \\cdot
                            (1 - V_{C1} \\cdot |\\theta/0.5236|)

        W_\\mathrm{real} &= \\frac{W_\\mathrm{meas}}
              {W_{C1} \\left(1 - 0.5 (\\varphi \\cdot W_{C2})^2\\right)}

        \\varphi &= \\arctan\\left(\\frac{V}{U}\\right)

        \\theta &= \\arctan\\left(\\frac{W}{\\sqrt{U^2 + V^2}}\\right)

    where :math:`U_{C1}`, :math:`U_{C2}`, :math:`U_{C3}`,
    :math:`V_{C1}`, :math:`W_{C1}`, :math:`W_{C2}`
    are fitting coefficients.
    An azimuth angle of zero is supposed to refer to a wind
    direction from the most optimal direction (i.e. the 'open'
    side of a sonic). Samples with an absolute azimuth angle of
    more than 40 degrees are rejected.
    """
    #
    #
    #      UC1 = Cal(QQExt6)
    #      UC2 = Cal(QQExt7)
    #      UC3 = Cal(QQExt8)
    #      VC1 = Cal(QQExt9)
    #      WC1 = Cal(QQExt10)
    #      WC2 = Cal(QQExt11)
    UC1 = conf.get('QQExt6', group='SonCal', kind='float')
    UC2 = conf.get('QQExt7', group='SonCal', kind='float')
    UC3 = conf.get('QQExt8', group='SonCal', kind='float')
    VC1 = conf.get('QQExt9', group='SonCal', kind='float')
    WC1 = conf.get('QQExt10', group='SonCal', kind='float')
    WC2 = conf.get('QQExt11', group='SonCal', kind='float')

    #
    #      ITMAX = 20
    #      NITER = 0
    #      AziOld = 9999D0
    #      ElevOld = 9999D0
    #      AziNew = ATAN(VDum/UDum)
    #      ElevNew = ATAN(WDum/SQRT(UDum**2 + VDum**2))
    ITMAX = 20

    # copy input data to output data frame
    # (will be overwritten subsequently)
    corr = raw[['ux', 'uy', 'uz']]

    for i in corr.index:
        UDum = corr.loc[i, 'ux']
        VDum = corr.loc[i, 'uy']
        WDum = corr.loc[i, 'uz']

        NITER = 0
        AziOld = 9999.
        ElevOld = 9999.
        AziNew = np.arctan(VDum/UDum)
        ElevNew = np.arctan(WDum/np.sqrt(UDum**2 + VDum**2))
#
#      UCorr = UDum
#      VCorr = VDum
#      WCorr = WDum
        UCorr = UDum
        VCorr = VDum
        WCorr = WDum

#      IF (ABS(AziNew) .LE. 0.698) THEN
#         DO WHILE (((ABS(AziNew-AziOld) .GT. 1./60) .OR.
#     &              (ABS(ElevNew-ElevOld) .GT. 1./60)) .AND.
#     &           (NITER .LT. ITMAX))
#            UCorr =  UDum/(UC1*(1.D0 - 0.5D0*
#     &              ((AziNew + (ElevNew/0.5236D0)*UC2)*
#     &              (1 - UC3*Abs(ElevNew/0.5236D0))
#     &              )**2        )
#     &                     )
#            VCorr =  VDum*(1 - VC1*Abs(ElevNew/0.5236D0))
#            WCorr =  WDum/(WC1*(1.D0 - 0.5D0*(ElevNew*WC2)**2))
#
#            AziOld = AziNew
#            ElevOld = ElevNew
#
#            AziNew = ATAN(Vcorr/UCorr)
#            ElevNew = ATAN(Wcorr/SQRT(UCorr**2 + VCorr**2))
#
#            NITER = NITER + 1
#         ENDDO
#      ENDIF
#
#      IF ((NITER .EQ. ITMAX) .OR. (ABS(AziNew) .GT. 0.698)) THEN
#         UError = .TRUE.
#         VError = .TRUE.
#         WError = .TRUE.
#      ELSE
#         UDum = UCorr
#         VDum = VCorr
#         WDum = WCorr
#      ENDIF

        if np.abs(AziNew) <= 0.698:
            while (((np.abs(AziNew-AziOld) > 1./60.) or
                    (np.abs(ElevNew-ElevOld) > 1./60.)) and
                   NITER .LT. ITMAX):
                UCorr = UDum/(UC1*(1. - 0.5 *
                                   ((AziNew + (ElevNew/0.5236)*UC2) *
                                    (1 - UC3*np.abs(ElevNew/0.5236))
                                    )**2)
                              )
                VCorr = VDum*(1 - VC1*np.abs(ElevNew/0.5236))
                WCorr = WDum/(WC1*(1. - 0.5*(ElevNew*WC2)**2))

                AziOld = AziNew
                ElevOld = ElevNew

                AziNew = np.arctan(VCorr/UCorr)
                ElevNew = np.arctan(WCorr/np.sqrt(UCorr**2 + VCorr**2))

                NITER = NITER + 1

        if (NITER == ITMAX) or (np.abs(AziNew) > 0.698):
            UCorr = np.nan
            VCorr = np.nan
            WCorr = np.nan

        corr.loc[i, 'ux'] = UCorr
        corr.loc[i, 'uy'] = VCorr
        corr.loc[i, 'uz'] = WCorr

    return corr


# -----------------------------------------------------------------------
#
def schotanus1(MeanQ, MeanTSon, Covin):
    """
    Compute Schotanus correction factors for sonic temperature and humidity effects.

    :param MeanQ: Mean specific humidity [kg/kg]
    :type MeanQ: float
    :param MeanTSon: Mean sonic temperature [K]
    :type MeanTSon: float
    :param Covin: Input covariance matrix
    :type Covin: pandas.DataFrame
    :return: Tuple of (correction_factors, temperature_factor)
    :rtype: tuple

    First step of Schotanus correction accounting for humidity effects
    on sonic temperature measurements. Sidewind correction applied separately.

    Name in ECPACK: EC_C_Schot1

    """

    #      DO i = 1,N
    #        Factor(i) = 1.D0 - 0.51D0*MeanQ
    #     &      -0.51D0*MeanTSon*Cov(i,SpecHum)/Cov(i,TSonic)
    #        IF (i.EQ.TSonic) Factor(i) = Factor(i)**2.D0
    #      ENDDO
    #
    #      TSonFact = 1.D0/(1.D0+0.51D0*MeanQ)
    factor = {}
    for v in ec.ecvar:
        if Covin.loc[v, 'ts'] != 0:
            factor[v] = (1. - 0.51*MeanQ -
                         0.51 *
                         MeanTSon*Covin.loc[v, 'q'] / Covin.loc[v, 'ts'])
        else:
            factor[v] = np.nan
        if v == 'ts':
            factor[v] = factor[v]**2
    TSonFact = 1./(1. + 0.51 * MeanQ)

    return factor, TSonFact

# -----------------------------------------------------------------------
#


def schotanus2(factor, TSonFact, MeanTSon, Covin):
    """
    Apply Schotanus correction factors to covariances and temperature.

    :param factor: Correction factors from schotanus1
    :type factor: dict
    :param TSonFact: Temperature correction factor
    :type TSonFact: float
    :param MeanTSon: Mean sonic temperature [K]
    :type MeanTSon: float
    :param Covin: Input covariance matrix
    :type Covin: pandas.DataFrame
    :return: Tuple of (corrected_covariances, corrected_temperature)
    :rtype: tuple

    Second step of Schotanus correction applying factors computed
    in schotanus1 to covariance matrix and mean temperature.

    Name in ECPACK: EC_C_Schot2
    """
    #      DO i = 1,N
    #         Cov(i,TSonic) = Factor(i)*Cov(i,TSonic)
    #         Cov(TSonic,i) = Cov(i,TSonic)
    #      ENDDO
    #
    #      MeanTSon = MeanTSon*TSonFact
    Covs = Covin.copy()
    for v in ec.ecvar:
        Covs.loc[v, 'ts'] = factor[v]*Covs.loc[v, 'ts']
        Covs.loc['ts', v] = Covs.loc[v, 'ts']

    MeanTSonCorr = MeanTSon*TSonFact

    return Covs, MeanTSonCorr


# ----------------------------------------------------------------
#
def schotanus3(temp, rhov, press):
    """
    Apply humidity correction to sonic temperature iteratively.

    :param temp: Uncorrected sonic temperature [K]
    :type temp: float
    :param rhov: Absolute humidity [kg/m³]
    :type rhov: float
    :param press: Atmospheric pressure [Pa]
    :type press: float
    :return: Humidity-corrected sonic temperature [K]
    :rtype: float

    Iterative solution for humidity-corrected temperature when
    thermocouple unavailable. Convergence criterion: 0.01% change.
    """
    #      IF (TEMP.NE.DUMMY) THEN
    #        IF (RHOV.NE.DUMMY.AND.Press.NE.DUMMY) THEN
    #          SPHUM = EC_Ph_Q(Temp, Rhov, Press)
    #          SPHUMNEW = 1.0D0
    #          NEWTEMP = Temp
    # C Does this converge ?
    #          DO WHILE (ABS((SPHUM - SPHUMNEW)/SPHUM) .GT. 0.0001)
    #            NEWTEMP = TEMP/(1.D0+0.51D0*SPHUM)
    #            SPHUMNEW = SPHUM
    #            SPHUM = EC_Ph_Q(NEWTEMP, Rhov, Press)
    #          ENDDO
    #        ELSE
    #          NEWTEMP = Temp
    #        ENDIF
    #      ELSE
    #        NEWTEMP=DUMMY
    #      ENDIF
    #      EC_C_Schot3 = NEWTEMP
    #      RETURN
    #      END
    if not (np.isnan(temp) or np.isnan(rhov) or np.isnan(press)):
        sphum = ec.spechum(rhov, temp, press)
        sphumnew = 1.
        newtemp = temp
        while np.abs((sphum - sphumnew) / sphum) > 0.0001:
            newtemp = temp/(1.+0.51*sphum)
            sphumnew = sphum
            sphum = ec.spechum(rhov, newtemp, press)
    else:
        newtemp = np.nan

    return newtemp

# ----------------------------------------------------------------
#


def tilt_matrix_pitch(Direction):
    """
    Generate rotation matrix for pitch angle correction.

    :param Direction: Pitch angle in degrees
    :type Direction: float
    :return: 3x3 pitch rotation matrix
    :rtype: pandas.DataFrame

    Rotation about y-axis (0,1,0). Positive angles rotate
    x-axis toward z-axis.

    Name in ECPACK: EC_C_T08
    """
    #
    #      SinTheta = SIN(PI*Direction/180.D0)
    #      CosTheta = COS(PI*Direction/180.D0)
    sintheta = np.sin(Direction*ec.deg2rad)
    costheta = np.cos(Direction*ec.deg2rad)
    #
    #      Pitch(1,1) = CosTheta
    #      Pitch(1,2) = 0.D0
    #      Pitch(1,3) = SinTheta
    #      Pitch(2,1) = 0.D0
    #      Pitch(2,2) = 1.D0
    #      Pitch(2,3) = 0.D0
    #      Pitch(3,1) = -SinTheta
    #      Pitch(3,2) = 0.D0
    #      Pitch(3,3) = CosTheta
    Pitch = pd.DataFrame([[costheta, 0., sintheta],
                          [0., 1.,       0.],
                          [-sintheta, 0., costheta]],
                         index=range(3), columns=range(3))
    return Pitch

# ----------------------------------------------------------------
#


def tilt_matrix_roll(Direction):
    """
    Generate rotation matrix for roll angle correction.

    :param Direction: Roll angle in degrees
    :type Direction: float
    :return: 3x3 roll rotation matrix
    :rtype: pandas.DataFrame

    Rotation about x-axis (1,0,0). Positive angles rotate
    y-axis toward z-axis.

    Name in ECPACK: EC_C_T10
    """

    #      SinRoll = SIN(PI*Direction/180.D0)
    #      CosRoll = COS(PI*Direction/180.D0)
    sinroll = np.sin(Direction*ec.deg2rad)
    cosroll = np.cos(Direction*ec.deg2rad)
    #
    #      Roll(1,1) = 1.D0
    #      Roll(1,2) = 0.D0
    #      Roll(1,3) = 0.D0
    #      Roll(2,1) = 0.D0
    #      Roll(2,2) = CosRoll
    #      Roll(2,3) = SinRoll
    #      Roll(3,1) = 0.D0
    #      Roll(3,2) = -SinRoll
    #      Roll(3,3) = CosRoll
    Roll = pd.DataFrame([[1.,      0.,      0.],
                         [0., cosroll, sinroll],
                         [0., -sinroll, cosroll]],
                        index=range(3), columns=range(3))
    return Roll


# ----------------------------------------------------------------
#
def tilt_matrix_yaw(Direction):
    """
    Generate rotation matrix for yaw angle correction.

    :param Direction: Yaw angle in degrees
    :type Direction: float
    :return: 3x3 yaw rotation matrix
    :rtype: pandas.DataFrame

    Rotation about z-axis (0,0,1). Positive angles rotate
    x-axis toward y-axis.

    Name in ECPACK: EC_C_T06
    """

    #      SinPhi = SIN(PI*Direction/180.D0)
    #      CosPhi = COS(PI*Direction/180.D0)
    singamma = np.sin(Direction*ec.deg2rad)
    cosgamma = np.cos(Direction*ec.deg2rad)
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
    Yaw = pd.DataFrame([[cosgamma, singamma, 0.],
                        [-singamma, cosgamma, 0.],
                        [0.,       0., 1.]],
                       index=range(3), columns=range(3))
    return Yaw

# ----------------------------------------------------------------
#


def tilt_mean_dir(MeanU, MeanV):
    """
    Calculate yaw angle to eliminate mean lateral wind component.

    :param MeanU: Mean u-velocity [m/s]
    :type MeanU: float
    :param MeanV: Mean v-velocity [m/s]
    :type MeanV: float
    :return: Yaw angle in degrees
    :rtype: float

    Rotates coordinate system so mean v-velocity = 0.
    Aligns x-axis with mean horizontal wind direction.

    Name in ECPACK: EC_C_T07
    """

    #      UHor = (MeanU**2+MeanV**2)**0.5D0
    #      SinPhi = MeanV/UHor
    #      CosPhi = MeanU/UHor
    #      Direction = 180.D0*ACOS(CosPhi)/PI
    #      IF (SinPhi.LT.0.D0) Direction = 360.D0-Direction
    UHor = np.sqrt(MeanU**2 + MeanV**2)
    SinPhi = MeanV/UHor
    CosPhi = MeanU/UHor
    Direction = np.arccos(CosPhi)/ec.deg2rad
    if SinPhi < 0.:
        Direction = 360. - Direction
    return Direction

# ----------------------------------------------------------------
#


def tilt_mean_roll(CovVV, CovVW, CovWW):
    """
    Calculate roll angle to eliminate v-w covariance.

    :param CovVV: v-velocity variance
    :type CovVV: float
    :param CovVW: v-w covariance
    :type CovVW: float
    :param CovWW: w-velocity variance
    :type CovWW: float
    :return: Roll angle in degrees
    :rtype: float

    Rotates coordinate system so Cov(v,w) = 0.
    Makes vertical and lateral wind fluctuations independent.

    Name in ECPACK: EC_C_T11
    """

    #
    #      Arg1 = 2*CovVW
    #      Arg2 = -CovVV+CovWW
    #      IF (Arg2.LT.0.D0) THEN
    #        RollAngl =  0.5D0*ATAN2(Arg1,-Arg2)
    #      ELSE
    #        RollAngl = -0.5D0*ATAN2(Arg1, Arg2)
    #      ENDIF
    #      Direction = 180.D0*RollAngl/Pi
    #
    Arg1 = 2*CovVW
    Arg2 = -CovVV+CovWW
    if Arg2 < 0.:
        RollAngl = 0.5 * np.atan2(Arg1, -Arg2)
    else:
        RollAngl = -0.5 * np.atan2(Arg1, Arg2)
    Direction = RollAngl/ec.deg2rad
    return Direction


# ----------------------------------------------------------------
#
def tilt_mean_vert(MeanU, MeanW):
    """
    Calculate pitch angle to eliminate mean vertical wind component.

    :param MeanU: Mean u-velocity [m/s]
    :type MeanU: float
    :param MeanW: Mean w-velocity [m/s]
    :type MeanW: float
    :return: Pitch angle in degrees
    :rtype: float

    Rotates coordinate system so mean w-velocity = 0.
    Aligns measurement plane with mean streamline.

    Name in ECPACK:  EC_C_T09
    """

    #      UTot = (MeanU**2+MeanW**2)**0.5D0
    #      SinTheta = MeanW/UTot
    #      Direction = 180.D0*ASIN(SinTheta)/PI
    UTot = np.sqrt(MeanU**2+MeanW**2)
    SinTheta = MeanW/UTot
    Direction = np.arcin(SinTheta)/ec.deg2rad

    return Direction

# ----------------------------------------------------------------
#


def tilt_rot_mean(Meani, Covi, Map):
    """
    Apply coordinate transformation to mean values and covariances.

    :param Meani: Input mean values
    :type Meani: pandas.Series
    :param Covi: Input covariance matrix
    :type Covi: pandas.DataFrame
    :param Map: 3x3 rotation matrix
    :type Map: pandas.DataFrame
    :return: Tuple of (rotated_means, rotated_covariances)
    :rtype: tuple

    Rotates velocity components and all covariances involving
    velocity. Used by all tilt correction procedures.

    Names in ECPACK: EC_C_T05, EC_C_T03, and EC_C_T04
    """

    #      CALL EC_C_T03(Mean,NMax,N,Cov,Speed,Stress,DumVecs,NNMax)
    #      DO i = U,W
    #        Speed(i) = Mean(i)
    #        DO j = U,W
    #          Stress(i,j) = Cov(i,j)
    #        ENDDO
    #        DO j = 4,N
    #          DumVecs(i,j) = Cov(i,j)
    #        ENDDO
    #      ENDDO
    xyz = ['ux', 'uy', 'uz']
    oth = [x for x in ec.ecvar if x not in xyz]
    Speed = pd.Series({x: Meani[x] for x in xyz})
    Stress = pd.DataFrame([[Covi.loc[i, j] for j in xyz] for i in xyz],
                          index=xyz, columns=xyz)
    DumVec = pd.DataFrame([[Covi.loc[i, j] for j in oth] for i in xyz],
                          index=xyz, columns=oth)
    #      CALL EC_M_MapVec(Map,Speed,Speed)
    Speed = Map.values.dot(Speed.values)
    #      CALL EC_M_MapMtx(Map,Stress,Stress)
    Stress = mapmtx(Map, Stress)
    #      DO j = 4,N
    #        CALL EC_M_MapVec(Map,DumVecs(1,j),DumVecs(1,j))
    for i in oth:
        DumVec.loc[:, i] = Map.dot(DumVec.loc[:, i].values)
    #      ENDDO
    #      CALL EC_C_T04(Speed,Stress,DumVecs,NNMax,Mean,NMax,N,Cov)
        #      DO i = U,W
        #        Mean(i) = Speed(i)
        #        DO j = U,W
        #          Cov(i,j) = Stress(i,j)
        #        ENDDO
        #        DO j = 4,N
        #          Cov(i,j) = DumVecs(i,j)
        #          Cov(j,i) = Cov(i,j)
        #        ENDDO
        #      ENDDO
    Meano = Meani.copy()
    for i, x in enumerate(xyz):
        Meano[x] = Speed[i]
    Covo = Covi.copy()
    for i in xyz:
        for j in xyz:
            Covo.loc[i, j] = Stress.loc[i, j]
        for j in oth:
            Covo.loc[i, j] = DumVec.loc[i, j]
            Covo.loc[j, i] = Covo.loc[i, j]
    #
    #      RETURN
    #      END
    return Meano, Covo

# ----------------------------------------------------------------

def tilt_rot_speed(Sample, Map):
    """
    Apply coordinate transformation to raw velocity samples.

    :param Sample: DataFrame with velocity measurements
    :type Sample: pandas.DataFrame
    :param Map: 3x3 rotation matrix
    :type Map: pandas.DataFrame
    :return: DataFrame with rotated velocities
    :rtype: pandas.DataFrame

    Applies rotation only to velocity components (ux, uy, uz).
    Other variables remain unchanged.
    """

    xyz = ['ux', 'uy', 'uz']
    Speed = Sample[xyz]
    Speed = pd.DataFrame.from_records(Speed.apply(Map.values.dot, axis=1))
    Rotated = Sample.copy()
    Rotated[xyz] = Speed

    return Rotated

# ----------------------------------------------------------------

def calcstruct(conf, sample, cindep):

    struct = pd.DataFrame(np.nan, index=ec.ecvar, columns=ec.ecvar)
    dstruct = pd.DataFrame(np.nan, index=ec.ecvar, columns=ec.ecvar)

    if ec.safe_len(sample) == 0:
        return struct, dstruct

    # Calculate the average of the length of the velocity (and not
    # the length of the average velocity!!!)

    #       UMean = 0.D0
    #       NOk = 0
    #       DO i=1,M
    #         IF ( (.NOT. Flag(U,i)).AND.
    #      &      ((.NOT. Flag(V,i)).AND.
    #      &       (.NOT. Flag(W,i)))) THEN
    #           NOk = NOk + 1
    #           UMean = UMean + Sample(U,i)**2D0+
    #      &                    Sample(V,i)**2D0+
    #      &                    Sample(W,i)**2D0
    #         ENDIF
    #       ENDDO
    #       IF (NOk.GT.0) UMean = UMean/DBLE(NOk)
    #       UMean = SQRT(UMean)

    lens = sample['ux']**2 + sample['uy']**2 + sample['uz']**2
    umean = np.sqrt(np.nanmean(lens))

    # Estimate how many samples delay one must go to let Taylor's
    # hypothesis of frozen turbulence give the correct spatial
    # separation R.
    # The discrete nature of sampling may call for strong rounding
    # off of the delay distance. The rounded off value for R is returned
    # to the calling routine.

    #      dR = UMean/Freq
    #      NSeparate = MAX(1,NINT(R/dR))
    #      R = R*NSeparate/(R/dR)

    freq = conf.get('FREQ','Par','float', na = np.nan)
    r =  conf.get('StructSep','Par','float', na = np.nan)
    dr = umean / freq
    nseparate = max(1.,np.rint(r/dr))

    # Calculate structure parameter

    #       Cxy = 0.D0
    #       NOk = 0
    #       DO i=1,(M-NSeparate)
    #         ok = (((.NOT.Flag(XIndex, i           )).AND.
    #      &         (.NOT.Flag(XIndex,(i+NSeparate))))
    #      &        .AND.
    #      &        ((.NOT.Flag(YIndex, i           )).AND.
    #      &         (.NOT.Flag(YIndex,(i+NSeparate)))))
    #         IF (ok) THEN
    #           NOk = NOk + 1
    #           Cxy = Cxy +
    #      &      (Sample(XIndex,i)-Sample(XIndex,(i+NSeparate)))*
    #      &      (Sample(YIndex,i)-Sample(YIndex,(i+NSeparate)))
    #         ENDIF
    #       ENDDO
    #       IF (NOk.GT.0) Cxy = Cxy/DBLE(Nok)
    #       Dum = Cxy ! For use in tolerance estimation loop
    #       IF (NSeparate.GT.0) Cxy = Cxy/R**TwoThird

    m = ec.safe_len(sample)


    for i, xcol in enumerate(sample.columns):
        for j, ycol in enumerate(sample.columns):

            # speed up: calculate only the combinations saved in output
            if (xcol, ycol) not in [
                ('ts', 'ts'),
                ('tcoup', 'tcoup'),
                ('q', 'q'),
                ('ts', 'q'),
                ('q', 'ts'),
                ('tcoup', 'q'),
                ('q', 'tcoup'),
            ]:
                continue

            cxy = ec.allnanok(
                np.nanmean,(
                    sample.loc[:(m - nseparate), xcol] *
                    sample.loc[nseparate:, xcol] +
                    sample.loc[:(m - nseparate), ycol] *
                    sample.loc[nseparate:, ycol]
                )
            )
            dum = cxy
            if nseparate > 0:
                cxy = cxy / (r ** (2./3.))

            # C
            # C Estimate tolerance of structure parameter
            # C
            #       dCxy = 0.D0
            #       IF (NSeparate.GT.0) THEN
            #         DO i=1,(M-NSeparate)
            #           ok = (((.NOT.Flag(XIndex, i           )).AND.
            #      &           (.NOT.Flag(XIndex,(i+NSeparate))))
            #      &          .AND.
            #      &          ((.NOT.Flag(YIndex, i           )).AND.
            #      &           (.NOT.Flag(YIndex,(i+NSeparate)))))
            #           IF (ok) THEN
            #             Increment =
            #      &        (Sample(XIndex,i)-Sample(XIndex,(i+NSeparate)))*
            #      &        (Sample(YIndex,i)-Sample(YIndex,(i+NSeparate)))
            #             dCxy = dCxy + (Increment - Dum)**2.D0
            #           ENDIF
            #         ENDDO
            #         IF (NOk.GT.0) dCxy = dCxy/DBLE(Nok)
            #         dCxy = SQRT(dCxy)/R**TwoThird ! Standard deviation
            #         dCxy = 2.D0*dCxy/SQRT(DBLE(CIndep(XIndex,YIndex))) ! Tolerance
            #       ENDIF

            dcxy = ec.allnanok(
                np.nanmean, (
                    ((sample.loc[:(m - nseparate), xcol] *
                      sample.loc[nseparate:, xcol] +
                      sample.loc[:(m - nseparate), ycol] *
                      sample.loc[nseparate:, ycol]
                      ) - dum) ** 2
                )
            )  / (r ** (2. / 3.)) # Standard deviation
            dcxy = 2. * dcxy / np.sqrt(cindep.loc[xcol, ycol])

            # C
            # C We use the number of independent samples found earlier in the estimation
            # C of the covariances
            # C
            #       IF (Nok .EQ. 0) THEN
            #          Cxy = DUMMY
            #          dCxy = DUMMY
            #       ENDIF
            #       RETURN
            #       END

            struct.loc[xcol, ycol] = cxy
            dstruct.loc[xcol, ycol] = dcxy

    return struct, dstruct, r, dr


# ----------------------------------------------------------------
#


def webb(Means, Covs, P, WhichTemp):
    """
    Calculate Webb correction velocity for density effects.

    :param Means: Mean values of all variables
    :type Means: pandas.Series
    :param Covs: Covariance matrix
    :type Covs: pandas.DataFrame
    :param P: Atmospheric pressure [Pa]
    :type P: float
    :param WhichTemp: Temperature variable to use
    :type WhichTemp: str
    :return: Webb correction velocity [m/s]
    :rtype: float

    Corrects scalar fluxes for air density fluctuations following
    :cite:`wpl_qjotrms80`. Accounts for temperature and
    humidity effects on air density.

    Name in ECPACK: EC_C_Webb
    """

    # C
    # C Ratio of mean densities of water vapour and dry air
    # C
    #      Sigma = Mean(Humidity)/EC_Ph_RhoDry(Mean(Humidity),
    #     &                                    Mean(WhichTemp),P)
    #      WebVel = (1.D0+Mu*Sigma)*Cov(W,WhichTemp)/Mean(WhichTemp) +
    #     &  Mu*Sigma*Cov(W,Humidity)/Mean(Humidity)
    #
    #      RETURN
    #      END

    Sigma = Means['h2o']/ec.rhodry(Means['h2o'], Means[WhichTemp], P)
    mu = ec.M_air/ec.M_vapour
    WebVel = ((1. + mu*Sigma)*Covs.loc['uz', WhichTemp]/Means[WhichTemp] +
              + mu*Sigma*Covs.loc['uz', 'h2o']/Means['h2o'])

    return WebVel

# ----------------------------------------------------------------
#

def flux_to_file(conf, intervals):
    """
    Write flux calculation results to formatted output file.

    :param conf: Configuration object with output settings
    :type conf: object
    :param intervals: DataFrame containing flux results
    :type intervals: pandas.DataFrame

    Creates comprehensive output file with fluxes, meteorology,
    quality measures, and covariances in EC-PACK format.
    Handles NaN values and unit conversions for output.
    """
    nanint = -99999

    def nanround(val):
        try:
            re = round(val)
        except ValueError:
            re = nanint
        return re
    #
    # header
    #
    datestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line0 = '# EC-PET version {:s} generated {:s}\n'.format(version, datestr)
    line1 = ''.join((
        '  DOY Hr Mn  ',
        '  DOY Hr Mn ',
        '#samples',
        '  #U     #V     #W  #TSon  #TCop  #RhoV     #q  #time   ',
        'Dir d(dir)   ',
        'Mean(vectorU)  dMean(vectorU)   ',
        'Mean(TSon)     dMean(TSon)      ',
        'Mean(TCop)     dMean(TCop)      ',
        'Mean(q)        dMean(q)         ',
        'sigma(TSon)    dsigma(TSon)     ',
        'sigma(TCop)    dsigma(TCop)     ',
        'sigma(q)       dsigma(q)        ',
        'sigma(u)       dsigma(u)        ',
        'sigma(v)       dsigma(v)        ',
        'sigma(w)       dsigma(w)        ',
        'cov(TSon,q)    dcov(TSon,q)     ',
        'cov(TCop,q)    dcov(TCop,q)     ',
        'cov(TSon,U)    dcov(TSon,U)     ',
        'cov(TCop,U)    dcov(TCop,U)     ',
        'cov(q,U)       dcov(q,U)        ',
        'H(Sonic)       Tol(HSonic)      ',
        'H(TCouple)     Tol(HTCouple     ',
        'LvECov         dLvECov          ',
        'LvEWebb        dLvEWebb         ',
        'LvE            dLvE             ',
        'UStar          dUStar           ',
        'Tau            dTau             ',
        'R(delay)       dR               ',
        'CTSon2         dCTSon2          ',
        'CTCop2         dCTCop2          ',
        'Cq2            dCq2             ',
        'CTSonq         dCTSonq          ',
        'CTCopq         dCTCopq          ',
        'MeanW          dMeanW           ',
        '#CO2           ',
        'MeanCO2        dMeanCO2         ',
        'MeanspecCO2    dMeanspecCO2     ',
        'stdCO2         dstdCO2          ',
        'stdspecCO2     dstdspecCO2      ',
        'FCO2Cov        dFCO2Cov         ',
        'FCO2Webb       dFCO2Webb        ',
        'FCO2           dFCO2            ',
        '#DeltaTemp     #PoorSignalLock  ',
        '#AmplHigh      #AmplLow         ',
        'Mean(U)        Mean(V)          ',
        'Mean(W)        Cov(U,U)         ',
        'Cov(U,V)       Cov(U,W)         ',
        'Cov(V,U)       Cov(V,V)         ',
        'Cov(V,W)       Cov(W,U)         ',
        'Cov(W,V)       Cov(W,W)         ',
        '\n'))
    line2 = ''.join((
        '-  -  -     ',
        '-  -  -    ',
        '[-]     ',
        '  [-]    [-]    [-] [-]    [-]    [-]       [-] [-]     ',
        '[degr] [degr]',
        ' [m/s]         [m/s]            ',
        '[K]            [K]              ',
        '[K]            [K]              ',
        '[kg/kg]        [kg/kg]          ',
        '[K]            [K]              ',
        '[K]            [K]              ',
        '[kg/kg]        [kg/kg]          ',
        '[m/s]          [m/s]            ',
        '[m/s]          [m/s]            ',
        '[m/s]          [m/s]            ',
        '[K*kg/kg]      [K*kg/kg]        ',
        '[K*kg/kg]      [K*kg/kg]        ',
        '[K*m/s]        [K*m/s]          ',
        '[K*m/s]        [K*m/s]          ',
        '[kg/kg*m/s]    [kg/kg*m/s]      ',
        '[W/m^2]        [W/m^2]          ',
        '[W/m^2]        [W/m^2]          ',
        '[W/m^2]        [W/m^2]          ',
        '[W/m^2]        [W/m^2]          ',
        '[W/m^2]        [W/m^2]          ',
        '[m/s]          [m/s]            ',
        '[N/m^2]        [N/m^2]          ',
        '[m]            [m]              ',
        '[K^2/m^2/3]    [K^2/m^2/3]      ',
        '[K^2/m^2/3]    [K^2/m^2/3]      ',
        '[1/m^2/3]      [1/m^2/3]        ',
        '[K*kg/kg/m^2/3] [K*kg/kg/m^2/3] ',
        '[K*kg/kg/m^2/3] [K*kg/kg/m^2/3] ',
        '[m/s]          [m/s]            ',
        '[-]            ',
        '[kg/m^3]       [kg/m^3]         ',
        '[kg/kg]        [kg/kg]          ',
        '[kg/m^3]       [kg/m^3]         ',
        '[kg/kg]        [kg/kg]          ',
        '[kg/m^2/s^1]   [kg/m^2/s^1]     ',
        '[kg/m^2/s^1]   [kg/m^2/s^1]     ',
        '[kg/m^2/s^1]   [kg/m^2/s^1]     ',
        '[-]            [-]              ',
        '[-]            [-]              ',
        '[m/s]          [m/s]            ',
        '[m/s]          [m/s]**2         ',
        '[m/s]**2       [m/s]**2         ',
        '[m/s]**2       [m/s]**2         ',
        '[m/s]**2       [m/s]**2         ',
        '[m/s]**2       [m/s]**2         ',
        '\n'))
    #
    # line format
    #
    # 55   FORMAT(2(I3,1X,2(I2,1X)),9(I6,1X),2(I5,1X),
    #     &        29(2(G15.5:,1X)),
    #     &        I13,  1X,
    #     &        7(2(G15.5:,1X)), 4(I15,1X), 12(G15.5:,1X))
    fmt = '{:5d} {:02d} {:02d} {:5d} {:02d} {:02d} '
    fmt += '{:6d} '*9
    fmt += '{:5g} '*2
    fmt += '{:15.5G} '*29*2
    fmt += '{:13g} '
    fmt += '{:15.5G} '*7*2
    fmt += '{:15g} '*4
    fmt += '{:15.5G} '*12
    fmt += '\n'
    #
    # get file name from config
    #
    fluxpath = conf.get('OutDir')
    fluxbase = conf.get('FluxName')
    fluxname = os.path.join(fluxpath, fluxbase)
    #
    fluxfile = io.open(fluxname, 'w+b')
    fluxfile.write(line0.encode())
    fluxfile.write(line1.encode())
    fluxfile.write(line2.encode())

    for i in intervals.to_dict(orient='records'):
        line = fmt.format(
            *[i['begin'].dayofyear+(i['begin'].year % 100)*1000, i['begin'].hour, i['begin'].minute,
              i['end'].dayofyear+(i['end'].year % 100)*1000, i['end'].hour, i['end'].minute] + [
                nanround(i['samples']), nanround(i['ok_ux']), nanround(
                    i['ok_uy']), nanround(i['ok_uz']),
                nanround(i['ok_ts']), nanround(i['ok_tcoup']), nanround(
                    i['ok_h2o']), nanround(i['ok_q']),
                # &       M,(Mok(i),i=1,7), Mok(TTime),
                nanround(i['samples']),
                # &       NINT(Phys(QPDirFrom)), NINT(dPhys(QPDirFrom)),
                nanround(i['dirfrom']), nanround(i['ddirfrom']),
                # &       Phys(QPVectWind), dPhys(QPVectWind),
                i['vectwind'], i['dvectwind'],
                # &       Mean(TSonic),dMean(TSonic),
                i['mean_ts'], i['dmean_ts'],
                # &       Mean(TCouple),dMean(TCouple),
                i['mean_tcoup'], i['dmean_tcoup'],
                # &       Mean(SpecHum),dMean(SpecHum),
                i['mean_q'], i['dmean_q'],
                # &       Std(Tsonic), dStd(TSonic),
                i['std_ts'], i['dstd_ts'],
                # &       Std(Tcouple), dStd(Tcouple),
                i['std_tcoup'], i['dstd_tcoup'],
                # &       Std(SpecHum), dStd(SpecHum),
                i['std_q'], i['dstd_q'],
                i['std_ux'], i['dstd_ux'],  # &       Std(U), dStd(U),
                i['std_uy'], i['dstd_uy'],  # &       Std(V), dStd(V),
                i['std_uz'], i['dstd_uz'],  # &       Std(W), dStd(W),
                # &       Cov(TSonic,SpecHum),dCov(TSonic,SpecHum),
                i['cov_ts_q'], i['dcov_ts_q'],
                # &       Cov(TCouple,SpecHum),dCov(TCouple,SpecHum),
                i['cov_tcoup_q'], i['dcov_tcoup_q'],
                # &       Cov(TSonic,U),dCov(TSonic,U),
                i['cov_ts_ux'], i['dcov_ts_ux'],
                # &       Cov(TCouple,U),dCov(TCouple,U),
                i['cov_tcoup_ux'], i['dcov_tcoup_ux'],
                # &       Cov(SpecHum,U),dCov(SpecHum,U),
                i['cov_q_ux'], i['cov_q_ux'],
                # &       Phys(QPHSonic),dPhys(QPHSonic),
                i['hson'], i['dhson'],
                i['hcoup'], i['dhcoup'],  # &       Phys(QPHTc),dPhys(QPHTc),
                i['ecov'], i['decov'],  # &       Phys(QPLvE),dPhys(QPLvE),
                # &       Phys(QPLvEWebb),dPhys(QPLvEWebb),
                i['ewebb'], i['dewebb'],
                # &       Phys(QPSumLvE), dPhys(QPSumLvE),
                i['esum'], i['desum'],
                # &       Phys(QPUstar),dPhys(QPUstar),
                i['ustar'], i['dustar'],
                i['tausum'], i['dtausum'],  # &       Phys(QPTau),dPhys(QPTau),
                i['r'], i['dr'],  # &       R,dR,
                # &       Struct(TSonic,TSonic), dStruct(TSonic,TSonic),
                i["struct_ts_ts"], i["dstruct_ts_ts"],
                # &       Struct(TCouple,TCouple), dStruct(TCouple,TCouple),
                i["struct_tcoup_tcoup"], i["dstruct_tcoup_tcoup"],
                # &       Struct(SpecHum,SpecHum), dStruct(SpecHum,SpecHum),
                i["struct_q_q"], i["dstruct_q_q"],
                # &       Struct(TSonic,SpecHum), dStruct(TSonic,SpecHum),
                i["struct_ts_q"], i["dstruct_ts_q"],
                # &       Struct(TCouple,SpecHum), dStruct(TCouple,SpecHum),
                i["struct_tcoup_q"], i["dstruct_tcoup_q"],
                # &       Phys(QPMeanW),dPhys(QPMeanW),
                i['meanw'], i['dmeanw'],
                i['ok_qco2'],  # &       Mok(CO2),
                # &       Mean(CO2), dMean(CO2),
                i['mean_co2'], i['dmean_co2'],
                # &       Mean(specCO2), dMean(specCO2),
                i['mean_qco2'], i['dmean_qco2'],
                i['std_co2'], i['dstd_co2'],  # &       Std(CO2), dStd(CO2),
                # &       Std(specCO2), dStd(specCO2),
                i['std_qco2'], i['dstd_qco2'],
                i['fco2'], i['dfco2'],  # &       Phys(QPFCO2),dPhys(QPFCO2),
                # &       Phys(QPFCO2Webb),dPhys(QPFCO2Webb),
                i['fco2webb'], i['dfco2webb'],
                # &       Phys(QPSumFCO2), dPhys(QPSumFCO2),
                i['fco2sum'], i['dfco2sum'],
                -1, -1,  # &       DiagFlag(QDDelta), DiagFlag(QDLock),
                -1, -1,  # &       DiagFlag(QDHigh), DiagFlag(QDLow),
                i['mean_ux'], i['mean_uy'],
                i['mean_uz'], i['cov_ux_ux'],
                i['cov_ux_uy'], i['cov_ux_uz'],
                i['cov_uy_ux'], i['cov_uy_uy'],
                i['cov_uy_uz'], i['cov_uz_ux'],
                i['cov_uz_uy'], i['cov_uz_uz']
            ]).replace('nan', 'NaN').replace('{:6d}'.format(nanint), 'NaN')
        fluxfile.write(line.encode())


# ----------------------------------------------------------------
# --- driving routines follow here
# ----------------------------------------------------------------

# ----------------------------------------------------------------
#
def cmain(conf, interval, Means, TolMean, Covs, TolCov):
    """
    Apply all flux corrections with optional iteration for interdependence.

    :param conf: Configuration object with correction settings
    :type conf: object
    :param interval: Single interval data record
    :type interval: dict
    :param Means: Mean values of calibrated signals
    :type Means: pandas.Series
    :param TolMean: Tolerances in mean values
    :type TolMean: pandas.Series
    :param Covs: Covariance matrix
    :type Covs: pandas.DataFrame
    :param TolCov: Covariance tolerances
    :type TolCov: pandas.DataFrame
    :return: Tuple of corrected means, tolerances, covariances, and Webb velocity
    :rtype: tuple

    Orchestrates Schotanus, oxygen, frequency response, and Webb corrections.
    Supports iteration to account for interdependence following
    :cite`ofv_bm07`

    Name in ECPACK: EC_C_MAIN
    """

    logger.debug('doing corrections')

    DoIterate = conf.get('DoIterate', group='Par', kind='bool')
    MaxIter = conf.get('MaxIter', group='Par', kind='int')
    qcsonic = conf.get('DoSonic', group='Par', kind='bool')
    qco2 = conf.get('DoO2', group='Par', kind='bool')
    qcfreq = conf.get('DoFreq', group='Par', kind='bool')
    qcwebb = conf.get('DoWebb', group='Par', kind='bool')

    # C
    # C Now we need to know if and which temperature we have. Default to
    # C Sonic temperature
    # C
    #      IF (HAVE_CAL(TSonic)) THEN
    #         WhichTemp = Tsonic
    #      ELSE IF (Have_CAL(TCouple)) THEN
    #         WhichTemp = TCouple
    #      ELSE
    #         WhichTemp = -1
    #      ENDIF
    if np.isfinite(Means['ts']):
        WhichTemp = 'ts'
    elif np.isfinite(Means['tcoup']):
        WhichTemp = 'tcoup'
    else:
        WhichTemp = None
    logger.debug('selected Temperature: '+str(WhichTemp))
    # C
    # C The following correction are optionally iterated to
    # C account for their interdependence
    # C Oncley et al.(2007) 'The Energy Balance Experiment EBEX-2000.
    # C Part I: overview and energy balance ' Boundary-Layer Meteorology,
    # C 123, 1-28 10.1007/s10546-007-9161-1
    # C
    #      IF (DoIterate) then
    #        NIter=MaxIter
    #      ELSE
    #        NIter=1
    #      ENDIF
    #      IIter=1
    #      ICov=Cov   ! save initial covariance matrix and Temperature
    #      ITso=Mean(TSonic)
    #      DO WHILE (IIter.eq.1.or.
    #     &         (IIter.le.NIter.and.IterRelChange.gt.IterMinChange))
    #        TCov=Cov ! store covariance/Temperature matrix after last iteration
    #        TTso=Mean(TSonic)
    #        Cov=ICov ! apply corrections to initial covariance matrix/Temperature
    #        Mean(TSonic)=ITso
    IterMinChange = 1.E-4
    if DoIterate:
        NIter = MaxIter
    else:
        NIter = 1
    IIter = 1
    IterRelChange = 1.
    # ! save initial covariance matrix and Temperature
    ICov = Covs.copy()
    ITso = Means['ts']
    BCov = None
    while IIter <= NIter and IterRelChange > IterMinChange:
        #
        logger.debug('iteration #{:d}'.format(IIter))
        # store covariance/Temperature matrix after last iteration
        TCov = Covs.copy()
        TTso = Means['ts']
        # apply corrections to initial covariance matrix/Temperature
        Covs = ICov
        Means['ts'] = ITso
        # C
        # C Correct sonic temperature and all covariances with sonic temperature
        # C for humidity. This is half the Schotanus-correction. Side-wind
        # C correction is done at calibration time directly after reading raw data.
        # C
        #        IF (DoCorr(QCSonic)) THEN
        #         IF (Mean(SpecHum).NE.DUMMY) THEN
        #           CALL EC_C_Schot1(Mean(SpecHum),TTso,NMax,N,TCov,
        #     &      SonFactr,TSonFact)
        #           CALL EC_C_Schot2(SonFactr,TSonFact,Mean(TSonic),NMax,N,Cov)
        #           CALL EC_G_Reset(Have_Cal, Mean, TolMean, Cov, TolCov,
        #     &                    DumIndep, DumCindep)
        if qcsonic:
            if np.isfinite(Means['q']):
                logger.debug('applying schotanus part 1')
                factor, TSonFact = schotanus1(Means['q'], TTso, Covs)
                Covs, Means[WhichTemp] = schotanus2(
                    factor, TSonFact, Means['ts'], Covs)

        # C
        # C
        # C Perform correction for oxygen-sensitivity of hygrometer
        # C
        # C
        #        IF (DoCorr(QCO2)) THEN
        #          IF (WhichTemp .GT. 0) THEN
        #            CALL EC_C_Oxygen1(Mean(WhichTemp),NMax,N,TCov,P,
        #     &        CalHyg(QQType),WhichTemp,O2Factor)
        #            CALL EC_C_Oxygen2(O2Factor,NMax,N,Cov)
        #            CALL EC_G_Reset(Have_Cal, Mean, TolMean, Cov, TolCov,
        #     &                    DumIndep, DumCindep)
        #
        #          ELSE
        #              WRITE(*,*) 'ERROR: can not perform O2 correction without ',
        #     &                   'a temperature'
        if qco2:
            if WhichTemp is not None:
                HygType = ec.code_ap(
                    conf.get('QQType', group='HygCal', kind='int'))
                Covs = oxygen(Means[WhichTemp], Covs,
                              interval['s_pp'], HygType, WhichTemp)
        # C
        # C
        # C Perform correction for poor frequency response and large paths
        # C
        # C
        #
        # C
        # C Constants for integration routine in correction frequency response
        # C
        #        NSTA   = -5.0D0    ! [?] start frequency numerical integration
        #        NEND   = LOG10(0.5*ExpVar(QEFreq)) ! [?] end frequency numerical integration
        #        NumINT = 39        ! [1] number of intervals
        #        TAUV   = 0.0D0     ! [?] Low pass filter time constant
        #        TauD   = 0.0D0     ! [?] interval length for running mean
        #
        #        IF (DoCorr(QCFreq)) THEN
        #          IF (WhichTemp .GT. 0) THEN
        #            CALL EC_C_F01(Mean,TCov,NMax,N,WhichTemp,
        #     &           NSta,NEnd,NumInt,ExpVar(QEFreq),TauD,TauV,
        #     &           CalSonic,CalTherm,CalHyg,
        #     &           CalCO2, FrCor)
        #            CALL EC_C_F02(FrCor,NMax,N,ExpVar(QELLimit),
        #     &                    ExpVar(QEULimit),Cov,TolCov)
        #
        #          ELSE
        #              WRITE(*,*) 'ERROR: can not perform freq. response ',
        #     &                   ' correction without a temperature'
        #          ENDIF
        #        ENDIF

        if qcfreq:
            if WhichTemp is not None:
                logger.debug('applying frequency correction')
                Covs, TolCov = freqcorr(conf, Means, Covs, TolCov, WhichTemp)
            else:
                logger.info('can not perform freq. response ' +
                              ' correction without a temperature')

        # C
        # C       Store matrix values without iteration (in case of no convergence)
        # C
        #        IF (IITER.EQ.1) THEN
        #          BCov=Cov
        #        ENDIF
        #        IterRelChange=maxval(abs(Cov-TCov)/TCov)
        #        IITER=IITER+1
        #      ENDDO

        if IIter == 1:
            BCov = Covs.copy()
        IterRelChange = ec.allnanok(np.nanmax, np.abs(Covs-TCov)/TCov)
        IIter = IIter+1

    # C
    # C     in case of no convergence: restore matrix values without iteration
    # C
    #      IF (DoIterate) THEN
    #        Write (*,*) '[iterate]',iiter,' iterations'
    #      ENDIF
    # !      IF (DoIterate.AND.IITER.gt.NITER) THEN
    # !        Write (*,*) '[iterate] **** iteration didnt converge !'
    # !          Cov=BCov
    # !      ENDIF
    if DoIterate:
        logger.debug('done {:d} iterations'.format(IIter))
    if DoIterate and IIter > NIter:
        logger.warning('[iterate] **** iteration didnt converge !')
        Covs = BCov
    # C
    # C
    # C Calculate mean vertical velocity according to Webb
    # C
    # C
    #      WebVel = DUMMY
    #      IF (DoCorr(QCWebb)) THEN
    #         IF (WhichTemp .GT. 0) THEN
    #           CALL EC_C_Webb(Mean,NMax,Cov,P, WhichTemp, WebVel)
    #           CALL EC_G_Reset(Have_Cal, Mean, TolMean, Cov, TolCov,
    #     &                  DumIndep, DumCindep)
    #           IF (QWebb) THEN
    #               WRITE(OutF,*) 'Webb-velocity (vertical) = ',WebVel,' m/s'
    #             CALL EC_G_ShwHead(OutF, 'After addition of Webb-term: ')
    #             CALL EC_G_Show(OutF,Mean,TolMean,Cov,TolCov,
    #     &              NMax,N)
    #           ENDIF
    #         ELSE
    #           WRITE(*,*) 'ERROR: can not perform Webb correction',
    #     &                 ' without a temperature'
    #         ENDIF
    #      ENDIF

    if qcwebb:
        if WhichTemp is not None:
            logger.debug('applying Webb correction')
            WebVel = webb(Means, Covs, interval['s_pp'], WhichTemp)
        else:
            WebVel = np.nan
            logger.info('can not perform Webb correction' +
                          ' without a temperature')
    else:
        WebVel = np.nan

    #
    #      RETURN
    #      END
    #
    return Means, TolMean, Covs, TolCov, WebVel
    # C     SonFactr: [REAL*8(NMax)] (out)
    # C               Correction factor due to Schotanus correction for
    # C               covariance of sonic temperature with each calibrated
    # C               signal.
    # C     O2Factor: [REAL*8(NMax)] (out)
    # C               Correction factor due to oxygen correction for
    # C               covariance of humidity with each calibrated
    # C     FrCor   : [REAL*8(NMax,NMax)] (out)
    # C               Correction factors for covariances for frequency
    # C               response
    # C     WebVel  : [REAL*8] (out)
    # C               Webb velocity


# ----------------------------------------------------------------
#
def process_flux_interval(args):
    """
    Process single averaging interval for flux calculations.

    :param args: Tuple of (configuration, interval_data) for multiprocessing
    :type args: tuple
    :return: Dictionary with processed interval results
    :rtype: dict

    Complete flux processing workflow including data retrieval,
    calibration, corrections, tilt correction, and flux calculation.
    Designed for parallel execution.

    """
    # Ensure custom logging is available in worker process
    from . import eclogger
    eclogger.ensure_logging_setup()

    Apf = None
    PreYaw = PrePitch = None
    DirPitch = DirRoll = None
    PreRoll = None
    #
    # unpack arguments
    conf, interval = args
    #
    # print interval
    logger.info('process {:s} -- {:s}'.format(
        str(interval['begin']), str(interval['end'])))
    #
    # get config values
    qcdetrend = conf.get('DoDetrend', group='Par', kind='bool')
    qctilt = conf.get('DoTilt', group='Par', kind='bool')
    qcyaw = conf.get('DoYaw', group='Par', kind='bool')
    qcpitch = conf.get('DoPitch', group='Par', kind='bool')
    qcroll = conf.get('DoRoll', group='Par', kind='bool')
    qcpf = conf.get('DoPF', group='Par', kind='bool')
    qcmean = conf.get('DoCrMean', group='Par', kind='bool')
    qcerrfisi = conf.get('DoErrFiSi', group='Par', kind='bool')
    qcstruct = conf.get('DoStruct', group='Par', kind='bool')
    #
    # get the data
    logger.debug('getting raw data')
    rawsampl = ecdb.retrieve_df('uncal', 'fast',
                                tbegin=interval['begin'],
                                tend=interval['end'])
    sample = ecdb.retrieve_df('calib', 'fast',
                              tbegin=interval['begin'],
                              tend=interval['end'])
    logger.debug('got {:d} data'.format(len(sample.index)))
    #
    # rename columns to ec.var names
    logger.insane('got uncalibrated columns :'+', '.join(sample.columns))
    logger.insane('got   calibrated columns :'+', '.join(sample.columns))
    for x in ec.var:
        if x not in rawsampl.columns:
            rawsampl[x] = np.nan
            logger.insane(
                'add empty column to uncalibrated data: {:s}'.format(x))
        if x not in sample.columns:
            sample[x] = np.nan
            logger.insane(
                'add empty column to   calibrated data: {:s}'.format(x))

    #
    # If planar fit tilt correction,
    # try to get rotation matrix
    #
    #      IF (DoCorr(QCPF)) THEN
    if qcpf:
        logger.debug('get planar fit parameters')
        # C Undo Yaw angle of planar fit untilt matrix
        #           CosGamma = COS(GAMMA*pi/180)
        #           SinGamma = SIN(GAMMA*pi/180)
        #           Yaw(1,1) = CosGamma
        #           Yaw(1,2) = SinGamma
        #           Yaw(1,3) = 0.D0
        #           Yaw(2,1) = -SinGamma
        #           Yaw(2,2) = CosGamma
        #           Yaw(2,3) = 0.D0
        #           Yaw(3,1) = 0.D0
        #           Yaw(3,2) = 0.D0
        #           Yaw(3,3) = 1.D0
        #         CALL EC_M_InvM(Yaw,InvYaw)
        #         CALL EC_M_MMul(InvYaw, Apf, Apf)
        Apf = pd.DataFrame(
            [[interval['apf_{:0d}{:0d}'.format(i+1, j+1)]
              for j in range(3)] for i in range(3)])
        CosGamma = np.cos(interval['gamma']*ec.deg2rad)
        SinGamma = np.sin(interval['gamma']*ec.deg2rad)
        Yaw = pd.DataFrame([[CosGamma, SinGamma, 0.],
                            [-SinGamma, CosGamma, 0.],
                            [0.,       0., 1.]])

        try:
            InvYaw = pd.DataFrame(np.linalg.pinv(
                Yaw.values), Yaw.columns, Yaw.index)
        except np.linalg.LinAlgError:
            logger.warning('planar fit inversion did not converge')
            InvYaw = pd.DataFrame(np.full((3, 3), np.nan))
        Apf = InvYaw.dot(Apf)
        M = len(sample.index)
    else:
        #  ELSE
        #    M = 0
        M = 0
        Apf = pd.DataFrame(np.identity(3))

    # --start-- EC_G_Main --start-- the original code calls the main
    #                               subroutine which is inlined after here

    # C
    # C Check whether we have the needed calibration info
    # C
    #  data are already calibrated
    #
    if any(np.isfinite(sample['ts'])):
        whichtemp = 'ts'
    elif any(np.isfinite(sample['tcoup'])):
        whichtemp = 'tcoup'
    else:
        # FIXME     whichtemp = None
        whichtemp = 'ts'

    logger.debug('chosen temperature: '+str(whichtemp))

    # C
    # C If thermocouple too bad, or absent
    # C
    #         BadTc = (NTcOut.GE.(M/2))
    #      ELSE
    #         BadTc = .TRUE.
    #      ENDIF
    #      IF (BadTc) THEN
    #        DO i=1,M
    #          CALL Calibr(RawSampl(1,i),Channels,P,CorMean,
    #     &      CalSonic,CalTherm,CalHyg,CalCO2,
    #     &      BadTc,Sample(1,i),N,Flag(1,i),
    #     &      Have_Uncal, FirstDay, i)
    #        ENDDO
    #      ENDIF
    badtc = (sum(pd.isnull(sample['tcoup'])) > len(sample.index)/2)
    if badtc:
        # calibrate again, with badtc=True
        sample = calibrat(
            conf, rawsampl, interval['s_pp'], badtc=True, tref=interval['s_tc'])
        whichtemp = 'ts'

    # C
    # C Calibrate the raw samples for the second time, now correcting mean
    # C quantities of drift-sensitive apparatus using slow signals.
    # C
    #      IF (DoCorr(QCMean)) THEN
    if qcmean:
        logger.debug('replacing means by slow references')
        # C
        # C Find the shift/drift in humidity of the krypton hygrometer
        # C
        #        CALL EC_M_Averag(Sample,NMax,N,MMax,M,Flag,
        #     &    Mean,TolMean,Cov,TolCov,MIndep,CIndep,Mok,Cok)
        # C mark variables as not present, if they conatain only invalid values
        #        DO j=1,N
        #          IF (MOK(j).EQ.0) THEN
        #            HAVE_CAL(j)=.FALSE.
        #          ENDIF
        #        ENDDO
        #        CALL EC_G_Reset(Have_cal, Mean, TolMean, Cov, TolCov,
        #     &                MIndep,  CIndep)
        #        IF (.NOT. Have_Cal(Humidity)) THEN
        #            Mean(Humidity) = Psychro
        #            MEAN(SpecHum) = EC_Ph_Q(Mean(Humidity), Mean(WhichTemp), P)
        #        ENDIF
        #        IF (DoPrint) THEN
        #           CALL EC_M_MinMax(Sample, NMax, N, MMax, M, Flag, MINS, MAXS)
        #           CALL EC_G_ShwMinMax(OutF, N, Mins, Maxs)
        #        ENDIF
        #
        #        CorMean(Humidity) = Psychro - Mean(Humidity)
        #        IF (DoPrint.AND.PCal) THEN
        #          WRITE(OutF,*)
        #          WRITE(OutF,*) 'Added to humidity : ',
        #     &       (Psychro - Mean(Humidity)),' [kg m^{-3}]'
        #          WRITE(OutF,*)
        #        ENDIF
        #
        #        DO i=1,M
        #          CALL Calibr(RawSampl(1,i),Channels,P,CorMean,
        #     &     CalSonic,CalTherm,CalHyg,CalCO2,
        #     &      BadTc,Sample(1,i),N,Flag(1,i),
        #     &      Have_Uncal, FirstDay, i)
        #        ENDDO
        #      ENDIF
        logger.debug('calculate means')
        means, tolmean, covs, tolcov, mindep, cindep = averag(sample)
        cormean_humidity = interval['s_rhov'] - means['h2o']  # kg m^{-3}
        if np.isfinite(cormean_humidity):
            logger.debug('replacing mean humidity')
            rawsampl['h2o'] = rawsampl['h2o'] + cormean_humidity
            # repeat calibration to adjust humidity-dependent corrections
            logger.debug('re-calibrate raw values')
            sample = calibrat(
                conf, rawsampl, interval['s_pp'], tref=interval['s_tc'])

    # C
    # C
    # C Estimate mean values, covariances and tolerances of both
    # C
    # C
    #      CALL EC_M_Averag(Sample,NMax,N,MMax,M,Flag,
    #     &                       Mean,TolMean,Cov,TolCov,MIndep,
    #     &                 CIndep,Mok,Cok)
    # C mark variables as not present, if they contain only invalid values
    #      DO j=1,N
    #        IF (MOK(j).EQ.0) THEN
    #          HAVE_CAL(j)=.FALSE.
    #        ENDIF
    #      ENDDO
    #      CALL EC_G_Reset(Have_cal, Mean, TolMean, Cov, TolCov,
    #     &                MIndep,  CIndep)
    # C
    # C replace Mean(Humidity) by Psychro only if user requests DoCrMean = T
    # C
    #      IF (DoCorr(QCMean).AND..NOT. Have_Cal(Humidity)) THEN
    #        Mean(Humidity) = Psychro
    #        MEAN(SpecHum) = EC_Ph_Q(Mean(Humidity), Mean(WhichTemp), P)
    #      ENDIF
    logger.debug('(re-)calculate means')
    means, tolmean, covs, tolcov, mindep, cindep = averag(sample)
    if not np.isfinite(means['h2o']):
        means['h2o'] = interval['s_rhov']
        means['q'] = ec.spechum(
            interval['s_rhov'], means[whichtemp], interval['s_pp'])

    #
    # C
    # C
    # C Subtract a linear trend from all quantities
    # C and / or
    # C do block detrending
    # C
    # C
    # ! QCPBlock = 1 hardcoded
    #      IF (DoCorr(QCDetrend) .OR. DoCorr(QCBlock)) THEN
    # ! always true
    #        IF (DoCorr(QCDetrend)) THEN
    #           CALL EC_M_Detren(Sample,NMax,N,MMAx,M,Mean,Cov,RC)
    #        ENDIF
    #        IF (DoCorr(QCBlock)) THEN
    # ! always true
    #           NBlock = INT(CorrPar(QCPBlock))
    # ! always 1
    #           CALL EC_M_BlockDet(Sample,NMax,N,MMAx,M,Mean,NBlock, Flag)
    # ! always sample - mean + mean -> does nothing
    #        ENDIF
    if qcdetrend:
        logger.debug('detrend data')
        sample = detrend(sample)
        # C
        # C
        # C Estimate mean values, covariances and tolerances of both
        # C for the detrended dataset
        # C
        # C
        #        CALL EC_M_Averag(Sample,NMax,N,MMax,M,Flag,
        #     &                         Mean,TolMean,Cov,TolCov,
        #     &                   MIndep,CIndep,Mok,Cok)
        # C replace Mean(Humidity) by Psychro only if user requests DoCrMean = T
        #        IF (DoCorr(QCMean).AND..NOT. Have_cal(Humidity)) THEN
        #          Mean(Humidity) = Psychro
        #          MEAN(SpecHum) = EC_Ph_Q(Mean(Humidity), Mean(WhichTemp), P)
        #        ENDIF
        #        CALL EC_M_MinMax(Sample, NMax, N, MMax, M, Flag, MINS, MAXS)
        #  #
        #      ENDIF
        logger.debug('re-calculate means')
        means, tolmean, covs, tolcov, mindep, cindep = averag(sample)
        if qcmean and not np.isfinite(means['h2o']):
            means['h2o'] = interval['s_rhov']
            means['q'] = ec.spechum(
                interval['s_rhov'], means[whichtemp], interval['s_pp'])
    #
    # C
    # C Get the mean W before we do tilt correction
    # C
    #      QPhys(QPMEANW) = MEAN(W)
    #      dQPhys(QPMEANW) = TolMean(W)
    qpmeanw = means['uz']
    dqpmeanw = tolmean['uz']
    # C
    # C Correct mean values and covariances for all thinkable effects, first
    # C time only to get run-based tilt correction (if needed). But
    # C before all that, the planar fit untilting needs to be applied.
    # C
    # C Do Planar fit tilt correction (only) here
    # C
    qcpf = conf.get('DoPF', group='Par', kind='bool')
    if qcpf:
        logger.debug('apply planar fit')
        #      IF (DoCorr(QCPF)) THEN
        # C
        # C Tilt ALL samples
        #        DO i=1,M
        #          Speed(1) = Sample(U,i)
        #          Speed(2) = Sample(V,i)
        #          Speed(3) = Sample(W,i)
        # C
        # C         Speed(3) = Speed3) - WBias
        #
        #          CALL EC_M_MapVec(Apf,Speed,Dumout)
        # C
        # C Feed planarfit rotated sample back into Sample array
        # C
        #          Sample(U,i) = Dumout(1)
        #          Sample(V,i) = Dumout(2)
        #          Sample(W,i) = Dumout(3)
        #        ENDDO
        #      ENDIF
        speed = sample[['ux', 'uy', 'uz']]
        # C SYNOPSIS
        # C     CALL EC_M_MapVec(a,x,y)
        # C FUNCTION
        # C     Calculates the image of "x" under the map "a"; y(i) = a(ij)x(j)
        dumout = pd.DataFrame.from_records(speed.apply(Apf.values.dot, axis=1))
        sample[['ux', 'uy', 'uz']] = dumout
#    for i,x in enumerate(['ux','uy','uz']):
#        sample[x] = [dumout[x][i] for x in dumout]
        #      CALL EC_M_Averag(Sample,NMax,N,MMax,M,Flag,
        #     &                       Mean,TolMean,Cov,TolCov,
        #     &                 MIndep,CIndep,Mok,Cok)
        # C mark variables as not present, if they conatain only invalid values
        #      DO j=1,N
        #        IF (MOK(j).EQ.0) THEN
        #          HAVE_CAL(j)=.FALSE.
        #        ENDIF
        #      ENDDO
        #      CALL EC_G_Reset(Have_cal, Mean, TolMean, Cov, TolCov,
        #     &                MIndep,  CIndep)
        # C replace Mean(Humidity) by Psychro only if user requests DoCrMean = T
        #      IF (DoCorr(QCMean).AND..NOT. Have_cal(Humidity)) THEN
        #          Mean(Humidity) = Psychro
        #          MEAN(SpecHum) = EC_Ph_Q(Mean(Humidity), Mean(WhichTemp), P)
        #      ENDIF
        logger.debug('re-calculate means')
        means, tolmean, covs, tolcov, mindep, cindep = averag(sample)
        if qcmean and not np.isfinite(means['h2o']):
            means['h2o'] = interval['s_rhov']
            means['q'] = ec.spechum(
                interval['s_rhov'], means[whichtemp], interval['s_pp'])

    #
    # C If 'classic' run-based tilt corrections are not done,
    # C the first call to EC_C_Main is redundant and skipped), else
    # C this run is only done to establish the 'classic' rotation
    # C angles.
    # C disable iteration to save time
    #      AnyTilt = ((DoCorr(QCTilt).OR.DoCorr(QCYaw)) .OR.
    #     &           (DoCorr(QCPitch).OR.DoCorr(QCRoll)))
    #      IF (AnyTilt) THen
    #        CALL EC_C_Main(OutF,
    #     &          DoPrint,
    #     &    Mean,NMax,N,TolMean,
    #     &          Cov,TolCov,
    #     &    DoCorr, PCorr, ExpVar,
    #     &    DirYaw,
    #     &          DirPitch,
    #     &          DirRoll,
    #     &          SonFactr,
    #     &          O2Factor,
    #     &          CalSonic,CalTherm,CalHyg,
    #     &    CalCO2, FrCor,
    #     &          WebVel, P,Have_cal,.false.,Maxiter)
    #        CALL EC_G_Reset(Have_cal, Mean, TolMean, Cov, TolCov,
    #     &                MIndep,  CIndep)
    #      ENDIF
    AnyTilt = (qctilt or qcyaw or qcpitch or qcroll)
    diryaw = 0
    if AnyTilt:
        logger.debug('apply rotation')

        # begin ==== EC_C_Main ====

#    speed=sample[['ux','uy','uz']]
        #      IF (DoCorr(QCTilt)) THEN
        #        CALL EC_C_T06(ExpVar(QEPreYaw),Yaw)
        #        CALL EC_C_T05(Mean,NMax,N,Cov,Yaw)
        #        CALL EC_C_T08(ExpVar(QEPrePitch),Pitch)
        #        CALL EC_C_T05(Mean,NMax,N,Cov,Pitch)
        #        CALL EC_C_T10(ExpVar(QEPreRoll),Roll)
        #        CALL EC_C_T05(Mean,NMax,N,Cov,Roll)
        if qctilt:
            logger.debug('apply pre-selected rotation')

            PreYaw = conf.get('PreYaw', group='Par', kind='float')
            Yaw = tilt_matrix_yaw(PreYaw)
            Means, covs = tilt_rot_mean(means, covs, Yaw)

            PrePitch = conf.get('PrePitch', group='Par', kind='float')
            Pitch = tilt_matrix_pitch(PrePitch)
            means, covs = tilt_rot_mean(means, covs, Pitch)

            PreRoll = conf.get('PreRoll', group='Par', kind='float')
            Roll = tilt_matrix_roll(PreRoll)
            means, covs = tilt_rot_mean(means, covs, Roll)

        #      IF (DoCorr(QCYaw)) THEN
        #        CALL EC_C_T07(Mean(U),Mean(V),DirYaw)
        #       CALL EC_C_T05(Mean,NMax,N,Cov,Yaw)
        if qcyaw:
            logger.debug('apply mean-wind rotation')
            diryaw = tilt_mean_dir(means['ux'], means['uy'])
            Yaw = tilt_matrix_yaw(diryaw)
            means, covs = tilt_rot_mean(means, covs, Yaw)

        # C
        # C
        # C Perform classic pitch-correction : Mean(W) --> 0
        # C
        # C
        #      IF (DoCorr(QCPitch)) THEN
        #        CALL EC_C_T09(Mean(U),Mean(W),DirPitch)
        #        CALL EC_C_T05(Mean,NMax,N,Cov,Pitch)
        if qcpitch:
            logger.debug('apply pitch rotation (w->0)')
            DirPitch = tilt_mean_vert(means['ux'], means['uw'])
            Pitch = tilt_matrix_pitch(DirPitch)
            means, covs = tilt_rot_mean(means, covs, Pitch)

        # C
        # C
        # C Perform classic roll-correction : Cov(W,V) --> 0
        # C
        # C
        #      IF (DoCorr(QCRoll)) THEN
        #        CALL EC_C_T11(Cov(V,V),Cov(V,W),Cov(W,W),DirRoll)
        #        CALL EC_C_T05(Mean,NMax,N,Cov,Roll)
        if qcroll:
            logger.debug('apply roll rotation (cov(w,v)->0)')
            DirRoll = tilt_mean_roll(covs['uy', 'uy'],
                                     covs['uy', 'uz'],
                                     covs['uz', 'uz'])
            Roll = tilt_matrix_roll(DirRoll)
            # noinspection PyUnusedLocal
            means, covs = tilt_rot_mean(means, covs, Roll)

        # end ==== EC_C_Main ====

        # C
        # C If any transformation of coordinates was required (one of the options
        # C DoTilt, DoYaw, DoPitch or DoRoll was selected), then the numbers
        # C of independent samples of the respective quantities has to be
        # C re-estimated. It is not possible to "tilt the error-bars" on basis of
        # C the quantities which have been calculated until here.
        # C Therefore we return to the calibrated time series and
        # C make the transformations BEFORE averaging. Then averaging and corrections
        # C are repeated all over again.
        # C
        # C Estimate mean values, covariances and tolerances of both
        # C for the planar fit untilted series
        # C
        # C
        # C
        # C Tilt ALL samples
        # C
        #        DO i=1,M
        #          Speed(1) = Sample(U,i)
        #          Speed(2) = Sample(V,i)
        #          Speed(3) = Sample(W,i)
        #
        #          IF (DoCorr(QCTilt)) THEN
        #            CALL EC_C_T06(ExpVar(QEPreYaw),Yaw)
        #            CALL EC_C_T05(Speed,3,3,DumCov,Yaw)

        #            CALL EC_C_T08(ExpVar(QEPrePitch),Pitch)
        #            CALL EC_C_T05(Speed,3,3,DumCov,Pitch)
        #            CALL EC_C_T10(ExpVar(QEPreRoll),Roll)
        #            CALL EC_C_T05(Speed,3,3,DumCov,Roll)
        if qctilt:
            logger.debug('apply pre-selected rotation to raw data')

            Yaw = tilt_matrix_yaw(PreYaw)
            sample = tilt_rot_speed(sample, Yaw)

            Pitch = tilt_matrix_pitch(PrePitch)
            sample = tilt_rot_speed(sample, Pitch)

            Roll = tilt_matrix_roll(PreRoll)
            sample = tilt_rot_speed(sample, Roll)
        #
        #          IF (DoCorr(QCYaw)) THEN
        #            CALL EC_C_T06(DirYaw,Yaw)
        #            CALL EC_C_T05(Speed,3,3,DumCov,Yaw)
        #          ENDIF
        #          IF (DoCorr(QCPitch)) THEN
        #            CALL EC_C_T08(DirPitch,Pitch)
        #            CALL EC_C_T05(Speed,3,3,DumCov,Pitch)
        #          ENDIF
        #          IF (DoCorr(QCRoll)) THEN
        #            CALL EC_C_T10(DirRoll,Roll)
        #            CALL EC_C_T05(Speed,3,3,DumCov,Roll)
        #          ENDIF
        if qcyaw:
            logger.debug('apply mean wind rotation to raw data')
            Yaw = tilt_matrix_yaw(diryaw)
            sample = tilt_rot_speed(sample, Yaw)
        if qcpitch:
            logger.debug('apply pitch rotation to raw data')
            Pitch = tilt_matrix_pitch(DirPitch)
            sample = tilt_rot_speed(sample, Pitch)
        if qcroll:
            logger.debug('apply roll rotation to raw data')
            Roll = tilt_matrix_roll(DirRoll)
            sample = tilt_rot_speed(sample, Roll)
        # C
        # C Reestablish the averages and covariances in the correct frame of reference.
        # C
        #        CALL EC_M_Averag(Sample,NMax,N,MMax,M,Flag,
        #     &                         Mean,TolMean,Cov,TolCov,
        #     &                   MIndep,CIndep,Mok,Cok)
        # C mark variables as not present, if they conatain only invalid values
        #        DO j=1,N
        #          IF (MOK(j).EQ.0) THEN
        #            HAVE_CAL(j)=.FALSE.
        #          ENDIF
        #        ENDDO
        #        CALL EC_G_Reset(Have_cal, Mean, TolMean, Cov, TolCov,
        #     &                MIndep,  CIndep)
        # C replace Mean(Humidity) by Psychro only if user requests DoCrMean = T
        #        IF (DoCorr(QCMean).AND..NOT. Have_cal(Humidity)) THEN
        #          Mean(Humidity) = Psychro
        #          MEAN(SpecHum) = EC_Ph_Q(Mean(Humidity), Mean(WhichTemp), P)
        #        ENDIF
        logger.debug('re-calculate means')
        means, tolmean, covs, tolcov, mindep, cindep = averag(sample)
        if qcmean and not np.isfinite(means['h2o']):
            means['h2o'] = interval['s_rhov']
            means['q'] = ec.spechum(
                interval['s_rhov'], means[whichtemp], interval['s_pp'])

    # C
    # C Perform all necessary corrections on the mean values and (co-)variances.
    # C This is the real thing (irrespective of tilt correction)
    # C
    #      CALL EC_C_Main(OutF,
    #     &          DoPrint,
    #     &          Mean,NMax,N,TolMean,
    #     &          Cov,TolCov,DirYaw = 180D0
    #     &    DumCorr, PDumCorr, ExpVar,
    #     &          DirYaw,
    #     &          DirPitch,
    #     &          DirRoll,
    #     &          SonFactr,
    #     &          O2Factor,
    #     &          CalSonic,CalTherm,CalHyg,CalCO2,FrCor,
    #     &          WebVel, P, Have_cal,
    #     &          DoCorr(QCIterate),MaxIter)
    #      CALL EC_G_Reset(Have_cal, Mean, TolMean, Cov, TolCov,
    #     &                MIndep,  CIndep)

    # begin ==== EC_C_Main ====

    logger.debug('apply all corrections')
    means, tolmean, covs, tolcov, webvel = cmain(
        conf, interval, means, tolmean, covs, tolcov)

    # end ==== EC_C_Main ====

    # C Re-establish the mean humidity signal if needed
    # C replace Mean(Humidity) by Psychro only if user requests DoCrMean = T
    #      IF (DoCorr(QCMean).AND..NOT. Have_cal(Humidity)) THEN
    #          Mean(Humidity) = Psychro
    #          MEAN(SpecHum) = EC_Ph_Q(Mean(Humidity), Mean(WhichTemp), P)
    #      ENDIF

    if qcmean and not np.isfinite(means['h2o']):
        means['h2o'] = interval['s_rhov']
        means['q'] = ec.spechum(
            interval['s_rhov'], means[whichtemp], interval['s_pp'])

    # C
    # C Calculate alternate error of covariances after Finkestein&Sims
    #      IF (DoCorr(QCErrFiSi)) THEN
    #        CALL EC_Ph_ErrFiSi(Sample,NMax,N,MMax,M,Flag,TolCov)
    #        TolCov=2.D00*TolCov
    #      ENDIF

    if qcerrfisi:
        logger.debug('re-calculate errors after Finkelstein&Sims')
        tolcov = 2. * errfisi(sample)

    # C
    # C Calculate fluxes from processed mean values and covariances.
    # C

    # C
    # C The 180 degrees is to trick ec_Ph_Flux
    # C
    #      IF (.NOT. DoCorr(QCYaw)) THEN
    #         DirYaw = 180D0
    #      ELSE
    #         DirYaw = DirYaw + 180D0
    #      ENDIF

    if qcyaw:
        diryaw = diryaw + 180.
    else:
        diryaw = 180.

    #
    #      CALL EC_Ph_Flux(Mean,NMax,Cov,TolMean,TolCov,p,BadTc,
    #     &                QPhys, dQPhys, WebVel, DirYaw)

    logger.debug('calculate fluxes')
    qphys, dqphys = flux(means, tolmean, covs, tolcov, badtc,
                         interval['s_pp'], webvel, diryaw)
# FIXME warum
    qphys['meanw'] = qpmeanw
# FIXME warum
    dqphys['meanw'] = dqpmeanw

    # C Re-establish the mean humidity signal if needed
    #      IF (DoCorr(QCMean).AND..NOT. Have_cal(Humidity)) THEN
    #          Mean(Humidity) = Psychro
    #          MEAN(SpecHum) = EC_Ph_Q(Mean(Humidity), Mean(WhichTemp), P)
    #      ENDIF

    if qcmean and not np.isfinite(means['h2o']):
        means['h2o'] = interval['s_rhov']
        means['q'] = ec.spechum(
            interval['s_rhov'], means[whichtemp], interval['s_pp'])

    # C
    # C Determine min and max of calibrated signal
    # C
    #  CALL EC_M_MinMax(Sample, NMax, N, MMax, M, Flag, MINS, MAXS)
    #
    #      RETURN
    #      END

    # --end-- EC_G_Main --end-- the original subroutine exits here

    # count values
    interval['samples'] = len(sample.index)
    for c in ec.ecvar:
        interval['ok_{:s}'.format(c)] = sum(np.isfinite(sample[c]))

    # C
    # C Calculate structure parameters
    # C
    #        IF (DoStruct) THEN
    #          DO I=1,NNMax
    #           DO J=1,NNMax
    #            IF ((HAVE_CAL(I) .AND. HAVE_CAL(J)) .AND.
    #     &              OutStr(I,J)) THEN
    #                   R = ExpVar(QEStructSep)
    #                   CALL EC_Ph_Struct(Sample,NNMax,MMMax,M,Flag,
    #     &                  I,J, R,dR,ExpVar(QEFreq),CIndep,
    #     &                  Struct(I,J), dStruct(I,J))
    #                   Struct(J,I) = Struct(I,J)
    #                   dStruct(J,I) = dStruct(I,J)
    #                ELSE
    #                   Struct(I,J) = DUMMY
    #                   dStruct(I,J) = DUMMY
    #                ENDIF
    #             ENDDO
    #          ENDDO
    #        ELSE
    #          DO I=1,NNMax
    #            DO J=1,NNMax
    #                R = DUMMY
    #                dR = DUMMY
    #                Struct(I,J) = DUMMY
    #                dStruct(I,J) = DUMMY
    #             ENDDO
    #          ENDDO
    #        ENDIF

    if qcstruct:
        logger.debug('calculate structure parameters')
        struct, dstruct, r, dr = calcstruct(conf, sample, cindep)

        # C
        # C Determine standard deviations
        # C
        #        DO I=1,NNMax
        #     IF (.NOT. HAVE_CAL(I).OR.Cov(I,I).EQ.0.D0) THEN
        #       Std(I) = DUMMY
        #       dStd(I) = DUMMY
        #     ELSE
        #       Std(I) = SQRT(Cov(I,I))
        #       dStd(I) = 0.5D0*TolCov(I,I)/
        #     &              SQRT(Cov(I,I))
        #           ENDIF
        #        ENDDO

        std = {}
        dstd = {}
        for c in means.index:
            std[c] = np.sqrt(covs.loc[c, c])
            if covs.loc[c, c] != 0:
                dstd[c] = 0.5 * tolcov.loc[c, c] / np.sqrt(covs.loc[c, c])
            else:
                dstd[c] = np.inf
    else:
        std = {c: np.nan for c in means.index}
        dstd = {c: np.nan for c in means.index}

    # re-organize values into columns in "intervals" dataframe

    res = interval.copy()
    for k, v in means.items():
        res['mean_{:s}'.format(k)] = v
    for k, v in tolmean.items():
        res['dmean_{:s}'.format(k)] = v
    for k, v in std.items():
        res['std_{:s}'.format(k)] = v
    for k, v in dstd.items():
        res['dstd_{:s}'.format(k)] = v
    for i in covs.columns:
        for j in covs.index:
            res['cov_{:s}_{:s}'.format(i, j)] = covs.loc[i, j]
    for i in tolcov.columns:
        for j in tolcov.index:
            res['dcov_{:s}_{:s}'.format(i, j)] = tolcov.loc[i, j]
    res['r'] = r
    res['dr'] = dr
    for i in struct.columns:
        for j in struct.index:
            res['struct_{:s}_{:s}'.format(i, j)] = struct.loc[i, j]
    for i in dstruct.columns:
        for j in dstruct.index:
            res['dstruct_{:s}_{:s}'.format(i, j)] = dstruct.loc[i, j]
    for k, v in qphys.items():
        res[k] = v
    for k, v in dqphys.items():
        res['d{:s}'.format(k)] = v
    res['whichtemp'] = ec.metvar.index(whichtemp)


    return res


# ----------------------------------------------------------------
#
def process_flux(conf, intervals):
    """
    Process all flux intervals with optional parallel execution.

    :param conf: Configuration object with processing parameters
    :type conf: object
    :param intervals: DataFrame with processing intervals
    :type intervals: pandas.DataFrame
    :return: DataFrame with flux calculation results
    :rtype: pandas.DataFrame

    Coordinates parallel processing of flux intervals using
    multiprocessing Pool. Number of processes controlled by conf['nproc'].
    """
    logger.debug('start processing fluxes')
    #
    # define number of threads
    #
    nproc = conf.get('nproc', kind='int')
    logger.info('starting {:d} parallel processes'.format(nproc))
    if nproc > 1:
        # execute parallel
        pool = Pool(nproc, initializer=ecdb.init_worker_process, initargs=(ecdb.dbfile,))
    elif nproc == 1:
        # execute serial
        pool = None
    else:
        # execute parallel
        pool = Pool(initializer=ecdb.init_worker_process, initargs=(ecdb.dbfile,))
    #
    # progress per interval:
    progress = 100.
    int_progress = float(progress)/float(len(intervals.index))
    ec.progress_reset()
    #
    # pack arguments and run thread(s)
    #

    args = [(conf, x)
            for x in intervals.to_dict(orient='records')]
    if nproc == 1:
        # execute serial
        results = []
        for a in args:
            result = process_flux_interval(a)
            results.append(result)
    else:
        # execute parallel
        # results = pool.map(process_flux_interval, args)
        # execute parallel
        results = []
        for result in pool.imap(process_flux_interval, args):
            ec.progress_increment(int_progress)
            results.append(result)
    #
    # convert results into dataframe
    intervals_out = pd.DataFrame.from_records(results)

    logger.debug('done processing fluxes')
    return intervals_out
