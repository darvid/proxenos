"""proxenos: A rendezvous hashing and service routing toolkit."""
from __future__ import absolute_import

import pkg_resources


try:  # pragma: no cover
    __version__ = pkg_resources.get_distribution(__name__).version
except:  # noqa: B901
    __version__ = 'unknown'
