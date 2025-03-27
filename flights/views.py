import requests
from decouple import config
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view
from .models import Flight, FlightBooking
from .serializers import FlightSerializer, FlightBookingSerializer
from rest_framework.views import APIView

class FetchFlightsView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        API_KEY = config("AVIATIONSTACK_API_KEY")
        url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            flights_data = data.get("data", [])

            saved_flights = []

            for flight in flights_data:
                flight_number = flight.get("flight", {}).get("iata")
                airline = flight.get("airline", {}).get("name")
                departure_airport = flight.get("departure", {}).get("airport")
                arrival_airport = flight.get("arrival", {}).get("airport")
                departure_time = flight.get("departure", {}).get("estimated")
                arrival_time = flight.get("arrival", {}).get("estimated")
                status = flight.get("flight_status")
                price = flight.get("price", {}).get("total")
                travel_class = flight.get("flight", {}).get("class")
                passengers = 1  # Default to 1 passenger for fetched flights

                if flight_number:  # Ensure flight number exists
                    flight_obj, created = Flight.objects.update_or_create(
                        flight_number=flight_number,
                        defaults={
                            "airline": airline,
                            "departure_airport": departure_airport,
                            "arrival_airport": arrival_airport,
                            "departure_time": departure_time,
                            "arrival_time": arrival_time,
                            "status": status,
                            "price": price,
                            "travel_class": travel_class,
                            "passengers": passengers,
                        }
                    )
                    saved_flights.append(flight_obj.flight_number)

            return Response({"message": "Flights updated successfully", "flights": saved_flights}, status=status.HTTP_200_OK)

        return Response({"error": "Failed to fetch flights"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FlightBookingView(APIView):
    def post(self, request):
        """
        Handle flight booking creation
        
        Args:
            request (Request): HTTP request object with booking details
        
        Returns:
            Response: Booking confirmation or error details
        """
        serializer = FlightBookingSerializer(data=request.data)
        
        try:
            if serializer.is_valid():
                booking = serializer.save()
                return Response({
                    "success": True,
                    "message": "Flight booked successfully!", 
                    "booking": serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                "success": False,
                "message": "Booking validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "success": False,
                "message": "An unexpected error occurred",
                "error_details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FlightListView(generics.ListAPIView):
    serializer_class = FlightSerializer
    
    def get_queryset(self):
        queryset = Flight.objects.all()
        departure = self.request.query_params.get("departure", None)
        arrival = self.request.query_params.get("arrival", None)
        travel_class = self.request.query_params.get("travel_class", None)
        
        if departure:
            queryset = queryset.filter(departure_airport__icontains=departure)
        if arrival:
            queryset = queryset.filter(arrival_airport__icontains=arrival)
        if travel_class:
            queryset = queryset.filter(travel_class=travel_class)
        
        return queryset
