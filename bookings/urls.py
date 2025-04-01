from django.urls import path
from .views import FlightListView, book_flight, verify_qr_code, check_in_flight, fetch_flights, get_available_seats, get_booking_details

urlpatterns = [
    path('flights/', FlightListView.as_view(), name='flight-list'),
    path('book-flight/', book_flight, name='book-flight'),
    path('verify/<uuid:booking_id>/', verify_qr_code, name='verify-qr'),
    path('check-in/<uuid:booking_id>/', check_in_flight, name='check-in'),
    path('fetch-flights/', fetch_flights, name='fetch-flights'),
    path('flights/<str:flight_number>/available-seats/', get_available_seats, name='available-seats'),
    path('bookings/<uuid:booking_id>/', get_booking_details, name='booking-details'),

]
