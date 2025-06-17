from django.urls import path
from . import views

app_name = 'tickets'
urlpatterns = [
    
    path('', views.index, name='index'),
    path('pull/', views.pull_request, name='pull_request'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('summary/', views.summary_view, name='summary'),
    path('in_progress', views.in_progress_view, name='in_progress'),
    path("help/", views.help_view, name="view_help"),
    path("privacy/", views.privacy_view, name="view_privacy"),
    path("terms/", views.terms_view, name="view_terms"),
    path('issues/', views.list_issues, name='list_issues'),
    path('changes/', views.view_changes, name='view_changes'),
    path("my/", views.my_tasks, name="my_tasks"),
    path('search/', views.search_tickets, name='search_tickets'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('new/', views.new_ticket, name='new_ticket'),
    path('closed/', views.list_closed_tickets, name='list_closed_tickets'),
    path('hidden/', views.list_hidden_tickets, name='list_hidden_tickets'),
    path('<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
    path('<int:ticket_id>/hide/', views.hide_ticket, name='hide_ticket'),
    path('<int:ticket_id>/unhide/', views.unhide_ticket, name='unhide_ticket'),
    path('<int:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    path('<int:ticket_id>/comment/', views.new_comment, name='new_comment'),
    path('<int:ticket_id>/comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('<int:ticket_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<int:ticket_id>/upvote/', views.upvote_ticket, name='upvote_ticket'),
    path('<int:ticket_id>/downvote/', views.downvote_ticket, name='downvote_ticket'),
    path('<int:ticket_id>/comment/<int:comment_id>/upvote/', views.upvote_comment, name='upvote_comment'),
    path('<int:ticket_id>/comment/<int:comment_id>/downvote/', views.downvote_comment, name='downvote_comment'),
    # Add api urls
    path('api/v1/list/', views.api_list_tickets, name='api_ticket_list'),
    path('api/v1/detail/<int:ticket_id>/', views.api_ticket_detail, name='api_ticket_detail'),
    path('api/v1/edit/<int:ticket_id>/', views.api_ticket_edit, name='api_ticket_edit'),
    path('api/v1/create/', views.api_ticket_create, name='api_ticket_create'),
    path('api/v1/add_comment/<int:ticket_id>/', views.api_add_comment, name='api_ticket_add_comment'),
    path('api/v1/search/', views.api_search_tickets, name='api_search_tickets'),
    path('api/v1/batch_close/', views.api_batch_close_tickets, name='api_batch_close_tickets'),
    path('api/v1/load-users/', views.load_users, name='ajax_load_users'),
    # Batch close tickets API
    path('api/v1/batch_close/', views.api_batch_close_tickets, name='api_batch_close_tickets'),
    # --- Added API endpoints for FastAPI proxy compatibility ---
    path('api/v1/categories/', views.api_list_categories, name='api_list_categories'),
    path('api/v1/priorities/', views.api_list_priorities, name='api_list_priorities'),
    path('api/v1/statuses/', views.api_list_statuses, name='api_list_statuses'),
    path('api/v1/profile/', views.api_profile, name='api_profile'),
    path('api/v1/users/<int:user_id>/', views.api_user_detail, name='api_user_detail'),
    path('api/v1/assignees/', views.api_list_assignees, name='api_list_assignees'),
    # API for summaries
    path('api/v1/summaries/', views.api_summaries, name='api_summaries'),
    path('api/v1/summaries/<int:summary_id>/', views.api_summary_instance, name='api_summary_instance'),
    path('api/v1/summaries/archive_all/', views.api_archive_all_summaries, name='api_archive_all_summaries'),
]
