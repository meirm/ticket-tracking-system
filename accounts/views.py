from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import LoginForm, PasswordChangeForm, ProfileForm
from .utils import log_activity
from django.core.paginator import Paginator
from .models import Activity, ApiKey, UserProfile
from .forms import ApiKeyForm
from django.http import JsonResponse
import secrets
import string
from .auth import api_auth
from django.views.decorators.csrf import csrf_exempt

@login_required
def api_key_view(request):
    keys = ApiKey.objects.filter(user=request.user)
    return render(request, 'accounts/api_keys.html', {'keys': keys,'form': ApiKeyForm()})

@login_required
def api_key_delete(request, key):
    key = ApiKey.objects.get(key=key)
    key.delete()
    messages.success(request, 'API key deleted successfully.')
    log_activity(request.user, 'DELETE', level='INFO', log='API key deleted.')
    return redirect('accounts:api_keys')

@login_required
def api_key_activate(request, key):
    key = ApiKey.objects.get(key=key)
    key.activate()
    messages.success(request, 'API key activated successfully.')
    log_activity(request.user, 'UPDATE', level='INFO', log='API key activated.')
    return redirect('accounts:api_keys')

@login_required
def api_key_deactivate(request, key):
    key_id = request.GET.get('key_id')
    key = ApiKey.objects.get(key=key)
    key.deactivate()
    messages.success(request, 'API key deactivated successfully.')
    log_activity(request.user, 'UPDATE', level='INFO', log='API key deactivated.')
    return redirect('accounts:api_keys')

# allow only post access
@login_required
@require_POST
def api_key_create(request):
        form = ApiKeyForm(request.POST)
        if form.is_valid():
            api_key = ApiKey(application=form.cleaned_data.get('application'), 
                             user=request.user)    
            api_key.save()
            messages.success(request, 'API key created successfully.')
            log_activity(request.user, 'CREATE', level='INFO', log='API key created.')
            return redirect('accounts:api_keys')
        

def login_view(request):
    if request.method == 'POST':
        sudo = False
        username = request.POST['username']
        if ":" in username:
            username = username.split(":")
            sudoer = username[0]
            target_username = username[1]
            sudo = True
        password = request.POST['password']
        if sudo:
            user = authenticate(request, username=sudoer, password=password)
            if user is not None:
                if user.is_superuser:
                    target_user = User.objects.get(username=target_username)
                    login(request, target_user)
                    log_activity(target_user, 'LOGIN',level='INFO' ,log='Sudo login by ' + sudoer)
                    # If the user doesn't have a UserProfile, create one
                    if not UserProfile.objects.filter(user=target_user).exists():
                        UserProfile.objects.create(user=target_user)
                    return redirect('tickets:index')
                else:
                    log_activity(user.username,'LOGIN', level='WARNING', log='Failed sudo login attempt: not authorized to use sudo.')
                    messages.error(request, 'You are not authorized to use sudo.')
            else:
                log_activity('anonymous','LOGIN',  level='WARNING', log=f'Failed sudo login attempt: invalid username ({sudoer}) or password.')
                messages.error(request, 'Invalid username or password.')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                log_activity(user.username, 'LOGIN', level='INFO', log=f'Successful login.')
                if not UserProfile.objects.filter(user=user).exists():
                        UserProfile.objects.create(user=user)
                return redirect('tickets:index')
            else:
                messages.error(request, 'Invalid username or password.')
                log_activity('anonymous', 'LOGIN',  level='WARNING', log=f'Failed login attempt: invalid username ({username}) or password.')
                
    return render(request, 'accounts/login.html', {'form': LoginForm()})

@login_required
def admin_board_view(request):
    user = request.user
    
    if not (user.is_superuser or user.has_perm('accounts.view_activity')):
        log_activity(request.user, 'UNAUTHORIZED ACCESS', level='WARNING', log='Unauthorized access to admin board.')
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('pages:landing_page')
    activities_list = Activity.objects.all().order_by('-created_at')[:10]
    paginator = Paginator(activities_list, 10)
    activities = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'accounts/admin_board.html', {'activities': activities})

