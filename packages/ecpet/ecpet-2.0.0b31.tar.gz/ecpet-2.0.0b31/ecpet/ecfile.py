# -*- coding: utf-8 -*-
"""
EC-PeT File Operations Module
=============================

File handling utilities for Campbell Scientific TOA5 data logger files and
eddy-covariance data processing workflows. Provides efficient reading, writing,
and validation of TOA5 format files commonly used in meteorological and
flux tower measurements.

The module handles:
    - File discovery with pattern matching and glob support
    - TOA5 format validation and header parsing
    - Efficient timestamp extraction from large files
    - File integrity verification with MD5 checksums
    - Campbell Scientific formatting conventions
    - Time range analysis across multiple files

"""
import csv
import glob
import hashlib
import io
import logging
import os
import re

import pandas as pd

from .ecutils import getfields

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
#
# find files from pattern list
#
def find(path, names):
    """
    Find files matching patterns in specified directory.

    :param path: Directory path to search in
    :type path: str
    :param names: File patterns or names to search for
    :type names: str, list, or None
    :return: List of filenames in TOA5 format
    :rtype: list

    Supports direct filenames, glob patterns, and directory listings.
    Returns only files that pass TOA5 format validation.
    """
    # make names a non-empty list
    if names is None:
        names = ['']
    elif isinstance(names, str):
        names = [names]
    elif len(names) == 0:
        names = ['']

    # Use list for efficient appending
    file_list = []

    # Pre-compute path for reuse
    for name in names:
        pattern = os.path.join(path, name)
        logger.debug('searching for "%s"' % pattern)
        # Check if path exists (single filesystem call)
        # if filename exists in RawDir
        if os.path.exists(pattern):
            # if it is a file -> use only this one
            if os.path.isfile(pattern):
                file_list.append(name)
                logger.debug('found data file %s' % pattern)
            # if it is a dir -> use all files in this dir (but no recursion)
            elif os.path.isdir(pattern):
                try:
                    new_list = os.listdir(pattern)
                    logger.debug(
                        'found %i data files in %s' % (len(new_list),
                                                       pattern))
                    # Extend is more efficient than repeated appends
                    file_list.extend(
                        os.path.join(name, file) for file in new_list)
                except OSError:
                    logger.warning(
                        'Error reading directory: %s' % pattern)
        else:
            # if RawDir/filename does not exist, assume it's a glob pattern
            try:
                new_list = [
                    os.path.relpath(file, path)
                    for file in glob.glob(pattern)
                    if os.path.isfile(file)
                ]
                logger.debug(
                    'found %i data files matching %s' % (len(new_list),
                                                         pattern))
                file_list.extend(new_list)
            except OSError:
                logger.warning('Error with glob pattern: %s' % pattern)

    logger.debug('found %i files in total' % len(file_list))

    # Filter for TOA5 files - pre-compute full paths to avoid repeated joins
    toa5_list = []
    for filename in file_list:
        full_path = os.path.join(path, filename)
        if toa5_check(full_path):
            toa5_list.append(filename)

    logger.debug('found %i files in TOA5 format' % len(toa5_list))
    return toa5_list

# ----------------------------------------------------------------
#
# check if a file is in TOA5-format
#


def toa5_check(filename):
    """
    Check if file is in Campbell Scientific TOA5 format.

    :param filename: Path to file to check
    :type filename: str
    :return: True if file is TOA5 format
    :rtype: bool
    """
    try:
        with io.open(filename, 'r', encoding='latin1') as fid:
            # Only read the first 5 characters we need
            magic = fid.read(5)
            if len(magic) < 5:
                logger.debug('file too short: %s' % filename)
                return False
            magic = magic[1:5]  # Skip first character, get next 4
    except (IOError, UnicodeDecodeError) as e:
        logger.warning('Error reading file: %s - %s' % (filename, str(e)))
        return False

    if magic != 'TOA5':
        logger.debug('expected "TOA5", got "%s"' % magic)
        logger.warning('not a TOA5 file: %s' % filename)
        return False

    return True

# ----------------------------------------------------------------
#
# get TOA5-file header information
#


def toa5_get_header(filename):
    """
    Extract header information from TOA5 file.

    :param filename: Path to TOA5 file
    :type filename: str
    :return: Dictionary containing header information
    :rtype: dict

    Returns station name, logger info, column names, units, and sampling info.
    Column names have parentheses replaced with underscores.
    """
    header = {}
    with io.open(filename, 'r') as fid:
        # read header line 1
        fields = getfields(fid.readline())
        header['station_name'] = fields[1]
        header['logger_name'] = fields[2]
        header['logger_serial'] = fields[3]
        header['logger_os'] = fields[4]
        header['logger_prog'] = fields[5]
        header['logger_sig'] = fields[6]
        header['table_name'] = fields[7]
        # read header line 2
        columns = getfields(fid.readline())
        columnnames = []
        for col in columns:
            columnnames.append(re.sub(r'[\(\)]', '_', col))
        header['column_count'] = len(columnnames)
        header['column_names'] = columnnames
        # read header line 3
        header['column_units'] = getfields(fid.readline())
        # read header line 4
        header['column_sampling'] = getfields(fid.readline())
    return header

