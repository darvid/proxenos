"""proxenos: A rendezvous hashing and service routing toolkit."""
from __future__ import absolute_import

import pkg_resources


try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = 'unknown'
