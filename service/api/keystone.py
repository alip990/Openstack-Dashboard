from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from dashboard.settings import OPENSTACK_URL, OPENSTACK_ADMIN_PASSWORD, OPENSTACK_ADMIN_USERNAME
import uuid

# 'http://172.16.2.45:5000',username="admin",password="0dNFOJeHuWne6AAeWPyCHOtPEAvU903F7XvukFG7"


def get_admin_keystone_client():
    auth = v3.Password(auth_url=OPENSTACK_URL, username=OPENSTACK_ADMIN_USERNAME,
                       password=OPENSTACK_ADMIN_PASSWORD, project_name="admin",
                       user_domain_id="default", project_domain_id="default")

    sess = session.Session(auth=auth)
    keystone = client.Client(session=sess)
    return keystone


def get_user_session(username, password):
    auth = v3.Password(auth_url=OPENSTACK_URL, username=OPENSTACK_ADMIN_USERNAME,
                       password=OPENSTACK_ADMIN_PASSWORD, project_name="admin",
                       user_domain_id="default", project_domain_id="default")

    sess = session.Session(auth=auth)
    return sess


def get_user_keystone_client(username, password):
    auth = v3.Password(auth_url=OPENSTACK_URL, username=OPENSTACK_ADMIN_USERNAME,
                       password=OPENSTACK_ADMIN_PASSWORD, project_name="admin",
                       user_domain_id="default", project_domain_id="default")

    sess = session.Session(auth=auth)
    keystone = client.Client(session=sess)
    return keystone


def get_user_project_list(keystone_client):
    return keystone_client.projects.list()


def create_openstack_user(email):
    client = get_admin_keystone_client()
    openstack_username = uuid.uuid4().hex[:10]
    openstack_password = uuid.uuid4().hex[:15]
    project = create_project(openstack_username +
                             '_default', 'Default project !')
    user = client.users.create(openstack_username, email,
                               password=openstack_password, role='member', domain='default', default_project=project)
    return {openstack_username: openstack_username, openstack_password: openstack_password}


def create_project(name: str, description: str, client):
    try:
        if not client:
            client = get_admin_keystone_client()
        project = client.projects.create(
            name=name, description=description, domain='default', enabled=True)
        return project
    except Exception as e:
        print(e)
