# Generated by Django 3.2.4 on 2021-07-10 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charges', '0003_alter_charge_name'),
        ('products', '0002_auto_20210630_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='charges',
            field=models.ManyToManyField(related_name='charges', to='charges.Charge'),
        ),
    ]
