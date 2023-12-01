from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet, WalletTransactions
from .serializers import WalletSerializer, WalletTransactionsSerializer
from django.db.models import Q
from datetime import datetime

from rest_framework.permissions import IsAuthenticated


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        wallet = Wallet.objects.get(owner=user.id)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


# class WalletTransactionListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, format=None):
#         wallet_transactions = WalletTransactions.objects.filter(
#             related_wallet__owner=request.user)
#         serializer = WalletTransactionsSerializer(
#             wallet_transactions, many=True)
#         return Response(serializer.data)

class WalletTransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        transaction_type = request.query_params.get('transaction_type', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        sort = request.query_params.get('sort', 'asc')

        wallet_transactions = WalletTransactions.objects.filter(
            related_wallet__owner=request.user)

        if transaction_type is not None:
            wallet_transactions = wallet_transactions.filter(
                Q(transaction_type=transaction_type)
            )

        if start_date is not None and end_date is not None:
            wallet_transactions = wallet_transactions.filter(
                Q(created_at__range=[start_date, end_date])
            )

        if sort == 'desc':
            wallet_transactions = wallet_transactions.order_by('-created_at')
        else:
            wallet_transactions = wallet_transactions.order_by('created_at')

        serializer = WalletTransactionsSerializer(
            wallet_transactions, many=True)
        return Response(serializer.data)
