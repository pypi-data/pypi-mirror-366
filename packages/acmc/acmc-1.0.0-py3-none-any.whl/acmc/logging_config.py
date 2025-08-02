"""
logging_config.py

This module defines functions to setup logging for acmc across all module.

"""

import pandas as pd
import logging

DEFAULT_LOG_FILE = "acmc.log"
"""The default acmc application log filename."""


def setup_logger(log_level: int = logging.INFO):
    """Sets up acmc logger as a singleton outputing to file and sysout syserr."""

    # Create a logger
    logger = logging.getLogger("acmc_logger")
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        # Create a file handler that logs to a file
        file_handler = logging.FileHandler(DEFAULT_LOG_FILE)
        file_handler.setLevel(logging.INFO)

        # Create a stream handler that prints to the console
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)

        # Create a formatter for how the log messages should look
        # Add the formatter to both handlers
        file_formatter = logging.Formatter(
            "%(asctime)s - - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        stream_formatter = logging.Formatter("[%(levelname)s] - %(message)s")
        stream_handler.setFormatter(stream_formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger


def set_log_level(log_level: int):
    """Sets the log level for the acmc logger.

    Args:
        log_level (int): log level from the python logging libraru

    """

    logger = logging.getLogger("acmc_logger")
    logger.setLevel(log_level)

    # Also update handlers to match the new level
    for handler in logger.handlers:
        handler.setLevel(log_level)
