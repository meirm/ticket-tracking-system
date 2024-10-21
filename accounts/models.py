from django.db import models

# Create your models here.
class Activity(models.Model):
    class meta:
        verbose_name_plural = 'Activities'
    class Type(models.TextChoices):
        LOGIN = 'LOGIN'
        LOGOUT = 'LOGOUT'
        CREATE = 'CREATE'
        UPDATE = 'UPDATE'
        DELETE = 'DELETE'
    class Level(models.TextChoices):
        INFO = 'INFO'
        WARNING = 'WARNING'
        ERROR = 'ERROR'
        DEBUG = 'DEBUG'
    user = models.CharField(max_length=16, default='SYSTEM')
    action = models.CharField(max_length=128, choices=Type.choices)
    level = models.CharField(max_length=11, choices=Level.choices, default=Level.INFO)
    log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    