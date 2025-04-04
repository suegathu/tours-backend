from django.contrib import admin
from .models import Hotel

class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude', 'price_per_night', 'has_wifi', 'has_parking')
    search_fields = ('name', 'address')
    list_filter = ('has_wifi', 'has_parking')
    ordering = ('price_per_night',)

admin.site.register(Hotel, HotelAdmin)
