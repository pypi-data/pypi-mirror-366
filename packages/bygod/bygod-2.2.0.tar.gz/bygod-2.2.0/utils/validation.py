#!/usr/bin/env python3

import argparse
import logging
import re

from meaningless.utilities.common import BIBLE_TRANSLATIONS

logger = logging.getLogger("colored")


def validate_bibles(value: str) -> list:
    """
    Validate Bible translation codes.

    :param value: Comma-separated list of Bible translation codes
    :type value: str
    :return: List of validated translation codes
    :rtype: list
    :raises: argparse.ArgumentTypeError if any translation is invalid
    """
    logger.debug(f"validate_bibles called with value: {value}")
    no_whitespace = re.sub(r"\s+", "", value.upper())
    values = no_whitespace.split(",")
    if any(v in BIBLE_TRANSLATIONS.keys() for v in values):
        return values
    raise argparse.ArgumentTypeError("Invalid or unsupported Bible.")


def validate_format(value: str) -> list:
    """
    Validate output format types.

    :param value: Comma-separated list of format types
    :type value: str
    :return: List of validated format types
    :rtype: list
    :raises: argparse.ArgumentTypeError if any format is invalid
    """
    logger.debug(f"validate_format called with value: {value}")
    no_whitespace = re.sub(r"\s+", "", value.lower())
    values = no_whitespace.split(",")
    valid_formats = ["json", "csv", "yml", "xml"]
    if any(v.lower() in valid_formats for v in values):
        return values
    raise argparse.ArgumentTypeError("Invalid format type.")


def validate_output_mode(value: str) -> str:
    """
    Validate output mode.

    :param value: Output mode string
    :type value: str
    :return: Validated output mode
    :rtype: str
    :raises: argparse.ArgumentTypeError if mode is invalid
    """
    logger.debug(f"validate_output_mode called with value: {value}")
    no_whitespace = re.sub(r"\s+", "", value.lower())
    if no_whitespace in ["all", "book", "books"]:
        return no_whitespace
    raise argparse.ArgumentTypeError("Invalid output mode.")
