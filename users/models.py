from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser

from users.managers import UserManager
# Create your models here.


class User(AbstractUser):
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    openstack_username = models.CharField(
        max_length=255, null=True, blank=True)
    openstack_password = models.CharField(
        max_length=255, null=True, blank=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
