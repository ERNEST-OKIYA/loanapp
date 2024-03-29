# Generated by Django 3.2.4 on 2021-06-30 19:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('charges', '0001_initial'),
        ('funds', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='charges',
            field=models.ManyToManyField(to='charges.Charge'),
        ),
        migrations.AddField(
            model_name='product',
            name='fund',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='funds.fund'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='interest_rate',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='max_repayment_months',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
