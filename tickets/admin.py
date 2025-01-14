from django.contrib import admin

# Register your models here.
from .models import Ticket, Comment, Category, Priority, Status

admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Priority)
admin.site.register(Status)