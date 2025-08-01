#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
EC-PeT Processing Engine
========================

Main orchestration module for complete eddy-covariance data processing workflows.
Coordinates the entire processing pipeline from raw data ingestion through final
flux calculations and quality-controlled output generation. Provides command-line
interface and stage-based processing with resumption capabilities.

Key Features:
    - Stage-based processing with checkpoint/resume functionality
    - Parallel processing support for large datasets
    - Automatic time range detection from raw data files
    - Column mapping for TOA5 datalogger formats
    - SQLite database for intermediate data management
    - Comprehensive progress reporting and logging
    - Command-line interface with configurable verbosity

Command Line Interface:
    Supports processing control, parallel execution settings,
    logging verbosity adjustment, and stage-specific restart
    capabilities for efficient workflow management.

"""

import argparse
import logging
import os

from . import ecconfig
from . import ecdb
from . import ecfile
from . import ecpack
from . import ecplan
from . import ecpost
from . import ecpre
from . import ecutils as ec

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------

def check_raw_columns(conf):
    """
    Resolve TOA5 column specifications from numbers to database names.

    :param conf: Configuration object with column specifications
    :type conf: object
    :return: Updated configuration with resolved column names
    :rtype: object

    Converts column numbers to standardized database column names by scanning
    TOA5 file headers. Handles both slow and fast data channels, validates
    consistency across multiple files, and updates configuration accordingly.
    """
    rawformat = conf.get('RawFormat', kind='str')
    #
    # default -- toa5
    if rawformat == 'toa5':
        #
        slownams = [ec.sccprefix+ec.refstem[x]+'_nam' for x in ec.refvar]
        fastnams = [ec.fccprefix+ec.stem[x]+'_nam' for x in ec.var]
#    print(slownams+fastnams)
        numnams = sum([len(conf.get(x)) != 0 for x in slownams+fastnams])
        slowcols = [ec.sccprefix+ec.refstem[x]+'_col' for x in ec.refvar]
        fastcols = [ec.fccprefix+ec.stem[x]+'_col' for x in ec.var]
#    print(slowcols+fastcols)
        numcols = sum([len(conf.get(x)) != 0 for x in slowcols+fastcols])
        #
        if numnams > 0:
            if numcols == 0:
                logger.debug('toa5 columns given by column names')
            else:
                logger.warning('toa5 columns given by both names and' +
                                ' numbers: numbers will be ignored!')
        elif numnams == 0 and numcols > 0:
            logger.debug('toa5 columns given by column numbers')
            #
            # test fast and slow data seperatedly
            #
            sf = [
                ['RawSlowData',
                 [ec.sccprefix+ec.refstem[x]+'_col' for x in ec.refvar],
                 ],
                ['RawFastData',
                 [ec.fccprefix+ec.stem[x]+'_col' for x in ec.var],
                 ]
            ]
            #
            # for each pass (slow/fast data) get name of the
            #    config paramters for file list (filepar)
            #    and column numbers (colpar) from the list above
            #
            for filepar, colpar in sf:
                h = []
                #
                # get the header for each file
                #
                rawdir = conf.get('RawDir', kind='str')
                for ff in [os.path.join(rawdir, x) for x in conf.get(filepar)]:
                    logger.insane('scanning file "'+ff+'"')
                    hh = ecfile.toa5_get_header(ff)
                    hh['dbcolumn'] = [
                        ecdb.dbcolumn_name(hh['column_names'][x],
                                           hh['column_units'][x],
                                           hh['column_sampling'][x])
                        for x in range(hh['column_count'])]
                    h.append(hh)
                #
                #  extract the column numbers
                #
                colnum = [conf.get(x, kind='int') for x in colpar]
                #
                #  for each column used (number >0 ) get the
                #  corresponding name from each file header
                #  and count how many different names we get
                #
                colnam = [None]*len(colnum)
                for i in range(len(colnum)):
                    if colnum[i] > 0:
                        try:
                            colnams = set(hh['dbcolumn'][colnum[i]-1]
                                          for hh in h)
                        except ValueError:
                            logger.error('column "{:s}" ({:d}) is missing in one or more files'.format(
                                colpar[i], i+1,))
                            raise ValueError
                        if len(colnams) > 1:
                            logger.error('column "{:s}" ({:d}) has different names : {:s}'.format(
                                colpar[i], i+1, ', '.join(colnams)))
                            raise ValueError
                        elif len(colnams) != 1:
                            logger.error('column "{:s}" ({:d}) not found in any file'.format(
                                colpar[i], colnum[i]))
                            raise ValueError
                        #
                        #  if name is unique remember ist
                        #
                        colnam[i] = list(colnams)[0]
                #
                #  store column names in config
                #
                for i in range(len(colnum)):
                    if colnam[i] is not None:
                        nampar = colpar[i].replace('_col', '_nam')
                        conf.put(nampar, '"{:s}"'.format(colnam[i]))
                        logger.debug(
                            'added to config: {:s} = {:s}'.format(nampar, colnam[i]))
                    conf.put(colpar[i], '')
        else:
            logger.debug(
                'toa5 columns not given (numbers {:d}, names {:d})'.format(numcols, numnams))
            raise ValueError

    return conf


# ----------------------------------------------------------------

def read_raw_data(conf):
    """
    Ingest raw data files into SQLite database for processing.

    :param conf: Configuration object with file paths and format settings
    :type conf: object

    Reads TOA5 files specified in configuration into database tables.
    Separates fast (high-frequency) and slow (reference) measurements
    into different tables with parallel processing support.
    """
    nproc = conf.get('nproc', kind='int')
    # default -- toa5
    if conf.get('RawFormat', kind='str') == 'toa5':
        fd = conf.get('RawDir', kind='str')
        ff = conf.get('RawFastData', kind='str', unlist=False)
        if len(ff) > 0:
            infiles = [os.path.join(fd, x) for x in ff]
            ecdb.ingest(infiles, nproc=nproc, station_name='raw',
                        table_name='fast', progress=90)
        ec.progress_percent(95)
        fs = conf.get('RawSlowData', kind='str', unlist=False)
        if len(fs) > 0:
            infiles = [os.path.join(fd, x) for x in fs]
            ecdb.ingest(infiles, nproc=nproc, station_name='raw',
                        table_name='slow', progress=4)
        ec.progress_percent(99)
    else:
        logger.critical('RawFormat "{:s}" not implemented'.format(
            conf.get('RawFormat', kind='str')))
        raise ValueError


# ----------------------------------------------------------------

def get_start_end(conf):
    """
    Determine processing time range from configuration or auto-detect from data.

    :param conf: Configuration object with date settings
    :type conf: object
    :return: Updated configuration with resolved time range
    :rtype: object

    Auto-detects time range from database if not specified in configuration.
    Updates DateBegin and DateEnd parameters for subsequent processing stages.
    """
    # if time interval is undefined by config:
    db = conf.get('DateBegin', kind="str")
    de = conf.get('DateEnd', kind="str")
    if len(db) == 0 or len(de) == 0:
        # autodetect time interval to process from raw data files
        logger.info('auto-detecting time range ...')
        date_begin, date_end = ecdb.retrieve_time_range('raw', 'fast')
        if len(db) == 0:
            conf.put('DateBegin', date_begin.strftime('%Y-%m-%d %H:%M'))
        if len(de) == 0:
            conf.put('DateEnd', date_end.strftime('%Y-%m-%d %H:%M'))
        logger.info(' ... detected time range  "{:s}" - "{:s}"'.format(
            conf.get('DateBegin'), conf.get('DateEnd')))
    else:
        logger.info('processing data time range "{:s}" - "{:s}"'.format(
            conf.get('DateBegin'), conf.get('DateEnd')))
    return conf


# ----------------------------------------------------------------
#   stage-driver routines
# ----------------------------------------------------------------

def collectdata(conf):
    """
    Stage 0: Collect and ingest raw data files into processing database.

    :param conf: Configuration object with file specifications
    :type conf: object
    :return: Updated configuration with resolved parameters
    :rtype: object

    Expands file patterns, auto-detects time ranges, resolves column
    mappings, and ingests all specified data files into SQLite database.
    """

    # expand filenam globbing patterns (e.g. "*ts*")
    conf1 = ecconfig.unglob(conf)

    # try to get time interval to process
    db = conf1.get('DateBegin', kind="str")
    de = conf1.get('DateEnd', kind="str")
    logger.debug('DateBegin:  "%s"' % db)
    logger.debug('DateEnd  :  "%s"' % de)

    # autodetect time interval to process if it is not specified
    if len(db) == 0 or len(de) == 0:
        time_range = ecfile.get_time_range(conf1.get('RawDir'),
                                           conf1.get('RawFastData', unlist=False))
        if len(db) == 0:
            conf1.put('DateBegin', time_range[0].strftime('%Y-%m-%d %H:%M'))
        if len(de) == 0:
            conf1.put('DateEnd', time_range[1].strftime('%Y-%m-%d %H:%M'))
        logger.info('auto-detected time range  "{}" - "{}"'.format(
            conf1.get('DateBegin'), conf1.get('DateEnd')))
    else:
        logger.info('requested data time range "{}" - "{}"'.format(
            conf1.get('DateBegin'), conf1.get('DateEnd')))
    # set progress display
    ec.progress_percent(1)

    # check if we hve the info we need
    conf2 = check_raw_columns(conf1)
    # set progress display
    ec.progress_percent(5)

    # call the reading routine
    read_raw_data(conf2)
    # set progress display
    ec.progress_percent(100)

    return conf2


# ----------------------------------------------------------------
#


def write_output(conf, intervals):
    """
    Stage 5: Generate final output files from processed intervals.

    :param conf: Configuration object with output settings
    :type conf: object
    :param intervals: DataFrame with processed interval results
    :type intervals: pandas.DataFrame

    Creates standardized output files including quality flags,
    flux data, and comprehensive results in multiple formats.
    """
    ecpre.flags1_to_file(conf, intervals)
    ec.progress_percent(25)
    ecpack.flux_to_file(conf, intervals)
    ec.progress_percent(50)
    ecpost.flags2_to_file(conf, intervals)
    ec.progress_percent(75)
    ecpost.output_to_file(conf, intervals)
    ec.progress_percent(99)


# ----------------------------------------------------------------
#


def process(conf, startat):
    """
    Main processing pipeline coordinator with stage-based execution.

    :param conf: Configuration object with all processing parameters
    :type conf: object
    :param startat: Stage number to begin processing (0-5)
    :type startat: int

    Orchestrates complete processing workflow with checkpoint capabilities.
    Each stage saves results to database, enabling restart at any point
    without reprocessing earlier stages.
    """

    intervals = None
    # get the number of processes to run
    nproc = conf.get('nproc', kind='int')
    logger.info('using {:d} parallel processes'.format(nproc))

    # start processing at the desired stage
    if startat <= 0:
        logger.info('calling collectdata')
        ec.progress_stage('start')
        conf = collectdata(conf)
        #        ecdb.conf_to_db(conf)
        logger.info('finished collectdata')

    if startat <= 1:
        conf = get_start_end(conf)
        logger.info('calling preprocessor')
        ec.progress_stage('pre')
        intervals = ecpre.preprocessor(conf)
        logger.info('finished preprocessor')
        logger.debug('{}'.format(intervals))
        ecdb.ingest_df(intervals, station_name='pre',
                       table_name='intervals', time_column='begin')
    if startat <= 2:
        conf = get_start_end(conf)
        if intervals is None:
            intervals = ecdb.retrieve_df(
                station_name='pre', table_name='intervals')
        logger.info('calling planar fit')
        ec.progress_stage('plan')
        intervals = ecplan.planarfit(conf, intervals)
        logger.info('finished planar fit')
        ecdb.ingest_df(intervals, station_name='plan',
                       table_name='intervals', time_column='begin')
    if startat <= 3:
        conf = get_start_end(conf)
        if intervals is None:
            intervals = ecdb.retrieve_df(
                station_name='plan', table_name='intervals')
        logger.info('calling flux calculation')
        ec.progress_stage('flux')
        intervals = ecpack.process_flux(conf, intervals)
        logger.info('finished flux calculation')
        ecdb.ingest_df(intervals, station_name='flux',
                       table_name='intervals', time_column='begin')
    if startat <= 4:
        conf = get_start_end(conf)
        if intervals is None:
            intervals = ecdb.retrieve_df(
                station_name='flux', table_name='intervals')
        logger.info('calling postprocessor')
        ec.progress_stage('post')
        intervals = ecpost.postprocessor(conf, intervals)
        logger.info('finished postprocessor')
        ecdb.ingest_df(intervals, station_name='post',
                       table_name='intervals', time_column='begin')
    if startat <= 5:
        conf = get_start_end(conf)
        if intervals is None:
            intervals = ecdb.retrieve_df(
                station_name='post', table_name='intervals')
        logger.info('calling output')
        ec.progress_stage('out')
        write_output(conf, intervals)
        logger.info('finished output')
        ec.progress_done()
        ecdb.mark_finished()


# ----------------------------------------------------------------
#
# user interface
#
def cli():
    """
    Command-line interface for EC-PeT processing engine.

    Provides argument parsing for processing control, parallel execution
    settings, verbosity levels, and stage-specific restart capabilities.
    Initializes logging, configuration, and database before starting
    the main processing pipeline.
    """

    parser = argparse.ArgumentParser(
        description='EC-PeT Engine')
    parser.add_argument('-p', '--processes', dest='nproc', metavar='NUM',
                        nargs='?', default=0,
                        help='number of parallel processes to run [0=auto]')
    parser.add_argument('-s', '--stage', dest='stage', metavar='STAGE',
                        choices=ec.stages, nargs='?', default='start',
                        help='(re)start at processing stagerun %(default)')
    parser.add_argument(dest='conf', metavar='FILE',
                        help='use configuration file FILE')
    verb = parser.add_mutually_exclusive_group()
    verb.add_argument('-v', dest='verbose', action='count',
                      help='increase output verbosity (i.e. debug level)')
    verb.add_argument('-q', dest='quiet', action='count',
                      help='decrease output verbosity')
    args = parser.parse_args()

    logging_levels = [logging.CRITICAL, logging.ERROR, logging.WARNING,
                      logging.NORMAL, logging.INFO, logging.DEBUG, logging.INSANE]
    logging_numeric = logging_levels.index(logging.NORMAL)
    if args.verbose is not None:
        logging_numeric = min(len(logging_levels)-1,
                              logging_numeric+args.verbose)
    elif args.quiet is not None:
        logging_numeric = max(0, logging_numeric-args.quiet)
    logging.root.setLevel(logging_levels[logging_numeric])
    logging.normal('logging level: {:s}'.format(
        logging.getLevelName(logging.root.getEffectiveLevel())))
    #
    logging.normal('')
    logging.normal('EC-PeT Data Processor')
    logging.normal('(c) 2018- Clemens Druee, Umweltmeteorologie, Uni Trier')
    logging.normal('')
    logging.normal('logging level: {:s}'.format(
        logging.getLevelName(logging.root.getEffectiveLevel())))
    #
    # get numeric value of stage to start at
    startat = ec.stages.index(args.stage)
    #
    conf_current = ecconfig.read_file(args.conf)
    conf = ecconfig.complete(conf_current)
    #
    ecdb.dbfile = os.path.join(conf.get('DatDir'), 'database.sqlite')
    logging.normal('using database file: {:s}'.format(ecdb.dbfile))
    #
    process(conf, startat)


# ----------------------------------------------------------------
#
# main call
#
if __name__ == "__main__":
    #
    #
    cli()
