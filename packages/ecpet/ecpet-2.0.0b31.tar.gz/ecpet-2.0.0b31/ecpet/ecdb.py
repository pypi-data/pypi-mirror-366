# -*- coding: utf-8 -*-
"""
EC-PeT Database Module
======================

SQLite database operations for eddy-covariance data processing workflows.
Provides comprehensive data ingestion, storage, and retrieval capabilities
for TOA5 datalogger files and processed results. Manages metadata, file
tracking, and temporal data organization with multiprocessing support.

Key Features:
    - TOA5 file ingestion with parallel processing
    - Automatic schema creation and column management
    - File deduplication using MD5 checksums
    - Temporal data retrieval with flexible filtering
    - Configuration persistence and retrieval
    - Processing stage checkpoint management

"""

import csv
import datetime as dt
import io
import logging
import os
import platform
import sqlite3
import sys
from collections import Counter
from multiprocessing import Pool, set_start_method

import numpy as np
import pandas as pd

from . import ecconfig
from . import ecfile
from . import ecutils as ec

logger = logging.getLogger(__name__)

# constants
MAX_RETRIES = 5
# default values
dbfile = 'database.sqlite'
colsep = ','
dbsep = ":"
sqlsep = ', '
force = False
#
# constants
tfmt = '%Y-%m-%d %H:%M:%S.%f'
#
# db table for header information
#
tab_head_name = 'headers'
tab_head_cols = ['header_id', 'station_name', 'table_name', 'column_count',
                 'logger_name', 'logger_os', 'logger_prog',
                 'logger_serial', 'logger_sig']
tab_head_types = {'default': 'text', 'header_id': 'integer primary key'}
#
# db table for file information
#
tab_file_name = 'files'
tab_file_cols = ['file_id', 'file_name', 'file_hash']
tab_file_types = {'default': 'text', 'file_id': 'integer primary key'}
#
# db table skeleton for data
#
tab_skeleton_meta = ['head_id', 'file_id']
tab_skeleton_index = ['TIMESTAMP', 'RECORD']
tab_skeleton_cols = tab_skeleton_index + tab_skeleton_meta
tab_skeleton_types = {'default': 'real',
                      'TIMESTAMP': 'text primary key',
                      'RECORD': 'integer',
                      'head_id': 'tinyint',
                      'file_id': 'tinyint'}
#
# db table for config
#
tab_conf_name = 'config'
tab_conf_cols = ['token', 'value']
tab_conf_types = {'token': 'text primary key', 'value': 'text'}


def timestamp_fill(stamp):
    """
    Complete partial timestamp strings to standard format.

    :param stamp: Timestamp string to standardize
    :type stamp: str
    :return: Standardized timestamp string
    :rtype: str

    Ensures timestamps match '%Y-%m-%d %H:%M:%S.%f' format by padding
    incomplete strings with appropriate defaults.
    """
    #
    # fill incomplete timestamp to match format  %Y-%m-%d %H:%M:%S.%f
    #
    empty = "0000-01-01 00:00:00.000"
    ls = len(stamp)
    logger.insane('completing stamp "%s" (len %i)' % (stamp, ls))
    if ls > 23:
        stamp = stamp[0:23]
        logger.insane('TIMESTAMP trimmed to %s' % stamp)
    elif ls >= 4:
        if ls < 10:
            logger.warning('no date in given in TIMESTAMP %s' % stamp)
        stamp = stamp + empty[len(stamp):]
        logger.insane('TIMESTAMP filled to %s' % stamp)
    else:
        logger.critical('incomprehensible TIMESTAMP %s' % stamp)
        exit()
    return stamp


def with_retry(func, *args, **kwargs):
    """
    Execute a function that operates on the database and retry if it fails.

    :param func: Function to execute
    :type func: function
    :param args: Positional arguments to pass to the function
    :param kwargs: Keyword arguments to pass to the function
    :return: Function result
    :rtype: Any

    The time between retries increases exponentially from try to try.
    At most :py:const:`MAX_RETRIES` attempts are made.
    """
    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            # Actually call the function with the provided arguments
            result = func(*args, **kwargs)
            return result  # Success - return the actual result

        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()

            # Check if this is a retryable error
            retryable_keywords = ['locked', 'busy', 'constraint',
                                  'database is locked',
                                  'database disk image is malformed',
                                  'constraint failed']

            is_retryable = any(
                keyword in error_msg for keyword in retryable_keywords)

            if is_retryable and attempt < MAX_RETRIES - 1:
                import time
                wait_time = 0.1 * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f'Database operation failed on attempt {attempt + 1}/{MAX_RETRIES}, '
                    f'waiting {wait_time:.1f}s before retry. Error: {e}')
                time.sleep(wait_time)
                continue
            else:
                # Either not retryable or max retries reached
                if attempt == MAX_RETRIES - 1:
                    logger.error(
                        f'Database operation failed after {MAX_RETRIES} attempts: {e}')
                else:
                    logger.error(
                        f'Database operation failed with non-retryable error: {e}')
                raise e

    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    else:
        raise RuntimeError(
            f"Function {func.__name__} failed after {MAX_RETRIES} attempts")


