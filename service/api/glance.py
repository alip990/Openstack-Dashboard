from glanceclient import Client as glance_client


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
