from django.urls import path
from .views import (
    fetch_restaurants_from_osm,
    fetch_restaurant_images,
    list_restaurants,
    create_reservation,
    restaurant_booking_link
)

urlpatterns = [
    path("restaurants/", list_restaurants, name="list_restaurants"),
    path("restaurants/images/<str:query>/", fetch_restaurant_images, name="fetch_restaurant_images"),
    path("restaurants/hotels/osm/", fetch_restaurants_from_osm, name="fetch_hotels_from_osm"),
    path("restaurants/reservations/", create_reservation, name="create_reservation"),
    path("restaurants/<int:restaurant_id>/booking-link/", restaurant_booking_link, name="restaurant_booking_link"),
]
