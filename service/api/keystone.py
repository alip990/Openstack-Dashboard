from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneauth1 import exceptions as keystone_exceptions
from keystoneclient.v3 import client
from dashboard.settings import OPENSTACK_URL, OPENSTACK_ADMIN_PASSWORD, OPENSTACK_ADMIN_USERNAME
import uuid
from .neutron import create_network, create_router
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import NotFound

# 'http://172.16.2.45:5000',username="admin",password="0dNFOJeHuWne6AAeWPyCHOtPEAvU903F7XvukFG7"


def get_admin_keystone_client():
    auth = v3.Password(auth_url=OPENSTACK_URL, username=OPENSTACK_ADMIN_USERNAME,
                       password=OPENSTACK_ADMIN_PASSWORD, project_name="admin",
                       user_domain_id="default", project_domain_id="default")

    sess = session.Session(auth=auth)
    keystone = client.Client(session=sess)
    return keystone


def get_admin_session():
    auth = v3.Password(auth_url=OPENSTACK_URL, username=OPENSTACK_ADMIN_USERNAME,
                       password=OPENSTACK_ADMIN_PASSWORD, project_name="admin",
                       user_domain_id="default", project_domain_id="default")

    sess = session.Session(auth=auth)
    return sess


def get_user_session(username, password, project_id=None):

    auth = v3.Password(auth_url=OPENSTACK_URL, username=username,
                       password=password, project_id=project_id,
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


def get_keystone_client_by_session(session):
    return client.Client(session=session)


def get_user_project_list(username):
    keystone_admin_client = get_admin_keystone_client()
    user = keystone_admin_client.users.list(name=username)[0]
    projects = keystone_admin_client.projects.list(user=user.id)
    return [{
            "description": project.description,
            "id": project.id,
            "name": project.name
            } for project in projects]


def create_openstack_user(email, admin_client, default_project=None):
    # openstack_username = uuid.uuid4().hex[:10]
    openstack_password = uuid.uuid4().hex[:15]
    user = admin_client.users.create(name=email, email=email,
                                     password=openstack_password,
                                     domain='default', default_project=default_project)
    return {'openstack_username': email,
            'openstack_password': openstack_password,
            'openstack_user_id': user.id}


def get_project(session, project_id):
    try:
        client = get_keystone_client_by_session(session)
        project = client.projects.get(project_id)
        return project
    except Exception as e:
        print(e)


def create_project(name: str, username: str, description: str, password: str):
    """
    create project and assign user member to it
    """
    try:
        client = get_admin_keystone_client()

        user = client.users.list(name=username)[0]

        project = client.projects.create(
            name=username+'_'+name, description=description, domain='default', enabled=True)
        role = client.roles.list(name='member')[0]
        client.roles.grant(
            role.id,
            user=user.id,
            project=project.id)
        print()
        session = get_user_session(
            username, password, project.id)

        net_id = create_network(project_name=project.name, session=session)
        create_router(network_id=net_id,
                      project_name=project.name, session=session)
        return project
    except keystone_exceptions.Conflict:
        raise ValidationError('project with this name already exists')


def delete_project(session, project_id):
    try:
        client = get_keystone_client_by_session(session)
        project = client.projects.delete(project_id)
        print(project)
    except Exception as e:
        print(e)


def project_update(session, project, username, name=None, description=None,
                   enabled=None,):
    try:
        client = get_keystone_client_by_session(session)
        if name:
            name = username+'_'+name
        pr = client.projects.update(project, name=name, description=description
                                    )

        return pr
    except keystone_exceptions.Conflict:
        raise ValidationError('project with this name already exists')
    except keystone_exceptions.Unauthorized:
        raise NotFound('No project found with this Id')
    except keystone_exceptions.NotFound:
        raise NotFound('No project found with this Id')
    except Exception as e:
        print(e)


def openstack_user_init(email):
    """
    admin should verify user in admin_panel to give user openstack access
    for initialise user we go throw these steps:
        1- create openstack user
        2- create default project in format of f"{user_name}_default" to avoid duplicate name
        3- grant member role to user for default project
        4- create network and router for project 
    """
    print('openstack_user_init')
    admin_client = get_admin_keystone_client()
    founded_user = None
    try:
        founded_user = admin_client.users.find(name=email)
    except:
        pass
    print('founded_user ', founded_user)
    if founded_user:
        raise Exception('email was already exists in openstack')
    # project = create_project(
    #     'default', user['openstack_username'], 'Default project!')
    project = admin_client.projects.create(
        name=email+'_default', description='Default project!', domain='default', enabled=True)
    print('openstack default project created ', project)

    user = create_openstack_user(email, admin_client, default_project=project)
    print('openstack user create ', user['openstack_user_id'])
    role = admin_client.roles.list(name='member')[0]
    admin_client.roles.grant(
        role.id,
        user=user['openstack_user_id'],
        project=project.id)
    session = get_user_session(
        user['openstack_username'], user['openstack_password'], project_id=project.id)
    net_id = create_network(project_name=project.name, session=session)
    create_router(network_id=net_id,
                  project_name=project.name, session=session)

    print(f"user granted project {project.id} ")

    return {'openstack_username': user['openstack_username'],
            'openstack_password': user['openstack_password']}


def check_user_exist(email):
    admin_client = get_admin_keystone_client()
    try:
        founded_user = admin_client.users.find(name=email)
        if founded_user:
            return True
    except:
        pass
    return False
