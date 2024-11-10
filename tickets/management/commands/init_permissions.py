from django.core.management.base import BaseCommand

# In a Django management command or a script
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tickets.models import Ticket, Comment

class Command(BaseCommand):
    help = 'Initializes permissions for the application'

    # def add_arguments(self, parser):
    #     parser.add_argument('slug', type=str, help='Slug of the tenant')
    #     parser.add_argument('by', type=str, choices=["pk","id"], help='A choice between pk and id')
    #     parser.add_argument('key', type=int,  help='the pk or id value of the query')

    def handle(self, *args, **options):
        # slug = options['slug']
        # by = options['by']
        # key = options['key']


        # Create groups
        untrusted_group, _ = Group.objects.get_or_create(name='Untrusted')
        readonly_group, _ = Group.objects.get_or_create(name='ReadOnly')
        admin_group, _ = Group.objects.get_or_create(name='Admin')

        # Get permissions
        ticket_content_type = ContentType.objects.get_for_model(Ticket)
        view_ticket = Permission.objects.get(codename='view_ticket', content_type=ticket_content_type)
        add_ticket = Permission.objects.get(codename='add_ticket', content_type=ticket_content_type)
        change_ticket = Permission.objects.get(codename='change_ticket', content_type=ticket_content_type)
        delete_ticket = Permission.objects.get(codename='delete_ticket', content_type=ticket_content_type)

        comment_content_type = ContentType.objects.get_for_model(Comment)
        view_comment = Permission.objects.get(codename='view_comment', content_type=comment_content_type)
        add_comment = Permission.objects.get(codename='add_comment', content_type=comment_content_type)
        change_comment = Permission.objects.get(codename='change_comment', content_type=comment_content_type)
        delete_comment = Permission.objects.get(codename='delete_comment', content_type=comment_content_type)
        
        
        # Assign permissions to groups
        untrusted_group.permissions.set([view_ticket, add_ticket, change_ticket, view_comment, add_comment, change_comment])
        readonly_group.permissions.set([view_ticket, view_comment])
        admin_group.permissions.set([view_ticket, add_ticket, change_ticket, delete_ticket, view_comment, add_comment, change_comment, delete_comment])
        self.stdout.write(self.style.SUCCESS(f"Permissions initialized successfully"))