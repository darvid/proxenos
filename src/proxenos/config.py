"""Provides configuration and configuration defaults."""
from __future__ import absolute_import

import biome


__all__ = (
    'env',
    'mmh_seed',
    'mmh_optimize',
    'prf',
    'siphash_key',
)

env = biome.proxenos
mmh_seed = env.get_int('mmh_seed', 0)
mmh_optimize = env.get('mmh_optimize', 'auto').lower()
prf = env.get('prf', default='siphash').upper()
siphash_key = env.get(
    'siphash_key',
    default=b'\xd9\x06\xb0z\x88\x13\x15\xce0\x88G\xa8\xc4\xdei\xc6')
