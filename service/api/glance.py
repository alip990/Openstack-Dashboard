from glanceclient import Client as glance_client


from service.api import base

from collections import abc
import itertools


from keystoneauth1.identity import v3
from keystoneauth1 import session

from dashboard.settings import OPENSTACK_URL, OPENSTACK_ADMIN_PASSWORD, OPENSTACK_ADMIN_USERNAME
import logging

LOG = logging.getLogger(__name__)


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
    return glance_client('2', session=session)


def get_admin_session():
    auth = v3.Password(auth_url=OPENSTACK_URL, username=OPENSTACK_ADMIN_USERNAME,
                       password=OPENSTACK_ADMIN_PASSWORD, project_name="admin",
                       user_domain_id="default", project_domain_id="default")
    sess = session.Session(auth=auth , )
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
        "os_distro": image['os_distro'],
        "os_version": image.os_version,
        "os_admin_user": image.os_admin_user,
        "created_at": image.created_at,
        "photo": image.photo,
    } for image in images]


def get_image_by_id(id, session):
    glance = glance_client('2', session=session)
    LOG.debug('get_image_by_id', id)
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


def _normalize_is_public_filter(filters):
    if not filters:
        return

    # Glance v2 uses filter 'visibility' ('public', 'private', ...).
    if 'is_public' in filters:
        # Glance v2: Replace 'is_public' with 'visibility'.
        visibility = PUBLIC_TO_VISIBILITY_MAP[filters['is_public']]
        del filters['is_public']
        if visibility is not None:
            filters['visibility'] = visibility


def _normalize_owner_id_filter(filters):
    if not filters:
        return

    # Glance v2 uses filter 'owner' (Project ID).
    if 'property-owner_id' in filters:
        # Glance v2: Replace 'property-owner_id' with 'owner'.
        filters['owner'] = filters['property-owner_id']
        del filters['property-owner_id']


def _normalize_list_input(filters, **kwargs):
    _normalize_is_public_filter(filters)
    _normalize_owner_id_filter(filters)


def image_delete(session, image_id):
    return glanceclient(session).images.delete(image_id)


def image_list_detailed(session, marker=None, sort_dir='desc',
                        sort_key='created_at', filters=None, paginate=False,
                        reversed_order=False, **kwargs):
    """Thin layer above glanceclient, for handling pagination issues.

    It provides iterating both forward and backward on top of ascetic
    OpenStack pagination API - which natively supports only iterating forward
    through the entries. Thus in order to retrieve list of objects at previous
    page, a request with the reverse entries order had to be made to Glance,
    using the first object id on current page as the marker - restoring
    the original items ordering before sending them back to the UI.

    :param request:

        The request object coming from browser to be passed further into
        Glance service.

    :param marker:

        The id of an object which defines a starting point of a query sent to
        Glance service.

    :param sort_dir:

        The direction by which the resulting image list throughout all pages
        (if pagination is enabled) will be sorted. Could be either 'asc'
        (ascending) or 'desc' (descending), defaults to 'desc'.

    :param sort_key:

        The name of key by which the resulting image list throughout all
        pages (if pagination is enabled) will be sorted. Defaults to
        'created_at'.

    :param filters:

        A dictionary of filters passed as is to Glance service.

    :param paginate:

        Whether the pagination is enabled. If it is, then the number of
        entries on a single page of images table is limited to the specific
        number stored in browser cookies.

    :param reversed_order:

        Set this flag to True when it's necessary to get a reversed list of
        images from Glance (used for navigating the images list back in UI).
    """
    limit = 100
    page_size = 100

    if paginate:
        request_size = page_size + 1
    else:
        request_size = limit

    _normalize_list_input(filters, **kwargs)
    kwargs = {'filters': filters or {}}

    if marker:
        kwargs['marker'] = marker
    kwargs['sort_key'] = sort_key

    if not reversed_order:
        kwargs['sort_dir'] = sort_dir
    else:
        kwargs['sort_dir'] = 'desc' if sort_dir == 'asc' else 'asc'

    images_iter = glanceclient(session).images.list(page_size=request_size,
                                                    limit=limit,
                                                    **kwargs)
    has_prev_data = False
    has_more_data = False
    if paginate:
        images = list(itertools.islice(images_iter, request_size))
        # first and middle page condition
        if len(images) > page_size:
            images.pop(-1)
            has_more_data = True
            # middle page condition
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
            images = sorted(images, key=lambda image:
                            (getattr(image, sort_key) or '').lower(),
                            reverse=(sort_dir == 'desc'))
    else:
        images = list(images_iter)

    # TODO(jpichon): Do it better
    wrapped_images = []
    for image in images:
        wrapped_images.append(Image(image))

    return wrapped_images, has_more_data, has_prev_data
