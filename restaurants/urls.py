from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, ReservationViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),

    # Additional custom endpoints
    path('restaurants/fetch_restaurants/', RestaurantViewSet.as_view({'get': 'fetch_restaurants'}), name='fetch_restaurants'),
    path('restaurants/import_restaurants/', RestaurantViewSet.as_view({'post': 'import_restaurants'}), name='import_restaurants'),
    path('reservations/<int:pk>/confirm/', ReservationViewSet.as_view({'patch': 'confirm'}), name='confirm_reservation'),
    path('reservations/<int:pk>/cancel/', ReservationViewSet.as_view({'patch': 'cancel'}), name='cancel_reservation'),
]
