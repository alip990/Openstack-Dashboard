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
    photo = serializers.SerializerMethodField()

    def get_photo(self, obj):
        # Check if the photo field is not empty
        if obj.photo:
            # Build the absolute URL for the photo field
            return f"{settings.BASE_URL}{obj.photo.url}"

        # If the photo field is empty, return None
        return None

    class Meta:
        model = UserWalletRequest
        
        fields = ( 'amount', 'description', 'photo', 'is_admin_approved')

