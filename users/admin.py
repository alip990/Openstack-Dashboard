from django.contrib import admin
from .models import User
from service.api.keystone import create_openstack_user
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    change_form_template = 'admin/user_change_form.html'

    def response_change(self, request, obj):
        print('response_change')
        if '_create_openstack_user' in request.POST:
            print('-------')
            print(obj)
            user = create_openstack_user(obj)
            User.objects.filter(email=obj,).update(
                openstack_username=user.openstack_username, openstack_password=user.openstack_password)
        return super().response_change(request, obj)
