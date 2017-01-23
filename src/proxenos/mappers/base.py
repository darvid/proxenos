"""Provides a base interface for node cluster data mappers.

Node clusters, or a set of :class:`~.node.SocketAddress`, to be
specific, are a pool of socket addresses representing remote services.
Cluster mappers implement the data mapper pattern, reading service
socket addresses from sources such as service discovery tools (i.e.
Consul, etcd, or ZooKeeper) into a set of :class:`~.node.SocketAddress`.

.. note::

   Cluster mappers are **not** thread-safe.

"""
from __future__ import absolute_import

import abc
import typing  # noqa: F401

import attr
import six

import proxenos.node  # noqa: F401
import proxenos.rendezvous


__all__ = ('BaseClusterMapper',)


@attr.s
@six.add_metaclass(abc.ABCMeta)
class BaseClusterMapper(object):
    """Serializes services into a set of :class:`~.node.SocketAddress`."""

    host = attr.ib()             # type: str
    port = attr.ib(convert=int)  # type: int
    cluster = attr.ib(
        default=attr.Factory(set),
        convert=set,
        repr=False)  # type: typing.Set[proxenos.node.SocketAddress]
    _conn = attr.ib(
        default=attr.NOTHING,
        repr=False,
        hash=False,
        init=False)  # type: typing.Any

    def __attrs_post_init__(self):
        self._conn = self.make_connection()

    @abc.abstractmethod
    def make_connection(self):
        # type: () -> typing.Any
        """Returns a connection to a service discovery system."""

    @abc.abstractmethod
    def update(self):
        # type: () -> None
        """Reads all service nodes into the socket address cluster."""

    def select(self,
               key,            # type: proxenos.rendezvous.KeyType
               hash_method,    # type: proxenos.rendezvous.HashMethod
               **hash_options  # type: typing.Any
               ):
        # type: (...) -> proxenos.node.SocketAddress
        """Selects a node from the cluster based using HRW hashing.

        Args:
            key (str or int): An arbitrary hashable object, typically a
                string or integer.
            hash_method (:class:`HashMethod`): The pseudorandom function
                (PRF) or hash function to use. Defaults to
                :attr:`HashMethod.SIPHASH`.
            **hash_options: Additional parameters to pass to the hash
                function, such as seed, salt, or key length.

        Returns:
            The :class:`SocketAddress` of the selected node.

        """
        return proxenos.rendezvous.select_node(self.cluster, key)
