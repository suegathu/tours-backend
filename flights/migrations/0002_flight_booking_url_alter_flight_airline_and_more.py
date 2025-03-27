# Generated by Django 5.1.7 on 2025-03-26 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='booking_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='airline',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='flight',
            name='arrival_airport',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='flight',
            name='arrival_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departure_airport',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departure_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='flight',
            name='flight_number',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='flight',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='flight',
            name='status',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='flight',
            name='travel_class',
            field=models.CharField(default='Economy', max_length=50),
        ),
    ]
