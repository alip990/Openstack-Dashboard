from django.urls import path
from .views import WalletTransactionListView, WalletView , UserWalletRequestListView
urlpatterns = [
    path('',
         WalletView.as_view(), name='wallet-list'),

    path('wallet-transactions/', WalletTransactionListView.as_view(),
         name='wallet-transactions-list'),
    path('user_requests/', UserWalletRequestListView.as_view()),

]
