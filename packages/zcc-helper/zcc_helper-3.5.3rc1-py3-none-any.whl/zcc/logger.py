'''ZCC Logger Module.'''
from __future__ import annotations

from zcc.constants import NAME, VERSION
import logging

# Module logger root - level is always set for all messages
logger = logging.getLogger(NAME + '-' + VERSION)

console_handler = logging.StreamHandler()

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger.setLevel(logging.DEBUG)

console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

dh = None

logger.addHandler(console_handler)


def add_debug_file_to_logger(filename: str):
    '''Add a debug file to store all messages.'''

    dh = logging.FileHandler(filename)
    dh.setLevel(logging.DEBUG)
    dh.setFormatter(formatter)
    logger.addHandler(dh)


def remove_debug_file_from_logger():
    '''Remove the debug file.'''

    logger.removeHandler(dh)
