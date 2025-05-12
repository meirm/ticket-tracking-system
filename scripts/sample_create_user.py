import requests
import json

class UserCreator:
    """
    A helper class to create a new user via the API.
    Usage:
        creator = UserCreator(api_url, superuser_api_key)
        response = creator.create_user(username, email, first_name, last_name, enabled, generate_api_key)
    """
    def __init__(self, api_url, superuser_api_key):
        """
        Initialize with the API endpoint and superuser API key.
        """
        self.api_url = api_url
        self.api_key = superuser_api_key

    def create_user(self, username, email, first_name='', last_name='', enabled=True, generate_api_key=False):
        """
        Create a new user with the given details.
        Returns the API response as a dict.
        """
        headers = {
            'X-API-AUTH': self.api_key,  # API key for authentication (must be a superuser)
            'Content-Type': 'application/json',
        }
        payload = {
            'username': username,           # Required
            'email': email,                 # Required
            'first_name': first_name,       # Optional
            'last_name': last_name,         # Optional
            'enabled': enabled,             # Optional (default: True)
            'generate_api_key': generate_api_key,  # Optional (default: False)
        }
        response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
        try:
            return response.status_code, response.json()
        except Exception:
            return response.status_code, response.text

if __name__ == "__main__":
    # Example usage
    # Set the API endpoint URL (change if your server is running elsewhere)
    API_URL = "http://localhost:8000/accounts/api_create_user/"
    # Set your superuser API key here
    SUPERUSER_API_KEY = "<SUPERUSER_API_KEY>"  # <-- Replace with your actual superuser API key

    # Set the new user's details
    NEW_USERNAME = "newuser"           # Required
    NEW_EMAIL = "newuser@example.com"  # Required
    FIRST_NAME = "New"                 # Optional
    LAST_NAME = "User"                 # Optional
    ENABLED = True                     # Optional
    GENERATE_API_KEY = True            # Optional

    # Create the UserCreator instance
    creator = UserCreator(API_URL, SUPERUSER_API_KEY)
    # Call the API to create the user
    status, result = creator.create_user(
        username=NEW_USERNAME,
        email=NEW_EMAIL,
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        enabled=ENABLED,
        generate_api_key=GENERATE_API_KEY
    )
    # Print the result
    print(f"Status: {status}")
    print("Response:")
    print(result) 