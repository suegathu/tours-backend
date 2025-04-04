from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
import requests
from requests_cache import CachedSession
import json
from .models import Restaurant, Reservation
from .serializers import RestaurantSerializer, ReservationSerializer

class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]  # Allow anyone to view restaurants
    
    @action(detail=False, methods=['get'], url_path='fetch_restaurants')
    def fetch_restaurants(self, request):
        """
        Fetch restaurants from OSM based on location parameter
        Usage: /api/restaurants/fetch_restaurants/?location=nairobi
        """
        location = request.query_params.get('location')
        if not location:  # If param is missing or empty
            return Response({'error': 'location is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Geocode the given location: location -> coordinates
        coords = self.geocode_location(location)
        if not coords:
            return Response({'error': 'Could not geocode the location'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Call OSM with the coordinates
        restaurants = self.fetch_restaurants_from_overpass(coords['lat'], coords['lon'])
        
        return Response({
            'location': location,
            'count': len(restaurants),
            'restaurants': restaurants
        })
    
    def geocode_location(self, location):
        """
        Convert location name to coordinates using Nominatim
        """
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': location,
            'format': 'json',
            'limit': 1
        }
        
        # Add a User-Agent header as required by Nominatim's usage policy
        headers = {
            'User-Agent': 'TravelWithSue/0.1'
        }
        
        try:
            response = requests.get(nominatim_url, params=params, headers=headers)
            data = response.json()
            
            if data and len(data) > 0:
                return {
                    'lat': float(data[0]['lat']),
                    'lon': float(data[0]['lon'])
                }
            return None
        except Exception as e:
            print(f"Error geocoding location: {e}")
            return None
    
    def fetch_restaurants_from_overpass(self, lat, lon, radius=5000):
        # Overpass API query
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        node["amenity"="restaurant"](around:{radius},{lat},{lon});
        out body;
        """

        session = CachedSession()
        
        try:
            response = session.get(overpass_url, params={"data": overpass_query})
            data = response.json()
            
            results = []
            for element in data.get('elements', []):
                if element.get('type') == 'node':
                    tags = element.get('tags', {})
                    osm_id = str(element.get('id'))
                    
                    # Create restaurant object
                    name = tags.get('name', 'Unknown Restaurant')
                    address = tags.get('addr:full', tags.get('addr:housenumber', '') + ' ' + tags.get('addr:street', '')).strip() or 'Address not available'
                    cuisine = tags.get('cuisine', 'Various')
                    
                    # Create or update restaurant in database
                    restaurant, created = Restaurant.objects.update_or_create(
                        osm_id=osm_id,
                        defaults={
                            'name': truncate_string(name, 200),
                            'address': address,
                            'latitude': element.get('lat'),
                            'longitude': element.get('lon'),
                            'cuisine': truncate_string(cuisine, 100),
                            'phone': tags.get('phone', ''),
                            'website': tags.get('website', '')
                        }
                    )
                    
                    # Get image for restaurant
                    if created or not restaurant.image_url:
                        restaurant.image_url = self.get_restaurant_image(cuisine)
                        restaurant.save()
                    
                    # Add to results
                    results.append({
                        'id': restaurant.id,
                        'osm_id': osm_id,
                        'name': name,
                        'address': address,
                        'cuisine': cuisine,
                        'lat': element.get('lat'),
                        'lon': element.get('lon'),
                        'image_url': restaurant.image_url
                    })
            
            return results
            
        except Exception as e:
            print(f"Error fetching from OSM: {e}")
            return []
    
    def get_restaurant_image(self, cuisine):
        # Replace with your Pexels API key
        pexels_api_key = "PEXELS_API_KEY"
        
        headers = {
            "Authorization": pexels_api_key
        }
        
        search_term = f"{cuisine} restaurant food"
        url = f"https://api.pexels.com/v1/search?query={search_term}&per_page=1"
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if 'photos' in data and len(data['photos']) > 0:
                return data['photos'][0]['src']['medium']
        except Exception as e:
            print(f"Error fetching image: {e}")
            
        # Return a default image if Pexels fetch fails
        return "https://images.pexels.com/photos/6267/menu-restaurant-vintage-table.jpg"

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [AllowAny]

    
    def create(self, request):
        data = request.data       
        data['user'] = request.user.id

        print(request.user)
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def truncate_string(s, length=100):
    if len(s) > length:
        return s[:length-3] + '...'
    return s
