"""Provides data mappers for Consul service discovery."""
from __future__ import absolute_import

import consulate

import proxenos.mappers.base
import proxenos.node


__all__ = ('ConsulClusterMapper',)


class ConsulClusterMapper(proxenos.mappers.base.BaseClusterMapper):
    """Reads service socket addresses from Consul."""

    def make_connection(self):
        # type: () -> consulate.Consul
        """Initializes a Consul connection with :mod:`consulate`."""
        return consulate.Consul(host=self.host, port=self.port)

    def update(self):
        # type: () -> None
        """Reads services from a Consul catalog into a cluster."""
        self.cluster.clear()
        service_names = [service for dc in self._conn.catalog.services()
                         for service in dc]
        for service in service_names:
            for node in self._conn.catalog.service(service):
                self.cluster.add(proxenos.node.SocketAddress(
                    node['ServiceAddress'], node['ServicePort']))
