# coding: utf-8
from __future__ import absolute_import

import hashlib
import random
import sys

import mmh3
import pytest
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


def test_hashex_hashlib():
    for algorithm in hashlib.algorithms_guaranteed:
        method = getattr(proxenos.rendezvous.HashMethod, algorithm.upper())
        assert (proxenos.rendezvous.hashex(method, 'secret') ==
                int(hashlib.new(algorithm, b'secret').hexdigest(), 16))


def test_hashex_siphash():
    key = proxenos.config.siphash_key
    assert proxenos.rendezvous.hashex(
        proxenos.rendezvous.HashMethod.SIPHASH,
        'secret') == int(siphash.SipHash24(key, b'secret').hexdigest(), 16)


def test_hashex_murmur():
    assert proxenos.rendezvous.hashex(
        proxenos.rendezvous.HashMethod.MMH3_32,
        'secret') == mmh3.hash('secret')

    assert proxenos.rendezvous.hashex(
        proxenos.rendezvous.HashMethod.MMH3_64,
        'secret') == mmh3.hash64('secret')[0]

    assert proxenos.rendezvous.hashex(
        proxenos.rendezvous.HashMethod.MMH3_128,
        'secret') == mmh3.hash128('secret')


def test_hashex_murmur_optimize_x64(mocker):
    mocker.patch.object(mmh3, 'hash64')
    proxenos.rendezvous.hashex(
        proxenos.rendezvous.HashMethod.MMH3_64,
        'secret',
        optimize='x64')
    mmh3.hash64.assert_called_once_with(b'secret', seed=0, x64arch=True)


def test_hashex_murmur_optimize_auto(mocker):
    mocker.patch.object(mmh3, 'hash64')
    proxenos.rendezvous.hashex(
        proxenos.rendezvous.HashMethod.MMH3_64,
        'secret',
        optimize='auto')
    mmh3.hash64.assert_called_once_with(
        b'secret', seed=0, x64arch=proxenos.rendezvous.ARCH == 64)


def test_hash_murmur_invalid_size():
    with pytest.raises(ValueError):
        proxenos.rendezvous.hash_murmur3('secret', size=1024)


@pytest.mark.parametrize('key,expected_host', (
    ('secret', '192.168.100.104:8000',),
    (six.text_type(u'touché'), '192.168.100.109:8000'),
    ('moist towelette', '192.168.100.106:8000'),
))
def test_select_node(cluster, key, expected_host):
    selected_node = proxenos.rendezvous.select_node(cluster, key)
    assert str(selected_node.socket_address) == expected_host
