from rest_framework.routers import DefaultRouter
from .views import EventViewSet, ReservationViewSet
from django.urls import path, include
# Use DefaultRouter and router.register() exactly as shown in class:

router = DefaultRouter()

router.register(r'events',       EventViewSet,       basename='event')

router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('', include(router.urls)),
]