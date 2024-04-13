# Generated by Django 5.0.4 on 2024-04-13 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0021_remove_room_max_occupancy_roomtype_max_occupancy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='amenities',
        ),
        migrations.RemoveField(
            model_name='room',
            name='description',
        ),
        migrations.AddField(
            model_name='roomtype',
            name='amenities',
            field=models.ManyToManyField(blank=True, to='booking.amenity'),
        ),
    ]
