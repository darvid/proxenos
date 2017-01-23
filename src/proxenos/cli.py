"""Provides the proxenos command line interface."""
from __future__ import absolute_import

import re

import click
import stevedore.driver

import proxenos.mappers
import proxenos.rendezvous


__all__ = ('main',)

DEFAULT_PORTS = {
    'consul': 8500,
    'etcd': 4001,
}

# XXX(darvid): https://github.com/python/mypy/issues/2305
HASH_METHODS = proxenos.rendezvous.HashMethod.__members__  # type: ignore


@click.group()
@click.pass_context
def main(ctx):
    # type: (click.Context) -> None
    """proxenos-cli: Consistently select nodes from service discovery."""


@main.command('select')
@click.option('-b', '--backend',
              default='consul',
              help='Service discovery backend.',
              type=click.Choice(proxenos.mappers.available_backends))
@click.option('-f', '--filter-pattern',
              help='Regex pattern to filter socket address strings.')
@click.option('-h', '--host', default='localhost',
              help='Service discovery host.')
@click.option('-p', '--port', help='Service discovery port.')
@click.option('-H', '--hash-method',
              callback=(lambda _, __, v:
                        getattr(proxenos.rendezvous.HashMethod, v.upper())),
              default='SIPHASH',
              envvar='PROXENOS_PRF',
              help='Hash method. Defaults to SipHash.',
              type=click.Choice(HASH_METHODS))
@click.argument('key')
def cmd_select(backend,         # type: str
               filter_pattern,  # type: str
               host,            # type: str
               port,            # type: int
               hash_method,     # type: proxenos.rendezvous.HashMethod
               key,             # type: str
               ):
    # type: (...) -> None
    """Selects a node from a cluster."""
    if port is None:
        port = DEFAULT_PORTS[backend]
    driver_manager = stevedore.driver.DriverManager(
        namespace=proxenos.mappers.NAMESPACE,
        name=backend,
        invoke_on_load=False)
    mapper = driver_manager.driver(host=host, port=port)
    mapper.update()
    cluster = mapper.cluster.copy()
    # TODO(darvid): Add filtering support in the mapper API itself
    if filter_pattern:
        pattern = re.compile(filter_pattern)
        cluster = {addr for addr in cluster if pattern.match(str(addr))}
    addr = proxenos.rendezvous.select_node(
        cluster, key, hash_method=hash_method)
    click.echo(str(addr))
