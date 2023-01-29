from neutronclient.v2_0.client import Client as neutron_client


from neutronclient.common import exceptions as neutron_exc
from neutronclient.v2_0 import client as neutron_client
from novaclient import exceptions as nova_exc

import netaddr


import collections
from collections.abc import Sequence
import copy
import itertools
# import memoized
from service.api import base

IP_VERSION_DICT = {4: 'IPv4', 6: 'IPv6'}

OFF_STATE = 'OFF'
ON_STATE = 'ON'


class NeutronAPIDictWrapper(base.APIDictWrapper):

    def __init__(self, apidict):
        if 'admin_state_up' in apidict:
            if apidict['admin_state_up']:
                apidict['admin_state'] = 'UP'
            else:
                apidict['admin_state'] = 'DOWN'

        # Django cannot handle a key name with ':', so use '__'.
        apidict.update({
            key.replace(':', '__'): value
            for key, value in apidict.items()
            if ':' in key
        })
        super().__init__(apidict)

    def set_id_as_name_if_empty(self, length=8):
        try:
            if not self._apidict['name'].strip():
                id = self._apidict['id']
                if length:
                    id = id[:length]
                self._apidict['name'] = '(%s)' % id
        except KeyError:
            pass

    def items(self):
        return self._apidict.items()

    @property
    def name_or_id(self):
        return (self._apidict.get('name').strip() or
                '(%s)' % self._apidict['id'][:13])


class Network(NeutronAPIDictWrapper):
    """Wrapper for neutron Networks."""


class PortAllowedAddressPair(NeutronAPIDictWrapper):
    """Wrapper for neutron port allowed address pairs."""

    def __init__(self, addr_pair):
        super().__init__(addr_pair)
        # Horizon references id property for table operations
        self.id = addr_pair['ip_address']


class Port(NeutronAPIDictWrapper):
    """Wrapper for neutron ports."""

    def __init__(self, apidict):
        if 'mac_learning_enabled' in apidict:
            apidict['mac_state'] = \
                ON_STATE if apidict['mac_learning_enabled'] else OFF_STATE
        pairs = apidict.get('allowed_address_pairs')
        if pairs:
            apidict = copy.deepcopy(apidict)
            wrapped_pairs = [PortAllowedAddressPair(pair) for pair in pairs]
            apidict['allowed_address_pairs'] = wrapped_pairs
        super().__init__(apidict)


class SecurityGroup(NeutronAPIDictWrapper):
    # Required attributes: id, name, description, tenant_id, rules

    def __init__(self, sg, sg_dict=None):
        if sg_dict is None:
            sg_dict = {sg['id']: sg['name']}
        if 'security_group_rules' not in sg:
            sg['security_group_rules'] = []
        sg['rules'] = [SecurityGroupRule(rule, sg_dict)
                       for rule in sg['security_group_rules']]
        super().__init__(sg)

    def to_dict(self):
        return {k: self._apidict[k] for k in self._apidict if k != 'rules'}


class SecurityGroupRule(NeutronAPIDictWrapper):
    # Required attributes:
    #   id, parent_group_id
    #   ip_protocol, from_port, to_port, ip_range, group
    #   ethertype, direction (Neutron specific)

    def _get_secgroup_name(self, sg_id, sg_dict):
        if not sg_id:
            return ''

        if sg_dict is None:
            sg_dict = {}
        # If sg name not found in sg_dict,
        # first two parts of UUID is used as sg name.
        return sg_dict.get(sg_id, sg_id[:13])

    def __init__(self, sgr, sg_dict=None):
        # In Neutron, if both remote_ip_prefix and remote_group_id are None,
        # it means all remote IP range is allowed, i.e., 0.0.0.0/0 or ::/0.
        if not sgr['remote_ip_prefix'] and not sgr['remote_group_id']:
            if sgr['ethertype'] == 'IPv6':
                sgr['remote_ip_prefix'] = '::/0'
            else:
                sgr['remote_ip_prefix'] = '0.0.0.0/0'

        rule = {
            'id': sgr['id'],
            'parent_group_id': sgr['security_group_id'],
            'direction': sgr['direction'],
            'ethertype': sgr['ethertype'],
            'ip_protocol': sgr['protocol'],
            'from_port': sgr['port_range_min'],
            'to_port': sgr['port_range_max'],
            'description': sgr.get('description', '')
        }
        cidr = sgr['remote_ip_prefix']
        rule['ip_range'] = {'cidr': cidr} if cidr else {}
        group = self._get_secgroup_name(sgr['remote_group_id'], sg_dict)
        rule['group'] = {'name': group} if group else {}
        super().__init__(rule)

    def __str__(self):
        if 'name' in self.group:
            remote = self.group['name']
        elif 'cidr' in self.ip_range:
            remote = self.ip_range['cidr']
        else:
            remote = 'ANY'
        direction = 'to' if self.direction == 'egress' else 'from'
        if self.from_port:
            if self.from_port == self.to_port:
                proto_port = ("%s/%s" %
                              (self.from_port, self.ip_protocol.lower()))
            else:
                proto_port = ("%s-%s/%s" %
                              (self.from_port, self.to_port,
                               self.ip_protocol.lower()))
        elif self.ip_protocol:
            try:
                ip_proto = int(self.ip_protocol)
                proto_port = "ip_proto=%d" % ip_proto
            except Exception:
                # well-defined IP protocol name like TCP, UDP, ICMP.
                proto_port = self.ip_protocol
        else:
            proto_port = ''

        return (_('ALLOW %(ethertype)s %(proto_port)s '
                  '%(direction)s %(remote)s') %
                {'ethertype': self.ethertype,
                 'proto_port': proto_port,
                 'remote': remote,
                 'direction': direction})