def exe_sql(cur, sql):
    """
    Execute SQL statement and return results with logging.

    :param cur: Database cursor
    :type cur: sqlite3.Cursor
    :param sql: SQL statement to execute
    :type sql: str
    :return: Query results
    :rtype: list

    Provides debug logging and error checking for database operations.
    """
    #
    # execute SQL statement and check if we got any answer
    #
    logger.insane('SQL=%s' % sql)
    cur.execute(sql)
    response = cur.fetchall()
    if len(response) < 1:
        logger.error('no response to SQL request')
        response = []
    elif len(response) <= 15:
        logger.insane('response=%s' % response)
    else:
        logger.insane('response=%s (...)' % (response[0:15]))
    return response


def get_free_index(cur, tab_name, id_name, reserv=None):
    """
    Find next available index number in database table.

    :param cur: Database cursor
    :type cur: sqlite3.Cursor
    :param tab_name: Table name to search
    :type tab_name: str
    :param id_name: ID column name
    :type id_name: str
    :param reserv: Reserved IDs to avoid, defaults to None
    :type reserv: list, optional
    :return: Next available index
    :rtype: int

    Finds lowest available ID number, accounting for reserved values
    and existing database entries.
    """
    #
    # get a free index number in table tab_name
    #
    if reserv is None:
        reserv = []
    sql = 'SELECT %s FROM %s;' % (id_name, tab_name)
    logger.insane('SQL=%s' % sql)
    cur.execute(sql)
    response = cur.fetchall()
    logger.insane('response=%s' % response)
    #
    # ids reassigned in database
    assig = [i[0] for i in response]
    #
    # sorted lis of all unavailable ids
    unavail = sorted(assig + reserv)
    if len(unavail) == 0:
        head_id = 1
    else:
        #
        # default: max value+1
        head_id = unavail[-1] + 1
        #
        # search for lower un-assigned value
        if len(unavail) != unavail[-1]:
            for i in range(len(response)):
                if i + 1 != unavail[i]:
                    head_id = i + 1
                    break
    return head_id


def column_prepare(cur, tab_name, col_name, col_type):
    """
    Ensure column exists in table, creating if necessary.

    :param cur: Database cursor
    :type cur: sqlite3.Cursor
    :param tab_name: Table name
    :type tab_name: str
    :param col_name: Column name to check/create
    :type col_name: str
    :param col_type: Column data type
    :type col_type: str
    :return: SQL query response
    :rtype: list

    Adds missing columns to existing tables with specified data type.
    """
    #
    # test if column col_name exists in table tab_name, create it if not
    #
    sql = 'PRAGMA table_info("%s");' % tab_name
    logger.insane("SQL=%s" % sql)
    cur.execute(sql)
    response = cur.fetchall()
    logger.insane('response=%s' % response)
    existingcols = []
    for row in response:
        existingcols.append(row[1])
    if col_name not in existingcols:
        logger.info('Add column: %s to table: "%s"' % (col_name, tab_name))
        sql = 'ALTER TABLE "%s" ADD COLUMN "%s" %s ;' % (
            tab_name, col_name, col_type)
        logger.debug('SQL=%s' % sql)
        cur.execute(sql)
        response = cur.fetchall()
        logger.insane('response=%s' % response)
    return response


def table_prepare(cur, tab_name, tab_cols, tab_types):
    """
    Ensure table exists with required columns, creating if necessary.

    :param cur: Database cursor
    :type cur: sqlite3.Cursor
    :param tab_name: Table name
    :type tab_name: str
    :param tab_cols: Required column names
    :type tab_cols: list
    :param tab_types: Column type specifications
    :type tab_types: dict
    :return: SQL query response
    :rtype: list

    Creates tables and adds missing columns according to specifications.
    """
    #
    # test if table already exists, create it if not
    #
    sql = 'SELECT "name" FROM "sqlite_master" WHERE type="table" AND name="%s";' % tab_name
    logger.debug('SQL=%s' % sql)
    cur.execute(sql)
    response = cur.fetchall()
    logger.insane('response=%s' % response)
    #
    # if no such table: create
    #
    if len(response) == 0:
        logger.info('Create table: "%s"' % tab_name)
        # create table with CREATE TABLE IF NOT EXISTS for safety
        sql = 'CREATE TABLE IF NOT EXISTS "%s" (' % tab_name
        cols = []
        for col in tab_cols:
            if col in tab_types:
                cols.append('"' + col + '" ' + tab_types[col])
            else:
                cols.append('"' + col + '" ' + tab_types['default'])
        sql += ', '.join(cols) + ');'
        logger.debug('SQL=%s' % sql)
        try:
            cur.execute(sql)
            response = cur.fetchall()
            logger.insane('response=%s' % response)
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                logger.debug('Table "%s" already exists (race condition)'
                             % tab_name)
                response = []
            else:
                raise
    else:
        logger.debug('Table "%s" already exists' % tab_name)
        #
        # make sure columns are there
        for col in tab_cols:
            if col in tab_types:
                typ = tab_types[col]
            else:
                typ = tab_types['default']
            column_prepare(cur, tab_name, col, typ)
    return response


def db_prepare(cur):
    """
    Initialize database with required metadata tables.

    :param cur: Database cursor
    :type cur: sqlite3.Cursor

    Creates headers and files metadata tables if they don't exist.
    """
    #
    # test if database contains the metadata-tables, create if not
    #
    table_prepare(cur, tab_head_name, tab_head_cols, tab_head_types)
    table_prepare(cur, tab_file_name, tab_file_cols, tab_file_types)


