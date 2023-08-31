from datetime import datetime, timedelta
from django.db import models
from service.models import VirtualMachineService
# # Create your models here.

from users.models import User
from decimal import Decimal


class VirtualMachineServiceUsage(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    vm = models.ForeignKey(to=VirtualMachineService, on_delete=models.CASCADE)
    usage_hours = models.FloatField(null=True, blank=True)

    def __str__(self) -> str:
        return self.vm

#     password = models.CharField(max_length=255)
#     email = models.CharField(max_length=255, unique=True)
#     openstack_username = models.CharField(
#         max_length=255, null=True, blank=True)
#     openstack_password = models.CharField(
#         max_length=255, null=True, blank=True)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     username = None

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
#     objects = UserManager()


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f"Invoice #{self.id} - User: {self.user}"


RECORD_TYPE = (
    ("VM", "VIRTUAL_MACHINE"),
    ("SNAPSHOT", "SNAPSHOT"),
    ("VOLUME", "VOLUME")
)


class InvoiceRecord(models.Model):
    invoice = models.ForeignKey(
        'Invoice', related_name='invoice_record', on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    description = models.TextField()
    record_type = models.CharField(choices=RECORD_TYPE, max_length=255)
    usage = models.FloatField()
    unit_price = models.PositiveIntegerField()