class SecurityGroupManager(object):
    """Manager class to implement Security Group methods

    SecurityGroup object returned from methods in this class
    must contains the following attributes:

    * id: ID of Security Group (int for Nova, uuid for Neutron)
    * name
    * description
    * tenant_id
    * shared: A boolean indicates whether this security group is shared
    * rules: A list of SecurityGroupRule objects

    SecurityGroupRule object should have the following attributes
    (The attribute names and their formats are borrowed from nova
    security group implementation):

    * id
    * direction
    * ethertype
    * parent_group_id: security group the rule belongs to
    * ip_protocol
    * from_port: lower limit of allowed port range (inclusive)
    * to_port: upper limit of allowed port range (inclusive)
    * ip_range: remote IP CIDR (source for ingress, dest for egress).
      The value should be a format of "{'cidr': <cidr>}"
    * group: remote security group. The value should be a format of
      "{'name': <secgroup_name>}"
    """
    backend = 'neutron'

    def __init__(self, session):
        self.session = session
        self.client = neutronclient(session)

    def _list(self, **filters):
        if (filters.get("tenant_id") and
                is_extension_supported(
                    self.session, 'security-groups-shared-filtering')):
            # NOTE(hangyang): First, we get the SGs owned by but not shared
            # to the requester(tenant_id)
            filters["shared"] = False
            secgroups_owned = self.client.list_security_groups(**filters)
            # NOTE(hangyang): Second, we get the SGs shared to the
            # requester. For a requester with an admin role, this second
            # API call also only returns SGs shared to the requester's tenant
            # instead of all the SGs shared to any tenant.
            filters.pop("tenant_id")
            filters["shared"] = True
            secgroups_rbac = self.client.list_security_groups(**filters)
            return [SecurityGroup(sg) for sg in
                    itertools.chain(secgroups_owned.get('security_groups'),
                                    secgroups_rbac.get('security_groups'))]
        secgroups = self.client.list_security_groups(**filters)
        return [SecurityGroup(sg) for sg in secgroups.get('security_groups')]

    # @profiler.trace
    def list(self, **params):
        """Fetches a list all security groups.

        :returns: List of SecurityGroup objects
        """
        # This is to ensure tenant_id key is not populated
        # if tenant_id=None is specified.
        # tenant_id = params.pop('tenant_id', self.request.user.tenant_id)
        # if tenant_id:
        #     params['tenant_id'] = tenant_id
        return self._list(**params)

    def _sg_name_dict(self, sg_id, rules):
        """Create a mapping dict from secgroup id to its name."""
        related_ids = set([sg_id])
        related_ids |= set(filter(None, [r['remote_group_id'] for r in rules]))
        related_sgs = self.client.list_security_groups(id=related_ids,
                                                       fields=['id', 'name'])
        related_sgs = related_sgs.get('security_groups')
        return dict((sg['id'], sg['name']) for sg in related_sgs)

    # @profiler.trace
    def get(self, sg_id):
        """Fetches the security group.

        :returns: SecurityGroup object corresponding to sg_id
        """
        secgroup = self.client.show_security_group(sg_id).get('security_group')
        sg_dict = self._sg_name_dict(sg_id, secgroup['security_group_rules'])
        return SecurityGroup(secgroup, sg_dict)

    # @profiler.trace
    def create(self, name, desc, project_id):
        """Create a new security group.

        :returns: SecurityGroup object created
        """
        body = {'security_group': {'name': name,
                                   'description': desc,
                                   'tenant_id': project_id}}
        secgroup = self.client.create_security_group(body)
        return SecurityGroup(secgroup.get('security_group'))

    # @profiler.trace
    def update(self, sg_id, name, desc):
        body = {'security_group': {'name': name,
                                   'description': desc}}
        secgroup = self.client.update_security_group(sg_id, body)
        return SecurityGroup(secgroup.get('security_group'))

    # @profiler.trace
    def delete(self, sg_id):
        """Delete the specified security group."""
        self.client.delete_security_group(sg_id)

    # @profiler.trace
    def rule_create(self, parent_group_id,
                    direction=None, ethertype=None,
                    ip_protocol=None, from_port=None, to_port=None,
                    cidr=None, group_id=None, description=None):
        """Create a new security group rule.

        :param parent_group_id: security group id a rule is created to
        :param direction: ``ingress`` or ``egress``
        :param ethertype: ``IPv4`` or ``IPv6``
        :param ip_protocol: tcp, udp, icmp
        :param from_port: L4 port range min
        :param to_port: L4 port range max
        :param cidr: Remote IP CIDR
        :param group_id: ID of Source Security Group
        :returns: SecurityGroupRule object
        """
        if not cidr:
            cidr = None
        if isinstance(from_port, int) and from_port < 0:
            from_port = None
        if isinstance(to_port, int) and to_port < 0:
            to_port = None
        if isinstance(ip_protocol, int) and ip_protocol < 0:
            ip_protocol = None

        params = {'security_group_id': parent_group_id,
                  'direction': direction,
                  'ethertype': ethertype,
                  'protocol': ip_protocol,
                  'port_range_min': from_port,
                  'port_range_max': to_port,
                  'remote_ip_prefix': cidr,
                  'remote_group_id': group_id}
        if description is not None:
            params['description'] = description
        body = {'security_group_rule': params}
        try:
            rule = self.client.create_security_group_rule(body)
        except neutron_exc.OverQuotaClient:
            raise Exception(
                'Security group rule quota exceeded.')
        except neutron_exc.Conflict:
            raise Exception(
                'Security group rule already exists.')
        rule = rule.get('security_group_rule')
        sg_dict = self._sg_name_dict(parent_group_id, [rule])
        return SecurityGroupRule(rule, sg_dict)

    # @profiler.trace
    def rule_delete(self, sgr_id):
        """Delete the specified security group rule."""
        self.client.delete_security_group_rule(sgr_id)

    # @profiler.trace
    def list_by_instance(self, instance_id):
        """Gets security groups of an instance.

        :returns: List of SecurityGroup objects associated with the instance
        """
        ports = port_list(self.session, device_id=instance_id)
        sg_ids = []
        for p in ports:
            sg_ids += p.security_groups
        return self._list(id=set(sg_ids)) if sg_ids else []

    # @profiler.trace
    def update_instance_security_group(self, instance_id,
                                       new_security_group_ids):
        """Update security groups of a specified instance."""
        ports = port_list(self.session, device_id=instance_id)
        for p in ports:
            params = {'security_groups': new_security_group_ids}
            port_update(self.session, p.id, **params)


