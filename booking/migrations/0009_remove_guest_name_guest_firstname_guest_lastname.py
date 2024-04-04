# Generated by Django 5.0.3 on 2024-04-04 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_reservation_room_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guest',
            name='name',
        ),
        migrations.AddField(
            model_name='guest',
            name='firstname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='guest',
            name='lastname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
