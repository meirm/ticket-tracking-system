Okay, I understand. You want to remove the entire UI layer (HTML templates, related static files, Django views rendering HTML, Django forms) and keep only the API backend, refactoring it to use Django REST Framework (DRF) best practices where appropriate.

Here's a plan and the corresponding changes:

**Plan:**

1.  **Add DRF Dependency:** Add `djangorestframework` to `requirements.txt`.
2.  **Configure DRF:** Add `rest_framework` to `INSTALLED_APPS` in `core/settings.py`.
3.  **Remove UI Apps/Files:**
    *   Delete the `pages` app entirely.
    *   Delete all `templates/` directories and their contents within `accounts`, `core`, `tickets`.
    *   Delete UI-related static files: `static/css/`, `static/js/clock.js`, `static/js/global_foot.js`, `static/js/global_head.js`, `static/js/jpost.js`, `static/js/tickets.js`, `static/js/widgets.js`. Keep `static/openapi.json`.
    *   Delete UI-related documentation: `Manual.md`, `screenshot.png`.
4.  **Remove UI Code:**
    *   Remove Django `forms.py` from `accounts` and `tickets`.
    *   Remove views that render HTML templates from `accounts/views.py`, `tickets/views.py`.
    *   Remove UI-related helper functions (like `filter_tickets`, `filter_ticket`, `load_users`) from `tickets/views.py`.
    *   Remove URLs pointing to UI views from `accounts/urls.py`, `tickets/urls.py`, `core/urls.py`.
5.  **Refactor API with DRF:**
    *   Create/Update `serializers.py` in `tickets` (and potentially `accounts`) for models (Ticket, Comment, User, Group, Category, Status, Priority, ApiKey).
    *   Refactor existing API views in `tickets/views.py` to use DRF's `APIView`, Generic Views (like `ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`), or `ViewSets`.
    *   Update API URLs in `tickets/urls.py` to point to the new DRF views/viewsets.
    *   Integrate DRF authentication (e.g., using the existing `api_auth` decorator or switching to DRF's `TokenAuthentication` or Session Authentication for the browsable API) and permissions (implementing logic similar to `tickets/authorization.py` and the old `filter_tickets` function within DRF permission classes).
6.  **Clean Up:**
    *   Update `core/settings.py` (remove `pages` from `INSTALLED_APPS`).
    *   Update `core/urls.py` (remove `pages` include).
    *   Update `README.md`, `project_tree.txt`, `ai_docs/api_integration.md`, `static/openapi.json` to reflect the API-only structure and DRF endpoints.

**Implementation:**

**1. Files/Directories to DELETE:**

*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/pages/` (entire directory)
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/accounts/templates/`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/core/templates/anon_base.html`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/core/templates/base.html`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/core/templates/messages.html`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/core/templates/navbar.html`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/tickets/templates/`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/accounts/forms.py`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/tickets/forms.py`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/static/css/`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/static/js/clock.js`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/static/js/global_foot.js`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/static/js/global_head.js`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/static/js/jpost.js`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/static/js/widgets.js`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/static/js/tickets.js`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/static/favicon.ico` (Likely UI specific)
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/Manual.md`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/screenshot.png`
*   `/Users/meirm/git/cyborgfi/ticket-tracking-system/tickets/statistics.py` (Stats were likely for UI, API could expose raw data if needed)

**2. Files to MODIFY:**

```diff
--- a/Users/meirm/git/cyborgfi/ticket-tracking-system/requirements.txt
+++ b/Users/meirm/git/cyborgfi/ticket-tracking-system/requirements.txt
@@ -6,6 +6,7 @@
 python-dotenv==1.0.1
 gunicorn==23.0.0
 graphene-django==3.2.2
+djangorestframework==3.15.1
 django-filter==21.1
 django-reset-migrations==0.4.0
 # graphene-django-filter==0.6.5 # not compatible with Django 5.1.1

```

```diff
--- a/Users/meirm/git/cyborgfi/ticket-tracking-system/core/settings.py
+++ b/Users/meirm/git/cyborgfi/ticket-tracking-system/core/settings.py
@@ -36,10 +36,10 @@
     'django.contrib.messages',
     'django.contrib.staticfiles',
     'reset_migrations',
+    'rest_framework', # Add DRF
     'graphene_django',
-    'pages',
+    # 'pages', # Remove UI app
     'accounts',
     'tickets',
 ]