# @profiler.trace
def port_list(session, **params):
    print("port_list(): params=%s", params)
    ports = neutronclient(session).list_ports(**params).get('ports')
    return [Port(p) for p in ports]


# @profiler.trace
def is_extension_supported(session, extension_alias):
    """Check if a specified extension is supported.

    :param request: django request object
    :param extension_alias: neutron extension alias
    """
    extensions = list_extensions(session)
    for extension in extensions:
        if extension['alias'] == extension_alias:
            return True
    else:
        return False


# @profiler.trace
def list_extensions(session):
    """List neutron extensions.

    :param request: django request object
    """
    neutron_api = neutronclient(session)
    try:
        extensions_list = neutron_api.list_extensions()
    except Exception:
        return {}
    if 'extensions' in extensions_list:
        return tuple(extensions_list['extensions'])
    return ()


def unescape_port_kwargs(**kwargs):
    keys = list(kwargs)
    for key in keys:
        if '__' in key:
            kwargs[':'.join(key.split('__'))] = kwargs.pop(key)
    return kwargs


# @profiler.trace
def port_update(session, port_id, **kwargs):
    print("port_update(): portid=%(port_id)s, kwargs=%(kwargs)s",
          {'port_id': port_id, 'kwargs': kwargs})
    kwargs = unescape_port_kwargs(**kwargs)
    body = {'port': kwargs}
    port = neutronclient(session).update_port(port_id, body=body).get('port')
    return Port(port)


# @memoized
def neutronclient(session):
    # token_id, neutron_url, auth_url = get_auth_params_from_request(request)
    # insecure = settings.OPENSTACK_SSL_NO_VERIFY
    # cacert = settings.OPENSTACK_SSL_CACERT
    # c = neutron_client.Client(token=token_id,
    #                           auth_url=auth_url,
    #                           endpoint_url=neutron_url,
    #                           insecure=insecure, ca_cert=cacert)
    return neutron_client.Client(session=session)


def create_network(project_name, session):

    network_name = project_name+'_network'
    neutron = neutron_client.Client(session=session)

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
        neutron = neutron_client.Client(session=session)
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
        neutron = neutron_client.Client(session=session)
        # network_name = project_name+'_network'
        network = neutron.list_networks()['networks'][0]
        print(network)
        return network
    except Exception as e:
        print(e)
