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


import logging
from decimal import Decimal
from django.db.models import Q, Sum
from django.utils import timezone
from .models import VirtualMachineService, VirtualMachineServiceUsage, Invoice, InvoiceRecord

LOG = logging.getLogger(__name__)

def generate_user_invoice(user, start_date, end_date):
    now = timezone.now()

    # Step 1: Retrieve virtual machine services with usage in the given date range
    vm_services = VirtualMachineService.objects.filter(
        (Q(user=user,
            virtualmachineserviceusage__start_date__gte=start_date,
            virtualmachineserviceusage__end_date__lte=end_date,
            virtualmachineserviceusage__usage_hours__isnull=False
           ) | Q(user=user,
                 virtualmachineserviceusage__start_date__gte=start_date,
                 virtualmachineserviceusage__usage_hours__isnull=True
                 ))
    ).distinct()

    # Step 2: Check if the user has any relevant virtual machine services with usage
    if not vm_services:
        LOG.debug(f"No relevant usage found for user {user}. Skipping invoice generation.")
        return None

    # Step 3: Create an invoice for the user
    invoice = Invoice.objects.create(
        user=user,
        start_date=start_date,
        end_date=end_date,
        total_amount=None
    )
    LOG.debug(f"Invoice created for user {user} with ID {invoice.id}.")

    # Step 4: Create invoice records for each virtual machine service and aggregate usage
    records = []
    for vm in vm_services:
        LOG.debug(f"Processing virtual machine service: {vm}")
        
        # Step 4.1: Aggregate usage for the virtual machine service in the date range
        vm_usages_not_ended = VirtualMachineServiceUsage.objects.filter(
            Q(vm=vm, start_date__gte=start_date, end_date__isnull=True, usage_hours__isnull=True)
        )

        # Step 4.2: Update the end_date and calculate the usage_hours for each record
        for vm_usage in vm_usages_not_ended:
            LOG.debug(f"Updating usage record: {vm_usage}")

            vm_usage.end_date = now
            # Calculate the usage in hours
            vm_usage.usage_hours = (now - vm_usage.start_date).total_seconds() / 3600
            vm_usage.save()
            # here we end a usage and create new usage which help us calculate invoice and we do not need to worry about active vms
            new_vm_usage = VirtualMachineServiceUsage.objects.create(
                start_date=now,
                vm=vm
            )
            LOG.debug(f"New usage record created: {new_vm_usage}")

        # Step 4.3: Aggregate usage for the virtual machine service in the date range (again)
        usage = VirtualMachineServiceUsage.objects.filter(Q(
            vm=vm,
            start_date__gte=start_date,
            end_date__lte=end_date,
            usage_hours__isnull=False)
        ).aggregate(Sum('usage_hours'))['usage_hours__sum'] or 0.0
        LOG.debug(f"Usage for virtual machine service {vm}: {usage} hours.")

        # Step 4.4: Calculate the price of the usage
        price = float(usage) * float(vm.flavor_rating_hourly)

        # Step 4.5: Create an invoice record for the virtual machine service
        description = f"VM Configuration: RAM {vm.flavor_ram}GB, CPUs {vm.flavor_cpu}, Disk {vm.flavor_disk}GB"
        record = InvoiceRecord.objects.create(
            invoice=invoice,
            name=vm.name,
            description=description,
            record_type="VM",
            usage=usage,
            unit_price=vm.flavor_rating_hourly
        )
        LOG.debug(f"Invoice record created for virtual machine service {vm}: {record}")

        records.append(record)

    # Step 5: Calculate the total amount of the invoice
    total_amount = sum(Decimal(record.usage) * record.unit_price for record in records)

    invoice.total_amount = Decimal(total_amount)
    invoice.save()
    LOG.debug(f"Total amount for invoice {invoice.id}: {invoice.total_amount}")

    # Step 6: Return the generated invoice
    return invoice


def generate_all_users_invoice_within_month():
    # Get the start and end dates for the previous month
    today = timezone.now().date()
    # last_day = today.replace(day=1) - timedelta(days=1) #last date of past month
    # first_day = last_day.replace(day=1) #todo
    
    # Calculate the first day of the current month
    first_day = today.replace(day=1)

    # Calculate the last day of the current month
    last_day = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Loop through all users and calculate their invoice
    for user in User.objects.all():
        # Calculate the user's invoice
        generate_user_invoice(user, first_day, last_day)

