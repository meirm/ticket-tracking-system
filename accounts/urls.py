from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin_board/', views.admin_board_view, name='admin_board'),
    path('password/change/', views.password_change_view, name='password_change'),
]