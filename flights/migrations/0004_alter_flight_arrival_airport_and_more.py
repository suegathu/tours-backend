# Generated by Django 5.1.7 on 2025-03-27 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0003_alter_flight_arrival_airport_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='arrival_airport',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departure_airport',
            field=models.CharField(max_length=255),
        ),
    ]
