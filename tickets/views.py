from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Changes, Ticket
from .forms import TicketForm, CommentForm
# Restrict access to the index view to authenticated users only.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from .statistics import Statistics
from functools import wraps
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# You could store API keys in settings or a more secure storage like a database
VALID_API_KEYS = {
    'your-api-key-1': 'Your username',
    'your-api-key-2': 'Another username',
}

def api_auth_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Get API key from request headers or query params
        api_key = request.headers.get('X-API-AUTH') or request.GET.get('api_key')
        
        if api_key and api_key in VALID_API_KEYS:
            user = User.objects.get(username=VALID_API_KEYS[api_key])
            request.user = user
            return view_func(request, *args, **kwargs)
        
        # If no valid API key is provided
        return JsonResponse({'error': 'Unauthorized. Invalid or missing API key.'}, status=401)

    return _wrapped_view
# API for listing all tickets (in JSON format)
@csrf_exempt
@api_auth_required
def api_add_comment(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)
    if 'comment' not in request.POST:
        return JsonResponse({'error': 'Comment is required'}, status=400)
    # Add comment
    ticket.comments.create(
        author=request.user,
        comment=request.POST['comment']
    )
    log_activity(ticket, request.user, "Added comment to ticket")
    return JsonResponse({'ticket_id': ticket.id})


@csrf_exempt
@api_auth_required
def api_ticket_edit(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)
    new_data = request.POST
    actions = []
    if 'priority' in new_data and new_data['priority'] not in Ticket.Priority:
        return JsonResponse({'error': 'Invalid priority value'}, status=400)
    if 'status' in new_data and new_data['status'] not in Ticket.Status:
        return JsonResponse({'error': 'Invalid status value'}, status=400)
    if 'category' in new_data and new_data['category'] not in Ticket.Category:
        return JsonResponse({'error': 'Invalid category value'}, status=400)
    if 'assignee' in new_data:
        try:
            new_assignee = User.objects.get(pk=request.POST['assignee'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid assignee'}, status=400)
        ticket.assignee = new_assignee
    if 'title' in new_data:
        actions.append(f"Title: {ticket.title} -> {request.POST['title']}")
        ticket.title = request.POST['title']
    if 'description' in new_data:
        actions.append(f"Description: {ticket.description} -> {request.POST['description']}")
        ticket.description = request.POST['description']
    if 'status' in new_data:
        actions.append(f"Status: {ticket.status} -> {request.POST['status']}")
        ticket.status = request.POST['status']
    if 'priority' in new_data:
        actions.append(f"Priority: {ticket.priority} -> {request.POST['priority']}")
        ticket.priority = request.POST['priority']
    if 'category' in new_data:
        actions.append(f"Category: {ticket.category} -> {request.POST['category']}")
        ticket.category = request.POST['category']
    if 'due_date' in new_data:
        actions.append(f"Due date: {ticket.due_date} -> {request.POST['due_date']}")
        ticket.due_date = request.POST['due_date']
    if actions:
        ticket.comments.create(
            author=request.user,
            comment=";\n".join(actions)
        )
        log_activity(ticket, request.user, "Changes to ticket")
    ticket.save()
    return JsonResponse({'ticket_id': ticket.id})

@csrf_exempt
@api_auth_required
def api_ticket_create(request):
    ticket = Ticket.objects.create(
        issuer=request.user,
        assignee=User.objects.get(pk=request.POST['assignee']),
        title=request.POST['title'],
        description=request.POST['description'],
        status=request.POST['status'],
        priority=request.POST['priority'],
        category=request.POST['category'],
        due_date=request.POST['due_date']
    )
    return JsonResponse({'ticket_id': ticket.id})

    
@api_auth_required
def api_list_tickets(request):
    tickets = Ticket.objects.filter(hidden=False) \
        .exclude(status=Ticket.Status.CLOSED).exclude(status=Ticket.Status.CANCELLED) \
        .order_by('-updated_at')
    tickets_data = [
        {
            'id': ticket.id,
            'title': ticket.title,
            'status': ticket.status,
            'priority': ticket.priority,
            'assignee': ticket.assignee.username,
            'created_at': ticket.created_at.isoformat(),
            'updated_at': ticket.updated_at.isoformat(),
            'due_date': ticket.due_date.isoformat() if ticket.due_date else None
        }
        for ticket in tickets
    ]
    # return JsonResponse({}, safe=False)  
    return JsonResponse({'tickets': tickets_data}, safe=False)

# API for ticket details
@api_auth_required
def api_ticket_detail(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)
    ticket_data = {
        'id': ticket.id,
        'title': ticket.title,
        'description': ticket.description,
        'status': ticket.status,
        'priority': ticket.priority,
        'assignee': ticket.assignee.username,
        'created_at': ticket.created_at.isoformat(),
        'updated_at': ticket.updated_at.isoformat(),
        'comments': [
            {
                'id': comment.id,
                'author': comment.author.username,
                'comment': comment.comment,
                'created_at': comment.created_at.isoformat(),
                'upvotes': comment.upvotes,
                'downvotes': comment.downvotes
            }
            for comment in ticket.comments.all()
        ]
    }
    return JsonResponse(ticket_data)
    
    
def statistics_view(request):
    context = {
        'avg_resolution_time': Statistics.average_ticket_resolution_time(),
        'open_tickets_assignee_to_users': Statistics.open_tickets_assignee_to_users(),
        'closed_tickets_assignee_to_users': Statistics.closed_tickets_assignee_to_users(),
        'ticket_status_summary': Statistics.ticket_status_summary(),
        'priority_summary': Statistics.priority_summary(),
        'over_due': Statistics.overdue_task_count(),
        'resolved_before': Statistics.not_overdue_task_count(),
        'open_tickets_per_user_category': Statistics.open_tickets_per_user_category(),
        'closed_tickets_per_user_category': Statistics.closed_tickets_per_user_category()
    }
    return render(request, 'tickets/statistics.html', context)

def app_index(request):
    return render(request, 'tickets/app_index.html')

def log_activity(ticket, request_user, log):
    actor = User.objects.get(pk=request_user.id)
    Changes.objects.create(
        ticket=ticket,
        actor=actor,
        log=log
    )
    
    
@login_required
def pull_request(request):
    # get the requests args
    # i.e. /api/tickets/pull?action=get_info&source=new_tickets_timestamp
    action = request.GET.get('action')
    source = request.GET.get('source')
    if action == 'get_info':
        if source == 'open_issues':
            # get the timestamp of the last ticket created
            open_bugs = Ticket.objects.all().filter(hidden=False).exclude(status=Ticket.Status.CLOSED).exclude(status=Ticket.Status.CANCELLED).order_by('-created_at').filter(category=Ticket.Category.BUG)
            # return json response
            return JsonResponse({
                                 'tickets': [{"id":last_ticket.pk, "title": last_ticket.title, "status": "new" if last_ticket.status == Ticket.Status.OPEN else "known" } for last_ticket in open_bugs]
                                 })   

@login_required
def help_view(request):
    return render(request, 'tickets/help.html')

@login_required
def list_issues(request):
    ticket_list = Ticket.objects.all().filter(hidden=False) \
    .filter(category=Ticket.Category.BUG) \
    .exclude(status=Ticket.Status.CLOSED).exclude(status=Ticket.Status.CANCELLED) \
    .order_by('-updated_at')
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
    .filter(status__in=[Ticket.Status.CLOSED, Ticket.Status.CANCELLED]) \
    .order_by('-updated_at')
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
    paginator = Paginator(ticket_list, 10)
    tickets_count = ticket_list.count()
    page_number = request.GET.get('page')
    changes = paginator.get_page(page_number)
    return render(request, 'tickets/changes.html', {'changes': changes, 'tickets_count': tickets_count})

@login_required
def index(request):
    ticket_list = Ticket.objects.filter(hidden=False).exclude(status=Ticket.Status.CLOSED).exclude(status=Ticket.Status.CANCELLED).order_by('-updated_at')
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
        tickets = tickets.filter(status=Ticket.Status.CLOSED) | tickets.filter(status=Ticket.Status.CANCELLED)
    else:
        tickets = tickets.exclude(status=Ticket.Status.CLOSED).exclude(status=Ticket.Status.CANCELLED)
    if tickets.count() == 0:
        messages.error(request, f'No tickets found for "{query}"')
    else:
        messages.success(request, f'Search results for "{query}" coming from {history}')
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
    ticket_list = Ticket.objects.filter(hidden=False, assignee=request.user).exclude(status=Ticket.Status.CLOSED).exclude(status=Ticket.Status.CANCELLED).order_by('-updated_at')
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
    ticket_list = Ticket.objects.filter(hidden=False, status=Ticket.Status.IN_PROGRESS).order_by('-updated_at')
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
            status=status,
            priority=priority,
            category=category,
            due_date=due_date
        )
        log_activity(ticket, request.user, "Created ticket")
        return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})
    else:
        return render(request, 'tickets/new_ticket.html', {"form": TicketForm()})
    
