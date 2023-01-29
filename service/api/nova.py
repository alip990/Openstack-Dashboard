from novaclient.client import Client as nova_client
from rest_framework.serializers import ValidationError
from .neutron import  get_project_default_network
from glanceclient import Client as glance_client
from .glance import get_image_by_id

from service.api import _nova
get_microversion = _nova.get_microversion
server_get = _nova.server_get
Server = _nova.Server


def update_pagination(entities, page_size, marker, reversed_order=False):
    has_more_data = has_prev_data = False
    if len(entities) > page_size:
        has_more_data = True
        entities.pop()
        if marker is not None:
            has_prev_data = True
    # first page condition when reached via prev back
    elif reversed_order and marker is not None:
        has_more_data = True
    # last page condition
    elif marker is not None:
        has_prev_data = True

    # restore the original ordering here
    if reversed_order:
        entities.reverse()

    return entities, has_more_data, has_prev_data


def server_list_paged(session,
                      search_opts=None,
                      detailed=True,
                      sort_dir="desc"):
    has_more_data = False
    has_prev_data = False
    nova_client = _nova.novaclient(session=session)
    page_size = 20
    search_opts = {} if search_opts is None else search_opts
    marker = search_opts.get('marker', None)

    # if not search_opts.get('all_tenants', False):
    #     search_opts['project_id'] = request.user.tenant_id

    if search_opts.pop('paginate', False):
        reversed_order = sort_dir == "asc"
        # LOG.debug("Notify received on deleted server: %r",
        #           ('server_deleted' in request.session))
        # deleted = request.session.pop('server_deleted',
        #                               None)
        deleted = None
        view_marker = 'possibly_deleted' if deleted and marker else 'ok'
        search_opts['marker'] = deleted if deleted else marker
        search_opts['limit'] = page_size + 1
        # NOTE(amotoki): It looks like the 'sort_keys' must be unique to make
        # the pagination in the nova API works as expected. Multiple servers
        # can have a same 'created_at' as its resolution is a second.
        # To ensure the uniqueness we add 'uuid' to the sort keys.
        # 'display_name' is added before 'uuid' to list servers in the
        # alphabetical order.
        sort_keys = ['created_at', 'display_name', 'uuid']

        servers = [Server(s, session=session)
                   for s in nova_client.servers.list(detailed, search_opts,
                                                     sort_keys=sort_keys,
                                                     sort_dirs=[sort_dir] * 3)]

        if view_marker == 'possibly_deleted':
            if not servers:
                view_marker = 'head_deleted'
                reversed_order = False
                servers = [Server(s, session)
                           for s in
                           nova_client.servers.list(detailed,
                                                    search_opts,
                                                    sort_keys=sort_keys,
                                                    sort_dirs=['desc'] * 3)]
            if not servers:
                view_marker = 'tail_deleted'
                reversed_order = True
                servers = [Server(s, session)
                           for s in
                           nova_client.servers.list(detailed,
                                                    search_opts,
                                                    sort_keys=sort_keys,
                                                    sort_dirs=['asc'] * 3)]
        (servers, has_more_data, has_prev_data) = update_pagination(
            servers, page_size, marker, reversed_order)
        has_prev_data = (False
                         if view_marker == 'head_deleted'
                         else has_prev_data)
        has_more_data = (False
                         if view_marker == 'tail_deleted'
                         else has_more_data)
    else:
        servers = [Server(s, session=session)
                   for s in nova_client.servers.list(detailed, search_opts)]
    return (servers, has_more_data, has_prev_data)


def server_list(session, search_opts=None, detailed=True):
    (servers, has_more_data, _) = server_list_paged(session,
                                                    search_opts,
                                                    detailed)
    return (servers, has_more_data)


def get_flavor_list(session):
    nova = nova_client('2', session=session)
    flavors = nova.flavors.list()
    return [{
        "id": flavor.id,
        'cpu': {"size": flavor.vcpus, 'unit': 'core'},
        'ram': {"size": flavor.ram, 'unit': 'mb'},
        'name': flavor.name,
        'disk': {"size": flavor.disk, 'unit': 'Gb'},
        "ratings": {
            "monthly": 379929600,
            "daily": 12664320,
            "hourly": 527680
        }

    } for flavor in flavors]


def get_flavor_by_id(id, session):
    nova = nova_client('2', session=session)
    flavor = nova.flavors.get(id)
    return {
        "id": flavor.id,
        'cpu': {"size": flavor.vcpus, 'unit': 'core'},
        'ram': {"size": flavor.ram, 'unit': 'mb'},
        'name': flavor.name,
        'disk': {"size": flavor.disk, 'unit': 'Gb'},
        "ratings": {
            "monthly": 379929600,
            "daily": 12664320,
            "hourly": 527680
        }
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
        return nova.keypairs.create(name=name, public_key=public_key)
    except Exception as e:
        # print(e.code, e.message)
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
        raise e
        if hasattr(e, 'code') and e.code == 404:
            print(e)
            raise ValidationError('object 22not found')
        print(e)
        raise ValidationError('object11 not found')


def get_server_list(session):
    nova = nova_client('2', session=session)
    servers = nova.servers.list(detailed=True)
    # print('server.image', servers[0].image_id)
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


def get_server_info(session, id):
    nova = nova_client('2', session=session)
    server = nova.servers.get(id)
    return {
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
    }
