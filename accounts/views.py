from django.shortcuts import redirect # redirect might not be needed
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404 # Use get_object_or_404
from .utils import log_activity
from .models import ApiKey
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action # Keep action decorator
from .serializers import ApiKeySerializer
from rest_framework.permissions import IsAuthenticated

class ProtectedView(viewsets.APIView):
    """
    Sample protected endpoint for testing API keys.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({'message': 'This is a protected endpoint.'})

class ApiKeyViewSet(viewsets.ViewSet): # Use ViewSet for custom actions
    """
    API endpoint for managing user API Keys.
    Requires Token or Session authentication.
    """
    serializer_class = ApiKeySerializer
    # Uses default permission class IsAuthenticated

    def list(self, request):
        """List API keys belonging to the authenticated user."""
        keys = ApiKey.objects.filter(user=request.user)
        serializer = self.serializer_class(keys, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new API key for the authenticated user."""
        application_name = request.data.get('application')
        if not application_name:
            return Response({'error': 'Application name is required'}, status=status.HTTP_400_BAD_REQUEST)

        api_key = ApiKey(application=application_name,
                         user=request.user)
        api_key.save() # save() generates the key
        log_activity(request.user, 'CREATE', level='INFO', log=f'API key created for {application_name}.')
        serializer = self.serializer_class(api_key)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Use detail_route requires pk in URL
    @action(detail=True, methods=['post']) # Use POST for actions with side-effects
    def activate(self, request, pk=None):
        """Activate an API key."""
        key_obj = get_object_or_404(ApiKey, pk=pk, user=request.user) # Ensure user owns key
        key_obj.activate()
        log_activity(request.user, 'UPDATE', level='INFO', log=f'API key {key_obj.key[:8]}... activated.')
        serializer = self.serializer_class(key_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an API key."""
        key_obj = get_object_or_404(ApiKey, pk=pk, user=request.user) # Ensure user owns key
        key_obj.deactivate()
        log_activity(request.user, 'UPDATE', level='INFO', log=f'API key {key_obj.key[:8]}... deactivated.')
        serializer = self.serializer_class(key_obj)
        return Response(serializer.data)

    # Use standard destroy method for deletion
    def destroy(self, request, pk=None):
        """Delete an API key."""
        key_obj = get_object_or_404(ApiKey, pk=pk, user=request.user) # Ensure user owns key
        key = key_obj.key # Get key before deleting
        key_obj.delete()
        log_activity(request.user, 'DELETE', level='INFO', log=f'API key {key[:8]}... deleted.')
        return Response(status=status.HTTP_204_NO_CONTENT)