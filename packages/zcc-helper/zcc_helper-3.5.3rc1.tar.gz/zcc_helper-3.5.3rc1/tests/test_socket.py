import socket
import pytest
from unittest.mock import Mock
from mockito import when, unstub

from zcc.socket import ControlPointSocket

TEST_HOST = '10.0.0.1'
TEST_PORT = 4567
TEST_TIMEOUT = 5


@pytest.fixture
def mock_tcp_socket():
    mock_socket = Mock(spec=socket.socket)
    return mock_socket


def test_socket_create(mock_tcp_socket, when):

    when(socket).socket(socket.AF_INET,
                        socket.SOCK_STREAM)\
        .thenReturn(mock_tcp_socket)

    controller_socket = ControlPointSocket(TEST_HOST, TEST_PORT)

    assert controller_socket.host == TEST_HOST
    assert controller_socket.port == TEST_PORT
    assert controller_socket.sock == mock_tcp_socket

    controller_socket.close()
    assert controller_socket.sock == None


def test_socket_create_timeout(mock_tcp_socket, when):

    when(socket).socket(socket.AF_INET,
                        socket.SOCK_STREAM)\
        .thenReturn(mock_tcp_socket)

    controller_socket = ControlPointSocket(
        TEST_HOST, TEST_PORT, timeout=TEST_TIMEOUT)

    assert controller_socket.host == TEST_HOST
    assert controller_socket.port == TEST_PORT
    assert controller_socket.sock == mock_tcp_socket

    assert mock_tcp_socket.settimeout.call_count == 1
    assert mock_tcp_socket.settimeout.call_args.args == (TEST_TIMEOUT,)

    controller_socket.close()
    assert controller_socket.sock == None