def dbtable_name(station, table):
    """
    Generate standardized database table name.

    :param station: Station identifier
    :type station: str
    :param table: Table identifier
    :type table: str
    :return: Combined table name
    :rtype: str

    Creates table names using station:table format.
    """
    dbtable = dbsep.join([station, table])
    logger.insane('dbtable: %s' % dbtable)
    return dbtable


def ingest_toa5(params):
    """
    Ingest single TOA5 file into database with multiprocessing support.

    :param params: Tuple of (filename, station_name, table_name, free_id, force)
    :type params: tuple

    Process designed for multiprocessing that handles complete TOA5 file
    ingestion including header parsing, hash checking, and data insertion.
    """

    def _ingest_toa5_impl(params):
        """Inner implementation that handles the actual ingestion"""
        from . import eclogger
        eclogger.ensure_logging_setup()

        # unpack params
        infile, station_name, table_name, free_id, force = params

        conn = None
        try:
            # Create NEW connection for this worker process
            conn = sqlite3.connect(dbfile, timeout=900)
            # Enable WAL mode for better concurrent access
            conn.execute('PRAGMA journal_mode=WAL;')
            # Reduce synchronization for better performance
            conn.execute('PRAGMA synchronous=NORMAL;')
            # Increase cache size
            conn.execute('PRAGMA cache_size=10000;')

            cur = conn.cursor()

            logger.debug('Probing file: %s' % infile)
            if not ecfile.toa5_check(infile):
                logger.error('error reading data from %s' % infile)
                return False

            logger.normal('Ingesting file: %s' % infile)
            #
            # get file info
            header = ecfile.toa5_get_header(infile)
            inhash = ecfile.toa5_get_hash(infile)
            #
            # reject files with missing column names
            if min([len(i) for i in header['column_names']]) == 0:
                logger.error('empty column name. rejecting file %s' % infile)
                return False

            # command line overrides file info
            if station_name is not None:
                header['station_name'] = station_name
            if table_name is not None:
                header['table_name'] = table_name
            #
            # assemble name of db table and columns
            #
            dbtable = dbtable_name(header['station_name'],
                                   header['table_name'])
            dbcolumns = []
            for i in range(header['column_count']):
                if not header['column_names'][i] in ('TIMESTAMP', 'RECORD'):
                    dbcolumn = dbcolumn_name(header['column_names'][i],
                                             header['column_units'][i],
                                             header['column_sampling'][i])
                else:
                    dbcolumn = header['column_names'][i]
                dbcolumns.append(dbcolumn)
            logger.insane('dbcolumns: %s' % ', '.join(dbcolumns))
            #
            # store file information, check if file already exists first
            #
            # search if file is already in database
            sql = 'SELECT file_id,file_name FROM "%s" WHERE "file_hash" = "%s";' % (
                tab_file_name, inhash)
            logger.insane('SQL=%s' % sql)
            cur.execute(sql)
            response = cur.fetchall()
            logger.insane('response=%s' % response)

            if len(response) > 1:
                file_new = False
                # error
                logger.error(
                    'duplicate file signatures in database: ' + inhash)
                logger.info('file already known as :')
                for r in response:
                    file_id = str(r[0])
                    file_name = str(r[1])
                    logger.info('file already known as  ID={:s} ({:s})'.format(
                        file_id, file_name))
            elif len(response) == 1:
                file_new = False
                # file is already in database, get id
                file_id = str(response[0][0])
                file_name = str(response[0][1])
                logger.info('file already known as  ID={:s} ({:s})'.format(
                    file_id, file_name))
            else:
                file_new = True
                # Try to insert with the reserved ID, but handle conflicts gracefully
                for retry in range(MAX_RETRIES):
                    try:
                        # Use the pre-allocated ID, but check for conflicts
                        if retry == 0:
                            file_id = free_id
                        else:
                            # If conflict, get a new ID
                            file_id = get_free_index(cur, tab_file_name,
                                                     'file_id')

                        # Prepare values for insertion
                        values = []
                        for col in tab_file_cols:
                            if col == 'file_id':
                                values.append(str(file_id))
                            elif col == 'file_name':
                                values.append('"' + infile + '"')
                            elif col == 'file_hash':
                                values.append('"' + inhash + '"')
                            else:
                                values.append('')

                        # Try to insert
                        sql = 'INSERT INTO "%s" (%s) VALUES (%s);' % (
                            tab_file_name,
                            ', '.join(tab_file_cols),
                            ', '.join(values)
                        )
                        logger.insane('SQL=%s' % sql)
                        cur.execute(sql)
                        response = cur.fetchall()
                        logger.insane('response=%s' % response)
                        break  # Success, exit retry loop

                    except sqlite3.IntegrityError as e:
                        if "UNIQUE constraint failed" in str(
                                e) and retry < MAX_RETRIES - 1:
                            logger.debug(
                                f'ID {file_id} already taken, '
                                f'retrying with new ID (attempt {retry + 1})')
                            continue
                        else:
                            logger.error(
                                f'Failed to insert file after '
                                f'{MAX_RETRIES} attempts: {e}')
                            raise

            logger.debug('file_new=' + str(file_new) + ', force=' + str(force))
            #
            # abort if file was already processed
            #
            if not (file_new or force):
                logger.info('skipped previously processed file: %s' % infile)
                return True

            # store header information
            #
            # search if header is already database
            where = []
            for col in tab_head_cols:
                if col in header:
                    where.append('"' + col + '" = "' + str(header[col]) + '"')
                elif col == 'header_id':
                    pass
            sql = 'SELECT header_id FROM "%s" WHERE %s ;' % (
                tab_head_name, ' AND '.join(where))
            logger.insane('SQL=%s' % sql)
            cur.execute(sql)
            response = cur.fetchall()
            logger.insane('response=%s' % response)

            if len(response) > 1:
                # error
                raise ValueError('duplicate headers found in database')
            elif len(response) == 1:
                # header is already in database, get id
                head_id = str(response[0][0])
                logger.info('header already known as  ID=' + head_id)
            else:
                # not found --> get new id and store header
                head_id = get_free_index(cur, tab_head_name, 'header_id')
                logger.info('header new, stored under ID=' + str(head_id))
                # get values into list
                values = []
                for col in tab_head_cols:
                    if col in header:
                        values.append('"' + str(header[col]) + '"')
                    elif col == 'header_id':
                        values.append(str(head_id))
                    else:
                        values.append('""')
                # store data
                sql = 'INSERT INTO "%s" (%s) VALUES (%s);' % (
                    tab_head_name,
                    ', '.join(tab_head_cols),
                    ', '.join(values)
                )
                logger.insane('SQL=%s' % sql)
                cur.execute(sql)
                response = cur.fetchall()
                logger.insane('response=%s' % response)
            #
            # insert the data
            #
            # create db table if it doesn't exist
            # create columns in db table if then don't exist
            for col in tab_skeleton_cols:
                if col not in dbcolumns:
                    dbcolumns.append(col)
            dbtypes = tab_skeleton_types
            table_prepare(cur, dbtable, dbcolumns, dbtypes)

            #
            # read the whole file
            #
            with io.open(infile, 'rb') as fid:
                # skip header
                fid.readline()
                fid.readline()
                fid.readline()
                fid.readline()
                #
                # fix "_csv.Error: line contains NULL byte"
                # see: http://stackoverflow.com/a/27121288
                # "fid" -> "(line.replace('\0','') for line in fid)"
                #
                incsv = csv.DictReader((line.decode().replace(
                    '\0', '') for line in fid), fieldnames=dbcolumns)
                to_db = []
                for row in incsv:
                    row['TIMESTAMP'] = timestamp_fill(row['TIMESTAMP'])
                    values = []
                    for col in dbcolumns:
                        if col == 'head_id':
                            values.append(head_id)
                        elif col == 'file_id':
                            values.append(file_id)
                        else:
                            values.append(row[col])
                    to_db.append(tuple(values))

                # Use batch insert for better performance
                colnames = '"' + '","'.join(dbcolumns) + '"'
                placeholder = ', '.join(['?'] * len(dbcolumns))
                sql = 'INSERT OR REPLACE INTO "%s" (%s) VALUES (%s);' % (
                    dbtable, colnames, placeholder)
                logger.insane('SQL=%s' % sql)

                # Insert in chunks to avoid memory issues
                chunk_size = 1000
                for i in range(0, len(to_db), chunk_size):
                    chunk = to_db[i:i + chunk_size]
                    cur.executemany(sql, chunk)

                conn.commit()
                logger.info('Processed data lines: %i' % len(to_db))
                return True

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            logger.error(f'Error processing {infile}: {e}')
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    # Use the retry wrapper
    return with_retry(_ingest_toa5_impl, params)


