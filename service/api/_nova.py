
"""
This module is a special module to define functions or other resources
which need to be imported outside of service.api.nova
 to avoid cyclic imports.
"""

# from django.conf import settings
# from glanceclient import exc as glance_exceptions
from novaclient import api_versions
from novaclient import client as nova_client
from service.api import glance, base, microversions, memoized
# from openstack_dashboard.contrib.developer.profiler import api as profiler


# Supported compute versions
# VERSIONS = base.APIVersionManager("compute", preferred_version=2)
# VERSIONS.load_supported_version(1.1, {"client": nova_client, "version": 1.1})
# VERSIONS.load_supported_version(2, {"client": nova_client, "version": 2})

# INSECURE = False
# CACERT = settings.OPENSTACK_SSL_CACERT


class Server(base.APIResourceWrapper):
    """Simple wrapper around novaclient.server.Server.

    Preserves the request info so image name can later be retrieved.
    """
    _attrs = ['addresses', 'attrs', 'id', 'image', 'links', 'description',
              'metadata', 'name', 'private_ip', 'public_ip', 'status', 'uuid',
              'image_name', 'VirtualInterfaces', 'flavor', 'key_name', 'fault',
              'tenant_id', 'user_id', 'created', 'locked',
              'OS-EXT-STS:power_state', 'OS-EXT-STS:task_state',
              'OS-EXT-SRV-ATTR:instance_name', 'OS-EXT-SRV-ATTR:host',
              'OS-EXT-SRV-ATTR:hostname', 'OS-EXT-SRV-ATTR:kernel_id',
              'OS-EXT-SRV-ATTR:ramdisk_id', 'OS-EXT-SRV-ATTR:root_device_name',
              'OS-EXT-SRV-ATTR:root_device_name', 'OS-EXT-SRV-ATTR:user_data',
              'OS-EXT-SRV-ATTR:reservation_id', 'OS-EXT-SRV-ATTR:launch_index',
              'OS-EXT-AZ:availability_zone', 'OS-DCF:diskConfig']

    def __init__(self, apiresource, session):
        super().__init__(apiresource)
        self.session = session

    # TODO(gabriel): deprecate making a call to Glance as a fallback.
    @property
    def image_name(self):
        if not self.image:
            return None
        if hasattr(self.image, 'name'):
            return self.image.name
        if 'name' in self.image:
            return self.image['name']
        try:
            image = glance.image_get(self.session, self.image['id'])
            self.image['name'] = image.name
            return image.name
        except Exception:
            self.image['name'] = None
            return None

    @property
    def availability_zone(self):
        return getattr(self, 'OS-EXT-AZ:availability_zone', "")

    @property
    def has_extended_attrs(self):
        return any(getattr(self, attr, None) for attr in [
            'OS-EXT-SRV-ATTR:instance_name', 'OS-EXT-SRV-ATTR:host',
            'OS-EXT-SRV-ATTR:hostname', 'OS-EXT-SRV-ATTR:kernel_id',
            'OS-EXT-SRV-ATTR:ramdisk_id', 'OS-EXT-SRV-ATTR:root_device_name',
            'OS-EXT-SRV-ATTR:root_device_name', 'OS-EXT-SRV-ATTR:user_data',
            'OS-EXT-SRV-ATTR:reservation_id', 'OS-EXT-SRV-ATTR:launch_index',
        ])

    @property
    def internal_name(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:instance_name', "")

    @property
    def host_server(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:host', "")

    @property
    def instance_name(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:instance_name', "")

    @property
    def reservation_id(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:reservation_id', "")

    @property
    def launch_index(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:launch_index', "")

    @property
    def hostname(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:hostname', "")

    @property
    def kernel_id(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:kernel_id', "")

    @property
    def ramdisk_id(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:ramdisk_id', "")

    @property
    def root_device_name(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:root_device_name', "")

    @property
    def user_data(self):
        return getattr(self, 'OS-EXT-SRV-ATTR:user_data', "")


# @memoized.memoized
def get_microversion(session, features):
    client = novaclient(session)
    min_ver, max_ver = api_versions._get_server_version_range(client)
    return (microversions.get_microversion_for_features(
        'nova', features, api_versions.APIVersion, min_ver, max_ver))


# def get_auth_params_from_request(request):
#     """Extracts properties needed by novaclient call from the request object.

#     These will be used to memoize the calls to novaclient.
#     """
#     return (
#         request.user.username,
#         request.user.token.id,
#         request.user.tenant_id,
#         request.user.token.project.get('domain_id'),
#         base.url_for(request, 'compute'),
#         base.url_for(request, 'identity')
#     )


# @memoized.memoized
# def cached_novaclient(request, version=None):
#     (
#         username,
#         token_id,
#         project_id,
#         project_domain_id,
#         nova_url,
#         auth_url
#     ) = get_auth_params_from_request(request)
#     if version is None:
#         version = VERSIONS.get_active_version()['version']
#     # c = nova_client.Client(version,
#     #                        username,
#     #                        token_id,
#     #                        project_id=project_id,
#     #                        project_domain_id=project_domain_id,
#     #                        auth_url=auth_url,
#     #                        insecure=INSECURE,
#     #                     #    cacert=CACERT,
#     #                        http_log_debug=True,
#     #                        auth_token=token_id,
#     #                        endpoint_override=nova_url)
#     return c


def novaclient(session, version=None):
    # if isinstance(version, api_versions.APIVersion):
    #     version = version.get_string()
    return nova_client.Client('2.37', session=session)


def get_novaclient_with_instance_desc(session):
    microversion = get_microversion(session, "instance_description")
    return novaclient(session, version=microversion)


# @profiler.trace
def server_get(session, instance_id):
    return Server(get_novaclient_with_instance_desc(session).servers.get(
        instance_id), session)
