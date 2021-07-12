# Generated by Django 3.2.4 on 2021-07-11 23:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0008_auto_20210712_0103'),
        ('payments', '0003_auto_20210712_0210'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payout',
            name='application',
        ),
        migrations.AddField(
            model_name='payout',
            name='loan',
            field=models.OneToOneField(default=2, on_delete=django.db.models.deletion.DO_NOTHING, to='loans.loan'),
            preserve_default=False,
        ),
    ]
