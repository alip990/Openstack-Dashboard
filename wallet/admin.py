from django.contrib import admin

# Register your models here.

from django.contrib import admin
from wallet.models import *


class WalletTransactionInline(admin.StackedInline):
    model = WalletTransactions
    extra = 0
    ordering = ['-created_time']
    can_delete = False

    def __init__(self, parent_model, admin_site):
        self.readonly_fields = [x.name for x in self.model._meta.fields]
        super().__init__(parent_model, admin_site)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return False


class WalletAdmin(admin.ModelAdmin):
    model = Wallet
    readonly_fields = ['balance']
    list_display = ['owner', 'balance']
    list_display_links = list_display
    search_fields = ['owner']
    inlines = [
        WalletTransactionInline
    ]


class WalletTransactionAdmin(admin.ModelAdmin):
    model = WalletTransactions
    list_display = ['related_wallet', 'amount',
                    'transaction_type', ]
    list_filter = ['transaction_type', ]
    readonly_fields = ['related_wallet', 'amount',
                       'transaction_type', 'related_bank_transaction', 'description']


admin.site.register(Wallet, WalletAdmin)
admin.site.register(WalletTransactions, WalletTransactionAdmin)
