from django.urls import path
from .views import WalletTransactionListView, WalletView
urlpatterns = [
    path('',
         WalletView.as_view(), name='wallet-list'),

    path('wallet-transactions/', WalletTransactionListView.as_view(),
         name='wallet-transactions-list'),
]
