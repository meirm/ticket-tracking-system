from rest_framework import serializers
from .models import Activity, ApiKey
from django.contrib.auth.models import User

class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() # Show username instead of ID
    class Meta:
        model = Activity
        fields = ['id', 'user', 'action', 'level', 'log', 'created_at']


class ApiKeySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) # Show user ID, set automatically

    class Meta:
        model = ApiKey
        fields = ['id', 'user', 'application', 'key', 'created_at', 'updated_at', 'active', 'readonly']
        read_only_fields = ['user', 'key', 'created_at', 'updated_at'] # Key generated on save

    
