from rest_framework import serializers
from .models import Wallet, WalletTransactions, UserWalletRequest
from django.conf import settings  # Import the Django settings module


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class WalletTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransactions
        fields = '__all__'


class UserWalletRequestSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = UserWalletRequest
        fields = ('amount', 'description', 'photo', 'is_admin_approved')

    def to_representation(self, instance):
        # Override this method to include the absolute URL for the photo in the response
        representation = super().to_representation(instance)
        if instance.photo:
            representation['photo'] = f"{settings.BASE_URL}{instance.photo.url}"
        return representation

