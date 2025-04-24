from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .utils import log_activity
from .models import Activity, ApiKey
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ApiKeySerializer

@login_required
def api_key_delete(request, key):
    try:
        key_obj = ApiKey.objects.get(key=key, user=request.user)
        key_obj.delete()
        log_activity(request.user, 'DELETE', level='INFO', log='API key deleted.')
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API Key not found or permission denied'}, status=status.HTTP_404_NOT_FOUND)

@login_required
def api_key_activate(request, key):
    try:
        key_obj = ApiKey.objects.get(key=key, user=request.user)
        key_obj.activate()
        log_activity(request.user, 'UPDATE', level='INFO', log='API key activated.')
        serializer = ApiKeySerializer(key_obj)
        return Response(serializer.data)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API Key not found or permission denied'}, status=status.HTTP_404_NOT_FOUND)

@login_required
def api_key_deactivate(request, key):
    try:
        key_obj = ApiKey.objects.get(key=key, user=request.user)
        key_obj.deactivate()
        log_activity(request.user, 'UPDATE', level='INFO', log='API key deactivated.')
        serializer = ApiKeySerializer(key_obj)
        return Response(serializer.data)
    except ApiKey.DoesNotExist:
        return Response({'error': 'API Key not found or permission denied'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_key_create_drf(request):
    application_name = request.data.get('application')
    if not application_name:
        return Response({'error': 'Application name is required'}, status=status.HTTP_400_BAD_REQUEST)

    api_key = ApiKey(application=application_name,
                     user=request.user)
    api_key.save()
    log_activity(request.user, 'CREATE', level='INFO', log=f'API key created for {application_name}.')
    serializer = ApiKeySerializer(api_key)
    return Response(serializer.data, status=status.HTTP_201_CREATED)