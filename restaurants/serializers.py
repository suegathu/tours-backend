from rest_framework import serializers
from .models import Restaurant, Reservation
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')
    user_email = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'restaurant', 'restaurant_name', 'user', 'user_email', 
            'reservation_datetime', 'party_size', 'status', 
            'special_requests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']
