from .models import Invoice, InvoiceRecord
from django.contrib import admin
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from admin_auto_filters.filters import AutocompleteFilter
from users.models import User
from .models import VirtualMachineServiceUsage

from django.contrib.auth import get_user_model

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

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
    pass


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_filter = (
        ('end_date', DateRangeFilter),
        ('start_date', DateTimeRangeFilter),
        UserFilter,
        ('user', RelatedOnlyFieldListFilter)
    )


@admin.register(InvoiceRecord)
class InvoiceRecordAdmin(admin.ModelAdmin):
    pass
