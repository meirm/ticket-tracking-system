from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Changes, Ticket, Category, Status, Priority, Comment
from django.contrib.auth.models import User, Group
from django.conf import settings
from rest_framework import generics, permissions, status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import TicketSerializer, CommentSerializer, UserSerializer, CategorySerializer, PrioritySerializer, StatusSerializer
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

# Get the User model
User = get_user_model()

def log_activity(ticket, request_user, log):
    actor = request_user if isinstance(request_user, User) else User.objects.get(pk=request_user.id)
    Changes.objects.create(
        ticket=ticket,
        actor=actor,
        log=log
    )

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        queryset = Ticket.objects.filter(hidden=False)

        if not user.is_authenticated:
            return Ticket.objects.none()
        
        if user.is_superuser or user.groups.filter(name='Admin').exists() or user.groups.filter(name='ReadOnly').exists():
            pass
        elif user.groups.filter(name='Untrusted').exists():
            queryset = queryset.filter(assignee=user) | queryset.filter(issuer=user)
        else:
            user_groups = user.groups.all()
            can_view_all = any(g.permissions.filter(codename='can_view_all_tickets').exists() for g in user_groups)

            if not can_view_all:
                group_tickets = Ticket.objects.none()
                viewable_group_ids = [g.id for g in user_groups if g.permissions.filter(codename='can_view_group_tickets').exists()]
                if viewable_group_ids:
                    group_tickets = queryset.filter(assigned_group_id__in=viewable_group_ids)

                queryset = queryset.filter(assignee=user) | queryset.filter(issuer=user) | group_tickets
                queryset = queryset.distinct()

        include_closed = self.request.query_params.get('include_closed', 'false').lower() == 'true'
        if not include_closed:
            queryset = queryset.exclude(status__closed=True)

        status_param = self.request.query_params.get('status')
        priority_param = self.request.query_params.get('priority')
        assignee_param = self.request.query_params.get('assignee')
        issuer_param = self.request.query_params.get('issuer')
        group_param = self.request.query_params.get('assigned_group')

        if status_param:
            statuses = status_param.split(',')
            queryset = queryset.filter(status__name__in=statuses)
        if priority_param:
            priorities = priority_param.split(',')
            queryset = queryset.filter(priority__name__in=priorities)
        if assignee_param:
            queryset = queryset.filter(assignee__username=assignee_param)
        if issuer_param:
            queryset = queryset.filter(issuer__username=issuer_param)
        if group_param:
            queryset = queryset.filter(assigned_group__name=group_param)

        return queryset.order_by('-updated_at')

    def perform_create(self, serializer):
        instance = serializer.save(issuer=self.request.user)
        log_activity(instance, self.request.user, "Created ticket")

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(instance, self.request.user, "Changes to ticket")

    # Override the default update method to allow partial updates via PUT
    def update(self, request, *args, **kwargs):
        # Set partial=True to allow partial updates for PUT requests
        # This makes PUT behave like PATCH, as required by our frontend constraint
        partial = True 
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        ticket = self.get_object()
        comment_text = request.data.get('comment')
        if not comment_text:
            return Response({'error': 'Comment text is required'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            ticket=ticket,
            author=request.user,
            comment=comment_text
        )
        log_activity(ticket, request.user, "Added comment to ticket")
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()
        ticket_id = self.request.query_params.get('ticket_id')
        if ticket_id:
            queryset = queryset.filter(ticket_id=ticket_id)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        ticket_id = self.request.data.get('ticket')
        if not ticket_id:
            raise serializers.ValidationError("Ticket ID is required.")
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
            instance = serializer.save(author=self.request.user, ticket=ticket)
            log_activity(ticket, self.request.user, "Added comment to ticket")
        except Ticket.DoesNotExist:
            raise serializers.ValidationError("Ticket not found.")

# ViewSet for Categories (Read-Only)
# Provides list and retrieve actions for Category model.
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows categories to be viewed.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ViewSet for Priorities (Read-Only)
# Provides list and retrieve actions for Priority model.
class PriorityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows priorities to be viewed.
    """
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ViewSet for Statuses (Read-Only)
# Provides list and retrieve actions for Status model.
class StatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows statuses to be viewed.
    """
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ViewSet for Users (Read-Only)
# Provides list and retrieve actions for User model.
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    Uses a simple UserSerializer.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Require authentication to view users
