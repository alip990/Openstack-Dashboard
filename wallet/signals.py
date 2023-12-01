# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Wallet
from users.models import User
import uuid


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Signal handler to create a wallet for the user when a new user is created.
    """
    if created:
        # Check if a wallet doesn't already exist for the user
        if not hasattr(instance, 'wallet'):
            address = uuid.uuid4()  # Import 'uuid' module at the top
            Wallet.objects.create(owner=instance, address=address)
