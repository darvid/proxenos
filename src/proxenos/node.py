"""Provides structures for representing nodes."""
from __future__ import absolute_import

import socket
import struct
import typing  # noqa: F401

import attr
import netaddr
import netaddr.strategy.ipv6


__all__ = ('SocketAddress',)


def ipv6_address(addr, resolve=True):
    # type: (typing.Union[str, int], bool) -> netaddr.IPAddress
    try:
        return netaddr.IPAddress(addr).ipv6(ipv4_compatible=True)
    except netaddr.AddrFormatError:
        if not resolve or isinstance(addr, int):
            raise
        return ipv6_address(socket.gethostbyname(str(addr)), resolve=False)


@attr.s(frozen=True, slots=True)
class SocketAddress(object):
    """Represents an Internet (AF_INET) socket address.

    Args:
        host (str or int): Accepts an IP address in the form of a string
            or integer, or a domain name. Both IPv4 and IPv6 addresses
            are supported.
        port (int): The port number of the destination socket.

    """

    host = attr.ib(convert=ipv6_address)  # type: netaddr.IPAddress
    port = attr.ib(convert=int)           # type: int

    # TODO(darvid): Add properties for IPv6 Flow Label and scope ID.

    @classmethod
    def unpack(cls, addr_bytes):
        # type: (typing.ByteString) -> 'SocketAddress'
        """Unpacks a 24-bit bytestring to a :class:`SocketAddress`.

        Args:
            addr_bytes: A bytestring containing an IPv6 address as a
                packed binary string followed by a port number.

        Returns:
            A :class:`~.node.SocketAddress` instance.

        """
        unpacked = struct.unpack('>8H4H', addr_bytes)
        port = 0
        for i, word in enumerate(unpacked[8:][::-1]):
            port |= word << 4 * i
        host = netaddr.strategy.ipv6.words_to_int(unpacked[:8])
        return cls(host, port)

    def pack(self):
        # type: () -> typing.ByteString
        """Packs a socket address into a 24-bit struct.

        Returns:
            A bytestring containing the packed host and port.

        """
        port_words = netaddr.strategy.ipv6.int_to_words(self.port, 4, 4)
        return struct.pack('>8H4H', *self.host.words + port_words)

    def __bytes__(self):
        # type: () -> typing.ByteString
        return self.pack()

    def __str__(self):
        # type: () -> str
        try:
            return '{}:{}'.format(self.host.ipv4(), self.port)
        except netaddr.AddrConversionError:
            return '{}:{}'.format(self.host, self.port)
