# Generated by Django 3.2.4 on 2021-06-30 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20210630_2201'),
        ('organisations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='center',
            name='products',
            field=models.ManyToManyField(to='products.Product'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='products',
            field=models.ManyToManyField(to='products.Product'),
        ),
    ]
