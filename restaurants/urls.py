from django.urls import path
from .views import RestaurantViewSet, ReservationViewSet

urlpatterns = [
    # Restaurant URLs
    path('restaurants/', RestaurantViewSet.as_view({'get': 'list', 'post': 'create'}), name='restaurant-list'),
    path('restaurants/<int:pk>/', RestaurantViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='restaurant-detail'),
    path('restaurants/search/', RestaurantViewSet.as_view({'get': 'search_restaurants'}), name='restaurant-search'),
    path('restaurants/import/', RestaurantViewSet.as_view({'post': 'import_restaurants'}), name='restaurant-import'),
    path('restaurants/<int:pk>/reserve/', RestaurantViewSet.as_view({'post': 'create_reservation'}), name='restaurant-reserve'),

    # Reservation URLs
    path('reservations/', ReservationViewSet.as_view({'get': 'list', 'post': 'create'}), name='reservation-list'),
    path('reservations/<int:pk>/', ReservationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='reservation-detail'),
]
