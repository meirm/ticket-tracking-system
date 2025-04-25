from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'tickets'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'tickets', views.TicketViewSet, basename='ticket')
router.register(r'comments', views.CommentViewSet, basename='comment')
# Register the new viewsets
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'priorities', views.PriorityViewSet, basename='priority')
router.register(r'statuses', views.StatusViewSet, basename='status')
router.register(r'users', views.UserViewSet, basename='user') # Endpoint for users

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/v1/', include(router.urls)),
    # Remove all old URLs (UI and previous API)
]
