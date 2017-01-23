"""Provides node selection based on Highest Random Weight (HRW) hashing."""
from __future__ import absolute_import

import enum
import hashlib
import random
import struct
import sys
import typing

import siphash
import six

import proxenos.config
import proxenos.node  # noqa: F401


try:
    import mmh3  # type: ignore
except ImportError:
    err = RuntimeError('Please install the mmh3 package from PyPI '
                       'for Murmur3 support')

    class mmh3(object):  # type: ignore

        def hash(self, *args, **kwargs):
            raise err

        def hash64(self, *args, **kwargs):
            raise err

        def hash128(self, *args, **kwargs):
            raise err


__all__ = (
    'HashMethod',
    'KeyType',
    'select_node',
    'weight',
)

ARCH = struct.calcsize('P') * 8
HashCallback = typing.Callable[[typing.Any, int], int]
KeyType = typing.Union[typing.AnyStr, int]


@enum.unique
class HashMethod(enum.IntEnum):
    """An enumeration of supported hash functions and PRFs."""

    MD5 = 1
    SHA1 = 2
    SHA224 = 3
    SHA256 = 4
    SHA384 = 5
    SHA512 = 6
    MMH3_32 = 7
    MMH3_64 = 8
    MMH3_128 = 9
    SIPHASH = 10


def hashex(method,    # type: HashMethod
           key,       # type: KeyType
           **options  # type: typing.Any
           ):
    # type: (...) -> int
    if method.name.lower() in hashlib.algorithms_guaranteed:
        return int(hashlib.new(method.name.lower(), key).hexdigest(), 16)
    elif method == HashMethod.MMH3_32:
        return hash_murmur3(key, size=32, **options)
    elif method == HashMethod.MMH3_64:
        return hash_murmur3(key, size=64, **options)
    elif method == HashMethod.MMH3_128:
        return hash_murmur3(key, size=128, **options)
    elif method == HashMethod.SIPHASH:
        return hash_siphash(key, **options)


def hash_murmur3(key,            # type: KeyType
                 seed=None,      # type: typing.Optional[int]
                 optimize=None,  # type: typing.Optional[str]
                 size=128,       # type: int
                 ):
    # type: (...) -> int
    if size not in (32, 64, 128):
        raise ValueError('size must be one of (32, 64, 128)')
    hash_fn = getattr(mmh3, 'hash{}'.format('' if size == 32 else size))
    options = {}
    if optimize is None:
        optimize = proxenos.config.mmh_optimize
    else:
        optimize = optimize.lower()
    if seed is None:
        seed = proxenos.config.mmh_seed
    options['seed'] = seed
    if size != 32:
        options['x64arch'] = False
        if optimize == 'x64':
            options['x64arch'] = True
        elif optimize == 'auto':
            options['x64arch'] = ARCH == 64
    digest = hash_fn(key, **options)
    if size == 64:
        return digest[0]
    return digest


def hash_siphash(key, secret=None):
    if secret is None:
        secret = proxenos.config.siphash_key
    return int(siphash.SipHash24(secret, key).hexdigest(), 16)


def srand(seed=0):
    # type: (KeyType) -> typing.Generator[int, None, None]
    if isinstance(seed, six.string_types) or isinstance(seed, bytes):
        if isinstance(seed, six.text_type):
            seed = seed.encode()
        seed_int = int(hashlib.sha512(seed).hexdigest(), 16)
        seed = typing.cast(int, seed_int)
    rng = random.Random(seed)
    while True:
        yield rng.randint(0, sys.maxsize)


def select_node(cluster,       # type: typing.Set[proxenos.node.SocketAddress]
                key,           # type: typing.Any
                hash_method=None,  # type: typing.Optional[HashMethod]
                **hash_options     # type: typing.Any
                ):
    # type: (...) -> proxenos.node.SocketAddress
    """Selects a node from the given cluster based using HRW hashing.

    Args:
        cluster (set of :class:`proxenos.node.SocketAddress`): A set of
            cluster nodes (:class:`~.node.SocketAddress` instances).
        key (str or int): An arbitrary hashable object, typically a
            string or integer.
        hash_method (:class:`HashMethod`): The pseudorandom function
            (PRF) or hash function to use. Defaults to
            :attr:`HashMethod.SIPHASH`.
        **hash_options: Additional parameters to pass to the hash
            function, such as seed, salt, or key length.

    Returns:
        The :class:`SocketAddress` of the selected node.

    """
    if hash_method is None:
        # XXX(darvid): https://github.com/python/mypy/issues/741
        # hash_method = HashMethod[proxenos.config.prf]
        hash_method = getattr(HashMethod, proxenos.config.prf)
    max_weight = 0
    selected_node = None
    for node in cluster:
        node_weight = weight(node, key, hash_method, **hash_options)
        if node_weight > max_weight:
            max_weight = node_weight
            selected_node = node
    return selected_node


def weight(socket_address,    # type: proxenos.node.SocketAddress
           key,               # type: typing.Union[typing.AnyStr, int]
           hash_method=None,  # type: typing.Optional[HashMethod]
           **hash_options     # type: typing.Any
           ):
    # type: (...) -> int
    """Calculates the weight of the given key and socket address.

    See :cite:`thaler.ravishankar.1996` for context.

    .. bibliography:: refs.bib

    Args:
        socket_address (:class:`proxenos.node.SocketAddress`): A socket
            address.
        key (str or int): An arbitrary hashable object, typically a
            string or integer.
        hash_method (:class:`HashMethod`): The pseudorandom function
            (PRF) or hash function to use. Defaults to
            :attr:`HashMethod.SIPHASH`.
        **hash_options: Additional parameters to pass to the hash
            function, such as seed, salt, or key length.

    Returns:
        An integer bounded by ``sys.maxsize``.

    """
    seed = next(srand(socket_address.pack()))
    digest = hashex(hash_method, key, **hash_options)
    return next(srand(seed ^ digest))
