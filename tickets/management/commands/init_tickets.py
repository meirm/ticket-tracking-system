from django.core.management.base import BaseCommand

# In a Django management command or a script
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tickets.models import Category, Priority, Status, Ticket, Comment

class Command(BaseCommand):
    help = 'Initializes categories, priorities, and statuses for the application'

    # def add_arguments(self, parser):
    #     parser.add_argument('slug', type=str, help='Slug of the tenant')
    #     parser.add_argument('by', type=str, choices=["pk","id"], help='A choice between pk and id')
    #     parser.add_argument('key', type=int,  help='the pk or id value of the query')

    def handle(self, *args, **options):
        # slug = options['slug']
        # by = options['by']
        # key = options['key']

        # Create categories
        bug_category, _ = Category.objects.get_or_create(name='Bug')
        feature_category, _ = Category.objects.get_or_create(name='Feature')
        support_category, _ = Category.objects.get_or_create(name='Support')
        self.stdout.write(self.style.SUCCESS(f"Categories initialized successfully"))
        
        # Create priorities
        low_priority, _ = Priority.objects.get_or_create(name='Low')
        medium_priority, _ = Priority.objects.get_or_create(name='Medium')
        high_priority, _ = Priority.objects.get_or_create(name='High')
        self.stdout.write(self.style.SUCCESS(f"Priorities initialized successfully"))
        
        # Create statuses
        draft_status, _ = Status.objects.get_or_create(name='Draft')
        open_status, _ = Status.objects.get_or_create(name='Open')
        in_progress_status, _ = Status.objects.get_or_create(name='In Progress')
        resolved_status, _ = Status.objects.get_or_create(name='Resolved')
        closed_status, _ = Status.objects.get_or_create(name='Closed')
        cancelled_status, _ = Status.objects.get_or_create(name='Cancelled')
        backlogged_status, _ = Status.objects.get_or_create(name='Backlog')
        self.stdout.write(self.style.SUCCESS(f"Statuses initialized successfully"))

    