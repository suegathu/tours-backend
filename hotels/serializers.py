from rest_framework import serializers
from .models import Hotel

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'
        extra_kwargs = {
            'latitude': {'required': False},
            'longitude': {'required': False},
            'image_url': {'required': False}
        }
