"""Provides data mappers for service discovery tools."""
from __future__ import absolute_import

import pkg_resources


__all__ = (
    'get_available_backends',
    'NAMESPACE',
)


NAMESPACE = 'proxenos.mapper'


def get_available_backends():
    # type: () -> Set[str]
    """Returns the names of available service discovery data mappers."""
    return {ep.name for ep in pkg_resources.iter_entry_points(NAMESPACE)}
