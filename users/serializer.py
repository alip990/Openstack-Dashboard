from dataclasses import fields
from rest_framework import serializers
from .models import User
from django.db.models.signals import *
from django.db.models.signals import post_save


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'national_id', 'phone_number' ,'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
