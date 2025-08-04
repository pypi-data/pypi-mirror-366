'''Setup Test Server.'''
import pytest

from zcc.controller import ControlPoint, ControlPointError
from tests.server import TestServer


@pytest.fixture
def test_server():
    '''Create (and delete) a Test Server'''
    return TestServer()
