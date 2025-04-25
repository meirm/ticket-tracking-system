# /accounts/management/commands/createuser.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a new user'

    def add_arguments(self, parser):
        parser.add_argument('--usage', action='store_true', help='Show this help message and exit')
        parser.add_argument('--username', type=str, required=True, help='Username of the user')
        parser.add_argument('--email', type=str, required=True, help='Email of the user')
        parser.add_argument('--password', type=str, required=True, help='Password of the user')

    def handle(self, *args, **options):
        if options['usage']:
            self.stdout.write(self.style.SUCCESS('Usage: python manage.py createuser --username=<username> --email=<email> --password=<password>'))
            return
        username = options['username']
        email = options['email']
        password = options['password']
        User.objects.create_user(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'User created: {username}'))