def ingest_df(df, station_name=None, table_name=None, time_column=None):
    """
    Ingest pandas DataFrame into database.

    :param df: DataFrame containing data to store
    :type df: pandas.DataFrame
    :param station_name: Station identifier, defaults to None
    :type station_name: str, optional
    :param table_name: Table identifier, defaults to None
    :type table_name: str, optional
    :param time_column: Column to use for timestamps, defaults to None
    :type time_column: str, optional

    Safe version of ingest_df with comprehensive error handling for multiprocessing.
    """

    def _ingest_df_impl(df, station_name=None, table_name=None,
                        time_column=None):
        """Inner implementation that handles the actual DataFrame ingestion"""
        conn = None
        try:
            # Create connection with longer timeout for busy databases
            conn = sqlite3.connect(dbfile, timeout=30)
            # Better for concurrent access
            conn.execute('PRAGMA journal_mode=WAL;')
            cur = conn.cursor()

            # Process DataFrame
            dw = df.copy()

            # Handle required columns
            for col in tab_skeleton_cols:
                if col not in dw.columns:
                    if col == 'TIMESTAMP':
                        if time_column is not None and time_column in dw.columns:
                            dw['TIMESTAMP'] = [timestamp_fill(x.strftime('%Y-%m-%d %H:%M:%S.%f'))
                                for x in dw[time_column]]
                        else:
                            logger.error(
                                'dataframe to ingest must either have '
                                'TIMESTAMP or time_column must be a '
                                'valid column')
                            raise ValueError('Missing time column')
                    elif col == 'RECORD':
                        dw['RECORD'] = [x + 1 for x in range(len(dw.index))]
                    elif col in ['head_id', 'file_id']:
                        dw[col] = ""
                    else:
                        logger.warning(
                            f"{col} not in dataframe but in "
                            f"tab_skeleton_cols and is not handled")
            #
            # assemble name of db table and columns
            #
            # table name
            dbtable = dbtable_name(station_name, table_name)
            dbcolumns = dw.columns
            logger.insane('dbcolumns: %s' % ', '.join(dbcolumns))
            #
            # create db table if it doesn't exist
            #
            # create db table if it doesn't exist
            dbtypes = tab_skeleton_types.copy()
            dbtypes['begin'] = 'text'
            dbtypes['end'] = 'text'

            table_prepare(cur, dbtable, dbcolumns, dbtypes)
            #
            # write the whole dataframe
            #
            to_db = []
            for row in dw.to_dict(orient='records'):
                values = []
                for col in dbcolumns:
                    if col == 'head_id':
                        values.append('null')
                    elif col == 'file_id':
                        values.append('null')
                    elif row[col] is None:
                        values.append('null')
                    elif type(row[col]) in [str, bytes]:
                        values.append(row[col])
                    elif (type(row[col]) is pd.Timestamp or
                          type(row[col]) is pd.DatetimeIndex or
                          type(row[col]) is np.datetime64):
                        try:
                            values.append(timestamp_fill(pd.Timestamp(
                                row[col]).strftime("%Y-%m-%d %H:%M:%S.%f")))
                        except:
                            values.append('null')
                    else:
                        try:
                            if np.isfinite(row[col]):
                                values.append(str(row[col]))
                            else:
                                values.append('null')
                        except TypeError:
                            #                    print(type(row[col]), row[col])
                            if row[col] is not None:
                                logger.warning('unknown value to ingest into database: {!s:s}={!s:s} ({!s:s})'.format(
                                    str(col), str(row[col]),type(row[col])))
                            else:
                                logger.warning(
                                    'unknown value to ingest into database: '
                                    '{!s:s}=None'.format(
                                        str(col)))
                            values.append('null')

                to_db.append(tuple(values))
            ##
            colnames = '"' + '","'.join(dbcolumns) + '"'
            placeholder = ', '.join(['?'] * len(dbcolumns))
            sql = 'INSERT OR REPLACE INTO "%s" (%s) VALUES (%s);' % (
                dbtable, colnames, placeholder)
            logger.insane('SQL=%s' % sql)
            cur.executemany(sql, to_db)
            rows = cur.fetchall()
            logger.insane('rows=%s' % rows)

            conn.commit()
            logger.info(f'Successfully ingested {len(dw)} rows')
            return True

        except Exception as e:
            # try to revert on error
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            # try to close
            if conn:
                try:
                    conn.close()
                except:
                    pass

    # Use the retry wrapper
    return with_retry(_ingest_df_impl, df, station_name=station_name,
                      table_name=table_name, time_column=time_column)


