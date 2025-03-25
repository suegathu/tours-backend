from django.core.management.base import BaseCommand
from hotels.models import Hotel
from services.osm_service import OpenStreetMapService
from services.pexels_service import PexelsService

class Command(BaseCommand):
    help = 'Import hotels from OpenStreetMap and get images from Pexels'
    
    def add_arguments(self, parser):
        parser.add_argument('city', type=str, help='City to search for hotels')
    
    def handle(self, *args, **options):
        city = options['city']
        
        # Search OSM for hotels
        osm_results = OpenStreetMapService.search_locations(f'hotels in {city}')
        
        for location in osm_results:
            # Search Pexels for hotel images
            pexels_images = PexelsService.search_images(f'hotel {location["display_name"]}')
            
            hotel = Hotel.objects.create(
                name=location.get('display_name', 'Unknown Hotel'),
                address=location.get('display_name', ''),
                latitude=location.get('lat'),
                longitude=location.get('lon'),
                price_per_night=0,  # You'd want to implement proper pricing logic
                image_url=pexels_images['photos'][0]['src']['original'] if pexels_images['photos'] else None
            )
            
            self.stdout.write(self.style.SUCCESS(f'Imported hotel: {hotel.name}'))
