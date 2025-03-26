import requests
from decouple import config
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from .models import Flight, FlightBooking
from .serializers import FlightSerializer, FlightBookingSerializer

class FetchFlightsView(generics.GenericAPIView):
    """
    Fetches live flight data from AviationStack using city names and updates the database.
    """
    def get(self, request, *args, **kwargs):
        API_KEY = config("AVIATIONSTACK_API_KEY")
        departure = request.query_params.get("departure", "").strip()
        arrival = request.query_params.get("arrival", "").strip()

        url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}"
        if departure:
            url += f"&dep_city={departure}"
        if arrival:
            url += f"&arr_city={arrival}"

        response = requests.get(url)

        if response.status_code == 200:
            flights_data = response.json().get("data", [])
            saved_flights = []

            for flight in flights_data:
                flight_number = flight.get("flight", {}).get("iata")
                airline = flight.get("airline", {}).get("name")
                departure_airport = flight.get("departure", {}).get("airport")
                arrival_airport = flight.get("arrival", {}).get("airport")
                departure_time = flight.get("departure", {}).get("estimated")
                arrival_time = flight.get("arrival", {}).get("estimated")
                status = flight.get("flight_status", "scheduled")
                price = flight.get("price", {}).get("total", 0)
                travel_class = flight.get("flight", {}).get("class", "Economy")
                passengers = 1  # Default to 1 passenger

                if flight_number:
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
    """
    Handles flight booking with availability checks.
    """
    def post(self, request):
        serializer = FlightBookingSerializer(data=request.data)

        try:
            if serializer.is_valid():
                flight_id = request.data.get("flight")
                flight = Flight.objects.filter(id=flight_id).first()

                if not flight:
                    return Response({
                        "success": False,
                        "message": "Selected flight not found."
                    }, status=status.HTTP_404_NOT_FOUND)

                # Ensure seats are available before booking
                if flight.passengers <= 0:
                    return Response({
                        "success": False,
                        "message": "No available seats on this flight."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Reduce available seats
                flight.passengers -= 1
                flight.save()

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
    """
    Lists available flights with optional filters.
    """
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = Flight.objects.filter(passengers__gt=0)  # Only return flights with available seats
        departure = self.request.query_params.get("departure", "").strip()
        arrival = self.request.query_params.get("arrival", "").strip()
        travel_class = self.request.query_params.get("travel_class", "").strip()

        if departure:
            queryset = queryset.filter(departure_airport__icontains=departure)
        if arrival:
            queryset = queryset.filter(arrival_airport__icontains=arrival)
        if travel_class:
            queryset = queryset.filter(travel_class=travel_class)

        return queryset