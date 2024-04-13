# Generated by Django 5.0.4 on 2024-04-12 17:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0019_alter_booking_check_in_alter_booking_check_out'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roomtype',
            name='images',
        ),
        migrations.CreateModel(
            name='RoomImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='room_images/')),
                ('room_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='booking.roomtype')),
            ],
        ),
    ]
