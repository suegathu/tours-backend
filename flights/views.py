import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Flight, FlightBooking
from .serializers import FlightBookingSerializer

class FlightBookingView(APIView):
    def post(self, request):
        """
        Handle flight booking creation with QR code and email confirmation.
        """
        serializer = FlightBookingSerializer(data=request.data)

        if serializer.is_valid():
            booking = serializer.save()
            
            # Generate a unique booking reference
            booking.booking_reference = str(uuid.uuid4())[:10]
            booking.save()

            # Generate QR Code
            qr_data = (
                f"BOOKING:{booking.booking_reference}|"
                f"FLIGHT:{booking.flight.flight_number}|"
                f"NAME:{booking.name}|"
                f"TICKETS:{booking.num_tickets}"
            )
            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            filename = f"qr_{booking.booking_reference}.png"
            
            # You need to add the qr_code field to your FlightBooking model
            if not hasattr(booking, 'qr_code'):
                # If field doesn't exist, we'll pass the image data to the email function
                qr_code_data = buffer.getvalue()
                booking.save()
            else:
                booking.qr_code.save(filename, ContentFile(buffer.getvalue()), save=True)

            # Send Email Confirmation
            self.send_booking_email(booking, qr_code_data if not hasattr(booking, 'qr_code') else None)

            return Response(
                {
                    "success": True,
                    "message": "Flight booked successfully!",
                    "booking": serializer.data,
                    "booking_reference": booking.booking_reference,
                    "qr_code_url": booking.qr_code.url if hasattr(booking, 'qr_code') and booking.qr_code else None,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "message": "Booking validation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def send_booking_email(self, booking, qr_code_data=None):
        """
        Send email confirmation with the booking QR code.
        """
        subject = f"Flight Booking Confirmation - {booking.flight.flight_number}"
        
        context = {
            "booking": booking,
            "flight_number": booking.flight.flight_number,
            "airline": booking.flight.airline,
            "departure_airport": booking.flight.departure_airport,
            "arrival_airport": booking.flight.arrival_airport,
            "departure_time": booking.flight.departure_time,
            "arrival_time": booking.flight.arrival_time,
            "booking_reference": booking.booking_reference,
            "num_tickets": booking.num_tickets,
        }
        
        html_message = render_to_string("email/booking_confirmation.html", context)
        
        plain_message = f"""
        Hello {booking.name},

        Your flight booking is confirmed!
        Booking Reference: {booking.booking_reference}
        Flight: {booking.flight.flight_number} - {booking.flight.airline}
        Departure: {booking.flight.departure_airport} at {booking.flight.departure_time}
        Arrival: {booking.flight.arrival_airport} at {booking.flight.arrival_time}
        Number of Tickets: {booking.num_tickets}
        
        Please keep your booking reference for check-in.
        """

        email = EmailMultiAlternatives(
            subject, 
            plain_message, 
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else settings.EMAIL_HOST_USER, 
            [booking.email]
        )
        email.attach_alternative(html_message, "text/html")

        # Attach QR code to the email
        if hasattr(booking, 'qr_code') and booking.qr_code:
            email.attach_file(booking.qr_code.path)
        elif qr_code_data:
            email.attach('booking_qrcode.png', qr_code_data, 'image/png')

        email.send()

from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def verify_qr_code(request, booking_reference):
    """
    Verify a booking QR code based on the booking reference.
    """
    try:
        booking = FlightBooking.objects.get(booking_reference=booking_reference)
        return JsonResponse({
            "status": "valid", 
            "message": "Booking confirmed!", 
            "name": booking.name,
            "flight_number": booking.flight.flight_number,
            "airline": booking.flight.airline,
            "departure": booking.flight.departure_airport,
            "arrival": booking.flight.arrival_airport,
            "tickets": booking.num_tickets
        })
    except FlightBooking.DoesNotExist:
        return JsonResponse({"status": "invalid", "message": "Invalid booking reference."})