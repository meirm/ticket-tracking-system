import requests
import sys
import json

class UserGroupManager:
    """
    Helper class to manage user-group membership via the API.
    Usage:
        mgr = UserGroupManager(api_url, superuser_api_key)
        mgr.view_groups(username)
        mgr.add_to_group(username, group)
        mgr.remove_from_group(username, group)
    """
    def __init__(self, api_url, superuser_api_key):
        self.api_url = api_url
        self.api_key = superuser_api_key
        self.headers = {
            'X-API-AUTH': self.api_key,
            'Content-Type': 'application/json',
        }

    def view_groups(self, username):
        """View all groups for a user."""
        params = {'username': username}
        response = requests.get(self.api_url, headers={'X-API-AUTH': self.api_key}, params=params)
        try:
            return response.status_code, response.json()
        except Exception:
            return response.status_code, response.text

    def add_to_group(self, username, group):
        """Add a user to a group."""
        payload = {'username': username, 'group': group}
        response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
        try:
            return response.status_code, response.json()
        except Exception:
            return response.status_code, response.text

    def remove_from_group(self, username, group):
        """Remove a user from a group."""
        payload = {'username': username, 'group': group}
        response = requests.delete(self.api_url, headers=self.headers, data=json.dumps(payload))
        try:
            return response.status_code, response.json()
        except Exception:
            return response.status_code, response.text

if __name__ == "__main__":
    # Usage instructions
    usage = (
        "Usage:\n"
        "  python sample_user_groups.py view <username>\n"
        "  python sample_user_groups.py add <username> <group>\n"
        "  python sample_user_groups.py remove <username> <group>\n"
        "\nReplace <SUPERUSER_API_KEY> with your actual API key in the script.\n"
    )

    # Set the API endpoint URL (change if your server is running elsewhere)
    API_URL = "http://localhost:8000/accounts/api_user_groups/"
    # Set your superuser API key here
    SUPERUSER_API_KEY = "<SUPERUSER_API_KEY>"  # <-- Replace with your actual superuser API key

    if len(sys.argv) < 3:
        print(usage)
        sys.exit(1)

    action = sys.argv[1]
    username = sys.argv[2]
    group = sys.argv[3] if len(sys.argv) > 3 else None

    mgr = UserGroupManager(API_URL, SUPERUSER_API_KEY)

    if action == 'view':
        status, result = mgr.view_groups(username)
    elif action == 'add':
        if not group:
            print("Group name required for add action.")
            print(usage)
            sys.exit(1)
        status, result = mgr.add_to_group(username, group)
    elif action == 'remove':
        if not group:
            print("Group name required for remove action.")
            print(usage)
            sys.exit(1)
        status, result = mgr.remove_from_group(username, group)
    else:
        print(f"Unknown action: {action}")
        print(usage)
        sys.exit(1)

    print(f"Status: {status}")
    print("Response:")
    print(result) 