@@ -59,7 +59,7 @@
 TEMPLATES = [
     {
         'BACKEND': 'django.template.backends.django.DjangoTemplates',
-        'DIRS': ["core/templates/"],
+        'DIRS': [], # Remove core templates dir, DRF browsable API uses its own
         'APP_DIRS': True,
         'OPTIONS': {
             'context_processors': [

```

```diff
--- a/Users/meirm/git/cyborgfi/ticket-tracking-system/core/urls.py
+++ b/Users/meirm/git/cyborgfi/ticket-tracking-system/core/urls.py
@@ -16,14 +16,15 @@
 from django.urls import path
 from django.urls.conf import include
 from tickets import urls as tickets_urls
-from accounts import urls as accounts_urls
-from pages import urls as pages_urls
+from accounts import urls as accounts_urls # Keep for potential API auth endpoints later
+# from pages import urls as pages_urls # Remove pages app
 from graphene_django.views import GraphQLView
 
 urlpatterns = [
     path("graphql", GraphQLView.as_view(graphiql=True)),
-    path('', include(pages_urls)),
-    path('accounts/', include(accounts_urls)),
+    # path('', include(pages_urls)), # Remove landing page
+    # path('accounts/', include(accounts_urls)), # Keep accounts URLs if planning API auth/profile endpoints
+    path('accounts/api/v1/', include(accounts_urls)), # Example: Namespace account API endpoints
     path('tickets/', include(tickets_urls)),
     path('admin/', admin.site.urls),
 ]

```

```diff
--- a/Users/meirm/git/cyborgfi/ticket-tracking-system/accounts/urls.py
+++ b/Users/meirm/git/cyborgfi/ticket-tracking-system/accounts/urls.py
@@ -4,14 +4,15 @@
 app_name = 'accounts'
 urlpatterns = [
     path('login/', views.login_view, name='login'),
-    path('logout/', views.logout_view, name='logout'),
-    path('profile/', views.profile_view, name='profile'),
-    path('admin_board/', views.admin_board_view, name='admin_board'),
-    path('password/change/', views.password_change_view, name='password_change'),
-    path('key/', views.api_key_view, name='api_keys'),
+    # Remove UI related views - replace with DRF endpoints if needed
+    # path('logout/', views.logout_view, name='logout'),
+    # path('profile/', views.profile_view, name='profile'),
+    # path('admin_board/', views.admin_board_view, name='admin_board'), # Admin board could be an API endpoint
+    # path('password/change/', views.password_change_view, name='password_change'),
+    # path('key/', views.api_key_view, name='api_keys'), # API Key management should be API endpoints
     path('key/create/', views.api_key_create, name='api_key_create'),
     path('key/deactivate/<str:key>/', views.api_key_deactivate, name='api_key_disable'),
     path('key/activate/<str:key>/', views.api_key_activate, name='api_key_enable'),
     path('key/delete/<str:key>/', views.api_key_delete, name='api_key_delete'),
+    # Add other DRF endpoints for auth, profile, etc. here
 ]
```

```python
# /Users/meirm/git/cyborgfi/ticket-tracking-system/accounts/views.py
# Remove all views except potentially the api_key actions (if kept as simple actions)
# and the log_activity utility if it's still needed.
# Consider replacing login/logout/profile/password views with DRF equivalents
# using packages like dj-rest-auth or djoser, or custom APIViews.
# The api_key actions might become API endpoints themselves.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required # Might not be needed if using DRF auth
from django.views.decorators.http import require_POST
# from .forms import LoginForm, PasswordChangeForm, ProfileForm, ApiKeyForm # Remove Forms
from .utils import log_activity
# from django.core.paginator import Paginator # Paginator likely not needed directly in views
from .models import Activity, ApiKey
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated # Example DRF permission
from rest_framework.response import Response
from rest_framework import status


# Keep API Key management actions, but potentially refactor as DRF API endpoints
@login_required # Or use DRF's IsAuthenticated
def api_key_delete(request, key):
    # ... (keep logic, but maybe return Response instead of redirect)
    try:
        key_obj = ApiKey.objects.get(key=key, user=request.user) # Ensure user owns key
        key_obj.delete()
        log_activity(request.user, 'DELETE', level='INFO', log='API key deleted.')
        # return redirect('accounts:api_keys') # Replace with API response
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ApiKey.DoesNotExist:
        # return redirect('accounts:api_keys') # Replace with API response
        return Response({'error': 'API Key not found or permission denied'}, status=status.HTTP_404_NOT_FOUND)


@login_required # Or use DRF's IsAuthenticated
def api_key_activate(request, key):
    # ... (keep logic, but maybe return Response instead of redirect)
     try:
        key_obj = ApiKey.objects.get(key=key, user=request.user) # Ensure user owns key
        key_obj.activate()
        log_activity(request.user, 'UPDATE', level='INFO', log='API key activated.')
        # return redirect('accounts:api_keys') # Replace with API response
        # Consider returning the updated key info using a serializer
        serializer = ApiKeySerializer(key_obj)
        return Response(serializer.data)
     except ApiKey.DoesNotExist:
        # return redirect('accounts:api_keys') # Replace with API response
        return Response({'error': 'API Key not found or permission denied'}, status=status.HTTP_404_NOT_FOUND)


@login_required # Or use DRF's IsAuthenticated
def api_key_deactivate(request, key):
     try:
        key_obj = ApiKey.objects.get(key=key, user=request.user) # Ensure user owns key
        key_obj.deactivate()
        log_activity(request.user, 'UPDATE', level='INFO', log='API key deactivated.')
        # return redirect('accounts:api_keys') # Replace with API response
        # Consider returning the updated key info using a serializer
        serializer = ApiKeySerializer(key_obj)
        return Response(serializer.data)
     except ApiKey.DoesNotExist:
        # return redirect('accounts:api_keys') # Replace with API response
        return Response({'error': 'API Key not found or permission denied'}, status=status.HTTP_404_NOT_FOUND)


# Refactor api_key_create using DRF
from .serializers import ApiKeySerializer # Assuming you create this serializer

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Use DRF permissions
def api_key_create_drf(request):
    # Use a serializer to validate input if needed, or directly create
    application_name = request.data.get('application')
    if not application_name:
         return Response({'error': 'Application name is required'}, status=status.HTTP_400_BAD_REQUEST)

    api_key = ApiKey(application=application_name,
                         user=request.user)
    api_key.save() # save() generates the key
    log_activity(request.user, 'CREATE', level='INFO', log=f'API key created for {application_name}.')
    serializer = ApiKeySerializer(api_key)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Remove all other views:
# login_view, admin_board_view, logout_view, profile_view, password_change_view, api_key_view

```

```diff
--- a/Users/meirm/git/cyborgfi/ticket-tracking-system/tickets/urls.py
+++ b/Users/meirm/git/cyborgfi/ticket-tracking-system/tickets/urls.py
@@ -4,28 +4,28 @@
 
 app_name = 'tickets'
 urlpatterns = [
-    
-    path('', views.index, name='index'),
-    path('pull/', views.pull_request, name='pull_request'),
-    path('statistics/', views.statistics_view, name='statistics'),
-    path('in_progress', views.in_progress_view, name='in_progress'),
-    path("help/", views.help_view, name="view_help"),
-    path("privacy/", views.privacy_view, name="view_privacy"),
-    path("terms/", views.terms_view, name="view_terms"),
-    path('issues/', views.list_issues, name='list_issues'),
-    path('changes/', views.view_changes, name='view_changes'),
-    path("my/", views.my_tasks, name="my_tasks"),
-    path('search/', views.search_tickets, name='search_tickets'),
-    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
-    path('new/', views.new_ticket, name='new_ticket'),
-    path('closed/', views.list_closed_tickets, name='list_closed_tickets'),
-    path('hidden/', views.list_hidden_tickets, name='list_hidden_tickets'),
-    path('<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
-    path('<int:ticket_id>/hide/', views.hide_ticket, name='hide_ticket'),
-    path('<int:ticket_id>/unhide/', views.unhide_ticket, name='unhide_ticket'),
-    path('<int:ticket_id>/comment/', views.new_comment, name='new_comment'),
-    path('<int:ticket_id>/comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
-    path('<int:ticket_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
-    path('<int:ticket_id>/upvote/', views.upvote_ticket, name='upvote_ticket'),
-    path('<int:ticket_id>/downvote/', views.downvote_ticket, name='downvote_ticket'),
-    path('<int:ticket_id>/comment/<int:comment_id>/upvote/', views.upvote_comment, name='upvote_comment'),
-    path('<int:ticket_id>/comment/<int:comment_id>/downvote/', views.downvote_comment, name='downvote_comment'),
+
+    # Remove all UI URLs
+    # path('', views.index, name='index'),
+    # path('pull/', views.pull_request, name='pull_request'), # This was likely for UI updates
+    # path('statistics/', views.statistics_view, name='statistics'),
+    # path('in_progress', views.in_progress_view, name='in_progress'),
+    # path("help/", views.help_view, name="view_help"),
+    # path("privacy/", views.privacy_view, name="view_privacy"),
+    # path("terms/", views.terms_view, name="view_terms"),
+    # path('issues/', views.list_issues, name='list_issues'),
+    # path('changes/', views.view_changes, name='view_changes'), # Changes could be an API endpoint
+    # path("my/", views.my_tasks, name="my_tasks"),
+    # path('search/', views.search_tickets, name='search_tickets'), # Search should be API filtering
+    # path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
+    # path('new/', views.new_ticket, name='new_ticket'),
+    # path('closed/', views.list_closed_tickets, name='list_closed_tickets'),
+    # path('hidden/', views.list_hidden_tickets, name='list_hidden_tickets'),
+    # path('<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
+    # path('<int:ticket_id>/hide/', views.hide_ticket, name='hide_ticket'), # Hiding could be an API action
+    # path('<int:ticket_id>/unhide/', views.unhide_ticket, name='unhide_ticket'), # Unhiding could be an API action
+    # path('<int:ticket_id>/comment/', views.new_comment, name='new_comment'),
+    # path('<int:ticket_id>/comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
+    # path('<int:ticket_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
+    # path('<int:ticket_id>/upvote/', views.upvote_ticket, name='upvote_ticket'), # Voting could be API actions
+    # path('<int:ticket_id>/downvote/', views.downvote_ticket, name='downvote_ticket'),
+    # path('<int:ticket_id>/comment/<int:comment_id>/upvote/', views.upvote_comment, name='upvote_comment'),
+    # path('<int:ticket_id>/comment/<int:comment_id>/downvote/', views.downvote_comment, name='downvote_comment'),
     # Add api urls
     path('api/v1/list/', views.api_list_tickets, name='api_ticket_list'),
     path('api/v1/detail/<int:ticket_id>/', views.api_ticket_detail, name='api_ticket_detail'),
     path('api/v1/edit/<int:ticket_id>/', views.api_ticket_edit, name='api_ticket_edit'),
     path('api/v1/create/', views.api_ticket_create, name='api_ticket_create'),
     path('api/v1/add_comment/<int:ticket_id>/', views.api_add_comment, name='api_ticket_add_comment'),
-    path('api/v1/load-users/', views.load_users, name='ajax_load_users'),
+    # path('api/v1/load-users/', views.load_users, name='ajax_load_users'), # Was AJAX for UI form
+    # You'll likely replace these with DRF ViewSets and Routers
 ]

```

```python
# /Users/meirm/git/cyborgfi/ticket-tracking-system/tickets/views.py
# Remove all non-API views and helpers. Refactor API views using DRF.

# from django.shortcuts import render, redirect # Keep redirect for now? Maybe not needed.
from django.http import JsonResponse
from .models import Changes, Ticket, Category, Status, Priority, Comment # Add Comment
# from .forms import TicketForm, CommentForm # Remove Forms
from django.contrib.auth.models import User, Group
# from django.contrib import messages # Messages are for UI
# from django.core.paginator import Paginator # Paginator used for UI lists
# from .statistics import Statistics # Statistics were for UI
# from functools import wraps # Not needed unless used elsewhere
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt # Potentially remove if using DRF auth
# from django.contrib.auth.decorators import login_required, permission_required # Use DRF permissions
# from tickets.authorization import can_view_group_tickets # Move logic to DRF permissions
from accounts.auth import api_auth # Keep or replace with DRF auth
import json

# DRF Imports
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import TicketSerializer, CommentSerializer, UserSerializer, GroupSerializer # Create these

# --- Remove UI Helper Functions ---
# def filter_tickets(request, ticket_list): ...
# def filter_ticket(request, ticket): ...
# def load_users(request): ...

# --- Keep Activity Logging Helper ---
def log_activity(ticket, request_user, log):
    # Ensure user is fetched correctly if request.user might be anonymous or different type
    actor = request_user if isinstance(request_user, User) else User.objects.get(pk=request_user.id)
    Changes.objects.create(
        ticket=ticket,
        actor=actor,
        log=log
    )

# --- Refactor API views using DRF ---

# Example using ViewSets (Recommended)

class TicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tickets to be viewed or edited.
    """
    serializer_class = TicketSerializer
    # permission_classes = [permissions.IsAuthenticated] # Add DRF permissions
    # Instead of api_auth decorator, configure DEFAULT_AUTHENTICATION_CLASSES in settings.py
    # or add authentication_classes = [...] here.

    def get_queryset(self):
        """
        This view should return a list of all the tickets
        for the currently authenticated user.
        Implement filtering logic similar to old filter_tickets function.
        """
        user = self.request.user
        queryset = Ticket.objects.filter(hidden=False) # Base queryset

        # Apply filtering based on user group and permissions
        # This logic needs to be adapted from the old `filter_tickets` function
        if user.is_superuser or user.groups.filter(name='Admin').exists() or user.groups.filter(name='ReadOnly').exists():
             # Admins and ReadOnly can see all non-hidden tickets (adjust ReadOnly if needed)
             pass # No additional filtering needed for these roles on the base queryset
        elif user.groups.filter(name='Untrusted').exists():
             queryset = queryset.filter(assignee=user) | queryset.filter(issuer=user)
        else:
             # Apply group/permission based filtering
             user_groups = user.groups.all()
             can_view_all = any(g.permissions.filter(codename='can_view_all_tickets').exists() for g in user_groups)

             if not can_view_all:
                group_tickets = Ticket.objects.none()
                # Check group permissions (adapt can_view_group_tickets logic)
                viewable_group_ids = [g.id for g in user_groups if g.permissions.filter(codename='can_view_group_tickets').exists()] # Example permission check
                if viewable_group_ids:
                     group_tickets = queryset.filter(assigned_group_id__in=viewable_group_ids)

                # Combine own, assigned, and viewable group tickets
                queryset = queryset.filter(assignee=user) | queryset.filter(issuer=user) | group_tickets
                # Ensure unique results if necessary
                queryset = queryset.distinct()


        # Apply status filtering (e.g., exclude closed by default)
        queryset = queryset.exclude(status__closed=True)

        # Apply query parameters for filtering (status, priority, dates, etc.)
        # Use django-filter package or implement manually
        status_param = self.request.query_params.get('status')
        priority_param = self.request.query_params.get('priority')
        # ... add other filters ...

        if status_param:
             statuses = status_param.split(',')
             queryset = queryset.filter(status__name__in=statuses) # Adjust field if using IDs
        if priority_param:
             priorities = priority_param.split(',')
             queryset = queryset.filter(priority__name__in=priorities) # Adjust field if using IDs

        return queryset.order_by('-updated_at')

    def perform_create(self, serializer):
        # Automatically set the issuer to the logged-in user
        instance = serializer.save(issuer=self.request.user)
        log_activity(instance, self.request.user, "Created ticket")


    def perform_update(self, serializer):
        # Log changes made during update
        # You might need to compare old and new values for detailed logging
        instance = serializer.save()
        # Simplified logging for now
        log_activity(instance, self.request.user, "Changes to ticket")

    # Add custom actions if needed (e.g., for adding comments)
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
        serializer = CommentSerializer(comment) # Assuming CommentSerializer exists
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows comments to be viewed or edited.
    """
    serializer_class = CommentSerializer
    # permission_classes = [permissions.IsAuthenticated] # Add permissions

    def get_queryset(self):
        """
        Optionally restrict comments visibility based on ticket access.
        """
        user = self.request.user
        # Add logic here to filter comments based on user's access to the parent ticket
        # For simplicity, showing all comments for now, assuming ticket filtering handles access
        return Comment.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
         # Requires ticket_id in the request data
         ticket_id = self.request.data.get('ticket')
         try:
             ticket = Ticket.objects.get(pk=ticket_id)
             # Add permission check: Can user comment on this ticket?
             # if not can_comment_on_ticket(self.request.user, ticket):
             #     raise PermissionDenied("You cannot comment on this ticket.")
             instance = serializer.save(author=self.request.user, ticket=ticket)
             log_activity(ticket, self.request.user, "Added comment to ticket")
         except Ticket.DoesNotExist:
              raise serializers.ValidationError("Ticket not found.") # Or return 404 Response

# --- Remove Old API Views ---
# @csrf_exempt
# @api_auth(required=True)
# def api_add_comment(request, ticket_id): ...

# @csrf_exempt
# @api_auth(required=True)
# def api_ticket_edit(request, ticket_id): ...

# @csrf_exempt
# @api_auth(required=True)
# def api_ticket_create(request): ...

# @api_auth(required=True)
# def api_list_tickets(request): ...

# @api_auth(required=True)
# def api_ticket_detail(request, ticket_id): ...


# --- Remove UI Views ---
# def statistics_view(request): ...
# def app_index(request): ...
# def pull_request(request): ...
# def privacy_view(request): ...
# def terms_view(request): ...
# def help_view(request): ...
# def list_issues(request): ...
# def list_closed_tickets(request): ...
# def list_hidden_tickets(request): ...
# def view_changes(request): ...
# def index(request): ...
# def ticket_detail(request, ticket_id): ...
# def search_tickets(request): ...
# def my_tasks(request): ...
# def in_progress_view(request): ...
# def new_ticket(request): ...
# def edit_ticket(request, ticket_id): ...
# def hide_ticket(request, ticket_id): ...
# def unhide_ticket(request, ticket_id): ...
# def new_comment(request, ticket_id): ...
# def edit_comment(request, ticket_id, comment_id): ...
# def delete_comment(request, ticket_id, comment_id): ...
# def upvote_ticket(request, ticket_id): ...
# def downvote_ticket(request, ticket_id): ...
# def upvote_comment(request, ticket_id, comment_id): ...
# def downvote_comment(request, ticket_id, comment_id): ...

```

**3. Create/Update Serializers:**

```python
# /Users/meirm/git/cyborgfi/ticket-tracking-system/tickets/serializers.py
from rest_framework import serializers
from .models import Ticket, Comment, Category, Priority, Status
from django.contrib.auth.models import User, Group

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email'] # Add more fields if needed

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ['id', 'name']

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name', 'closed']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True) # Display author details
    ticket = serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all(), write_only=True) # For creating comments

    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'author', 'comment', 'created_at', 'updated_at', 'upvotes', 'downvotes']
        read_only_fields = ['author', 'created_at', 'updated_at'] # Author set automatically

class TicketSerializer(serializers.ModelSerializer):
    # Make relationships readable, but accept IDs for writing
    issuer = UserSerializer(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True), allow_null=True, required=False)
    assigned_group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), allow_null=True, required=False)
    priority = serializers.PrimaryKeyRelatedField(queryset=Priority.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())

    # Add nested comments for detail view
    comments = CommentSerializer(many=True, read_only=True)
    # Use StringRelatedField for readable names in list views if preferred
    assignee_username = serializers.StringRelatedField(source='assignee.username', read_only=True)
    assigned_group_name = serializers.StringRelatedField(source='assigned_group.name', read_only=True)
    priority_name = serializers.StringRelatedField(source='priority.name', read_only=True)
    category_name = serializers.StringRelatedField(source='category.name', read_only=True)
    status_name = serializers.StringRelatedField(source='status.name', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'issuer', 'assignee', 'assigned_group', 'permissions',
            'priority', 'category', 'status', 'title', 'description',
            'created_at', 'updated_at', 'due_date', 'upvotes', 'downvotes',
            'hidden', 'comments',
            # Read-only fields for convenience
            'assignee_username', 'assigned_group_name', 'priority_name',
            'category_name', 'status_name',
        ]
        read_only_fields = ['issuer', 'created_at', 'updated_at', 'comments'] # Issuer set automatically

    # Add validation if needed, e.g., assignee must be in assigned_group
    def validate(self, data):
        assignee = data.get('assignee')
        assigned_group = data.get('assigned_group')
        if assignee and assigned_group:
            if not assignee.groups.filter(id=assigned_group.id).exists():
                raise serializers.ValidationError("Assignee must belong to the assigned group.")
        return data

```

```python
# /Users/meirm/git/cyborgfi/ticket-tracking-system/accounts/serializers.py
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
        fields = ['id', 'user', 'application', 'key', 'created_at', 'updated_at', 'active']
        read_only_fields = ['user', 'key', 'created_at', 'updated_at'] # Key generated on save

```

**4. Update Documentation:**

*   **`README.md`:** Rewrite to describe an API-only backend using DRF. Remove UI setup/usage instructions. Add DRF setup.
*   **`project_tree.txt`:** Regenerate or manually update to remove UI files/folders.
*   **`ai_docs/api_integration.md`:** Update endpoint examples and descriptions to match the new DRF structure (e.g., using ViewSet URLs).
*   **`static/openapi.json`:** Regenerate this based on the DRF serializers and viewsets, potentially using a tool like `drf-spectacular`.

**5. Final Steps:**

*   Run `pip install -r requirements.txt`.
*   Run `python manage.py makemigrations` (in case model changes were needed, though unlikely for this refactor).
*   Run `python manage.py migrate`.
*   Test the API endpoints thoroughly using tools like `curl`, Postman, or writing API client tests.

This process transforms the project into a pure DRF backend, removing all the Django template rendering and UI-specific logic. Remember to implement robust authentication and permission classes in DRF to replace the logic previously handled by decorators and helper functions.
