from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin_board/', views.admin_board_view, name='admin_board'),
    path('password/change/', views.password_change_view, name='password_change'),
    path('key/', views.api_key_view, name='api_keys'),
    path('key/create/', views.api_key_create, name='api_key_create'),
    path('key/deactivate/<str:key>/', views.api_key_deactivate, name='api_key_disable'),
    path('key/activate/<str:key>/', views.api_key_activate, name='api_key_enable'),
    path('key/delete/<str:key>/', views.api_key_delete, name='api_key_delete'),
]