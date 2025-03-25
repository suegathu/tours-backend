import os
import requests
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Hotel
from .serializers import HotelSerializer

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    
    # Filtering and search capabilities
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    filterset_fields = ['has_wifi', 'has_parking']
    search_fields = ['name', 'address']
    ordering_fields = ['price_per_night', 'rating']

    @action(detail=False, methods=['GET'])
    def search_locations(self, request):
        """
        Search locations using OpenStreetMap and fetch hotel images from Pexels
        """
        query = request.query_params.get('query', '')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # OpenStreetMap Search
            osm_results = self._search_osm_locations(query)
            
            # Enrich results with Pexels images
            enriched_results = self._add_pexels_images(osm_results)
            
            return Response(enriched_results)
        
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _search_osm_locations(self, query):
        """
        Internal method to search locations via OpenStreetMap with a User-Agent
        """
        osm_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f'hotels in {query}',
            'format': 'json',
            'limit': 10
        }
        headers = {
            'User-Agent': 'YourAppName/1.0 (your@email.com)'  # Replace with your email
        }
        
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
        headers = {
            'Authorization': pexels_api_key
        }

        enriched_locations = []
        for location in locations:
            try:
                pexels_params = {
                    'query': location.get('display_name', 'hotel'),
                    'per_page': 1
                }
                
                pexels_response = requests.get(
                    pexels_url, 
                    headers=headers, 
                    params=pexels_params
                )
                pexels_response.raise_for_status()
                pexels_data = pexels_response.json()

                location_data = {
                    'name': location.get('display_name', 'Unknown Hotel'),
                    'address': location.get('display_name', ''),
                    'latitude': location.get('lat'),
                    'longitude': location.get('lon'),
                    'image_url': (
                        pexels_data.get('photos', [{}])[0]
                        .get('src', {})
                        .get('original')
                    )
                }
                
                enriched_locations.append(location_data)
            
            except requests.RequestException:
                location_data = {
                    'name': location.get('display_name', 'Unknown Hotel'),
                    'address': location.get('display_name', ''),
                    'latitude': location.get('lat'),
                    'longitude': location.get('lon'),
                    'image_url': None
                }
                enriched_locations.append(location_data)

        return enriched_locations

    @action(detail=False, methods=['POST'])
    def import_locations(self, request):
        """
        Bulk import locations as hotels
        """
        query = request.data.get('query')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            locations = self._search_osm_locations(query)
            enriched_locations = self._add_pexels_images(locations)

            hotels_to_create = [
                Hotel(
                    name=location['name'],
                    address=location['address'],
                    latitude=location['latitude'],
                    longitude=location['longitude'],
                    image_url=location['image_url'],
                    price_per_night=0,  
                )
                for location in enriched_locations
            ]

            created_hotels = Hotel.objects.bulk_create(hotels_to_create)

            serializer = self.get_serializer(created_hotels, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
