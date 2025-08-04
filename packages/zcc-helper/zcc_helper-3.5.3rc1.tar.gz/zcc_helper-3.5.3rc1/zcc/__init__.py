'''ZCC Support Library to support ZIMI based home network elements'''
import logging
import sys

from .controller import ControlPoint
from .description import ControlPointDescription
from .discovery import ControlPointDiscoveryService
from .errors import ( ControlPointError,
                     ControlPointConnectionRefusedError,
                     ControlPointCannotConnectError,
                     ControlPointInvalidHostError,
                     ControlPointTimeoutError)

logging.basicConfig(stream=sys.stderr)
