#!/usr/bin/env python3

import logging
import os
from datetime import datetime

import colorlog


class ColoredFormatterWithTimezone(colorlog.ColoredFormatter):
    def __init__(self, *args, tz=None, **kwargs):
        super().__init__(*args, **kwargs)

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return s


def setup_logging(script_name: str) -> logging.Logger:
    """
    Sets up logging with both file and console output.

    :param script_name: Name of the script for log file naming
    :type script_name: str
    :return: Configured logger
    :rtype: logging.Logger
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Create a timestamp for the log file
    # timestamp = ...

    # Create formatters

    console_formatter = ColoredFormatterWithTimezone(
        "%(log_color)s%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    logger = logging.getLogger("colored")
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger
