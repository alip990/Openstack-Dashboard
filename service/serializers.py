from rest_framework import serializers


class KeypairSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    public_key = serializers.CharField()
