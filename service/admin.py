from django.contrib import admin
from .models import Flavor, VirtualMachineService
# Register your models here.


@admin.register(Flavor)
class FlavorAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating_per_hour', 'cpu_core',  'ram', 'disk']
    readonly_fields = ['id', 'name', 'cpu_core',  'ram', 'disk', 'is_deleted']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(VirtualMachineService)
class VirtualMachineServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'status',  'flavor_name', 'openstack_id', 'user']
