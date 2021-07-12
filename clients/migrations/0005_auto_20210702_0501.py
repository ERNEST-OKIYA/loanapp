# Generated by Django 3.2.4 on 2021-07-02 02:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20210630_2201'),
        ('clients', '0004_auto_20210702_0229'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='loanprofile',
            name='clients_loanprofile_unique_product_client',
        ),
        migrations.AlterUniqueTogether(
            name='loanprofile',
            unique_together={('product', 'client')},
        ),
    ]
