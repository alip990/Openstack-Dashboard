from django.apps import AppConfig
from django.db.models.signals import post_migrate


def seed_database(sender, **kwargs):
    print('---------------------')
    from .utils import seed_flavors
    seed_flavors()


class ServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "service"

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import service.signals
        post_migrate.connect(seed_database, sender=self)
        print('seed_database connected')