def init_worker_process(database_path):
    """Worker connects to existing database - does NOT create it."""
    global dbfile
    dbfile = database_path

    from . import eclogger
    eclogger.ensure_logging_setup()

    # Verify database exists (should be created by main process)
    if not os.path.exists(dbfile):
        logger.error(f'Database not found: {dbfile}')
        raise FileNotFoundError(
            'Main process should have created database')

    # ONLY verify connection - do NOT call db_prepare()
    try:
        conn = sqlite3.connect(dbfile, timeout=900)
        cur = conn.cursor()

        # Just verify tables exist
        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        if len(tables) == 0:
            logger.error('Database has no tables!')
            raise RuntimeError('Database not properly initialized')

        conn.close()
        logger.debug(f'Worker {os.getpid()} connected to existing database')
    except Exception as e:
        logger.error(f'Worker {os.getpid()} failed to connect: {e}')
        raise

def ingest(infiles, force=False, nproc=0, station_name=None,
           table_name=None, progress=100):
    """
    Ingest multiple TOA5 files with parallel processing support.

    :param infiles: List of file paths to process
    :type infiles: list
    :param force: Force reprocessing of existing files, defaults to False
    :type force: bool, optional
    :param nproc: Number of parallel processes (0=auto), defaults to 0
    :type nproc: int, optional
    :param station_name: Override station name, defaults to None
    :type station_name: str, optional
    :param table_name: Override table name, defaults to None
    :type table_name: str, optional
    :param progress: Progress reporting weight, defaults to 100
    :type progress: int, optional

    Coordinates parallel ingestion with ID reservation and progress tracking.
    """
    # number of processes
    logger.normal('start ingesting data ino database {:s}'.format(dbfile))
    # verbose info
    if station_name is not None:
        logger.debug(
            'overriding station name in files with {:s}'.format(
                station_name))
    if table_name is not None:
        logger.debug(
            'overriding table name in files with {:s}'.format(table_name))

    # Create database directory if needed
    db_dir = os.path.dirname(dbfile)
    if db_dir != '' and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # CRITICAL: Ensure database is initialized BEFORE multiprocessing
    logger.info('preparing database {:s}'.format(dbfile))
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    db_prepare(cur)
    logger.debug('done preparing database')

    # build parameter list
    logger.info('building file-parameter list')
    pro_para = []
    reserved_ids = []
    file_progress = float(progress) / float(len(infiles))

    for infile in sorted(infiles):
        free_id = get_free_index(cur, tab_file_name, 'file_id',
                                 reserved_ids)
        reserved_ids.append(free_id)
        pro_para.append(
            (infile, station_name, table_name, free_id, force))
    #
    # close db for now
    #
    conn.close()
    logger.debug('done building file-parameter list')
    #
    # start parallel processes
    #
    if nproc == 1:
        logger.info('starting sequential processing of files')
        for i, p in enumerate(pro_para):
            try:
                ingest_toa5(p)
                logger.info('[{:3d}%]'.format(
                    int(float(i + 1) * 100. / float(len(pro_para)))))
            except Exception as e:
                logger.error(f'Failed to process {p[0]}: {e}')
    else:
        logger.info('starting {:d} parallel processes'.format(nproc))

        # Force spawn method on all platforms for better isolation
        try:
            if platform.system() == 'Windows':
                # Force spawn method on Windows for better isolation
                set_start_method('spawn', force=True)
            else:
                # Use fork on Unix-like systems, but be careful
                set_start_method('fork', force=True)
        except RuntimeError:
            pass  # Method already set

        # Create pool with proper initialization
        pool_args = {
            'initializer': init_worker_process,
            'initargs': (dbfile,),
            'maxtasksperchild': 50
            # Restart workers periodically to prevent memory leaks
        }

        if nproc == 0:
            pool = Pool(**pool_args)
        else:
            pool = Pool(nproc, **pool_args)

        try:
            # Process files with error handling
            results = []
            for i, result in enumerate(pool.imap(ingest_toa5, pro_para)):
                results.append(result)
                ec.progress_increment(file_progress)
        except Exception as e:
            logger.error(f'Multiprocessing error: {e}')
            raise
        finally:
            pool.close()
            pool.join()

    logger.info('done ingesting data into database')


