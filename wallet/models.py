from django.db import models

# Create your models here.

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.transaction import atomic
from users.models import User


class BaseCreatedTime(models.Model):
    created_time = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        abstract = True


class BaseCreatedUpdatedTime(BaseCreatedTime):
    updated_time = models.DateTimeField(_('آخرین ویرایش'), auto_now=True)

    class Meta:
        abstract = True


class Wallet(models.Model):
    address = models.UUIDField(
        _('آدرس کیف پول'), unique=True, null=False, blank=False, editable=False)
    owner = models.OneToOneField(
        User, related_name='wallet_owner', on_delete=models.CASCADE, null=False, db_index=True)
    balance = models.DecimalField(
        _('موجودی'), max_digits=20, decimal_places=3, default=0, null=False, blank=False)

    @atomic
    def add_to_balance(self, amount, description=''):
        self.balance += amount
        self.save()
        WalletTransactions.objects.create(
            related_wallet=self,
            amount=amount,
            transaction_type='deposit',
            description=description
        )

    @atomic
    def reduce_from_balance(self, amount, description: str = None):
        self.balance -= amount
        self.save()
        WalletTransactions.objects.create(
            related_wallet=self,
            amount=amount,
            transaction_type='withdraw',
            description=description
        )
        return True

    class Meta:
        verbose_name = 'کیف پول'
        verbose_name_plural = 'کیف پول‌ها'

    def __str__(self):
        return f"{self.owner.first_name} {self.owner.last_name}"


class WalletTransactions(BaseCreatedTime):
    TYPE = (
        ('deposit', 'واریز'),
        ('withdraw', 'برداشت'),
    )
    related_wallet = models.ForeignKey(verbose_name=_('کیف پول'), to="Wallet", on_delete=models.CASCADE, db_index=True,
                                       null=False, blank=False)
    amount = models.DecimalField(
        _('مقدار تراکنش'), max_digits=20, decimal_places=3, null=False, blank=False)
    transaction_type = models.CharField(_('نوع تراکتش'), max_length=10, blank=False, null=False, default='deposit',
                                        choices=TYPE)
    description = models.TextField(_('شرح'), blank=True, null=True)
    created_at = models.DateTimeField(
        verbose_name='تاریخ ایجاد', auto_now_add=True, )

    def __str__(self):
        return self.description or ''

    class Meta:
        verbose_name = 'تراکنش کیف پول'
        verbose_name_plural = 'تراکنش‌های کیف پول'


class UserWalletRequest(BaseCreatedUpdatedTime):
    user_id = models.ForeignKey(
        to=User, on_delete=models.CASCADE , null=False)
    amount = models.DecimalField(_("مبلغ"), max_digits=10, decimal_places=2)
    description = models.TextField(_("توضیحات"))
    photo = models.ImageField(_("عکس"), upload_to='wallet_requests/', blank=True, null=True)
    is_admin_approved = models.BooleanField(_("تایید شده توسط مدیر"), default=False)

    class Meta:
        verbose_name = _("درخواست افزایش شارژ کیف پول کاربر")
        verbose_name_plural = _("درخواست افزایش شارژ کیف پول کاربران")

    def __str__(self):
        return f"{self.user_id} - {self.amount} - {self.is_admin_approved}"
