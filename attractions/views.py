import requests
from rest_framework import generics, response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Attraction
from .serializers import AttractionSerializer

# OSM and Pexels API configurations
OSM_OVERPASS_URL = "http://overpass-api.de/api/interpreter"
PEXELS_API_KEY = "v4L5uDaLQzbSebE9Ib21qQ9ScL2gpH7heumuQH00FJvCKNHrFZ3KmaDB"
PEXELS_URL = "https://api.pexels.com/v1/search"

class AttractionList(generics.ListAPIView):
    serializer_class = AttractionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category"]

    def get_queryset(self):
        """
        Fetch new data from OSM and Pexels, then return updated attractions.
        """
        self.fetch_osm_attractions()
        return Attraction.objects.all()

    def fetch_osm_attractions(self):
        """
        Fetch attractions from OpenStreetMap and update the database.
        """
        query = """
        [out:json];
        node["tourism"="attraction"](around:10000, -1.286389, 36.817223);
        out body;
        """
        response = requests.get(OSM_OVERPASS_URL, params={"data": query})

        if response.status_code != 200:
            return

        data = response.json()
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name", "Unknown Attraction")
            osm_id = element["id"]
            lat, lon = element["lat"], element["lon"]
            category = element.get("tags", {}).get("tourism", "attraction")

            # Fetch image from Pexels
            image_url = self.fetch_image_from_pexels(name)

            # Save to database
            Attraction.objects.update_or_create(
                osm_id=osm_id,
                defaults={
                    "name": name,
                    "latitude": lat,
                    "longitude": lon,
                    "category": category,
                    "image_url": image_url,
                },
            )

    def fetch_image_from_pexels(self, query):
        """
        Fetch attraction image from Pexels API.
        """
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 1}
        response = requests.get(PEXELS_URL, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data["photos"]:
                return data["photos"][0]["src"]["large"]
        return None


class AttractionDetail(generics.RetrieveAPIView):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer
