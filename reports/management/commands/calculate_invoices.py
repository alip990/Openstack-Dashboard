from django.core.management.base import BaseCommand
from reports.utils import generate_all_users_invoice_within_month


class Command(BaseCommand):
    help = 'Calculates user invoices for the previous month'

    def handle(self, *args, **options):
        generate_all_users_invoice_within_month()
