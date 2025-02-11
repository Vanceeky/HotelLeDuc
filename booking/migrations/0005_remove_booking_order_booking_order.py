# Generated by Django 5.0.3 on 2024-03-31 14:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_remove_booking_order_booking_order'),
        ('restaurant', '0007_order_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='order',
        ),
        migrations.AddField(
            model_name='booking',
            name='order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='restaurant.order'),
        ),
    ]
