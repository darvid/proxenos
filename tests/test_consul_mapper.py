# coding: utf-8
from __future__ import absolute_import

import consulate
import pytest
import six

import proxenos.errors
import proxenos.mappers.consul


def test_mapper_construction(consul_mapper, consul_host, consul_port):
    consulate.Consul.assert_called_once_with(
        host=consul_host, port=consul_port)


def test_mapper_update(consul_mapper_synced, cluster):
    assert consul_mapper_synced.cluster == cluster


def test_mapper_connection_error():
    with pytest.raises(proxenos.errors.ServiceDiscoveryConnectionError):
        mapper = proxenos.mappers.consul.ConsulClusterMapper(
            host='127.0.0.1', port=65537)


@pytest.mark.parametrize('key,expected_host', (
    ('secret', '192.168.100.104:8000',),
    (six.text_type(u'touché'), '192.168.100.109:8000'),
    ('moist towelette', '192.168.100.106:8000'),
))
def test_mapper_select(consul_mapper_synced, key, expected_host):
    assert (str(consul_mapper_synced.select(key).socket_address) ==
            expected_host)