def dbcolumn_name(n, u, s):
    """
    Generate database column name with metadata.

    :param n: Column name
    :type n: str
    :param u: Units
    :type u: str
    :param s: Sampling information
    :type s: str
    :return: Combined column identifier
    :rtype: str

    Creates column names including measurement units and sampling metadata.
    """
    dbc = dbsep.join([n, u, s])
    return dbc


def dbcolumn_split(dbcolumn, check=True):
    """
    Parse database column name into components.

    :param dbcolumn: Database column identifier
    :type dbcolumn: str
    :param check: Whether to validate skeleton columns, defaults to True
    :type check: bool, optional
    :return: Tuple of (name, units, sampling)
    :rtype: tuple

    Extracts measurement metadata from standardized column names.
    """
    dbcolumn = dbcolumn + '::'
    (name, unit, sampling) = dbcolumn.split(':')[0:3]
    # skip the metadata columns
    if check and not (name in tab_skeleton_cols):
        if unit == '' and sampling == '':
            # in case of column name (not three colon-separated fields)
            logger.debug(
                'column name "%s" does not contain required fields' % dbcolumn)
            # add empty "fields"
        # split db table name into column name,units and sampling
    return name, unit, sampling


def db_get_columns(cur, dbtable, check=True):
    """
    Retrieve column names from database table.

    :param cur: Database cursor
    :type cur: sqlite3.Cursor
    :param dbtable: Table name
    :type dbtable: str
    :param check: Whether to validate metadata fields, defaults to True
    :type check: bool, optional
    :return: List of column names
    :rtype: list

    Gets data columns excluding metadata fields.
    """
    #
    # get the column names of db table
    #
    dbcolumns = []
    # get info
    response = exe_sql(cur, 'PRAGMA table_info("%s");' % dbtable)
    # loop the response entries
    for field in response:
        if check and len(field) < 6:
            # abort in case of invalid fields
            logger.error('column "%s" does not contain required fields' %
                         response.index(field))
        else:
            # column name is in field #1
            dbcolumn = field[1]
            name = dbcolumn_split(dbcolumn, check=check)[0]
            if not (name in tab_skeleton_meta):
                dbcolumns.append(dbcolumn)
    return dbcolumns


def db_get_header(cur, opt, dbtable, time_condition):
    """
    Retrieve header information for specified table and time period.

    :param cur: Database cursor
    :type cur: sqlite3.Cursor
    :param opt: Header selection option ('f'=first, 'l'=last, 'u'=unique, 'm'=majority)
    :type opt: str
    :param dbtable: Table name
    :type dbtable: str
    :param time_condition: SQL time condition clause
    :type time_condition: str
    :return: Dictionary with header information
    :rtype: dict

    Selects appropriate header metadata based on temporal constraints.
    """
    #
    # get one of the header(s)
    #     associated with table dbtable
    #     that occur in the specified time window
    #
    # opt: which header to choose
    #      f -> first
    #      l -> last
    #      u -> synthesize header from unique entries a placeholders
    #      m -> majority header
    #
    fields = tab_head_cols
    if 'header_id' in fields:
        fields.remove('header_id')
    lf = len(fields)
    #
    # get header ids
    #
    response = exe_sql(cur, ('SELECT "head_id" FROM "%s" ' + time_condition
                             + ';') % dbtable)
    header_ids = [tup[0] for tup in response]
    # print "headers      : "+str(set(header_ids))
    # print "first header :"+str(header_ids[0])
    # print "last  header :"+str(header_ids[-1])
    cols = ', '.join(['"' + col + '"' for col in fields])
    ids = ', '.join([str(i) for i in list(set(header_ids))])
    response = exe_sql(cur,
                       'SELECT %s FROM headers WHERE header_id IN ( %s );'
                       % (cols, ids))
    # for i in range(0,len(response[0])):
    #  vals=[tup[i] for tup in response ]
    #  print set(vals)
    get_header = {}
    if len(response) > 0:
        if opt in ['f', 'l', 'm']:
            if opt == 'l':
                idx = len(response) - 1
            elif opt == 'm':
                idx = Counter(response).most_common()
            else:  # opt == 'f' is default
                idx = 0
            for i in range(lf):
                get_header[fields[i]] = response[idx][i]
        elif opt == 'u':
            for i in range(lf):
                vals = [tup[i] for tup in response]
                if vals == 1:
                    get_header[fields[i]] = vals[0]
                else:
                    get_header[fields[i]] = u''
        else:
            logger.critical('option %s not among allowed options' % opt)
    else:
        logger.error('no headers found')
    return get_header


