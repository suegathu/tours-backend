from django.db import models

class Flight(models.Model):
    flight_number = models.CharField(max_length=20, null=True, blank=True)
    airline = models.CharField(max_length=100, null=True, blank=True)
    departure_airport = models.CharField(max_length=100, null=True, blank=True)
    arrival_airport = models.CharField(max_length=100, null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.flight_number or 'Unknown'} - {self.airline or 'Unknown'}"

class FlightBooking(models.Model):
    flight_number = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.flight_number}"
