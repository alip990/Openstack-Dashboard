from django.contrib import admin
from .models import Flavor, VirtualMachineService
# Register your models here.


@admin.register(Flavor)
class FlavorAdmin(admin.ModelAdmin):
    pass


@admin.register(VirtualMachineService)
class VirtualMachineServiceAdmin(admin.ModelAdmin):
    pass
