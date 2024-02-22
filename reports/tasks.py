
from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone

from reports.utils import generate_all_users_invoice_within_month
from dashboard.celery import app

from django_celery_beat.models import CrontabSchedule , PeriodicTask
import logging
from .models import Invoice 
from wallet.models import Wallet
LOG = logging.getLogger(__name__)


@app.on_after_finalize.connect()
def setup_periodic_tasks(sender, **kwargs):
    
    schedule, created = CrontabSchedule.objects.get_or_create(
    minute='0',      # Minute (0 - 59)
    hour='*/2',      # Hour (0 - 23)
    day_of_week='*',  # Day of the week (0 - 6, where 0 is Sunday)
    day_of_month='*',  # Day of the month (1 - 31)
    month_of_year='*',  # Month (1 - 12)
)
    LOG.debug(f"Schedule Created  {schedule.__str__()}.")

    periodic_task, created = PeriodicTask.objects.get_or_create(
        name="generate_all_users_invoice_within_month",
        crontab = schedule, 
        task = 'reports.tasks.generate_user_invoices',)
    LOG.debug(f"generate_all_users_invoice_within_month task Created  {periodic_task.__str__()}.")
    
        # defaults={
        #     'task': 'reports.tasks.generate_user_invoices',  
        #     'crontab': schedule,
        #     "args":{},
        # }
    

    invoice_schedule, created = CrontabSchedule.objects.get_or_create(
    minute='2',      # Minute (0 - 59)
    hour='*',      # Hour (0 - 23)
    day_of_week='*',  # Day of the week (0 - 6, where 0 is Sunday)
    day_of_month='*',  # Day of the month (1 - 31)
    month_of_year='*',  # Month (1 - 12)
)
    LOG.debug(f"Invoice Schedule Created  {invoice_schedule.__str__()}.")

    invoice_periodic_task, created = PeriodicTask.objects.get_or_create(
        name="process_expired_invoices",
        crontab = invoice_schedule, 
        task = 'reports.tasks.process_expired_invoices',)
    LOG.debug(f"process_expired_invoices task Created  {invoice_periodic_task.__str__()}.")

    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     generate_user_invoices.s('generate_all_users_invoice_within_month'),
    # )





@app.task()
def generate_user_invoices():
  generate_all_users_invoice_within_month()

    



@app.task()
def process_expired_invoices():
    current_time = timezone.now()
    expired_invoices = Invoice.objects.filter(payment_deadline__lt=current_time, paid_date__isnull=True)
    LOG.debug(f"Expired invoices {expired_invoices.__str__()}.")

    for invoice in expired_invoices:
        user_wallet = Wallet.objects.get(owner=invoice.user)
        user_wallet.reduce_from_balance(invoice.total_amount, f" پرداخت برای فاکتور:#{invoice.id}")
        invoice.paid_date = current_time
        invoice.save()