@login_required
def edit_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    if request.method == 'POST':
        # We want to create a new comment entry with the details of the changes made to the ticket.
        changes = []
        if User.objects.get(pk=request.POST['assignee']).id != ticket.assignee.id:
            try:
                changes.append(f"Assigned: {ticket.assignee} -> {User.objects.get(pk=request.POST['assignee'])}")
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid assignee'}, status=400)
        if request.POST['priority'] != ticket.priority:
            if request.POST['priority'] not in Ticket.Priority:
                return JsonResponse({'error': 'Invalid priority value'}, status=400)
            changes.append(f"Priority: {ticket.priority} -> {request.POST['priority']}")
        if request.POST['category'] != ticket.category:
            if request.POST['category'] not in Ticket.Category:
                return JsonResponse({'error': 'Invalid category value'}, status=400)
            changes.append(f"Category: {ticket.category} -> {request.POST['category']}")
        if request.POST['title'] != ticket.title:
            changes.append(f"Title: {ticket.title} -> {request.POST['title']}")
        if request.POST['description'] != ticket.description:
            changes.append(f"Description: {ticket.description} -> {request.POST['description']}")
        if request.POST['status'] != ticket.status:
            if request.POST['status'] not in Ticket.Status:
                return JsonResponse({'error': 'Invalid status value'}, status=400)
            changes.append(f"Status: {ticket.status} -> {request.POST['status']}")
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
        ticket.priority = request.POST['priority']
        ticket.category = request.POST['category']
        ticket.assignee = User.objects.get(pk=request.POST['assignee'])
        ticket.status = request.POST['status']
        if request.POST['due_date'] != "":
            ticket.due_date = request.POST['due_date']
        ticket.save()
        return redirect('tickets:ticket_detail', ticket_id=ticket_id)
    else:
        return render(request, 'tickets/edit_ticket.html', {'ticket': ticket, 'edit_form': TicketForm(instance=ticket)})
    
@login_required
def hide_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket.hidden = True
    ticket.save()
    messages.success(request, f'Ticket {ticket_id} hidden successfully')
    log_activity(ticket, request.user, "Hided ticket")
    return redirect('tickets:index')

@login_required
def unhide_ticket(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket.hidden = False
    ticket.save()
    messages.success(request, f'Ticket #{ticket_id} unhidden successfully')
    log_activity(ticket, request.user, "Unhided ticket")
    return redirect('tickets:index')

@login_required
def new_comment(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
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
