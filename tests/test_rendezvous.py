# coding: utf-8
from __future__ import absolute_import

import hashlib
import random
import sys

import six
import siphash

import proxenos.config
import proxenos.node
import proxenos.rendezvous


def test_srand():
    rng = random.Random()
    for _ in six.moves.xrange(1000):
        seed = rng.randint(0, sys.maxsize)
        rng.seed(seed)
        assert next(proxenos.rendezvous.srand(seed)) == rng.randint(
            0, sys.maxsize)


def test_srand_bytes():
    bs = b'\x00\x00\x00\x00'
    int_value = int(hashlib.sha512(bs).hexdigest(), 16)
    rng = random.Random()
    rng.seed(int_value)
    assert next(proxenos.rendezvous.srand(bs)) == rng.randint(0, sys.maxsize)


def test_srand_unicode():
    s = six.text_type(u'touché')
    int_value = int(hashlib.sha512(s.encode('utf-8')).hexdigest(), 16)
    rng = random.Random()
    rng.seed(int_value)
    assert next(proxenos.rendezvous.srand(s)) == rng.randint(0, sys.maxsize)


def test_hashex():
    for algorithm in hashlib.algorithms_guaranteed:
        method = getattr(proxenos.rendezvous.HashMethod, algorithm.upper())
        assert (proxenos.rendezvous.hashex(method, 'secret') ==
                int(hashlib.new(algorithm, b'secret').hexdigest(), 16))

    key = proxenos.config.siphash_key
    assert proxenos.rendezvous.hashex(
        proxenos.rendezvous.HashMethod.SIPHASH,
        'secret') == int(siphash.SipHash24(key, b'secret').hexdigest(), 16)