def db_get_values(cur, dbtable, columns, time_condition, check=True):
    """
    Retrieve data values from database table with time filtering.

    :param cur: Database cursor
    :type cur: sqlite3.Cursor
    :param dbtable: Table name
    :type dbtable: str
    :param columns: Columns to retrieve (None for all)
    :type columns: list or None
    :param time_condition: SQL time condition clause
    :type time_condition: str
    :param check: Whether to validate columns, defaults to True
    :type check: bool, optional
    :return: Tuple of (column_names, data_rows)
    :rtype: tuple

    Retrieves measurement data with temporal filtering and column validation.
    """
    #  get_header=db_get_header(cur,'l',dbtable,time_condition)
    dbcolumns = db_get_columns(cur, dbtable, check=check)
    if columns is None:
        columns = dbcolumns
    if not all([col in dbcolumns for col in columns]):
        for col in columns:
            if col not in dbcolumns:
                logger.error('no column "%s" data in table "%s"' %
                             (col, dbtable))
                raise ValueError
    #
    # read the data from db
    #
    # make sure skeleton columns are contained but not duplicated
    getcols = columns + list(set(tab_skeleton_index) - set(columns))
    #
    colstr = ', '.join(['"' + col + '"' for col in getcols])
    response = exe_sql(cur, ('SELECT %s FROM "%s" ' + time_condition
                             + ';') % (str(colstr), dbtable))
    return getcols, response


def conf_to_db(conf):
    """
    Store configuration parameters in database.
    """

    def _conf_to_db_impl(conf):
        """Inner implementation that handles the actual config storage"""
        conn = None
        try:
            # Create connection with longer timeout for busy databases
            conn = sqlite3.connect(dbfile, timeout=30)
            # Better for concurrent access
            conn.execute('PRAGMA journal_mode=WAL;')
            cur = conn.cursor()
            #
            # test if table already exists, create it if not
            #
            table_prepare(cur, tab_conf_name, tab_conf_cols, tab_conf_types)
            #
            # put the data
            #
            colnames = '"' + '","'.join(tab_conf_cols) + '"'
            for k, v in conf.items():
                #
                # escape quotes by doubling them
                vv = ''.join(x if x != '"' else '""' for x in str(v))
                values = '"' + '","'.join((str(k), vv)) + '"'
                sql = 'INSERT OR REPLACE INTO "%s" (%s) VALUES (%s);' % (
                    tab_conf_name, colnames, values)
                logger.insane('SQL=%s' % sql)
                cur.execute(sql)

            conn.commit()
            logger.debug('stored config in database')
            return True
        except Exception as e:
            # try to revert on error
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            # try to close conn
            if conn:
                try:
                    conn.close()
                except:
                    pass

    # Use the retry wrapper
    return with_retry(_conf_to_db_impl, conf)


def conf_from_db():
    """
    Retrieve configuration parameters from database.

    :return: Configuration object with stored parameters
    :rtype: Config

    Restores processing configuration for workflow continuation.
    """
    #
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    #
    colnames = '"' + '","'.join(tab_conf_cols) + '"'
    sql = 'SELECT %s FROM "%s" ;' % (colnames, tab_conf_name)
    logger.insane('SQL=%s' % sql)
    cur.execute(sql)
    rows = cur.fetchall()
    logger.insane('rows=%s' % rows)
    #
    #values = {str(k): str(v) for k, v in rows}
    #
    known_parameters = [y.upper() for y in ecconfig.defaults.keys()]
    values = {}
    for k, v in rows:
        if not str(k).upper() in known_parameters:
            logging.warning(f'discarding unknown parameter "{k}"')
        else:
            values[str(k)] = str(v)
    logger.debug('got config from database')

    if any(x.upper() not in [y.upper() for y in ecconfig.defaults.keys()]
           for x in values.keys()):
        logger
    #
    # clean up
    conn.close()
    #
    conf = ecconfig.Config(values)
    #
    return conf


