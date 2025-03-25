from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    osm_id = models.BigIntegerField(unique=True, default=0)  
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reservations")
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    date_time = models.DateTimeField()
    guests = models.IntegerField(default=1)
    special_request = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user_name} - {self.restaurant.name} on {self.date_time}"