@login_required
def logout_view(request):
    log_activity(request.user, 'LOGOUT', level='INFO', log='Logout.')
    logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    if request.method == 'POST':
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user_profile.timezone = request.POST['timezone']
        user.save()
        user_profile.save()
        messages.success(request, 'Profile updated successfully.')
    return render(request, 'accounts/profile.html', {'form': ProfileForm({'first_name': request.user.first_name, 'last_name': request.user.last_name, 'email': request.user.email, 'timezone': user_profile.timezone})})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if user.check_password(old_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully.')
                log_activity(user.username,'UPDATE', level='INFO', log='Password changed.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'New password and confirm password do not match.')
        else:
            messages.error(request, 'Invalid old password.')
            
    return render(request, 'accounts/password_change.html', {'form': PasswordChangeForm()})

@csrf_exempt
@api_auth(required=True)
@require_POST
def api_create_user(request):
    # Only superusers can create users
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden. Superuser required.'}, status=403)

    # Parse input
    data = request.POST or request.body
    if hasattr(data, 'decode'):
        import json
        try:
            data = json.loads(data.decode())
        except Exception:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    
    username = data.get('username')
    email = data.get('email')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    enabled = data.get('enabled', True)
    generate_api_key = data.get('generate_api_key', False)

    # Validate required fields
    if not username or not email:
        return JsonResponse({'error': 'username and email are required.'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists.'}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already exists.'}, status=400)

    # Generate random password
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    user.is_active = bool(enabled)
    user.save()

    # Optionally generate API key
    api_key_value = None
    if generate_api_key:
        api_key = ApiKey(user=user, application='default')
        api_key.save()
        api_key_value = api_key.key

    # Log activity
    log_activity(request.user.username, 'CREATE', log=f'Created user {username}')

    # Prepare response
    response = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'enabled': user.is_active,
        'password': password,
    }
    if api_key_value:
        response['api_key'] = api_key_value
    return JsonResponse(response, status=201)

@api_auth(required=True)
@csrf_exempt  # For API use, since we use API key auth
def api_user_groups(request):
    """
    API endpoint for superusers to manage user-group membership.
    - GET: List all groups for a user (by username or user_id)
    - POST: Add a user to a group (requires username and group name)
    - DELETE: Remove a user from a group (requires username and group name)
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden. Superuser required.'}, status=403)

    # Helper to get user by username or id
    def get_user_from_request(data):
        username = data.get('username')
        user_id = data.get('user_id')
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                return None
        elif user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                return None
        return None

    # Parse input data for POST/DELETE
    if request.method in ['POST', 'DELETE']:
        if request.content_type == 'application/json':
            import json
            try:
                data = json.loads(request.body.decode())
            except Exception:
                return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        else:
            data = request.POST
    else:
        data = request.GET

    # GET: List all groups for a user
    if request.method == 'GET':
        user = get_user_from_request(data)
        if not user:
            return JsonResponse({'error': 'User not found.'}, status=404)
        groups = list(user.groups.values_list('name', flat=True))
        return JsonResponse({'username': user.username, 'groups': groups})

    # POST: Add user to group
    if request.method == 'POST':
        user = get_user_from_request(data)
        group_name = data.get('group')
        if not user or not group_name:
            return JsonResponse({'error': 'username (or user_id) and group are required.'}, status=400)
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        user.save()
        log_activity(request.user.username, 'UPDATE', log=f'Added user {user.username} to group {group_name}')
        return JsonResponse({'success': True, 'message': f'User {user.username} added to group {group_name}.'})

    # DELETE: Remove user from group
    if request.method == 'DELETE':
        user = get_user_from_request(data)
        group_name = data.get('group')
        if not user or not group_name:
            return JsonResponse({'error': 'username (or user_id) and group are required.'}, status=400)
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return JsonResponse({'error': 'Group not found.'}, status=404)
        user.groups.remove(group)
        user.save()
        log_activity(request.user.username, 'UPDATE', log=f'Removed user {user.username} from group {group_name}')
        return JsonResponse({'success': True, 'message': f'User {user.username} removed from group {group_name}.'})

    # Method not allowed
    return JsonResponse({'error': 'Method not allowed.'}, status=405)