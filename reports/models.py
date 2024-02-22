from django.db import models
from django.utils.translation import gettext_lazy as _

from service.models import VirtualMachineService
from users.models import User
from datetime import timedelta
from django.utils import timezone

class BaseCreatedTime(models.Model):
    created_time = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        abstract = True


class BaseCreatedUpdatedTime(BaseCreatedTime):
    updated_time = models.DateTimeField(_('آخرین ویرایش'), auto_now=True)

    class Meta:
        abstract = True

class VirtualMachineServiceUsage(BaseCreatedUpdatedTime):
    start_date = models.DateTimeField(verbose_name=_('زمان شروع'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('زمان پایان'))
    vm = models.ForeignKey(to=VirtualMachineService, on_delete=models.CASCADE, verbose_name=_('سرویس ماشین مجازی'))
    usage_hours = models.FloatField(null=True, blank=True, verbose_name=_('ساعات استفاده'))

    def __str__(self) -> str:
        return str(self.vm)

    class Meta:
        verbose_name = _('استفاده از سرویس ماشین مجازی')
        verbose_name_plural = _('استفاده‌های سرویس ماشین مجازی')

class Invoice(BaseCreatedUpdatedTime):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    start_date = models.DateTimeField(verbose_name=_('زمان شروع'))
    end_date = models.DateTimeField(null=True, verbose_name=_('زمان پایان'))
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, verbose_name=_('مجموع مبلغ'))
    payment_deadline = models.DateTimeField(
        null=True, blank=True, verbose_name=_('مهلت پرداخت')
    )
    paid_date  = models.DateTimeField(null = True , verbose_name = _("تاریخ پرداخت"))

    def __str__(self):
        return f"فاکتور #{self.id} - کاربر: {self.user}"

    def save(self, *args, **kwargs):
        # Set payment_deadline if it's not provided
        if not self.payment_deadline:
            self.payment_deadline = timezone.now() + timedelta(weeks=1)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')

RECORD_TYPE = (
    ("VM", "VIRTUAL_MACHINE"),
    ("SNAPSHOT", "SNAPSHOT"),
    ("VOLUME", "VOLUME")
)

class InvoiceRecord(models.Model):
    invoice = models.ForeignKey(
        'Invoice', related_name='invoice_record', on_delete=models.CASCADE, verbose_name=_('فاکتور'))
    name = models.CharField(max_length=1024, verbose_name=_('نام'))
    description = models.TextField(verbose_name=_('توضیحات'))
    record_type = models.CharField(choices=RECORD_TYPE, max_length=255, verbose_name=_('نوع رکورد'))
    usage = models.FloatField(verbose_name=_('مقدار مصرف'))
    unit_price = models.PositiveIntegerField(verbose_name=_('قیمت واحد'))

    def __str__(self):
        return f"رکورد #{self.id} - {self.name}"

    class Meta:
        verbose_name = _('رکورد فاکتور')
        verbose_name_plural = _('رکوردهای فاکتور')
