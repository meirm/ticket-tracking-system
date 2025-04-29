from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

# This signal handler will automatically create a UserProfile
# whenever a new User is created.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a UserProfile for the new user
        UserProfile.objects.create(user=instance)

# This signal handler ensures that the UserProfile is saved
# whenever the User is saved (optional, but good practice)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save() 