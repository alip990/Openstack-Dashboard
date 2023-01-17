from django.contrib import admin
from django import forms

from .models import User
from service.api.keystone import openstack_user_init, check_user_exist
from django.core.exceptions import ValidationError
# Register your models here.


class UserModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.check_openstack_user_email = kwargs.pop(
            'check_openstack_user_email', None)

        super(UserModelForm, self).__init__(*args, **kwargs)

    class Meta():
        model = User
        fields = '__all__'
        # help_texts = {'type_id': test_choices_str}

    def clean(self):
        if self.check_openstack_user_email:
            if check_user_exist(self.cleaned_data['email']):
                raise ValidationError(f"{self.cleaned_data['email']} already exists in openstack ")
        return super().clean()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    change_form_template = 'admin/user_change_form.html'
    form = UserModelForm


    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(UserAdmin, self).get_form(request, obj, **kwargs)

        class ModelFormWithRequest(ModelForm):
            def __new__(cls, *args, **kwargs):
                if '_create_openstack_user' in request.POST:
                    kwargs['check_openstack_user_email'] = True
                # else:
                #     kwargs['check_openstack_user_email'] = False

                return ModelForm(*args, **kwargs)

        return ModelFormWithRequest

    def response_change(self, request, obj):
        print('response_change')
        if '_create_openstack_user' in request.POST:
            user = openstack_user_init(str(obj))
            # raise ValidationError(vm.errors)
            User.objects.filter(email=obj,).update(
                openstack_username=user['openstack_username'], openstack_password=user['openstack_password'])
        return super().response_change(request, obj)
