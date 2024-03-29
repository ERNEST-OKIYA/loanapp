# Generated by Django 3.2.4 on 2021-06-30 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_alter_client_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanprofile',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='loanprofile',
            constraint=models.UniqueConstraint(fields=('product', 'client'), name='clients_loanprofile_unique_product_client'),
        ),
    ]
