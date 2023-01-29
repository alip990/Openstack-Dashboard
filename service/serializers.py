from rest_framework import serializers


class KeypairSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    public_key = serializers.CharField(required=False, default=None)


class VmSerializer(serializers.Serializer):
    image_id = serializers.CharField(max_length=200)
    flavor_id = serializers.IntegerField()
    keypair_id = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)


class ProjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)
