from django.db import models
from django.db.models.signals import post_save, pre_save
from users.models import User


class Flavor(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    cpu_core = models.SmallIntegerField()
    ram = models.IntegerField()
    disk = models.IntegerField()
    rating_per_hour = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name='price per hour')
    created_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return self.name


VirtualMachineServiceStatus = (
    ("ACTIVE", "ACTIVE"),  # billing only be calculated for active virtual machines
    ("SUSPENDED", "SUSPENDED"),  # admin can suspend user virtual machines
    ("SHUTOFF", "SHUTOFF"),
    ("UNKNOWN", "UNKNOWN"))


class VirtualMachineService(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=255, choices=VirtualMachineServiceStatus)
    openstack_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    flavor_name = models.CharField(max_length=255)
    flavor_ram = models.IntegerField()
    flavor_cpu = models.SmallIntegerField()
    flavor_disk = models.SmallIntegerField()
    flavor_rating_hourly = models.DecimalField(max_digits=10, decimal_places=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name
