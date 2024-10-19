from django.contrib import admin

# Register your models here.
from .models import Ticket, Comment

admin.site.register(Ticket)
admin.site.register(Comment)