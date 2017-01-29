"""Provides common exceptions."""
from __future__ import absolute_import


__all__ = (
    'ProxenosError',
    'ServiceDiscoveryConnectionError',
)


class ProxenosError(Exception):
    """Base exception class for all proxenos errors."""


class ServiceDiscoveryConnectionError(ProxenosError):
    """Unable to connect to a service discovery tool."""
