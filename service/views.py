from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.serializers import ValidationError
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from service.api import keystone, nova, neutron
from .api.keystone import get_admin_keystone_client, get_user_project_list, get_user_session, create_project, get_admin_session
from .api.glance import get_image_list
from .api.nova import get_flavor_list, get_keypair_list, create_keypair, create_server, get_server_list, get_server_info
from .serializers import KeypairSerializer, VmSerializer, ProjectSerializer, SecurityGroupRuleSerializer
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
        project = keystone.get_project(session, id)
        return JsonResponse({"name": project.name, "description": project.description, "id": id}, safe=False)

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
        project = keystone.get_project(session, id)

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
        return JsonResponse({'name': keypair.name, 'public_key': keypair.public_key})


class VmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        vm = VmSerializer(data=request.data)
        if vm.is_valid():
            user = User.objects.get(email=request.user)
            session = get_user_session(
                user.openstack_username,
                user.openstack_password,
                project_id=vm.validated_data.get('project_id'))
            # server = create_server(vm.validated_data.get('name'),
            #                        vm.validated_data.get('flavor_id'),
            #                        vm.validated_data.get('image_id'),
            #                        vm.validated_data.get('keypair_id'),
            #                        session
            #                        )
            data = vm.validated_data
            server = nova.server_create(session=session, name=data['name'],
                                        key_name=data['keypair_id'],
                                        image_id=data['image_id'],
                                        flavor_id=data['flavor_id'],
                                        instance_count=data['instance_count'],
                                        # security_groups=['default']
                                        )
            return JsonResponse({"success": True, 'virtual_machine_id': server.id}, safe=False)
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


class VmOperation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.query_params.get('project_id', None)
        if not project_id:
            raise ValidationError(
                'project_id should be provided in query param')
        virtual_machine_id = request.query_params.get(
            'virtual_machine_id', None)
        if not virtual_machine_id:
            raise ValidationError(
                'virtual_machine_id should be provided in query param')

        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password, project_id)

        operation = request.data.get('operation', None)
        operations = {
            'stop': nova.server_stop,
            'start': nova.server_start,
            'pause': nova.server_pause,
            'unpause': nova.server_unpause,
            'suspend': nova.server_suspend,
            'resume': nova.server_resume,
            'hard_reboot': lambda r, s: nova.server_reboot(r, s, False),
            'soft_reboot': lambda r, s: nova.server_reboot(r, s, True),
        }
        operations[operation](session, virtual_machine_id)
        return Response(status=201)


class VmSecurityGroupView(APIView):
    def get(self, request):
        pass


class SecurityGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.GET.get('project_id', None)
        if not project_id:
            raise ValidationError('you should provide project_id in query')
        user = User.objects.get(email=request.user)
        session = keystone.get_user_session(
            user.openstack_username, user.openstack_password, project_id)
        sg_manager = neutron.SecurityGroupManager(session)
        sgs = sg_manager.list(project_id=project_id)
        return JsonResponse({'data': [sg.to_dict() for sg in sgs]}, safe=False)

    def post(self, request):
        name = request.data.get('name', None)
        if not name:
            raise ValidationError('name is required')
        description = request.data.get('description', None)
        project_id = request.query_params.get('project_id', None)
        if not project_id:
            raise ValidationError(
                'project_id should be provided in query param')
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password)
        sg_manager = neutron.SecurityGroupManager(session)
        sg = sg_manager.create(
            name=name, desc=description, project_id=project_id)
        neutron.security_group_create(session, name=name, desc=description)
        return JsonResponse({'data': sg.to_dict()}, safe=False)

    def delete(self, request):
        project_id = request.query_params.get('project_id', None)
        security_id = request.query_params.get('security_id', None)
        if not project_id or not security_id:
            raise ValidationError(
                'project_id and security_id should be provided in query params ')

        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password)
        sg_manager = neutron.SecurityGroupManager(session)
        sg_manager.delete(security_id)
        return Response(status=201)

    def patch(self, request):
        project_id = request.query_params.get('project_id', None)
        security_id = request.query_params.get('security_id', None)
        if not project_id or not security_id:
            raise ValidationError(
                'project_id and security_id should be provided in query params ')
        name = request.POST.get('name', None)
        description = request.POST.get('description', None)
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password, project_id=project_id)
        sg_manager = neutron.SecurityGroupManager(session)
        sg = sg_manager.update(security_id, name, desc=description)
        return JsonResponse({"data": sg.to_dict()}, safe=False)


class SecurityGroupRuleView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        project_id = request.query_params.get('project_id', None)
        rule_id = request.query_params.get('rule_id', None)
        if not project_id or not rule_id:
            raise ValidationError(
                'project_id and security_id should be provided in query params ')
        user = User.objects.get(email=request.user)
        session = get_user_session(
            user.openstack_username, user.openstack_password, project_id=project_id)
        sg_manager = neutron.SecurityGroupManager(session)
        sg_manager.rule_delete(rule_id)
        return Response(status=201)

    def post(self, request):
        rule = SecurityGroupRuleSerializer(data=request.data)
        if rule.is_valid():
            user = User.objects.get(email=request.user)
            session = get_user_session(
                user.openstack_username, user.openstack_password)
            sg_manager = neutron.SecurityGroupManager(session)
            sg_rule = sg_manager.rule_create(rule.validated_data['security_group_id'],
                                             direction=rule.validated_data['direction'],
                                             ethertype=rule.validated_data['ether_type'],
                                             ip_protocol=rule.validated_data['protocol'],
                                             to_port=rule.validated_data['port_range_max'],
                                             from_port=rule.validated_data['port_range_min'],
                                             cidr=rule.validated_data['remote_ip_prefix']

                                             )
            return JsonResponse({"data": sg_rule.to_dict()}, safe=False)
        else:
            raise ValidationError(rule.errors)
