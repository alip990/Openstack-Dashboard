from rest_framework import serializers
from .models import Wallet, WalletTransactions


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class WalletTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransactions
        fields = '__all__'
