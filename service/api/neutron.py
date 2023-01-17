from neutronclient.v2_0.client import Client as neutron_client


def create_network(project_name, session):

    network_name = project_name+'_network'
    neutron = neutron_client(session=session)

    try:
        body_sample = {'network': {'name': network_name,
                       'admin_state_up': True}}

        netw = neutron.create_network(body=body_sample)
        net_dict = netw['network']
        network_id = net_dict['id']
        print('Network %s created' % network_id)

        body_create_subnet = {'subnets': [{'cidr': '192.168.199.0/24',
                              'ip_version': 4, 'network_id': network_id}]}

        subnet = neutron.create_subnet(body=body_create_subnet)
        print('Created subnet %s' % subnet)
    except Exception as e:
        print(e)


def create_router(network_id, project_name, session):

    try:
        neutron = neutron_client(session=session)
        router_name = project_name+'_router'
        neutron.format = 'json'
        request = {'router': {'name': router_name,
                              'admin_state_up': True}}
        router = neutron.create_router(request)
        router_id = router['router']['id']
        router = neutron.show_router(router_id)
        print(router)
        body_value = {'port': {
            'admin_state_up': True,
            'device_id': router_id,
            'name': 'port1',
            'network_id': network_id,
        }}

        response = neutron.create_port(body=body_value)
        print(response)
    finally:
        print("Execution completed")
        return router


def get_project_default_network(session):
    # todo
    try:
        print('*******************88888', session)
        neutron = neutron_client(session=session)
        # network_name = project_name+'_network'
        print('///////////////////////////////////////////')

        network = neutron.list_networks()['networks'][0]
        print(network)
        return network
    except Exception as e:
        print(e)
