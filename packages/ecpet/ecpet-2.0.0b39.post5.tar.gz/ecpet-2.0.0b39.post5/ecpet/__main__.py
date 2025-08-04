#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2021  Clemens Drüe, Universität Trier
#
"""
EC-PeT Module Entry Point
=========================

Entry point for running EC-PeT as a module with 'python -m ecpet'.
Delegates to the main user interface function.
"""

from . import ecmain

if __name__ == '__main__':
    ecmain.user_interface()
