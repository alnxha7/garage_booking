# Generated by Django 4.2.3 on 2024-08-22 06:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0006_remove_garageprofile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='GarageImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='garage_profile_images/')),
                ('garage_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='car.garageprofile')),
            ],
        ),
    ]
