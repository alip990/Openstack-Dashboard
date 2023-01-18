from novaclient.client import Client as nova_client
from rest_framework.serializers import ValidationError
from .neutron import create_router, create_network, get_project_default_network
from glanceclient import Client as glance_client
from .glance import get_image_by_id


def get_flavor_list(session):
    nova = nova_client('2', session=session)
    flavors = nova.flavors.list()
    return [{
        "id": flavor.id,
        'cpu': {"size": flavor.vcpus, 'unit': 'core'},
        'ram': {"size": flavor.ram, 'unit': 'mb'},
        'name': flavor.name,
        'disk': {"size": flavor.disk, 'unit': 'Gb'}
    } for flavor in flavors]


def get_flavor_by_id(id, session):
    nova = nova_client('2', session=session)
    flavor = nova.flavors.get(id)
    return {
        "id": flavor.id,
        'cpu': {"size": flavor.vcpus, 'unit': 'core'},
        'ram': {"size": flavor.ram, 'unit': 'mb'},
        'name': flavor.name,
        'disk': {"size": flavor.disk, 'unit': 'Gb'}
    }


def get_keypair_list(session):
    nova = nova_client('2', session=session)
    keypairs = nova.keypairs.list()
    return [{
        "id": keypair.id,
        "name": keypair.name,
        "public_key": keypair.public_key,
    }for keypair in keypairs]


def create_keypair(name, public_key, session):
    nova = nova_client('2', session=session)
    try:
        nova.keypairs.create(name=name, public_key=public_key)
    except Exception as e:
        print(e.code, e.message)
        if e.code == 400:
            raise ValidationError(
                {"public_key": ["public_key is invalid " + e.message]})
        if e.code == 409:
            raise ValidationError({"name": ["already exist" + e.message]})

        raise ValidationError(e.message)


def create_server(name, flavor_id, image_id, keypair_name, session):
    try:
        nova = nova_client('2', session=session)
        # flavor = get_flavor_by_id(1, session)
        glance = glance_client('2', session=session)
        image = glance.images.get(image_id)
        network = get_project_default_network(session)
        nics = [{'net-id': network['id']}]
        instance = nova.servers.create(name=name, image=image,
                                       flavor=flavor_id, key_name=keypair_name, nics=nics)
        return instance
    except Exception as e:
        if hasattr(e, 'code') and e.code == 404:
            print(e)
            raise ValidationError('object not found')
        print(e)
        raise ValidationError('object not found')


def get_server_list(session):
    nova = nova_client('2', session=session)
    servers = nova.servers.list(detailed=True)
    # print('server.image', servers[0].image_id)
    print('------------------',
          get_image_by_id(servers[0].image['id'], session))
    a = [{
        "accessIPv4": server.accessIPv4,
        "accessIPv6": server.accessIPv6,
        "addresses": server.addresses,
        "created": server.created,
        "id": server.id,
        "image": get_image_by_id(server.image['id'], session),
        "key_name": server.key_name,
        "metadata": server.metadata,
        "name": server.name,
        "networks": server.networks,
        "project_id": server.tenant_id,
        "status": server.status,
        "hostId": server.hostId,
        "flavor": get_flavor_by_id(server.flavor['id'], session)
    } for server in servers]
    print(a)
    return a