# ----------------------------------------------------------------
#
# get checksum of TOA5-file
#


def toa5_get_hash(filename):
    """
    Calculate MD5 hash of TOA5 file.

    :param filename: Path to TOA5 file
    :type filename: str
    :return: MD5 hash as hexadecimal string
    :rtype: str
    """
    blocksise = 128
    hasher = hashlib.md5()
    with open(filename, 'rb') as afile:
        buf = afile.read(blocksise)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksise)
    return hasher.hexdigest()

# ----------------------------------------------------------------
#
# get TOA5-file time information
#


def toa5_get_times(filename, count=False):
    """
    Extract first and last timestamps from TOA5 file.

    :param filename: Path to TOA5 file
    :type filename: str
    :param count: Whether to count total records, defaults to False
    :type count: bool, optional
    :return: List with [first_time, last_time] or [first_time, last_time, count]
    :rtype: list

    Uses efficient file seeking to find last timestamp without reading entire file.
    """
    with io.open(filename, 'rb') as fid:
        # skip header
        for i in range(4):
            fid.readline()
        first_line = fid.readline().decode()
        if count:
            n = 1
            for x in fid.readlines():
                last_line = x.decode()
                n += 1
        else:
            last_line = None
            offs = -100
            while last_line is None:
                fid.seek(offs, os.SEEK_END)
                lines = fid.readlines()
                if len(lines) > 1:
                    last_line = lines[-1].decode()
                else:
                    offs *= 2
        first = getfields(first_line)[0]
        last = getfields(last_line)[0]
        if count:
            info = [first, last, n]
        else:
            info = [first, last]
    return info

# ----------------------------------------------------------------
#
# get time information from a list of files
#
#


def get_time_range(d, fl):
    """
    Determine overall time range from list of TOA5 files.

    :param d: Directory containing files
    :type d: str
    :param fl: List of filenames
    :type fl: list
    :return: List with [earliest_time, latest_time] as pandas Timestamps
    :rtype: list
    """
    time_range = [pd.Timestamp.now(tz='UTC'), pd.to_datetime(
        '1970-01-01 00:00:00', utc=True)]
    files = [os.path.join(d, x) for x in fl]
    for f in files:
        fs = toa5_get_times(f)
        ft = [pd.to_datetime(x[0:16]+':00', utc=True) for x in fs]
        time_range[0] = min(time_range[0], ft[0])
        time_range[1] = max(time_range[1], ft[1])
    return time_range

# ----------------------------------------------------------------
#
# write TOA5-file header information
#


def toa5_put_header(file, header):
    """
    Write TOA5 header information to file.

    :param file: Path to output file
    :type file: str
    :param header: Dictionary containing header information
    :type header: dict

    Creates 4-line TOA5 header with station info, column names, units, and sampling.
    """
    with io.open(file, 'wb') as fid:
        csvwriter = csv.writer(fid, delimiter=',', quotechar='"',
                               quoting=csv.QUOTE_ALL)
        # read header line 1
        fields = ['TOA5',
                  header['station_name'],
                  header['logger_name'],
                  header['logger_serial'],
                  header['logger_os'],
                  header['logger_prog'],
                  header['logger_sig'],
                  header['table_name']]
        csvwriter.writerow([str(f) for f in fields])
        # read header line 2
        csvwriter.writerow([str(f) for f in header['column_names']])
        # read header line 3
        csvwriter.writerow([str(f) for f in header['column_units']])
        # read header line 4
        csvwriter.writerow([str(f) for f in header['column_sampling']])


# ----------------------------------------------------------------
#
# format numbers in Campbell Scientific TOA style
#

def cs_style(v):
    """
    Format values in Campbell Scientific TOA5 style.

    :param v: Value to format
    :type v: int, float, str, bytes, or None
    :return: Formatted string representation
    :rtype: str

    Applies precision rules based on magnitude and strips trailing zeros.
    """
    if type(v) == bytes:
        s = '"'+str(v).rstrip('0').rstrip('.')+'"'
    elif type(v) == str:
        s = '"'+v.rstrip('0').rstrip('.')+'"'
    elif type(v) == float:
        if abs(v) < 0.001:
            s = '%15.10f' % v
        elif abs(v) < 0.01:
            s = '%15.9f' % v
        elif abs(v) < 0.1:
            s = '%15.8f' % v
        elif abs(v) < 1.:
            s = '%15.7f' % v
        else:
            s = '%15.7g' % v
        if '.' in s:
            s = s.rstrip('0').rstrip('.')
    elif type(v) == int:
        s = '%15i' % v
    elif v is None:
        s = '"NAN"'
    else:
        s = str(v)
    return s.lstrip()
