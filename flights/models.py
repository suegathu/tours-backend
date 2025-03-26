from django.db import models

class Flight(models.Model):
    flight_number = models.CharField(max_length=20, null=True, blank=True)
    airline = models.CharField(max_length=100, null=True, blank=True)
    departure_airport = models.CharField(max_length=100, null=True, blank=True)
    arrival_airport = models.CharField(max_length=100, null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    passengers = models.IntegerField(default=1)
    travel_class = models.CharField(max_length=50, choices=[("economy", "Economy"), ("business", "Business"), ("first", "First Class")], null=True, blank=True)

    def __str__(self):
        return f"{self.flight_number or 'Unknown'} - {self.airline or 'Unknown'}"

class FlightBooking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="bookings")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    booked_at = models.DateTimeField(auto_now_add=True)
    num_tickets = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} - {self.flight.flight_number if self.flight else 'Unknown'}"
