"""Provides data mappers for service discovery tools."""
from __future__ import absolute_import

import pkg_resources


__all__ = (
    'available_backends',
    'NAMESPACE',
)


NAMESPACE = 'proxenos.mapper'
available_backends = (
    ep.name for ep in pkg_resources.iter_entry_points(NAMESPACE))
