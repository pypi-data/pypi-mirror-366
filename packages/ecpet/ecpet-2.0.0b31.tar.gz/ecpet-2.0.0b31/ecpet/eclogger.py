#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EC-PeT Custom Logging Module
============================

Custom logging levels and setup for EC-PeT that work reliably
with multiprocessing across different Python versions.

Provides additional logging levels:
    - NORMAL (25): For normal output usually shown by print statements
    - INSANE (5): For debugging messages in frequently executed loops

@author: clemens
"""

import logging


def setup_custom_logging():
    """
    Setup custom logging levels that work with multiprocessing.

    Additional logging levels are:
    
    - logging.NORMAL: for normal output usually shown by ``print``
      but routed to the log instead
    - logging.INSANE: for debugging messages that are produced
      in loops that are executed really often.

    """

    # Add custom levels
    logging.INSANE = 5
    logging.addLevelName(logging.INSANE, 'INSANE')
    logging.NORMAL = 25
    logging.addLevelName(logging.NORMAL, 'NORMAL')

    # Create module-level functions instead of monkey-patching
    def insane(logger, message, *args, **kwargs):
        if logger.isEnabledFor(logging.INSANE):
            logger._log(logging.INSANE, message, args, **kwargs)

    def normal(logger, message, *args, **kwargs):
        if logger.isEnabledFor(logging.NORMAL):
            logger._log(logging.NORMAL, message, args, **kwargs)

    # Store the functions in the logging module for global access
    logging.insane = insane
    logging.normal = normal

    # Monkey patch the Logger class (but check if already done)
    if not hasattr(logging.Logger, 'insane'):
        def logger_insane(self, message, *args, **kwargs):
            if self.isEnabledFor(logging.INSANE):
                self._log(logging.INSANE, message, args, **kwargs)

        def logger_normal(self, message, *args, **kwargs):
            if self.isEnabledFor(logging.NORMAL):
                self._log(logging.NORMAL, message, args, **kwargs)

        logging.Logger.insane = logger_insane
        logging.Logger.normal = logger_normal


def ensure_logging_setup():
    """
    Ensure that the custom logging levels are set up.

    Call this in multiprocessing workers for Python 3.13+.
    Safe to call multiple times.
    """
    if (not hasattr(logging.Logger, 'insane') or
            not hasattr(logging.Logger, 'normal')):
        setup_custom_logging()
