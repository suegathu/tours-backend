import os
import requests
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Restaurant, Reservation
from .serializers import RestaurantSerializer, ReservationSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cuisine_type', 'has_delivery']
    search_fields = ['name', 'address']
    ordering_fields = ['average_price']

    @action(detail=False, methods=['GET'])
    def fetch_restaurants(self, request):
        """
        Fetch restaurants from OpenStreetMap and enrich them with images from Pexels.
        """
        location = request.query_params.get('location', '')
        if not location:
            return Response({'error': 'Location parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            osm_data = self._fetch_osm_restaurants(location)
            enriched_data = self._enrich_with_pexels(osm_data)
            return Response(enriched_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _fetch_osm_restaurants(self, location):
        """
        Fetch restaurant data from OpenStreetMap API.
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': f'restaurants in {location}', 'format': 'json', 'limit': 10}
        headers = {'User-Agent': 'YourAppName/1.0 (your-email@example.com)'}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        if not data:
            raise Exception("No restaurants found in the specified location.")
        
        return data

    def _enrich_with_pexels(self, locations):
        """
        Add restaurant images using Pexels API.
        """
        pexels_api_key = os.environ.get('PEXELS_API_KEY')
        if not pexels_api_key:
            raise ValueError("Pexels API key is not configured")
        
        headers = {'Authorization': pexels_api_key}
        pexels_url = "https://api.pexels.com/v1/search"
        enriched_data = []
        
        for location in locations:
            try:
                query = location.get('display_name', 'restaurant')
                params = {'query': query, 'per_page': 1}
                pexels_response = requests.get(pexels_url, headers=headers, params=params)
                pexels_response.raise_for_status()

                pexels_data = pexels_response.json()
                image_url = pexels_data.get('photos', [{}])[0].get('src', {}).get('original', None)
                
                enriched_data.append({
                    'name': location.get('display_name', 'Unknown Restaurant'),
                    'address': location.get('display_name', ''),
                    'latitude': location.get('lat'),
                    'longitude': location.get('lon'),
                    'image_url': image_url
                })
            except requests.RequestException:
                enriched_data.append({
                    'name': location.get('display_name', 'Unknown Restaurant'),
                    'address': location.get('display_name', ''),
                    'latitude': location.get('lat'),
                    'longitude': location.get('lon'),
                    'image_url': None
                })

        return enriched_data

    @action(detail=False, methods=['POST'])
    def import_restaurants(self, request):
        """
        Import restaurant data from OSM into the database with Pexels images.
        """
        location = request.data.get('location')
        if not location:
            return Response({'error': 'Location parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            osm_data = self._fetch_osm_restaurants(location)
            enriched_data = self._enrich_with_pexels(osm_data)

            restaurants_to_create = []
            for data in enriched_data:
                if not Restaurant.objects.filter(name=data['name']).exists():
                    restaurants_to_create.append(
                        Restaurant(
                            name=data['name'],
                            address=data['address'],
                            latitude=data['latitude'],
                            longitude=data['longitude'],
                            image_url=data['image_url'],
                            average_price=0.0
                        )
                    )

            Restaurant.objects.bulk_create(restaurants_to_create)
            return Response({'message': 'Restaurants imported successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReservationViewSet(viewsets.ModelViewSet):
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
