from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=500)
    
    # OpenStreetMap related fields
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Amenities
    has_wifi = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    
    # Pricing and ratings
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    # Pexels image related field
    image_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name