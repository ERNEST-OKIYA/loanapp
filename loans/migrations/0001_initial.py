# Generated by Django 3.2.4 on 2021-06-30 19:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0002_auto_20210630_2201'),
        ('clients', '0002_alter_client_products'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_due', models.DateTimeField()),
                ('disbursed_on', models.DateTimeField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('waived_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('is_waived', models.BooleanField(default=False)),
                ('extended', models.BooleanField(default=False)),
                ('extended_on', models.DateTimeField(blank=True, null=True)),
                ('extended_days', models.IntegerField(default=0)),
                ('is_cleared', models.BooleanField(default=False)),
                ('cleared_on', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='loan_approved_by', to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='clients.client')),
                ('extended_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='loan_extended_by', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
