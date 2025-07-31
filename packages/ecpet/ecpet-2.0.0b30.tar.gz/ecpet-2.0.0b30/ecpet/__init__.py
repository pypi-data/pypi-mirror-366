#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2021  Clemens Drüe, Universität Trier
#
"""
EC-PeT: Eddy-Covariance Processing Toolkit
===========================================

A comprehensive Python package for processing eddy-covariance flux tower data.
Provides complete workflow from raw datalogger files to quality-controlled
surface-atmosphere exchange measurements following established micrometeorological
principles and best practices.

Key Modules:
    - ecengine: Main processing orchestration and command-line interface
    - ecpack: Core flux calculation algorithms and atmospheric corrections
    - ecconfig: Configuration management with validation and defaults
    - ecdb: SQLite database operations for data persistence
    - ecfile: TOA5 file operations and format handling
    - ecplan: Planar fit coordinate system corrections
    - ecpost: Quality control and flux validation
    - ecpre: Data preprocessing and despiking

License:
    Copyright (C) Clemens Drüe, Universität Trier
    See LICENSE.txt file for terms and conditions.
"""

# make version number public
from ._version import __release__ as __version__

def main():
    """
    Entry point for command-line interface.

    Launches the main EC-PeT user interface for interactive
    processing workflow management.
    """
    from . import ecmain
    ecmain.user_interface()

