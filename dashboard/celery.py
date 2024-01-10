from __future__ import absolute_import, unicode_literals
import os
from django.apps import apps

from celery import Celery
from django.conf import settings
import logging
from celery.signals import after_setup_logger  # Add this import

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard.settings')

app = Celery('dashboard')
app.conf.enable_utc = False

app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])
app.autodiscover_tasks()

logger = logging.getLogger(__name__)

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add filehandler
    fh = logging.FileHandler('logs_celery.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
