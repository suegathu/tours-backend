from django.urls import path
from .views import AttractionList, AttractionDetail

urlpatterns = [
    path("attractions/", AttractionList.as_view(), name="attraction-list"),
    path("attractions/<int:pk>/", AttractionDetail.as_view(), name="attraction-detail"),
]
