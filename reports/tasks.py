
from celery import shared_task
from celery.schedules import crontab

from reports.utils import generate_all_users_invoice_within_month
from dashboard.celery import app

from django_celery_beat.models import CrontabSchedule , PeriodicTask


@app.on_after_finalize.connect()
def setup_periodic_tasks(sender, **kwargs):
    
    schedule, created = CrontabSchedule.objects.get_or_create(
    minute='0',      # Minute (0 - 59)
    hour='*/2',      # Hour (0 - 23)
    day_of_week='*',  # Day of the week (0 - 6, where 0 is Sunday)
    day_of_month='*',  # Day of the month (1 - 31)
    month_of_year='*',  # Month (1 - 12)
)

    periodic_task, created = PeriodicTask.objects.get_or_create(
        name="generate_all_users_invoice_within_month",
        crontab = schedule, 
        task = 'reports.tasks.generate_user_invoices',
        
        # defaults={
        #     'task': 'reports.tasks.generate_user_invoices',  
        #     'crontab': schedule,
        #     "args":{},
        # }
    )


    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     generate_user_invoices.s('generate_all_users_invoice_within_month'),
    # )





@app.task()
def generate_user_invoices():
  generate_all_users_invoice_within_month()

    