def list_tables():
    """
    List all tables in database.

    :return: List of table names
    :rtype: list

    Provides inventory of available data tables.
    """
    #
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    #
    # test if table already exists, create it if not
    #
    rows = exe_sql(
        cur, 'SELECT "name" FROM "sqlite_master" WHERE type="table";')
    #
    # make list
    #
    if len(rows) > 0:
        re = [str(x[0]) for x in rows]
    else:
        re = []
    #
    # clean up
    conn.close()
    #
    return re


def retrieve_columns(station_name, table_name):
    """
    Get available columns for specified station and table.

    :param station_name: Station identifier
    :type station_name: str
    :param table_name: Table identifier
    :type table_name: str
    :return: List of column names
    :rtype: list

    Returns measurement variables available in specified dataset.
    """
    #
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    #
    # table name
    dbtable = dbtable_name(station_name, table_name)
    #
    # read database
    columns = db_get_columns(cur, dbtable)
    #
    # clean up
    conn.close()
    return columns


def mark_finished():
    """
    Mark processing as completed in database.

    Creates completion marker for workflow status tracking.
    """
    #
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    #
    # table name
    table_prepare(cur, 'out:files', ['date'], {'date': 'text primary key'})
    #
    # clean up
    conn.close()
    return


def retrieve_df(station_name, table_name, columns=None, tbegin=None,
                tend=None):
    """
    Retrieve data as pandas DataFrame with temporal filtering.

    :param station_name: Station identifier
    :type station_name: str
    :param table_name: Table identifier
    :type table_name: str
    :param columns: Columns to retrieve (None for all), defaults to None
    :type columns: list, optional
    :param tbegin: Start time for filtering, defaults to None
    :type tbegin: datetime, pd.Timestamp, or str, optional
    :param tend: End time for filtering, defaults to None
    :type tend: datetime, pd.Timestamp, or str, optional
    :return: DataFrame with requested data
    :rtype: pandas.DataFrame

    Main data retrieval interface with automatic type conversion and indexing.
    """
    logger.debug('retrieving dataframe {:s} {:s}'.format(
        station_name, table_name))
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    #
    # format time condition
    time_condition = ''
    condition = []
    if tbegin is not None:
        if isinstance(tbegin, pd.Timestamp):
            tbegin = tbegin.to_pydatetime()
        elif isinstance(tbegin, (str, bytes)):
            tbegin = dt.datetime.strptime(tbegin, tfmt)
        begin_str = timestamp_fill(dt.datetime.strftime(tbegin, tfmt))
        condition.append('"TIMESTAMP" > "%s" ' % begin_str)
    if tend is not None:
        if isinstance(tend, pd.Timestamp):
            tend = tend.to_pydatetime()
        elif isinstance(tend, (str, bytes)):
            tend = dt.datetime.strptime(tend, tfmt)
        end_str = timestamp_fill(dt.datetime.strftime(tend, tfmt))
        condition.append('"TIMESTAMP" <= "%s" ' % end_str)
    if len(condition) > 0:
        time_condition = 'WHERE ' + 'AND'.join(condition)
    #
    # wozu das???
    # ???  cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #
    # table name
    dbtable = dbtable_name(station_name, table_name)
    #
    # read database
    logger.insane('requested columns:' + str(columns))
    outcols, response = db_get_values(
        cur, dbtable, columns, time_condition, check=False)
    logger.insane('obtained  columns:' + str(outcols))
    #
    # convert to dataframe
    df = pd.DataFrame(response, columns=outcols)
    df = df.map(lambda x: ec.unquote(
        x) if isinstance(x, (str, bytes)) else x)

    logger.insane(df.columns)
    for c in df:
        #         if (c in ['TIMESTAMP', 'begin', 'end'] or
        #            not pd.api.types.is_numeric_dtype(df.dtypes[c])):
        #            try:
        #                df[c] = pd.to_datetime(df[c], utc=True)
        #            except:
        #                df[c] = pd.to_numeric(df[c], errors='coerce')
        if c in ['TIMESTAMP', 'begin', 'end']:
            df[c] = pd.to_datetime(df[c], utc=True)
        else:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    #
    # clean up
    conn.close()
    return df


def retrieve_time_range(station_name, table_name):
    """
    Get temporal extent of data in specified table.

    :param station_name: Station identifier
    :type station_name: str
    :param table_name: Table identifier
    :type table_name: str
    :return: Tuple of (earliest_time, latest_time)
    :rtype: tuple

    Efficiently determines data coverage for time range planning.
    """
    logger.debug('retrieving from dataframe {:s} {:s}'.format(
        station_name, table_name))
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    #
    # table name
    dbtable = dbtable_name(station_name, table_name)
    #
    # read database
    getcols = tab_skeleton_index
    colstr = ', '.join(
        ['%s(%s)' % (mm, col) for mm in ["MIN", "MAX"] for col in getcols])
    response = exe_sql(cur,
                       ('SELECT %s FROM "%s" ;') % (colstr, dbtable))
    #
    conn.close()
    #
    # convert to dataframe
    df = pd.DataFrame(response,
                      columns=[x.strip() for x in colstr.split(',')])
    logger.insane(df.columns)
    for c in df:
        if 'TIMESTAMP' in c:
            df[c] = pd.to_datetime(df[c], utc=True)
        else:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    time_begin = df['MIN(TIMESTAMP)'][0]
    time_end = df['MAX(TIMESTAMP)'][0]
    logger.insane(format([time_begin, time_end]))

    return time_begin, time_end
