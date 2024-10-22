from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, PasswordChangeForm, ProfileForm
from .utils import log_activity
from django.core.paginator import Paginator
from .models import Activity


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
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = request.POST['email']
        user.save()
        messages.success(request, 'Profile updated successfully.')
    return render(request, 'accounts/profile.html', {'form': ProfileForm({'first_name': request.user.first_name, 'last_name': request.user.last_name, 'email': request.user.email})})


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