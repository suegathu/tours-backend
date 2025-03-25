from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet

router = DefaultRouter()
router.register(r'hotels', HotelViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Ensure a valid view or include() is used
]
