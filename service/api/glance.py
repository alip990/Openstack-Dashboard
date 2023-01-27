from glanceclient import Client as glance_client


from service.api import base

from collections import abc


from keystoneauth1.identity import v3
from keystoneauth1 import session


class Image(base.APIResourceWrapper):
    _attrs = {"architecture", "container_format", "disk_format", "created_at",
              "owner", "size", "id", "status", "updated_at", "checksum",
              "visibility", "name", "is_public", "protected", "min_disk",
              "min_ram"}
    _ext_attrs = {"file", "locations", "schema", "tags", "virtual_size",
                  "kernel_id", "ramdisk_id", "image_url"}

    def __getattribute__(self, attr):
        # Because Glance v2 treats custom properties as normal
        # attributes, we need to be more flexible than the resource
        # wrappers usually allow.
        if attr == "properties":
            return {k: v for (k, v) in self._apiresource.items()
                    if self.property_visible(k)}
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return getattr(self._apiresource, attr)

    @property
    def name(self):
        return getattr(self._apiresource, 'name', None)

    @property
    def size(self):
        image_size = getattr(self._apiresource, 'size', 0)
        if image_size is None:
            return 0
        return image_size

    @size.setter
    def size(self, value):
        self._apiresource.size = value

    @property
    def is_public(self):
        # Glance v2 no longer has a 'is_public' attribute, but uses a
        # 'visibility' attribute instead.
        return (getattr(self._apiresource, 'is_public', None) or
                getattr(self._apiresource, 'visibility', None) == "public")

    def property_visible(self, prop_name, show_ext_attrs=False):
        if show_ext_attrs:
            return prop_name not in self._attrs
        return prop_name not in (self._attrs | self._ext_attrs)

    def to_dict(self, show_ext_attrs=False):
        if not isinstance(self._apiresource, abc.Iterable):
            return self._apiresource.to_dict()
        image_dict = super().to_dict()
        image_dict['is_public'] = self.is_public
        image_dict['properties'] = {
            k: self._apiresource[k] for k in self._apiresource
            if self.property_visible(k, show_ext_attrs=show_ext_attrs)}
        return image_dict

    def __eq__(self, other_image):
        return self._apiresource == other_image._apiresource

    def __ne__(self, other_image):
        return not self.__eq__(other_image)


def image_get(session, image_id):
    """Returns an Image object populated with metadata for a given image."""
    image = glanceclient(session).images.get(image_id)
    return Image(image)


def glanceclient(session=None):
    # api_version = VERSIONS.get_active_version()

    # url = base.url_for(request, 'image')
    # insecure = settings.OPENSTACK_SSL_NO_VERIFY
    # cacert = settings.OPENSTACK_SSL_CACERT

    # return api_version['client'].Client(url, token=request.user.token.id,
    #                                     insecure=insecure, cacert=cacert)
    return glance_client('2', session=get_admin_session())


def get_admin_session():
    auth = v3.Password(auth_url="http://172.16.2.45:5000/v3/", username="admin",
                       password="0dNFOJeHuWne6AAeWPyCHOtPEAvU903F7XvukFG7", project_name="admin",
                       user_domain_id="default", project_domain_id="default")
    sess = session.Session(auth=auth)
    return sess


def get_image_list(session):
    glance = glance_client('2', session=session)

    images = glance.images.list()
    return [{
        "id": image.id,
        "size": image.size,
        "name": image.name,
        "min_disk": image.min_disk,
        "min_ram": image.min_ram,
        "os_distro": image.os_distro,
        "os_version": image.os_version,
        "os_admin_user": image.os_admin_user,
        "created_at": image.created_at,
        "photo": image.photo,
    } for image in images]


def get_image_by_id(id, session):
    glance = glance_client('2', session=session)
    print('get_image_by_id', id)
    image = glance.images.get(id)
    return {"id": image.id,
            "size": image.size,
            "name": image.name,
            "min_disk": image.min_disk,
            "min_ram": image.min_ram,
            "os_distro": image.os_distro,
            "os_version": image.os_version,
            "os_admin_user": image.os_admin_user,
            "created_at": image.created_at,
            "photo": image.photo,
            }
