from novaclient import client
from rest_framework.serializers import ValidationError


def get_flavor_list(session):
    nova = client.Client('2', session=session)
    flavors = nova.flavors.list()
    return [{
        "id": flavor.id,
        'cpu': {"size": flavor.vcpus, 'unit': 'core'},
        'ram': {"size": flavor.ram, 'unit': 'mb'},
        'name': flavor.name,
        'disk': {"size": flavor.disk, 'unit': 'Gb'}
    } for flavor in flavors]


def get_keypair_list(session):
    nova = client.Client('2', session=session)
    keypairs = nova.keypairs.list()
    return [{
        "id": keypair.id,
        "name": keypair.name,
        "public_key": keypair.public_key,
    }for keypair in keypairs]


def create_keypair(name, public_key, session):
    nova = client.Client('2', session=session)
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


def update_keypair(name, public_key):
    pass
