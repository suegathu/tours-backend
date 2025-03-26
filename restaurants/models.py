import os
import requests
from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    image_url = models.URLField(blank=True, null=True)
    average_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cuisine_type = models.CharField(max_length=255, blank=True, null=True)
    has_delivery = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @classmethod
    def fetch_restaurants_from_osm(cls, location):
        """
        Fetch restaurants from OpenStreetMap based on location.
        """
        osm_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f'restaurant in {location}',
            'format': 'json',
            'limit': 10
        }
        headers = {'User-Agent': 'YourApp/1.0 (youremail@example.com)'}  

        try:
            response = requests.get(osm_url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            if not data:
                raise Exception("No restaurants found in the specified location.")

            return data

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch data from OpenStreetMap: {e}")

    @classmethod
    def fetch_image_from_pexels(cls, query):
        """
        Fetch a restaurant image from Pexels.
        """
        pexels_api_key = os.environ.get("PEXELS_API_KEY")
        if not pexels_api_key:
            raise ValueError("Pexels API key is not configured")

        pexels_url = "https://api.pexels.com/v1/search"
        headers = {'Authorization': pexels_api_key}
        params = {'query': query, 'per_page': 1}

        try:
            response = requests.get(pexels_url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("photos", [{}])[0].get("src", {}).get("original")

        except requests.RequestException:
            return None  # Return None if image fetching fails

    @classmethod
    def import_restaurants(cls, location):
        """
        Fetch restaurants from OSM, get images from Pexels, and store them in the database.
        """
        osm_data = cls.fetch_restaurants_from_osm(location)
        restaurants = []

        for place in osm_data:
            name = place.get("display_name", "Unknown Restaurant")
            latitude = place.get("lat")
            longitude = place.get("lon")
            address = place.get("display_name", "")

            image_url = cls.fetch_image_from_pexels(name)  # Get image from Pexels

            restaurant = cls(
                name=name,
                address=address,
                latitude=latitude,
                longitude=longitude,
                image_url=image_url or "",  
                average_price=0.0,
            )
            restaurants.append(restaurant)

        cls.objects.bulk_create(restaurants)  # Save all at once
        return restaurants


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def get_default_user():
    """Fetch the first available user or create a default one."""
    user = User.objects.first()
    return user.id if user else None  # Ensure it returns an integer

class Reservation(models.Model):
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE, related_name="reservations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations", default=get_default_user, null=True, blank=True)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    date_time = models.DateTimeField()
    guests = models.IntegerField(default=1)
    special_request = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name} on {self.date_time}"
