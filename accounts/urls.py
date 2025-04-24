from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'keys', views.ApiKeyViewSet, basename='apikey')

urlpatterns = [
    # The API URLs are now determined automatically by the router.
    path('', include(router.urls)),
    # TODO: Add URLs for login/logout/registration if using dj-rest-auth or djoser
]