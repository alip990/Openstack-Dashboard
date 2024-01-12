import logging
from django.utils import timezone
from datetime import timedelta
from service.models import VirtualMachineService
from users.models import User
from reports.models import Invoice, VirtualMachineServiceUsage
from decimal import Decimal
from django.db.models import Sum
from django_celery_beat.models import PeriodicTask , IntervalSchedule

from reports.models import InvoiceRecord
from django.db.models import Q
import logging

LOG = logging.getLogger(__name__)




def generate_user_invoice(user, start_date, end_date):
    now = timezone.now()

    # Get all virtual machine services of the user that have usage in the given date range
    vmservices = VirtualMachineService.objects.filter(
        (Q(user=user,
            virtualmachineserviceusage__start_date__gte=start_date,
            virtualmachineserviceusage__end_date__lte=end_date,
            virtualmachineserviceusage__usage_hours__isnull=False
           ) | Q(user=user,
                 virtualmachineserviceusage__start_date__gte=start_date,
                 virtualmachineserviceusage__usage_hours__isnull=True
                 ))
    ).distinct()

 # Create an invoice for the user
    invoice = Invoice.objects.create(
        user=user,
        start_date=start_date,
        end_date=end_date,
        total_amount=None
    )

  # Create invoice records for each virtual machine service and aggregate usage
    records = []
    for vm in vmservices:
        LOG.debug("in vm")
        LOG.debug(vm)

        # Aggregate usage for the virtual machine service in the date range
        vm_usages_not_ended = VirtualMachineServiceUsage.objects.filter(
            Q(vm=vm, start_date__gte=start_date,
              end_date__isnull=True, usage_hours__isnull=True)
        )
        LOG.debug("vm_usages_not_ended")
        LOG.debug(vm_usages_not_ended)
        # Update the end_date and calculate the usage_hours for each record
        for vm_usage in vm_usages_not_ended:
            LOG.debug("vm_usage")
            LOG.debug(vm_usages_not_ended)

            vm_usage.end_date = now
            # Calculate the usage in hours
            vm_usage.usage_hours = (
                now - vm_usage.start_date).total_seconds() / 3600
            vm_usage.save()
            new_vm_usage = VirtualMachineServiceUsage.objects.create(
                start_date=now,
                vm=vm
            )

        usage = VirtualMachineServiceUsage.objects.filter(Q(
            vm=vm,
            start_date__gte=start_date,
            end_date__lte=end_date,
            usage_hours__isnull=False)
        ).aggregate(Sum('usage_hours'))['usage_hours__sum'] or 0.0

        # Calculate the price of the usage
        price = float(usage) * float(vm.flavor_rating_hourly)

        # Create an invoice record for the virtual machine service
        description = f"{vm.flavor_ram}GB RAM, {vm.flavor_cpu} CPUs, {vm.flavor_disk}GB Disk"
        record = InvoiceRecord.objects.create(
            invoice=invoice,
            name=vm.name,
            description=description,
            record_type="VM",
            usage=usage,
            unit_price=vm.flavor_rating_hourly
        )
        records.append(record)

    # Calculate the total amount of the invoice
    total_amount = sum(Decimal(record.usage) *
                       record.unit_price for record in records)

    invoice.total_amount = Decimal(total_amount)
    invoice.save()

    return invoice


def generate_all_users_invoice_within_month():
    # Get the start and end dates for the previous month
    today = timezone.now().date()
    first_day = today.replace(day=1) - timedelta(days=1)
    last_day = first_day.replace(day=1) #todo
    # Loop through all users and calculate their invoice
    for user in User.objects.all():
        # Calculate the user's invoice for the previous month
        generate_user_invoice(user, first_day, last_day)

