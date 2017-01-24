import typing

import netaddr


class SocketAddress(object):
    host = ...  # type: netaddr.IPAddress
    port = ...  # type: int

    def __init__(self, host: netaddr.IPAddress, port: int) -> None: ...

    @classmethod
    def unpack(cls, addr_bytes: typing.ByteString) -> 'SocketAddress': ...
    def pack(self) -> typing.ByteString: ...
    def __bytes__(self) -> typing.ByteString: ...
    def __str__(self) -> str: ...


class Service(object):
    name = ...            # type: str
    socket_address = ...  # type: SocketAddress
    tags = ...            # type: Set[str]

    def __init__(self, name: str,
                 socket_address: SocketAddress,
                 tags: Set[str]) -> None: ...
