from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.serializers import ValidationError
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from service.api import keystone, nova
from .api.keystone import get_admin_keystone_client, get_user_project_list, get_user_session, create_project, get_admin_session
from .api.glance import get_image_list
from .api.nova import get_flavor_list, get_keypair_list, create_keypair, create_server, get_server_list, get_server_info
from .serializers import KeypairSerializer, VmSerializer, ProjectSerializer
# Create your views here.
from users.models import User


class ProjectsView(APIView):

    permission_classes = [IsAuthenticated]
    # renderer_classes = [JSONRenderer]       # policy attribute

    def get(self, request):
        """
        API over user projects 
        """
        user = User.objects.get(email=request.user)
        projects = keystone.get_user_project_list(user.openstack_username)
        return JsonResponse(projects, safe=False)

    def post(self, request, id=None):
        """Create a single project.

        The PATCH data should be an application/json object with  the
        attributes to set to new values: "name" (string),  "description"
        """
        user = User.objects.get(email=request.user)
        data = ProjectSerializer(data=request.data)
        if data.is_valid():
            project = create_project(data.validated_data.get('name'), user.openstack_username,
                                     data.validated_data.get('description'), user.openstack_password)
            if not project:
                raise ValidationError('project with this name already exists')
            return JsonResponse({"name": request.data['name'], "description": request.data['description'], "id": project.id}, safe=False)
        else:
            raise ValidationError(data.errors)


class ProjectView(APIView):

    """API over a single project.

    Note that in the following "project" is used exclusively where in the
    underlying keystone API the terms "project" and "tenant" are used
    interchangeably.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get a specific project by id."""
        # return api.keystone.tenant_get(request, id, admin=False).to_dict()
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password)
        session = get_admin_session()
        servers = nova.server_list_paged(session)
        print('-----!!!!!!!___________________________________')
        print(servers[0][0].image_name)
        return Response(status=204)

    def delete(self, request, id):
        """Delete a single project by id.

        This method returns HTTP 204 (no content) on success.
        """
        # keystone.tenant_delete(request, id)
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password)
        keystone.delete_project(session=session, project_id=id)
        return Response(status=204)

    def patch(self, request, id):
        """Update a single project.

        The PATCH data should be an application/json object with  the
        attributes to set to new values: "name" (string),  "description"

        This method returns HTTP 204 (updated project) on success.
        """
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password)
        name = request.data.get('name', None)
        description = request.data.get('description', None)
        if not name or not description:
            raise ValidationError('name or description should be provided')

        project = keystone.project_update(
            session, id, username=user.email, name=name, description=description)

        return JsonResponse({"name": project.name, "description": project.description, "id": id}, safe=False)


class ImageView(APIView):

    def get(self, request):
        session = get_admin_session()
        images = get_image_list(session)
        return JsonResponse({"data": images}, safe=False)


class FlavorView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # user = User.objects.get(email=request.user)
        session = get_admin_session()
        flavors = get_flavor_list(session)
        print(flavors)
        print('flavors')

        return JsonResponse({'data': flavors}, safe=False)


class KeypairView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password)
        keypairs = get_keypair_list(session=session)
        print('keypair', keypairs)
        return JsonResponse({'data': keypairs}, safe=False)

    def post(self, request):
        k = KeypairSerializer(data=request.data)
        if k.is_valid():
            user = User.objects.get(email=request.user)
            session = get_user_session(
                user.openstack_username, user.openstack_password)
            keypair = create_keypair(k.validated_data.get('name'),
                                     k.validated_data.get('public_key'), session)

        else:
            raise ValidationError(k.errors)
        return JsonResponse({'name': k.validated_data.get('name'), 'public_key': k.validated_data.get('public_key')})


class VmView(APIView):
    def post(self, request):
        vm = VmSerializer(data=request.data)
        if vm.is_valid():
            user = User.objects.get(email=request.user)
            session = get_user_session(
                user.openstack_username, user.openstack_password, vm.validated_data.get('project_id'),)
            server = create_server(vm.validated_data.get('name'),
                                   vm.validated_data.get('flavor_id'),
                                   vm.validated_data.get('image_id'),
                                   vm.validated_data.get('keypair_id'),
                                   session
                                   )
            return JsonResponse({"success": True}, safe=False)
        else:
            raise ValidationError(vm.errors)

    def get(self, request, virtual_machine_id=None):
        user = User.objects.get(email=request.user)
        project_id = request.GET.get('project_id', None)
        virtual_machine_id = request.GET.get('virtual_machine_id', None)

        session = get_user_session(
            user.openstack_username, user.openstack_password, project_id)
        if virtual_machine_id:
            vm = get_server_info(session, virtual_machine_id)
            return JsonResponse({'data': [vm]}, safe=False)
        vms = get_server_list(session)
        return JsonResponse({'data': vms}, safe=False)
