from enum import Enum
import json
from json.decoder import JSONDecodeError
from pprint import pformat
import logging
import socket
import sys
import threading
import time
import typing

from zcc.socket import ControlPointSocket
from zcc.protocol import ControlPointProtocol


class ControlPointSingleError(Exception):
    pass


class ControlPointSingle:
    '''Represents a Control Point proxy for single-shot actions'''

    def __init__(self,
                 host: str = None,
                 port: int = None,
                 timeout: int = 3,
                 device: str = None,
                 debug: bool = False):

        self.debug = debug

        self.logger = logging.getLogger('ControlPointProxy')
        if self.debug:
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        else:
            logging.basicConfig(stream=sys.stderr, level=logging.INFO)

        self.host = host
        self.port = int(port) if port else None

        self.device = device

        self.timeout = timeout

        if not self.host:
            raise ControlPointSingleError('Missing host')
        if not self.port:
            raise ControlPointSingleError('Missing port')

    def __str__(self):
        return pformat(vars(self)) + '\n'

    def __action(self, action: str, params: object = None):
        '''Sends an action for a device and checks response'''
        if self.device:
            for item in self.__set(self.device, action, params=params):
                for device in item:
                    received_identifier = device['id']
                    if self.device == received_identifier:
                        if device['result'] == 'fail':
                            raise ControlPointSingleError(
                                "Attempt to send %s to %s failed" % (action, identifier))
        else:
            raise ControlPointSingleError('missing device')

    def __set(self, identifier: str, action: str, params: object = None):
        '''Sends an action for a device and yields response objects'''

        sock = ControlPointSocket(self.host, self.port, timeout=self.timeout)
        sock.sendall(ControlPointProtocol.set(identifier, action, params))
        data = sock.recvall()
        sock.close()

        lines = data.split('\n')
        for line in lines:
            try:
                response = json.loads(line).get('response')
                if response:
                    target_response = response.get(
                        ControlPointProtocol.set_response_key())
                    if target_response:
                        yield target_response
            except JSONDecodeError as e:
                break

    def close_door(self):
        self.__action("CloseDoor")

    def fade(self, brightness, timeperiod):
        self.__action("SetBrightness",
                      params={
                          "brightness": int(brightness),
                          "timeperiod": int(timeperiod)})

    def open_door(self):
        self.__action("OpenDoor")

    def open_to_percentage(self, percentage):
        self.__action("OpenToPercentage",
                      params={"openpercentage": int(percentage)})

    def set_brightness(self, brightness):
        self.__action("SetBrightness",
                      params={"brightness": int(brightness)})

    def set_fanspeed(self, fanspeed):
        self.__action("SetFanSpeed",
                      params={"fanspeed": int(fanspeed)})

    def turn_on(self):
        self.__action("TurnOn")

    def turn_off(self):
        self.__action("TurnOff")
