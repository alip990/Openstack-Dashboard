from rest_framework import serializers

from .models import Flavor

class FlavorSerializer(serializers.ModelSerializer):
    id = serializers.CharField( read_only=True)
    cpu = serializers.SerializerMethodField()
    ram = serializers.SerializerMethodField()
    name = serializers.CharField()
    disk = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()

    class Meta:
        model = Flavor
        fields = ['id', 'name', 'cpu', 'ram', 'disk', 'ratings']

    def get_cpu(self, flavor):
        return {"size": flavor.cpu_core, 'unit': 'core'}

    def get_ram(self, flavor):
        return {"size": flavor.ram, 'unit': 'mb'}

    def get_disk(self, flavor):
        return {"size": flavor.disk, 'unit': 'Gb'}

    def get_ratings(self, flavor):
        hourly_rating = int(flavor.rating_per_hour)
        daily_rating = hourly_rating * 24
        monthly_rating = daily_rating * 30  

        return {
            "monthly": monthly_rating,
            "daily": daily_rating,
            "hourly": hourly_rating
        }



class VMViewSerializer(serializers.Serializer):
    accessIPv4 = serializers.SerializerMethodField()
    accessIPv6 = serializers.IPAddressField(read_only=True)
    addresses = serializers.DictField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    id = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField()
    key_name = serializers.CharField(read_only=True)
    metadata = serializers.DictField(read_only=True)
    name = serializers.CharField()
    networks = serializers.DictField(read_only=True)
    project_id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    hostId = serializers.CharField(read_only=True)
    flavor = serializers.SerializerMethodField()

    class Meta:
        fields = ['accessIPv4', 'accessIPv6', 'addresses', 'created', 'id', 'image', 'key_name',
                  'metadata', 'name', 'networks', 'project_id', 'status', 'hostId', 'flavor']

    def get_image(self, server):
        return {
            "id": server['image']['id'],
            "size": server['image']['size'],
            "name": server['image']['name'],
            "min_disk": server['image']['min_disk'],
            "min_ram": server['image']['min_ram'],
            "os_distro": server['image']['os_distro'],
            "os_version": server['image']['os_version'],
            "os_admin_user": server['image']['os_admin_user'],
            "created_at": server['image']['created_at'],
            "photo": server['image']['photo']
        }

    def get_accessIPv4(self, server):
        for network_name, addresses in server['addresses'].items():
            if addresses and isinstance(addresses, list):
                return addresses[0].get('addr')
        return None

    def get_flavor(self, server):
        flavor_name = server['flavor']['name']
        flavor_instance = Flavor.objects.filter(name=flavor_name).first()
        
        if flavor_instance:
            return FlavorSerializer(flavor_instance).data
        else:
            return None




class KeypairSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    public_key = serializers.CharField(required=False, default=None)


class VmSerializer(serializers.Serializer):
    project_id = serializers.CharField(max_length=200)
    image_id = serializers.CharField(max_length=200)
    flavor_id = serializers.IntegerField()
    keypair_id = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)
    instance_count = serializers.IntegerField(required=False, default=1)


class ProjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)


DIRECTION = ('ingress', 'egress')
PROTOCOL = ('tcp', 'udp', 'icmp')
ETHER_TYPE = ('IPv6', 'IPv4')


class SecurityGroupRuleSerializer(serializers.Serializer):
    direction = serializers.ChoiceField(choices=DIRECTION)
    protocol = serializers.ChoiceField(choices=PROTOCOL)
    remote_ip_prefix = serializers.CharField(max_length=200)
    port_range_min = serializers.IntegerField(
        required=False, min_value=0, max_value=65535, default=None)
    port_range_max = serializers.IntegerField(
        required=False, min_value=0, max_value=65535, default=None)
    description = serializers.CharField(max_length=200, required=False)
    ether_type = serializers.ChoiceField(choices=ETHER_TYPE)
    security_group_id = serializers.CharField(max_length=200)
