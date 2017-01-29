import click.testing
import consulate
import pytest
import six

import proxenos.cli
import proxenos.mappers
import proxenos.mappers.consul

import pkg_resources


@pytest.fixture
def patched_mapper(consul_mapper_synced, mocker):
    mocker.patch('proxenos.mappers.consul.ConsulClusterMapper',
                 return_value=consul_mapper_synced)
    return consul_mapper_synced


@pytest.fixture
def runner():
    return click.testing.CliRunner()


@pytest.mark.parametrize('key,expected_host', (
    ('secret', '192.168.100.104:8000',),
    (six.text_type(u'touché'), '192.168.100.109:8000'),
    ('moist towelette', '192.168.100.106:8000'),
))
def test_select_consul(patched_mapper, runner, key, expected_host):
    result = runner.invoke(proxenos.cli.cmd_select, ['-b', 'consul', key])
    assert result.exit_code == 0
    proxenos.mappers.consul.ConsulClusterMapper.assert_called_once_with(
        host='localhost', port=proxenos.cli.DEFAULT_PORTS['consul'])
    assert expected_host in result.output


@pytest.mark.parametrize('key,expected_host', (
    ('secret', '192.168.100.109:8000',),
))
def test_select_consul_filter_addr(patched_mapper, runner, key, expected_host):
    result = runner.invoke(
        proxenos.cli.cmd_select,
        ['-b', 'consul', '-A', r'^192\.168\.100\.(?!104)', key])
    assert result.exit_code == 0
    proxenos.mappers.consul.ConsulClusterMapper.assert_called_once_with(
        host='localhost', port=proxenos.cli.DEFAULT_PORTS['consul'])
    assert expected_host in result.output


@pytest.mark.parametrize('key,expected_host', (
    ('secret', '192.168.100.104:8000',),
))
def test_select_consul_filter_name(patched_mapper, runner, service_name, key,
                                   expected_host):
    result = runner.invoke(
        proxenos.cli.cmd_select,
        ['-b', 'consul', '-N', r'^{}$'.format(service_name), key])
    assert result.exit_code == 0
    proxenos.mappers.consul.ConsulClusterMapper.assert_called_once_with(
        host='localhost', port=proxenos.cli.DEFAULT_PORTS['consul'])
    assert expected_host in result.output


@pytest.mark.parametrize('key,expected_host', (
    ('secret', '192.168.100.104:8000',),
))
def test_select_consul_filter_tags(patched_mapper, runner, service_tags, key,
                                   expected_host):
    tags = '|'.join(service_tags)
    result = runner.invoke(
        proxenos.cli.cmd_select,
        ['-b', 'consul', '-T', r'^{}$'.format(tags), key])
    assert result.exit_code == 0
    proxenos.mappers.consul.ConsulClusterMapper.assert_called_once_with(
        host='localhost', port=proxenos.cli.DEFAULT_PORTS['consul'])
    assert expected_host in result.output


def test_select_consul_connection_error(runner):
    result = runner.invoke(
        proxenos.cli.cmd_select, ['-b', 'consul', '-p', 65537, 'secret'])
    assert result.exit_code == proxenos.const.ExitCode.CONNECTION_FAILURE


def test_select_consul_no_services(patched_mapper, runner):
    patched_mapper.cluster.clear()
    patched_mapper.update = lambda: None
    result = runner.invoke(
        proxenos.cli.cmd_select, ['-b', 'consul', 'secret'])
    assert result.exit_code == proxenos.const.ExitCode.SERVICES_NOT_FOUND
