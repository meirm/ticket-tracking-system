from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile

# Create your tests here.

class UserProfileSignalTest(TestCase):
    def test_userprofile_created_on_user_creation(self):
        # Create a new user
        user = User.objects.create_user(username='testuser', password='testpass')
        # Try to get the related UserProfile
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = None
        # Assert that the UserProfile was created
        self.assertIsNotNone(profile, "UserProfile should be created automatically when a User is created.")
        # Assert that the profile is linked to the correct user
        self.assertEqual(profile.user, user, "UserProfile should be linked to the correct User.")

        # Optional: check default timezone
        self.assertEqual(profile.timezone, 'UTC', "Default timezone should be 'UTC'.")

# This test ensures that the post_save signal for User correctly creates a UserProfile.
