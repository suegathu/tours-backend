# Generated by Django 5.1.7 on 2025-03-25 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0002_alter_flight_arrival_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='airline',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='arrival_airport',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departure_airport',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='flight_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
