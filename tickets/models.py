from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    


# Create your models here.
class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW'
        MEDIUM = 'MEDIUM'
        HIGH = 'HIGH'
    class Category(models.TextChoices):
        BUG = 'BUG'
        FEATURE = 'FEATURE'
        SUPPORT = 'SUPPORT'
    class Status(models.TextChoices):
        DRAFT = 'DRAFT'
        OPEN = 'OPEN'
        IN_PROGRESS = 'IN PROGRESS'
        RESOLVED = 'RESOLVED'
        CLOSED = 'CLOSED'
        CANCELLED = 'CANCELLED'
    issuer = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='issued_tickets')
    assignee = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='assignee_tickets')
    priority = models.CharField(max_length=6, choices=Priority.choices, default=Priority.LOW)
    category = models.CharField(max_length=7, choices=Category.choices, default=Category.FEATURE)
    status = models.CharField(max_length=11, choices=Status.choices, default=Status.DRAFT)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    hidden = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.comment
    

class Changes(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='changes')
    actor = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.change