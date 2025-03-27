from django.urls import path
from .views import FetchFlightsView, FlightListView, FlightBookingView

urlpatterns = [
    path('fetch-flights/', FetchFlightsView.as_view(), name='fetch-flights'),
    path('flights/', FlightListView.as_view(), name='flight-list'),
    path('book-flight/', FlightBookingView.as_view(), name='book-flight'),
    
]
