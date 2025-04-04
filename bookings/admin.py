from django.contrib import admin

# Register your models here.
from .models import Flight, FlightBooking

admin.site.register(FlightBooking),
admin.site.register(Flight)