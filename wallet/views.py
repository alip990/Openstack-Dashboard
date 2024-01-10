from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from .models import Wallet, WalletTransactions , UserWalletRequest
from .serializers import WalletSerializer, WalletTransactionsSerializer  , UserWalletRequestSerializer
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


class UserWalletRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_wallet_requests = UserWalletRequest.objects.filter(user_id=request.user.id)
        serializer = UserWalletRequestSerializer(user_wallet_requests, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserWalletRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Set the user_id to the current user before saving
            serializer.validated_data['user_id'] = User.objects.get(id=request.user.id)
            instance = serializer.save()

            # Explicitly call to_representation to include the photo URL in the response
            response_data = serializer.to_representation(instance)

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
