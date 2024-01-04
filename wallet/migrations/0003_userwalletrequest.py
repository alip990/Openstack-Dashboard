# Generated by Django 4.1.2 on 2024-01-04 18:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wallet', '0002_wallettransactions_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWalletRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='مبلغ')),
                ('description', models.TextField(verbose_name='توضیحات')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='wallet_requests/', verbose_name='عکس')),
                ('is_admin_approved', models.BooleanField(default=False, verbose_name='تایید شده توسط مدیر')),
                ('user_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'درخواست کیف پول کاربر',
                'verbose_name_plural': 'درخواست\u200cهای کیف پول کاربران',
            },
        ),
    ]
