from django.contrib import messages
from django.contrib import admin
from wallet.models import *
from django.utils.translation import gettext_lazy as _


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


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    model = Wallet
    readonly_fields = ['balance']
    list_display = ['owner', 'balance']
    list_display_links = list_display
    search_fields = ['owner']
    inlines = [
        WalletTransactionInline
    ]


@admin.register(WalletTransactions)
class WalletTransactionAdmin(admin.ModelAdmin):
    model = WalletTransactions
    list_display = ['related_wallet', 'amount', 'transaction_type']
    list_filter = ['transaction_type']
    # readonly_fields = ['related_wallet', 'amount',
    #                    'transaction_type', 'description']

    actions = None  # Disable all admin actions

    def save_model(self, request, obj, form, change):
        # Check if the transaction type is 'withdraw'
        if obj.transaction_type == 'withdraw':
            # Check if the user has enough balance for the withdrawal
            if obj.related_wallet.balance >= obj.amount:
                # Deduct the amount from the user's balance
                obj.related_wallet.balance -= obj.amount
                obj.related_wallet.save()
                obj.save()
            else:
                # User doesn't have enough balance, display a validation error
                messages.error(request, "موجودی برای برداشت کافی نیست")
        elif obj.transaction_type == 'deposit':
            # For 'deposit' transactions, add the amount to the user's balance
            obj.related_wallet.balance += obj.amount
            obj.related_wallet.save()
            obj.save()
        else:
            # Handle other transaction types as needed
            obj.save

    def has_add_permission(self, request):
        # Allow creating new transactions, but disable editing or deleting
        return True

    def has_change_permission(self, request, obj=None):
        # Disable editing existing transactions
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable deleting existing transactions
        return False


@admin.register(UserWalletRequest)
class UserWalletRequestAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'amount', 'description', 'is_admin_approved')
    list_filter = ('is_admin_approved', )
    search_fields = ('user_id', 'amount', 'description')
    readonly_fields = ('user_id', 'amount', 'description', 'photo', 'is_admin_approved')

    fieldsets = (
        (_("اطلاعات کاربر"), {
            'fields': ('user_id',)
        }),
        (_("جزئیات درخواست"), {
            'fields': ('amount', 'description', 'photo', 'is_admin_approved')
        }),
    )

    def has_add_permission(self, request):
        # Disable the ability to add new UserWalletRequest instances via the admin
        return False
