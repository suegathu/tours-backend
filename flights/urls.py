from django.urls import path
from .views import FlightBookingView, FL

urlpatterns = [
    path('flights/', FlightListView.as_view(), name='flight-list'),
    path('flights/fetch/', views.FetchFlightsView.as_view(), name='fetch-flights'),
    path('booking/', views.FlightBookingView.as_view(), name='flight-booking'),
    path('verify-qr/<str:booking_reference>/', views.verify_qr_code, name='verify-qr'),
]