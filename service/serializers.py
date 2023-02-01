from rest_framework import serializers


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
