import os
import requests
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Restaurant, Reservation
from .serializers import RestaurantSerializer, ReservationSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    
    # Filtering and search capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['has_wifi', 'has_parking']
    search_fields = ['name', 'address']
    ordering_fields = ['rating']

    @action(detail=False, methods=['GET'])
    def search_restaurants(self, request):
        """
        Search restaurants using OpenStreetMap and fetch restaurant images from Pexels
        """
        query = request.query_params.get('query', '')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            osm_results = self._search_osm_restaurants(query)
            enriched_results = self._add_pexels_images(osm_results)
            return Response(enriched_results)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _search_osm_restaurants(self, query):
        """
        Internal method to search restaurants via OpenStreetMap with a User-Agent
        """
        osm_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f'restaurants in {query}',
            'format': 'json',
            'limit': 10
        }
        headers = {'User-Agent': 'YourApp/1.0 (contact@yourapp.com)'}
        
        response = requests.get(osm_url, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()

    def _add_pexels_images(self, locations):
        """
        Enrich location results with Pexels images
        """
        pexels_api_key = os.environ.get('PEXELS_API_KEY')
        if not pexels_api_key:
            raise ValueError("Pexels API key is not configured")
        
        pexels_url = "https://api.pexels.com/v1/search"
        headers = {'Authorization': pexels_api_key}
        
        enriched_locations = []
        for location in locations:
            try:
                pexels_params = {'query': location.get('display_name', 'restaurant'), 'per_page': 1}
                pexels_response = requests.get(pexels_url, headers=headers, params=pexels_params)
                pexels_response.raise_for_status()
                pexels_data = pexels_response.json()

                location_data = {
                    'name': location.get('display_name', 'Unknown Restaurant'),
                    'address': location.get('display_name', ''),
                    'latitude': location.get('lat'),
                    'longitude': location.get('lon'),
                    'image_url': (
                        pexels_data.get('photos', [{}])[0].get('src', {}).get('original', None)
                    )
                }
            
            except requests.RequestException:
                location_data = {
                    'name': location.get('display_name', 'Unknown Restaurant'),
                    'address': location.get('display_name', ''),
                    'latitude': location.get('lat'),
                    'longitude': location.get('lon'),
                    'image_url': None
                }
            
            enriched_locations.append(location_data)
        
        return enriched_locations

    @action(detail=False, methods=['POST'])
    def import_restaurants(self, request):
        """
        Bulk import restaurants
        """
        query = request.data.get('query')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            locations = self._search_osm_restaurants(query)
            enriched_locations = self._add_pexels_images(locations)
            
            existing_ids = set(Restaurant.objects.values_list('osm_id', flat=True))
            new_restaurants = [
                Restaurant(
                    osm_id=location['name'],  # Change to a unique field like lat+lon if needed
                    name=location['name'],
                    address=location['address'],
                    latitude=location['latitude'],
                    longitude=location['longitude'],
                    image_url=location['image_url'],
                )
                for location in enriched_locations if location['name'] not in existing_ids
            ]
            
            with transaction.atomic():
                Restaurant.objects.bulk_create(new_restaurants)
            
            serializer = self.get_serializer(new_restaurants, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['POST'])
    def create_reservation(self, request, pk=None):
        """
        Create a restaurant reservation
        """
        restaurant = get_object_or_404(Restaurant, pk=pk)
        request.data['restaurant'] = restaurant.id  # Associate with the restaurant
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
