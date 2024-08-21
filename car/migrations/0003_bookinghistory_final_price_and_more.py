# Generated by Django 4.2.3 on 2024-08-21 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0002_todaybookingstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinghistory',
            name='final_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='bookinghistory',
            name='garage_earnings',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='bookinghistory',
            name='is_canceled',
            field=models.BooleanField(default=False),
        ),
    ]
