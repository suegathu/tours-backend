from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    image_url = models.URLField(blank=True, null=True)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cuisine_type = models.CharField(max_length=255, blank=True, null=True)  # Add this field
    has_delivery = models.BooleanField(default=False)  # Add this field


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
