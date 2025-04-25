# accounts/management/commands/apikey.py

"""
This command is used to CRUD API key for a user.

Usage:
python manage.py apikey --action=create --user=username [--application=my_app] 
python manage.py apikey --action=list 
python manage.py apikey --action=delete  --user=username  --key=api_key_id
python manage.py apikey --action=activate --user=username --key=api_key_id
python manage.py apikey --action=deactivate --user=username --key=api_key_id
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User 
from accounts.models import ApiKey

class Command(BaseCommand):
    help = 'Manage API keys for users'

    def add_arguments(self, parser):
        parser.add_argument('--action', type=str, required=True, help='Action to perform: create, list, delete')    
        parser.add_argument('--user', type=str, help='Username of the user')
        parser.add_argument('--application', type=str, help='Application name')
        parser.add_argument('--key', type=str, help='API key ID')

    def handle(self, *args, **options):
        action = options['action']  
        user = options['user']
        application = options['application']
        key = options['key']

        if action == 'create':
            self.create_api_key(user, application)  
        elif action == 'list':
            self.list_api_keys()
        elif action == 'delete':
            self.delete_api_key(user, key)
        elif action == 'activate':
            self.activate_api_key(user, key)
        elif action == 'deactivate':
            self.deactivate_api_key(user, key)
        else:
            self.stderr.write(self.style.ERROR('Invalid action'))
            
    def create_api_key(self, user, application):
        user = User.objects.get(username=user)
        api_key = ApiKey.objects.create(user=user, application=application)
        self.stdout.write(self.style.SUCCESS(f'API key created: {api_key.key}'))

    def list_api_keys(self):
        api_keys = ApiKey.objects.all()
        for api_key in api_keys:
            self.stdout.write(f'{api_key.user.username} - {api_key.application}: {api_key.key}')

    def delete_api_key(self, user, key):
        user = User.objects.get(username=user)
        api_key = ApiKey.objects.get(key=key, user=user)
        api_key.delete()
        self.stdout.write(self.style.SUCCESS(f'API key deleted: {key}'))

    def activate_api_key(self, user, key):
        user = User.objects.get(username=user)
        api_key = ApiKey.objects.get(key=key, user=user)
        api_key.is_active = True
        api_key.save()
        self.stdout.write(self.style.SUCCESS(f'API key activated: {key}'))

    def deactivate_api_key(self, user, key):
        user = User.objects.get(username=user)
        api_key = ApiKey.objects.get(key=key, user=user)
        api_key.is_active = False
        api_key.save()
        self.stdout.write(self.style.SUCCESS(f'API key deactivated: {key}'))

