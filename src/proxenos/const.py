"""Provides shared constants."""
from __future__ import absolute_import

import enum


__all__ = ('ExitCode',)


class ExitCode(enum.IntEnum):
    """Exit codes used by the CLI, in the range 64-113."""

    CONNECTION_FAILURE = 64
    SERVICES_NOT_FOUND = 65
