from django.db import models

class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    airline = models.CharField(max_length=100)
    departure_airport = models.CharField(max_length=255)
    arrival_airport = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    travel_class = models.CharField(max_length=50, default="Economy")
    passengers = models.IntegerField(default=1)
    booking_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.flight_number or 'Unknown'} - {self.airline or 'Unknown'}"

class FlightBooking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="bookings")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    booked_at = models.DateTimeField(auto_now_add=True)
    num_tickets = models.PositiveIntegerField(default=1)
    booking_reference = models.CharField(max_length=10, unique=True, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.flight.flight_number if self.flight else 'Unknown'}"