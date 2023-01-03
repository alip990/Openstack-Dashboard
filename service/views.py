from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.serializers import ValidationError
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .api.keystone import get_admin_keystone_client, get_user_project_list, get_user_session
from .api.glance import get_image_list
from .api.nova import get_flavor_list, get_keypair_list, create_keypair
from .serializers import KeypairSerializer
# Create your views here.


class ProjectView(APIView):

    # permission_classes = [IsAuthenticated]  # policy attribute
    # renderer_classes = [JSONRenderer]       # policy attribute

    def get(self, request):
        client = get_admin_keystone_client()
        print('get client')
        projects = get_user_project_list(client)
        response = []
        for project in projects:
            response.append(
                {"description": project.description, "id": project.id, "name": project.name})
        return JsonResponse(response, safe=False)

    def post(self, request):
        print("request")
        print(request.data)

        return JsonResponse({"name": request.data['name'], "description": request.data['description'], "id": 'id12123'}, safe=False)


class ImageView(APIView):

    def get(self, request):
        session = get_user_session('', '')
        images = get_image_list(session)
        d = [{
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
        return JsonResponse({"data": d}, safe=False)


class FlavorView(APIView):
    def get(self, request):
        session = get_user_session('', '')
        flavors = get_flavor_list(session)
        print(flavors)
        print('flavors')

        return JsonResponse({'data': flavors}, safe=False)


class KeypairView(APIView):
    def get(self, request):
        session = get_user_session('', '')
        keypairs = get_keypair_list(session=session)
        print('keypair', keypairs)
        return JsonResponse({'data': keypairs}, safe=False)

    def post(self, request):
        k = KeypairSerializer(data=request.data)
        if k.is_valid():
            print('is valid')
            session = get_user_session('', '')
            
            create_keypair(k.validated_data.get('name'),
                           k.validated_data.get('public_key'), session)
        else:
            raise ValidationError(k.errors)
        return Response('ali')
