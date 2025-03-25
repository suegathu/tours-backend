from django.urls import path
from .views import FetchFlightsView, FlightListView, FlightBooking

urlpatterns = [
    path('fetch-flights/', FetchFlightsView.as_view(), name='fetch-flights'),
    path('flights/', FlightListView.as_view(), name='flight-list'),
    path('book-flight/', FlightBooking, name='book_flight'),
]
