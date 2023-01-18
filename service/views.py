from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.serializers import ValidationError
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .api.keystone import get_admin_keystone_client, get_user_project_list, get_user_session, create_project, get_admin_session
from .api.glance import get_image_list
from .api.nova import get_flavor_list, get_keypair_list, create_keypair, create_server, get_server_list
from .serializers import KeypairSerializer, VmSerializer, ProjectSerializer
# Create your views here.
from users.models import User


class ProjectView(APIView):

    permission_classes = [IsAuthenticated]
    # renderer_classes = [JSONRenderer]       # policy attribute

    def get(self, request):
        user = User.objects.get(email=request.user)
        projects = get_user_project_list(user.openstack_username)
        return JsonResponse(projects, safe=False)

    def post(self, request):
        user = User.objects.get(email=request.user)
        data = ProjectSerializer(data=request.data)
        if data.is_valid():
            project = create_project(data.validated_data.get('name'), user.openstack_username,
                                     data.validated_data.get('description'))
            if not project:
                raise ValidationError('project with this name already exists')
            return JsonResponse({"name": request.data['name'], "description": request.data['description'], "id": project.id}, safe=False)
        else:
            raise ValidationError(data.errors)


class ImageView(APIView):

    def get(self, request):
        session = get_admin_session()
        images = get_image_list(session)
        return JsonResponse({"data": images}, safe=False)


class FlavorView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(email=request.user)
        session = get_admin_session()
        flavors = get_flavor_list(session)
        print(flavors)
        print('flavors')

        return JsonResponse({'data': flavors}, safe=False)


class KeypairView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password, project_id)
        keypairs = get_keypair_list(session=session)
        print('keypair', keypairs)
        return JsonResponse({'data': keypairs}, safe=False)

    def post(self, request, project_id):
        k = KeypairSerializer(data=request.data)
        if k.is_valid():
            user = User.objects.get(email=request.user)
            session = get_user_session(
                user.openstack_username, user.openstack_password, project_id)
            keypair = create_keypair(k.validated_data.get('name'),
                                     k.validated_data.get('public_key'), session)

        else:
            raise ValidationError(k.errors)
        return JsonResponse({'name': k.validated_data.get('name'), 'public_key': k.validated_data.get('public_key')})


class VmView(APIView):
    def post(self, request, project_id):
        vm = VmSerializer(data=request.data)
        if vm.is_valid():
            user = User.objects.get(email=request.user)
            session = get_user_session(
                user.openstack_username, user.openstack_password, project_id)
            server = create_server(vm.validated_data.get('name'),
                                   vm.validated_data.get('flavor_id'),
                                   vm.validated_data.get('image_id'),
                                   vm.validated_data.get('keypair_id'),
                                   session
                                   )
            return JsonResponse({"success": True}, safe=False)
        else:
            raise ValidationError(vm.errors)

    def get(self, request, project_id):
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password, project_id)
        vms = get_server_list(session)
        return JsonResponse({'data': vms}, safe=False)
