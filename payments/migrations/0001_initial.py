# Generated by Django 3.2.4 on 2021-07-11 22:03

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_enumfield.db.fields
import payments.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0009_auto_20210712_0101'),
        ('loans', '0008_auto_20210712_0103'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayOut',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('receipient_phone', models.CharField(max_length=13)),
                ('status', django_enumfield.db.fields.EnumField(default=0, enum=payments.models.PayOutStatusEnum)),
                ('notes', models.CharField(max_length=50)),
                ('mpesa_code', models.CharField(max_length=10, null=True)),
                ('results', models.JSONField(default=dict)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='loans.application')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PayIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('mpesa_code', models.CharField(max_length=10)),
                ('bill_ref_no', models.CharField(blank=True, max_length=10, null=True)),
                ('transaction_date', models.DateTimeField()),
                ('status', django_enumfield.db.fields.EnumField(default=0, enum=payments.models.PayInStatusEnum)),
                ('notes', models.CharField(max_length=50)),
                ('raw', models.JSONField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='clients.client')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
