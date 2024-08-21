# Generated by Django 4.2.3 on 2024-08-21 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0003_bookinghistory_final_price_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_plate', models.CharField(max_length=15, unique=True)),
                ('model', models.CharField(max_length=100)),
                ('booking_history', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='car.bookinghistory')),
            ],
        ),
    ]
