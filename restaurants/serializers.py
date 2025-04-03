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
    user_email = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = '__all__'
        
    def get_user_email(self, obj):
        return obj.user.email
        
    def get_restaurant_name(self, obj):
        return obj.restaurant.name
