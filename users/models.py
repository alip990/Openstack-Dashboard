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
    first_name = models.CharField(max_length=255)
    national_id = models.CharField(max_length =10 , null = True , blank= True)
    phone_number = models.CharField(max_length = 13 , null = True)
    last_name = models.CharField(max_length=255)
    
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
