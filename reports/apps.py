from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reports"


from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

LOG = logging.getLogger(__name__)



class ReportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reports"

    def ready(self):
        # signals are imported, so that they are defined and can be used
        pass