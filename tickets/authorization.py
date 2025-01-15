from django.contrib.auth.models import User
from .models import Ticket

def can_view_all_tickets(user: User) -> bool:
    return user.is_superuser or user.groups.filter(name='Support').exists()

def can_view_ticket(user: User, ticket: Ticket) -> bool:
    return user.is_superuser or user == ticket.issuer or user.groups.filter(name='Support').exists()

def can_edit_ticket(user: User, ticket: Ticket) -> bool:
    return user.is_superuser or user == ticket.issuer or user == ticket.assignee or user.groups.filter(name='Support').exists()

def can_view_group_tickets(user: User, group_id: int) -> bool:
    return user.is_superuser or user.groups.filter(id=group_id).exists()

