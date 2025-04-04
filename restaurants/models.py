from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from accounts.models import UserProfile  

User = get_user_model()

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    cuisine = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  
    image_url = models.URLField(blank=True)
    osm_id = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return self.name

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    )
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)  # Linking to UserProfile
    reservation_datetime = models.DateTimeField()
    party_size = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reservation_datetime']
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.reservation_datetime}"

    def get_user_profile(self):
        """Access the user profile from the reservation."""
        return self.user.profile  
