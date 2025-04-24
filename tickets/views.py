from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Changes, Ticket, Category, Status, Priority, Comment
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from accounts.auth import api_auth
import json
from rest_framework import generics, permissions, status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import TicketSerializer, CommentSerializer, UserSerializer, GroupSerializer

def log_activity(ticket, request_user, log):
    actor = request_user if isinstance(request_user, User) else User.objects.get(pk=request_user.id)
    Changes.objects.create(
        ticket=ticket,
        actor=actor,
        log=log
    )

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer

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

def app_index(request):
    return render(request, 'tickets/app_index.html')

def privacy_view(request):
    return render(request, 'tickets/privacy.html') 

def terms_view(request):
    return render(request, 'tickets/terms.html')

@login_required
def help_view(request):
    return render(request, 'tickets/help.html')

@login_required
def list_issues(request):
    ticket_list = Ticket.objects.all().filter(hidden=False) \
    .filter(category__name="Bug") \
    .exclude(status__closed=True) \
    .order_by('-updated_at')
    ticket_list = filter_tickets(request, ticket_list)
            
    paginator = Paginator(ticket_list, 10)
    tickets_count = ticket_list.count()
    tickets = paginator.get_page(request.GET.get('page'))
    context = {
        'tickets': tickets,
        'page_title': 'Open Issues',
        'tickets_count': tickets_count,
    }
    return render(request, 'tickets/index.html',context)
    
    
@login_required
def list_closed_tickets(request):
    ticket_list = Ticket.objects.all().filter(hidden=False) \
    .filter(status__closed=True) \
    .order_by('-updated_at')
    ticket_list = filter_tickets(request, ticket_list)
    paginator = Paginator(ticket_list, 10)  # Show 10 tickets per page.
    tickets_count = ticket_list.count()
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)
    context = {
            'tickets': tickets,
            'page_title': 'Closed Tickets',
            'tickets_count': tickets_count,
        }
    return render(request, 'tickets/index.html',context)

@login_required
def list_hidden_tickets(request):
    ticket_list = Ticket.objects.all().filter(hidden=True).order_by('-updated_at')
    ticket_list = filter_tickets(request, ticket_list)
    paginator = Paginator(ticket_list, 10)  # Show 10 tickets per page.
    tickets_count = ticket_list.count()
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)

    context = {
        'tickets': tickets,
        'page_title': 'Hidden Tickets',
        'tickets_count': tickets_count,
    }
    return render(request, 'tickets/index.html',context)

@login_required
def view_changes(request):
    ticket_list = Changes.objects.all().order_by('-created_at') 
    # FIXME: filter by permissions
    paginator = Paginator(ticket_list, 10)
    tickets_count = ticket_list.count()
    page_number = request.GET.get('page')
    changes = paginator.get_page(page_number)
    return render(request, 'tickets/changes.html', {'changes': changes, 'tickets_count': tickets_count})

@login_required
def index(request):
    ticket_list = Ticket.objects.filter(hidden=False).exclude(status__closed=True).order_by('-updated_at')
    ticket_list = filter_tickets(request, ticket_list)
    paginator = Paginator(ticket_list, 10)  # Show 10 tickets per page.
    tickets_count = ticket_list.count()
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)

    context = {
        'tickets': tickets,
        'page_title': 'Tickets',
        'tickets_count': tickets_count,
    }
    return render(request, 'tickets/index.html',context)

@login_required
def ticket_detail(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket = filter_ticket(request, ticket)
    if not ticket:
        messages.error(request, 'You do not have permission to view this ticket')
        return redirect('tickets:index')
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket, 'comments': ticket.comments.all().order_by('-created_at')})

@login_required
def search_tickets(request):
    # We want to search for tickets based on the title and description fields.
    # check the browser history for the query to see if the search was done when showing all tasks, mine, closed, or hidden
    if 'q' not in request.GET:
        return redirect('tickets:index')
    query = request.GET['q']
    if not query:
        return redirect('tickets:index')
    # get history from browser
    history = request.META.get('HTTP_REFERER').split('/')[-2]
    
    # check if the search was done when showing all tasks
     #check if it matches a user
    if User.objects.filter(username__icontains=query).exists():
        all_tickets = Ticket.objects.filter(assignee=User.objects.get(username__icontains=query))
    else:
        all_tickets = Ticket.objects.filter(title__icontains=query) | Ticket.objects.filter(description__icontains=query)
    if 'my' in history:
        tickets = all_tickets.filter(assignee=request.user)
    # check if the search was done when showing hidden tasks
    elif 'hidden' in history:
        tickets = all_tickets.filter(hidden=True)
        
    else:
        tickets = all_tickets.filter(hidden=False)
    if 'closed' in history:
        tickets = tickets.filter(status__closed=True)
    else:
        tickets = tickets.exclude(status__closed=True)
    if tickets.count() == 0:
        messages.error(request, f'No tickets found for "{query}"')
    else:
        messages.success(request, f'Search results for "{query}" coming from {history}')
    tickets = filter_tickets(request, tickets)
    ticket_list = tickets.order_by('-updated_at')
    
    paginator = Paginator(tickets, 10)
    tickets_count = ticket_list.count()
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)
    context = {
        'tickets': tickets,
        'page_title': 'Search results',
        'tickets_count': tickets_count,
    }
    return render(request, 'tickets/index.html',context)
    

