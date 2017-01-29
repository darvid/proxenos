import pytest

import proxenos.rendezvous


def update_mapper(mapper, consul_services, service_name):
    mapper._conn.catalog.services.return_value = [[service_name]]
    mapper._conn.catalog.service.side_effect = lambda _: consul_services
    mapper.update()


@pytest.fixture
def consul_host():
    return '127.0.0.1'


@pytest.fixture
def consul_port():
    return 8500


@pytest.fixture
def consul_mapper(mocker, consul_host, consul_port):
    mocker.patch('consulate.Consul')
    return proxenos.mappers.consul.ConsulClusterMapper(
        consul_host, consul_port)


@pytest.fixture
def consul_mapper_synced(consul_mapper, consul_services, service_name):
    update_mapper(consul_mapper, consul_services, service_name)
    return consul_mapper


@pytest.fixture
def consul_services(cluster, service_name, service_tags):
    return [
        {
            'Address': service.socket_address.host.ipv4(),
            'ServiceName': service_name,
            'ServicePort': service.socket_address.port,
            'ServiceTags': service_tags,
        }
        for service in cluster
    ]

@pytest.fixture(scope='module')
def cluster(service_name, service_tags):
    return {
        proxenos.node.Service(
            name=service_name,
            socket_address=proxenos.node.SocketAddress(
                host='192.168.100.{}'.format(100 + i),
                port=8000),
            tags=service_tags)
        for i in range(10)
    }


@pytest.fixture(scope='module')
def service_name():
    return 'frobnicator'


@pytest.fixture(scope='module')
def service_tags():
    return ['frobnitz']
