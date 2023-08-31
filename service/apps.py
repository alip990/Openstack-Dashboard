from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

LOG = logging.getLogger(__name__)


def seed_database(sender, **kwargs):
    LOG.debug('Start seeding database for new flavors')
    from .utils import seed_flavors
    seed_flavors()
    LOG.debug('Seeding database finished!')


class ServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "service"

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import service.signals
        post_migrate.connect(seed_database, sender=self)
        LOG.debug('seed_database connected')
