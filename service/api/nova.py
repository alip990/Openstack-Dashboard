from novaclient import client


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
