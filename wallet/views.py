from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet, WalletTransactions
from .serializers import WalletSerializer, WalletTransactionsSerializer

from rest_framework.permissions import IsAuthenticated

class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        wallet = Wallet.objects.get(owner=user.id)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


class WalletTransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        wallet_transactions = WalletTransactions.objects.filter(
            related_wallet__owner=request.user)
        serializer = WalletTransactionsSerializer(
            wallet_transactions, many=True)
        return Response(serializer.data)
