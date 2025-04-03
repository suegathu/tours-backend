from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.conf import settings
import requests
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
        location = request.query_params.get('location', 'nairobi')
        
        # Get geocoded coordinates for the location (simplified for demo)
        # In production, use a geocoding API like Nominatim
        locations = {
            'nairobi': {'lat': -1.2921, 'lon': 36.8219},
            'new york': {'lat': 40.7128, 'lon': -74.0060},
            'london': {'lat': 51.5074, 'lon': -0.1278},
            # Add more locations as needed
        }
        
        # Default to Nairobi if location not found
        coords = locations.get(location.lower(), locations['nairobi'])
        
        # Call OSM with the coordinates
        restaurants = self.fetch_restaurants_from_osm(coords['lat'], coords['lon'])
        
        return Response({
            'location': location,
            'count': len(restaurants),
            'restaurants': restaurants
        })
    
    def fetch_restaurants_from_osm(self, lat, lon, radius=5000):
        # Overpass API query
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        node["amenity"="restaurant"](around:{radius},{lat},{lon});
        out body;
        """
        
        try:
            response = requests.get(overpass_url, params={"data": overpass_query})
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
                            'name': name,
                            'address': address,
                            'latitude': element.get('lat'),
                            'longitude': element.get('lon'),
                            'cuisine': cuisine,
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
        pexels_api_key = "YOUR_PEXELS_API_KEY"
        
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
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=user)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Associate with current user
            serializer.save(user=request.user)
            
            # Get reservation details for email
            reservation = Reservation.objects.get(id=serializer.data['id'])
            restaurant = reservation.restaurant
            
            # Send confirmation email
            subject = f"Reservation Confirmation - {restaurant.name}"
            message = f"""
            Hello {request.user.first_name or request.user.username},
            
            Your reservation has been booked successfully!
            
            Details:
            Restaurant: {restaurant.name}
            Address: {restaurant.address}
            Date & Time: {reservation.reservation_datetime}
            Party Size: {reservation.party_size}
            
            Special Requests: {reservation.special_requests or 'None'}
            
            Thank you for using our service!
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
