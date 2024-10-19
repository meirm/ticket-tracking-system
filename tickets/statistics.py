from django.db.models import Count, Avg, F
from datetime import timedelta
from django.utils.timezone import now
from .models import Ticket
from django.db.models import ExpressionWrapper, fields
from django.db.models.functions import Now
class Statistics:
    
    @staticmethod
    def overdue_task_count():
        # Count the number of overdue tasks (tickets still open and past due date)
        overdue_count = Ticket.objects.filter(
            status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS],  # Still open
            due_date__lt=now()  # Past their due date
        ).count()
        return overdue_count

    @staticmethod
    def not_overdue_task_count():
        # Count the number of tasks resolved before the deadline
        not_overdue_count = Ticket.objects.filter(
            status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED],  # Resolved or closed
            updated_at__lt=F('due_date')  # Resolved before due date
        ).count()
        return not_overdue_count

    @staticmethod
    def priority_summary():
        return Ticket.objects.values('priority').annotate(
            count=Count('id')
        ).order_by('-count')
    
    @staticmethod
    def open_tickets_per_user_category():
        # Open tickets categorized by user and ticket category
        return Ticket.objects.filter(
            status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
        ).values('assignee__username', 'category').annotate(
            total_tickets=Count('id')
        ).order_by('assignee__username', 'category')

    @staticmethod
    def closed_tickets_per_user_category():
        # Closed tickets categorized by user and ticket category
        return Ticket.objects.filter(
            status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]
        ).values('assignee__username', 'category').annotate(
            total_tickets=Count('id')
        ).order_by('assignee__username', 'category')
        
    @staticmethod
    def average_ticket_resolution_time():
        # Assuming 'RESOLVED' status means the ticket is completed
        tickets = Ticket.objects.filter(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED])
        
        # Calculate the time difference in seconds (or any other unit)
        tickets = tickets.annotate(
            time_taken=ExpressionWrapper(
                F('updated_at') - F('created_at'),
                output_field=fields.DurationField()
            )
        )
    
        avg_time_in_seconds = tickets.aggregate(average_time=Avg('time_taken'))['average_time']
        
        # If there's no average time, return 0 seconds
        return avg_time_in_seconds if avg_time_in_seconds else timedelta(0)
    
    @staticmethod
    def open_tickets_assignee_to_users():
        # Tickets that are still open (not resolved or closed)
        return Ticket.objects.filter(
            status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
        ).values('assignee__username').annotate(
            total_tickets=Count('id')
        ).order_by('-total_tickets')

    @staticmethod
    def closed_tickets_assignee_to_users():
        # Tickets that are closed (resolved or closed)
        return Ticket.objects.filter(
            status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]
        ).values('assignee__username').annotate(
            total_tickets=Count('id')
        ).order_by('-total_tickets')
        

    @staticmethod
    def ticket_status_summary():
        return Ticket.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')