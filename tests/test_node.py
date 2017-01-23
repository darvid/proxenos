from __future__ import absolute_import

import netaddr
import pytest

import proxenos.node


def test_ipv6_address_from_ipv4():
    ipv6_addr = proxenos.node.ipv6_address("127.0.0.1")
    assert str(ipv6_addr) == '::127.0.0.1'


def test_ipv6_address_from_ipv6():
    ipv6_addr = proxenos.node.ipv6_address('::')
    assert str(ipv6_addr) == '::'
    assert int(ipv6_addr) == 0


def test_ipv6_address_from_int():
    ipv6_addr = proxenos.node.ipv6_address(2130706433)
    assert str(ipv6_addr) == '::127.0.0.1'


def test_ipv6_address_resolve():
    ipv6_addr = proxenos.node.ipv6_address('localhost')
    assert str(ipv6_addr) == '::127.0.0.1'


def test_ipv6_address_invalid():
    with pytest.raises(netaddr.AddrFormatError):
        proxenos.node.ipv6_address('256.256.256.256', resolve=False)


def test_ipv6_address_resolve_failure():
    with pytest.raises(IOError):
        proxenos.node.ipv6_address('google.invalid')


def test_socket_address_pack_ipv4():
    socket_addr = proxenos.node.SocketAddress('127.0.0.1', 80)
    packed_expected = (b'\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x7f\x00\x00\x01'
                       b'\x00\x00\x00\x00\x00\x05\x00\x00')
    assert socket_addr.pack() == packed_expected
    assert socket_addr.__bytes__() == packed_expected


def test_socket_address_pack_ipv6():
    socket_addr = proxenos.node.SocketAddress('fd95:3a46:4c76::', 80)
    packed_expected = (b'\xfd\x95:FLv\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x05\x00\x00')
    assert socket_addr.pack() == packed_expected
    assert socket_addr.__bytes__() == packed_expected


def test_socket_address_unpack():
    socket_addr = proxenos.node.SocketAddress('127.0.0.1', 80)
    assert proxenos.node.SocketAddress.unpack(
        socket_addr.pack()) == socket_addr

    socket_addr = proxenos.node.SocketAddress('fd95:3a46:4c76::', 80)
    assert proxenos.node.SocketAddress.unpack(
        socket_addr.pack()) == socket_addr


def test_socket_address_str():
    socket_addr = proxenos.node.SocketAddress('127.0.0.1', 80)
    assert str(socket_addr) == '127.0.0.1:80'

    socket_addr = proxenos.node.SocketAddress('fd95:3a46:4c76::', 80)
    assert str(socket_addr) == 'fd95:3a46:4c76:::80'