@login_required
def my_tasks(request):
    ticket_list = Ticket.objects.filter(hidden=False, assignee=request.user).exclude(status__closed=True).order_by('-updated_at')
    ticket_list = filter_tickets(request, ticket_list)
    paginator = Paginator(ticket_list, 10)
    tickets_count = ticket_list.count()
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)

    context = {
        'tickets': tickets,
        'page_title': 'My tasks',
        'tickets_count': tickets_count,
    }
    return render(request, 'tickets/index.html',context)

@login_required
def in_progress_view(request):
    ticket_list = Ticket.objects.filter(hidden=False, status__name = "In Progress").order_by('-updated_at')
    ticket_list = filter_tickets(request, ticket_list)
    paginator = Paginator(ticket_list, 10)
    tickets_count = ticket_list.count()
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)
    context = {
        'tickets': tickets,
        'page_title': 'In Progress',
        'tickets_count': tickets_count,
    }
    return render(request, 'tickets/index.html',context)

@login_required
def new_ticket(request):
    if not request.user.has_perm('tickets.add_ticket'):
        messages.error(request, 'You do not have permission to create a ticket')
        return redirect('tickets:index')
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        title = request.POST['title']
        description = request.POST['description']
        status = request.POST['status']
        priority = request.POST['priority']
        category = request.POST['category']
        assignee = User.objects.get(pk=request.POST['assignee'])
        due_date = request.POST['due_date']
        if due_date == "":
            due_date = None
        if not assignee:
            assignee = user
        
        ticket = Ticket.objects.create(
            issuer=request.user,
            assignee=assignee,
            title=title,
            description=description,
            status=Status.objects.get(id=status),
            priority=Priority.objects.get(id=priority),
            category=Category.objects.get(id=category),
            due_date=due_date
        )
        log_activity(ticket, request.user, "Created ticket")
        return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})
    else:
        return render(request, 'tickets/new_ticket.html', {"form": TicketForm()})
    
@login_required
def edit_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket = filter_ticket(request, ticket)
    if not ticket:
        messages.error(request, 'You do not have permission to edit this ticket')
        return redirect('tickets:index')
    if request.method == 'POST':
        # We want to create a new comment entry with the details of the changes made to the ticket.
        changes = []
        if User.objects.get(pk=request.POST['assignee']).id != ticket.assignee.id:
            try:
                changes.append(f"Assigned: {ticket.assignee} -> {User.objects.get(pk=request.POST['assignee'])}")
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid assignee'}, status=400)
        # Return error if the priority value is not a valid Priority names
        
        if request.POST['priority']:
            if not Priority.objects.filter(pk=request.POST['priority']).exists():
                return JsonResponse({'error': 'Invalid priority value'}, status=400)
            priority = Priority.objects.get(pk=request.POST['priority'])
            if priority != ticket.priority:
                changes.append(f"Priority: {ticket.priority.name} -> {priority.name}")
        if request.POST['category']:
            if not Category.objects.filter(pk=request.POST['category']).exists():
                return JsonResponse({'error': 'Invalid category value'}, status=400)
            category = Category.objects.get(pk=request.POST['category'])
            if category != ticket.category:
                changes.append(f"Category: {ticket.category.name} -> {category.name}")
        if request.POST['status']:
            if not Status.objects.filter(pk=request.POST['status']).exists():
                return JsonResponse({'error': 'Invalid status value'}, status=400)
            status = Status.objects.get(pk=request.POST['status'])
            if status != ticket.status:
                changes.append(f"Status: {ticket.status.name} -> {status.name}")
        if request.POST['assigned_group']:
            if not Group.objects.filter(pk=request.POST['assigned_group']).exists():
                return JsonResponse({'error': 'Invalid group value'}, status=400)
            assigned_group = Group.objects.get(pk=request.POST['assigned_group'])
            if ticket.assigned_group is None:
                changes.append(f"Assigned group: None -> {assigned_group.name}")
            elif assigned_group != ticket.assigned_group:
                changes.append(f"Assigned group: {ticket.assigned_group.name} -> {assigned_group.name}")
                
        if request.POST['title'] != ticket.title:
            changes.append(f"Title: {ticket.title} -> {request.POST['title']}")
        if request.POST['description'] != ticket.description:
            changes.append(f"Description: {ticket.description} -> {request.POST['description']}")
       
        
        # we have an issue with the date format, it is  reporting Due date: 2024-10-08 00:00:00+00:00 -> 2024-10-08 when actually the date is 2024-10-08 00:00:00
        # we need to fix this, we can use the date filter to format the date
        ticket_due_date = ticket.due_date.isoformat() if ticket.due_date else ""
        if request.POST['due_date'] != "" and request.POST['due_date'] != ticket_due_date:
            changes.append(f"Due date: {ticket.due_date} -> {request.POST['due_date']}")
        if changes:
            ticket.comments.create(
                author=request.user,
                comment=";\n".join(changes)
            )
            messages.success(request, f'Ticket #{ticket_id}  updated successfully')
            log_activity(ticket, request.user, "Changes to ticket")
        ticket.title = request.POST['title']
        ticket.description = request.POST['description']
        ticket.priority = Priority.objects.get(pk=request.POST['priority'])
        ticket.category = Category.objects.get(pk=request.POST['category'])
        ticket.assignee = User.objects.get(pk=request.POST['assignee'])
        ticket.status = Status.objects.get(pk=request.POST['status'])
        ticket.assigned_group = Group.objects.get(pk=request.POST['assigned_group'])
        if request.POST['due_date'] != "":
            ticket.due_date = request.POST['due_date']
        ticket.save()
        return redirect('tickets:ticket_detail', ticket_id=ticket_id)
    else:
        return render(request, 'tickets/edit_ticket.html', {'ticket': ticket, 'edit_form': TicketForm(instance=ticket)})
    
