"""Provides data mappers for Consul service discovery."""
from __future__ import absolute_import

import consulate
import requests.exceptions

import proxenos.errors
import proxenos.mappers.base
import proxenos.node


__all__ = ('ConsulClusterMapper',)


class ConsulClusterMapper(proxenos.mappers.base.BaseClusterMapper):
    """Reads service socket addresses from Consul."""

    def make_connection(self):
        # type: () -> consulate.Consul
        """Initializes a Consul connection with :mod:`consulate`.

        Raises:
            :class:`~.errors.ServiceDiscoveryConnectionError`: Unable to
                connect to a Consul agent.

        Returns:
            :class:`consulate.Consul`: A Consul agent connection.

        """
        try:
            conn = consulate.Consul(host=self.host, port=self.port)
            conn.status.leader()
            return conn
        except requests.exceptions.RequestException as err:
            raise proxenos.errors.ServiceDiscoveryConnectionError(str(err))

    def update(self):
        # type: () -> None
        """Reads services from a Consul catalog into a cluster."""
        self.cluster.clear()
        service_names = [service for dc in self._conn.catalog.services()
                         for service in dc]
        for service in service_names:
            for node in self._conn.catalog.service(service):
                socket_address = proxenos.node.SocketAddress(
                    node['Address'], node['ServicePort'])
                self.cluster.add(proxenos.node.Service(
                    name=node['ServiceName'],
                    socket_address=socket_address,
                    tags=node['ServiceTags']))
