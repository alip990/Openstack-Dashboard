# Generated by Django 4.1.2 on 2023-05-12 20:56

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_invoice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='month',
        ),
        migrations.AddField(
            model_name='invoice',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.CreateModel(
            name='InvoiceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('description', models.TextField()),
                ('record_type', models.CharField(choices=[('VM', 'VIRTUAL_MACHINE'), ('SNAPSHOT', 'SNAPSHOT'), ('VOLUME', 'VOLUME')], max_length=255)),
                ('usage', models.FloatField()),
                ('unit_price', models.PositiveIntegerField()),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='reports.invoice')),
            ],
        ),
    ]
