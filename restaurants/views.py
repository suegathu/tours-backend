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
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter, 
        filters.OrderingFilter
    ]
    
    filterset_fields = ['cuisine_type', 'has_delivery']
    search_fields = ['name', 'address']
    ordering_fields = ['average_price', 'rating']

    @action(detail=False, methods=['GET'])
    def search_locations(self, request):
        """
        Search locations using OpenStreetMap and fetch restaurant images from Pexels
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
            'q': f'restaurants in {query}',
            'format': 'json',
            'limit': 10
        }
        headers = {
            'User-Agent': 'Suegathu/1.0 (suegathul0@icloud.com)'  
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
                    'query': location.get('display_name', 'restaurant'),
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
                    'name': location.get('display_name', 'Unknown Restaurant'),
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
                    'name': location.get('display_name', 'Unknown Restaurant'),
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
        Bulk import locations as restaurants
        """
        query = request.data.get('query')
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            locations = self._search_osm_locations(query)
            enriched_locations = self._add_pexels_images(locations)

            restaurants_to_create = [
                Restaurant(
                    name=location['name'],
                    address=location['address'],
                    latitude=location['latitude'],
                    longitude=location['longitude'],
                    image_url=location['image_url'],
                    average_price=0,  
                )
                for location in enriched_locations
            ]

            created_restaurants = Restaurant.objects.bulk_create(restaurants_to_create)

            serializer = self.get_serializer(created_restaurants, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReservationViewSet(viewsets.ModelViewSet):
    """
    Handles restaurant reservations.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['restaurant']
    search_fields = ['user_name', 'user_email']
    ordering_fields = ['date_time']

    @action(detail=True, methods=['PATCH'])
    def confirm(self, request, pk=None):
        """
        Confirm a reservation.
        """
        reservation = get_object_or_404(Reservation, pk=pk)
        reservation.save()
        return Response({"message": "Reservation confirmed."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PATCH'])
    def cancel(self, request, pk=None):
        """
        Cancel a reservation.
        """
        reservation = get_object_or_404(Reservation, pk=pk)
        reservation.delete()
        return Response({"message": "Reservation canceled."}, status=status.HTTP_200_OK)
