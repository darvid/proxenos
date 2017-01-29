"""Provides the proxenos command line interface."""
from __future__ import absolute_import

import re

import click
import stevedore.driver

import proxenos.const
import proxenos.errors
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
              type=click.Choice(proxenos.mappers.get_available_backends()))
@click.option('-h', '--host', default='localhost',
              help='Service discovery host.')
@click.option('-p', '--port', help='Service discovery port.')
@click.option('-A', '--filter-address',
              help='Filters service addresses by provided regular expression.')
@click.option('-N', '--filter-service-name',
              help='Filters service names by provided regular expression.')
@click.option('-T', '--filter-service-tags',
              help='Filters service tags by provided regular expression.')
@click.option('-H', '--hash-method',
              callback=(lambda _, __, v:
                        getattr(proxenos.rendezvous.HashMethod, v.upper())),
              default='SIPHASH',
              envvar='PROXENOS_PRF',
              help='Hash method. Defaults to SipHash.',
              type=click.Choice(HASH_METHODS))
@click.argument('key')
@click.pass_context
def cmd_select(ctx,                  # type: click.Context
               backend,              # type: str
               host,                 # type: str
               port,                 # type: int
               filter_address,       # type: str
               filter_service_name,  # type: str
               filter_service_tags,  # type: str
               hash_method,          # type: proxenos.rendezvous.HashMethod
               key,                  # type: str
               ):
    # type: (...) -> None
    """Selects a node from a cluster."""
    if port is None:
        port = DEFAULT_PORTS[backend]
    driver_manager = stevedore.driver.DriverManager(
        namespace=proxenos.mappers.NAMESPACE,
        name=backend,
        invoke_on_load=False)
    try:
        mapper = driver_manager.driver(host=host, port=port)
    except proxenos.errors.ServiceDiscoveryConnectionError as err:
        click.secho(str(err), fg='red')
        ctx.exit(proxenos.const.ExitCode.CONNECTION_FAILURE)
    mapper.update()
    cluster = mapper.cluster.copy()
    # TODO(darvid): Add filtering support in the mapper API itself
    if filter_service_tags:
        pattern = re.compile(filter_service_tags)
        cluster = {service for service in cluster
                   if all(pattern.match(tag) for tag in service.tags)}
    if filter_service_name:
        pattern = re.compile(filter_service_name)
        cluster = {service for service in cluster
                   if pattern.match(service.name)}
    if filter_address:
        pattern = re.compile(filter_address)
        cluster = {service for service in cluster
                   if pattern.match(str(service.socket_address))}
    service = proxenos.rendezvous.select_node(
        cluster, key, hash_method=hash_method)
    if service is None:
        ctx.exit(proxenos.const.ExitCode.SERVICES_NOT_FOUND)
    click.echo(str(service.socket_address))
