from dataclasses import fields
from rest_framework import serializers
from .models import User
from django.db.models.signals import *
from django.db.models.signals import post_save


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        for signal in [pre_save, pre_init, pre_delete, post_save, post_delete, post_init]:
            # print a List of connected listeners
             print(signal.receivers)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
