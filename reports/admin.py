from .models import Invoice, InvoiceRecord
from django.contrib import admin
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from admin_auto_filters.filters import AutocompleteFilter
from users.models import User
from .models import VirtualMachineServiceUsage
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.contrib import messages

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from admin_numeric_filter.admin import RangeNumericFilter
from wallet.models import Wallet, WalletTransactions
User = get_user_model()


class UserFilter(AutocompleteFilter):
    title = 'User'
    field_name = 'user'
    model = User

    def get_queryset(self, request):
        qs = self.model._default_manager.all()
        return qs.order_by('email')


@admin.register(VirtualMachineServiceUsage)
class VirtualMachineServiceUsageAdmin(admin.ModelAdmin):
    list_display = [
        'vm',
        'start_date',
        'end_date',
        'usage_hours'
    ]
    list_filter = [('usage_hours', RangeNumericFilter), ]

class InvoiceRecordInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = InvoiceRecord
    extra = 1  # Number of empty forms to display

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'end_date', 'start_date', 'total_amount']
    list_filter = [
        ('end_date', DateRangeFilter),
        ('start_date', DateTimeRangeFilter),
        UserFilter,
        ('user', RelatedOnlyFieldListFilter),
        ('total_amount', RangeNumericFilter),
    ]
    inlines = [InvoiceRecordInline]
    
    actions = ['pay_invoices']

    def pay_invoices(self, request, queryset):
        for invoice in queryset:
            # Check if the invoice is already paid
            if invoice.paid_date:
                messages.warning(request, f"فاکتور #{invoice.id} در حال حاضر پرداخت شده است.")
                continue

            # Retrieve the user's wallet
            user_wallet = Wallet.objects.get(owner=invoice.user)

            # Check if the user has enough balance
            if user_wallet.balance < invoice.total_amount:
                messages.error(request, f"اعتبار کافی برای پرداخت فاکتور #{invoice.id} وجود ندارد.")
                continue

            # Reduce the amount from the user's wallet
            user_wallet.reduce_from_balance(invoice.total_amount, f"پرداخت برای فاکتور #{invoice.id}")

            # Update the invoice paid_date to the current time
            invoice.paid_date = timezone.now()
            invoice.save()

            messages.success(request, f"فاکتور #{invoice.id} با موفقیت پرداخت شد.")

    pay_invoices.short_description = "پرداخت فاکتورهای انتخاب شده"

@admin.register(InvoiceRecord)
class InvoiceRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'record_type', 'usage', 'unit_price']
    list_filter = ['record_type', ('usage', RangeNumericFilter)]
