from datetime import datetime
import logging

from service.models import VirtualMachineService
from reports.models import VirtualMachineServiceUsage

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
LOG = logging.getLogger(__name__)


@receiver(pre_save, sender=VirtualMachineService)
def on_vm_status_change(sender, instance: VirtualMachineService, **kwargs):

    if instance.id is None:  # new object will be created
        pass
    else:
        previous = VirtualMachineService.objects.get(id=instance.id)
        LOG.debug(
            f'vm:{instance.id} status updated! previous:{previous.status} , new status:{instance.status}')
        if previous.status != instance.status:  # field will be updated
            if instance.status == "ACTIVE":
                VirtualMachineServiceUsage.objects.create(
                    start_date=datetime.now(), vm_id=instance.id)
            elif instance.status == "SUSPENDED" or instance.status == "SHUTOFF" or instance.status == "UNKNOWN":
                usage = VirtualMachineServiceUsage.objects.get(
                    vm_id=instance.id, end_date__isnull=True)
                usage.end_date = datetime.now()
                a = (usage.end_date - usage.start_date.replace(tzinfo=None)
                     ).total_seconds()
                usage.usage_hours = a/3600
                usage.save()


@receiver(post_save, sender=VirtualMachineService)
def on_vm_create(sender, instance, created, **kwargs):
    if created:
        LOG.debug(
            f'vm:{instance.id} created! new status:{instance.status}')
        VirtualMachineServiceUsage.objects.create(
            start_date=datetime.now(), vm_id=instance.id)