@login_required
def hide_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket = filter_ticket(request, ticket)
    if not ticket:
        messages.error(request, 'You do not have permission to hide this ticket')
        return redirect('tickets:index')
    ticket.hidden = True
    ticket.save()
    messages.success(request, f'Ticket {ticket_id} hidden successfully')
    log_activity(ticket, request.user, "Hided ticket")
    return redirect('tickets:index')

@login_required
def unhide_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket = filter_ticket(request, ticket)
    if not ticket:
        messages.error(request, 'You do not have permission to unhide this ticket')
        return redirect('tickets:index')
    ticket.hidden = False
    ticket.save()
    messages.success(request, f'Ticket #{ticket_id} unhidden successfully')
    log_activity(ticket, request.user, "Ticket unhiden")
    return redirect('tickets:index')

@login_required
def new_comment(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket = filter_ticket(request, ticket)
    if not ticket:
        messages.error(request, 'You do not have permission to add a comment to this ticket')
        return redirect('tickets:index')
    if request.method == 'POST':
        comment = request.POST['comment']
        ticket.comments.create(
            author=request.user,
            comment=comment
        )
        messages.success(request, f'Comment added successfully to the ticket #{ticket_id}' )
        log_activity(ticket, request.user, "Added comment to ticket")
        return redirect('tickets:ticket_detail', ticket_id=ticket_id)
    else:
        return render(request, 'tickets/new_comment.html', {'comment_form':CommentForm(),'ticket': ticket})
    
@login_required
def edit_comment(request, ticket_id, comment_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket = filter_ticket(request, ticket)
    if not ticket:
        messages.error(request, 'You do not have permission to edit a comment in this ticket')
        return redirect('tickets:index')
    comment = ticket.comments.get(pk=comment_id)
    if request.method == 'POST':
        comment.comment = request.POST['comment']
        comment.save()
        messages.success(request, f'Comment updated successfully to ticket #{ticket_id}')
        log_activity(ticket, request.user, "Edited comment in ticket")
        return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})
    else:
        return render(request, 'tickets/edit_comment.html', {'ticket': ticket, 'comment': comment})
    
@login_required
def delete_comment(request, ticket_id, comment_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket = filter_ticket(request, ticket)
    if not ticket:
        messages.error(request, 'You do not have permission to delete a comment in this ticket')
        return redirect('tickets:index')
    comment = ticket.comment_set.get(pk=comment_id)
    comment.delete()
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def upvote_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket.upvotes += 1
    ticket.save()
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def downvote_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket.downvotes += 1
    ticket.save()
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def upvote_comment(request, ticket_id, comment_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    comment = ticket.comment_set.get(pk=comment_id)
    comment.upvotes += 1
    comment.save()
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def downvote_comment(request, ticket_id, comment_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    comment = ticket.comment_set.get(pk=comment_id)
    comment.downvotes += 1
    comment.save()
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})
