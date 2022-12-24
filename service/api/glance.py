from glanceclient import Client


def get_image_list(session):
    glance = Client('2', session=session)
    return glance.images.list()
