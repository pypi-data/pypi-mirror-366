'''Test Basic Controller functionality.'''
import pytest

from zcc.controller import ControlPoint, ControlPointError
from zcc.device import ControlPointDevice

from tests.test_server import test_server


def test_controller_discover(test_server):
    '''Test for connection to a Controller connected to the Test Server'''

    controller = ControlPoint(timeout=1)

    assert controller.ready is True
    assert controller.host is not None
    assert controller.port == 5003
    assert controller.brand == 'zimi'
    assert len(controller.devices) == 31
    assert len(controller.doors) == 0
    assert len(controller.fans) == 0
    assert len(controller.lights) == 20
    assert len(controller.outlets) == 0


def test_controller_discover_timeout():
    '''Test if a UDP discovery times out - goes out over wire'''

    try:
        ControlPoint(timeout=1)
        assert False
    except ControlPointError as error:
        assert error.args[0] == '__init() failed - unable to discover and connect to ZCC'


def test_controller_device(test_server):
    '''Test turn_on works for valid devices'''

    controller = ControlPoint(timeout=1)

    light = controller.lights[0]

    assert light.is_off() is not True
    assert light.is_on() is True

    assert light.is_opening is not True
    assert light.is_open is not True
    assert light.location == "lounge LED strip/Lounge"
    assert light.name == "lounge LED strip"

    with pytest.raises(ControlPointDeviceError):
        light.open_door()

    with pytest.raises(ControlPointDeviceError):
        light.close_door()

    light.turn_on()

    light.turn_off()
