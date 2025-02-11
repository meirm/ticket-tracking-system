import hashlib
import time
from django.db import models
from django.contrib.auth.models import User
import pytz

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
    


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default='UTC'
    )

class ApiKey(models.Model):
    # the user should be able to have multiple api keys, each for different applications
    # The user can't change the key, but can deactivate it or delete it.
    # The key should be unique for each application
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    application = models.CharField(max_length=128)
    key = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    class meta:
        verbose_name_plural = 'ApiKeys'
        unique_together = ('user', 'application')
    
    def __str__(self):
        return self.key
    
    def generate_key(self):
        return hashlib.sha256((self.user.username + str(time.time())).encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)
    
    def deactivate(self):
        self.active = False
        self.save()

    def activate(self):
        self.active = True
        self.save()

    
