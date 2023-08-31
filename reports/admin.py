from .models import Invoice, InvoiceRecord
from django.contrib import admin
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from admin_auto_filters.filters import AutocompleteFilter
from users.models import User
from .models import VirtualMachineServiceUsage

from django.contrib.auth import get_user_model

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from admin_numeric_filter.admin import RangeNumericFilter

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


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'end_date', 'start_date', 'total_amount']
    list_filter = (
        ('end_date', DateRangeFilter),
        ('start_date', DateTimeRangeFilter),
        UserFilter,
        ('user', RelatedOnlyFieldListFilter)
    )
    list_filter = [('total_amount', RangeNumericFilter), ]


@admin.register(InvoiceRecord)
class InvoiceRecordAdmin(admin.ModelAdmin):
    list_display = ['name',
                    'description',
                    'record_type',
                    'usage',
                    'unit_price'
                    ]
    list_filter = ['record_type', ('usage', RangeNumericFilter), ]
