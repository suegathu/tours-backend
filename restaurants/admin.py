from django.contrib import admin
from .models import Restaurant, Reservation

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'cuisine', 'latitude', 'longitude', 'phone', 'website')
    search_fields = ('name', 'address', 'cuisine')
    ordering = ('name',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'reservation_datetime', 'party_size', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'restaurant', 'reservation_datetime')
    search_fields = ('restaurant__name', 'user__email', 'status')
    ordering = ('-reservation_datetime',)
