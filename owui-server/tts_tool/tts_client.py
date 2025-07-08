import httpx
from typing import Optional, Dict, Any, List
import os
from urllib.parse import urljoin

# TTSClient: Encapsulates all TTS API communication logic for reuse in CLI and server
class TTSClient:
    """
    Client for interacting with the Ticket Tracking System (TTS) API.
    Handles authentication and provides methods for common operations.
    """
    def __init__(self, base_url: str, api_token: str):
        """
        Initialize the client with base URL and API token.
        """
        self.base_url = base_url.rstrip("/") + "/"
        self.headers = {
            "X-API-AUTH": api_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def list_tickets(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List tickets from the TTS API. Always returns a dict with a 'tickets' key.
        """
        url = f"{self.base_url}list/"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                # If the API returns a list, wrap it
                if isinstance(data, list):
                    return {"tickets": data}
                return data
        except Exception as e:
            print(f"[ERROR] Failed to list tickets: {e}")
            raise

    def id_to_username(self, user_id: int) -> str:
        """
        Map user_id to username by querying the TTS API. Raises ValueError if not found.
        """
        url = f"{self.base_url}assignees/"
        try:
            with httpx.Client() as client:
                resp = client.get(url, headers=self.headers)
                resp.raise_for_status()
                users = resp.json().get("results", [])
                for user in users:
                    if user.get("id") == user_id:
                        return user.get("username")
        except Exception as e:
            print(f"[ERROR] Failed to map user_id {user_id} to username: {e}")
        raise ValueError(f"User ID {user_id} not found.")

    def id_to_name(self, model: str, obj_id: int) -> str:
        """
        Map an ID to a name for category, priority, or status. Raises ValueError if not found.
        """
        url = f"{self.base_url}{model}/"
        try:
            with httpx.Client() as client:
                resp = client.get(url, headers=self.headers)
                resp.raise_for_status()
                items = resp.json().get("results", [])
                for item in items:
                    if item.get("id") == obj_id:
                        return item.get("name")
        except Exception as e:
            print(f"[ERROR] Failed to map {model} id {obj_id} to name: {e}")
        raise ValueError(f"{model.title()} ID {obj_id} not found.")

    def id_to_group_name(self, group_id: int) -> str:
        """
        Map group_id to group name by querying the TTS API. Raises ValueError if not found.
        """
        url = f"{self.base_url}groups/"
        try:
            with httpx.Client() as client:
                resp = client.get(url, headers=self.headers)
                resp.raise_for_status()
                groups = resp.json().get("results", [])
                for group in groups:
                    if group.get("id") == group_id:
                        return group.get("name")
        except Exception as e:
            print(f"[ERROR] Failed to map group_id {group_id} to group name: {e}")
        raise ValueError(f"Group ID {group_id} not found.")

    def list_related_items(self, item_type: str, limit: int = 50, offset: int = 0) -> dict:
        """
        List related items (users, categories, priorities, statuses, groups) from the TTS API.
        Handles both paginated (with 'results') and non-paginated (with 'users') responses.
        """
        if item_type == "users":
            target_url = f"{self.base_url}assignees/"
        else:
            base_api_path = self.base_url if self.base_url.endswith('/') else f"{self.base_url}/"
            target_url = f"{base_api_path}{item_type}/"
        try:
            with httpx.Client() as client:
                response = client.get(target_url, headers=self.headers, params={"limit": limit, "offset": offset})
                response.raise_for_status()
                data = response.json()
                # Accept both paginated and non-paginated formats
                if isinstance(data, dict):
                    if 'results' in data and 'count' in data:
                        # Paginated format
                        return data
                    elif 'users' in data:
                        # Non-paginated user list
                        return {'results': data['users'], 'count': len(data['users'])}
                print(f"[ERROR] Unexpected response format from TTS listing {item_type}.")
                raise ValueError(f"Unexpected response format from TTS listing {item_type}.")
        except Exception as e:
            print(f"[ERROR] Failed to list related items for {item_type}: {e}")
            raise

    def search_tickets(self, params: Dict[str, Any]) -> dict:
        """
        Search tickets by query and filters. Returns dict with 'tickets' key.
        Expects params dict with keys: q, scope, status, priority, from_date, to_date, due_date, assignee, issuer, limit, offset
        """
        url = f"{self.base_url}search/"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to search tickets: {e}")
            raise

    def create_ticket(self, payload: dict) -> dict:
        """
        Create a new ticket. Payload should contain all required fields.
        Returns the created ticket's details.
        """
        url = f"{self.base_url}create/"
        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to create ticket: {e}")
            raise

    def get_ticket(self, ticket_id: int) -> dict:
        """
        Get details for a single ticket by ID.
        """
        url = f"{self.base_url}detail/{ticket_id}/"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get ticket {ticket_id}: {e}")
            raise

    def update_ticket(self, ticket_id: int, payload: dict) -> dict:
        """
        Update an existing ticket by ID. Payload should contain fields to update.
        """
        url = f"{self.base_url}edit/{ticket_id}/"
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        try:
            with httpx.Client() as client:
                response = client.post(url, data=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to update ticket {ticket_id}: {e}")
            raise

    def delete_ticket(self, ticket_id: int) -> None:
        """
        Delete a ticket by ID. Returns None on success.
        """
        url = f"{self.base_url}tickets/{ticket_id}/"
        try:
            with httpx.Client() as client:
                response = client.delete(url, headers=self.headers)
                response.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Failed to delete ticket {ticket_id}: {e}")
            raise

    def add_comment(self, ticket_id: int, comment: str) -> dict:
        """
        Add a comment to a ticket. Returns the API response.
        """
        url = f"{self.base_url}add_comment/{ticket_id}/"
        payload = {"comment": comment}
        try:
            with httpx.Client() as client:
                response = client.post(url, data=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to add comment to ticket {ticket_id}: {e}")
            raise

    def close_ticket(self, ticket_id: int) -> dict:
        """
        Close a ticket by setting its status to 'Closed'.
        """
        url = f"{self.base_url}edit/{ticket_id}/"
        headers = self.headers.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        payload = {"status": "Closed"}
        try:
            with httpx.Client() as client:
                response = client.post(url, data=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to close ticket {ticket_id}: {e}")
            raise

    def batch_close_tickets(self, ticket_ids: list) -> dict:
        """
        Batch close tickets by IDs. Returns summary dict.
        """
        url = f"{self.base_url}batch_close/"
        payload = {"ticket_ids": ticket_ids}
        try:
            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to batch close tickets: {e}")
            raise

    def list_users(self, limit: int = 50, offset: int = 0) -> dict:
        """
        List users (assignees) from the TTS API. Returns paginated dict.
        """
        return self.list_related_items("users", limit=limit, offset=offset)

    def list_categories(self, limit: int = 50, offset: int = 0) -> dict:
        """
        List categories from the TTS API. Returns paginated dict.
        """
        return self.list_related_items("categories", limit=limit, offset=offset)

    def list_priorities(self, limit: int = 50, offset: int = 0) -> dict:
        """
        List priorities from the TTS API. Returns paginated dict.
        """
        return self.list_related_items("priorities", limit=limit, offset=offset)

    def list_statuses(self, limit: int = 50, offset: int = 0) -> dict:
        """
        List statuses from the TTS API. Returns paginated dict.
        """
        return self.list_related_items("statuses", limit=limit, offset=offset)

    def list_groups(self) -> dict:
        """
        List groups from the TTS API using the new /accounts/api_groups/ endpoint.
        """
        api_url = os.getenv("TTS_API_URL")
        api_token = os.getenv("TTS_API_TOKEN")
        if not api_url or not api_token:
            raise RuntimeError("TTS_API_URL and TTS_API_TOKEN must be set in the environment.")
        # Remove any trailing path and add /accounts/api_groups/
        base_url = api_url.split('/tickets')[0]  # up to the domain
        url = urljoin(base_url, '/accounts/api_groups/')
        headers = {"X-API-AUTH": api_token}
        try:
            import requests
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"[ERROR] Failed to list groups: {e}")
            raise

    def get_user(self, user_id: int) -> dict:
        """
        Get details for a specific user by ID.
        """
        url = f"{self.base_url}users/{user_id}/"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get user {user_id}: {e}")
            raise

    def get_profile(self) -> dict:
        """
        Get the profile of the currently authenticated user from the TTS API.
        """
        url = f"{self.base_url}profile/"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get profile: {e}")
            raise

    def update_profile(self, update_data: dict) -> dict:
        """
        Update the profile (email, first_name, last_name) of the currently authenticated user.
        """
        url = f"{self.base_url}profile/"
        try:
            with httpx.Client() as client:
                response = client.put(url, json=update_data, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to update profile: {e}")
            raise

    def list_summaries(self, params: Optional[Dict[str, Any]] = None) -> dict:
        """
        List all summaries, optionally filtered by archived status.
        """
        url = f"{self.base_url}summaries/"
        query_params = {}
        if params:
            if 'archived' in params and params['archived'] is not None:
                query_params['archived'] = str(params['archived']).lower()
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers, params=query_params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to list summaries: {e}")
            raise

    def create_summary(self, summary_data: dict) -> dict:
        """
        Create a new summary.
        """
        url = f"{self.base_url}summaries/"
        try:
            with httpx.Client() as client:
                response = client.post(url, json=summary_data, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to create summary: {e}")
            raise

    def get_summary(self, summary_id: int) -> dict:
        """
        Get details for a specific summary by ID.
        """
        url = f"{self.base_url}summaries/{summary_id}/"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get summary {summary_id}: {e}")
            raise

    def update_summary(self, summary_id: int, summary_data: dict) -> dict:
        """
        Update an existing summary by ID.
        """
        url = f"{self.base_url}summaries/{summary_id}/"
        try:
            with httpx.Client() as client:
                response = client.put(url, json=summary_data, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to update summary {summary_id}: {e}")
            raise

    def delete_summary(self, summary_id: int) -> None:
        """
        Delete a summary by ID. Returns None on success.
        """
        url = f"{self.base_url}summaries/{summary_id}/"
        try:
            with httpx.Client() as client:
                response = client.delete(url, headers=self.headers)
                response.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Failed to delete summary {summary_id}: {e}")
            raise

    def archive_all_summaries(self) -> dict:
        """
        Archive all unarchived summaries.
        """
        url = f"{self.base_url}summaries/archive_all/"
        try:
            with httpx.Client() as client:
                response = client.post(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to archive all summaries: {e}")
            raise

    def get_user_groups(self, username: str) -> dict:
        """
        Get all groups for a specific user.
        """
        # Extract base URL from tickets URL
        base_url = self.base_url.split('/tickets')[0]
        url = urljoin(base_url, '/accounts/api_user_groups/')
        headers = {"X-API-AUTH": self.headers["X-API-AUTH"]}
        params = {"username": username}
        
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params)
                if response.status_code == 404:
                    return {"error": f"User '{username}' not found."}
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get groups for user {username}: {e}")
            raise

    def get_group_members(self, group_name: str) -> dict:
        """
        Get all members of a specific group.
        """
        # Extract base URL from tickets URL
        base_url = self.base_url.split('/tickets')[0]
        url = urljoin(base_url, '/accounts/api_group_members/')
        headers = {"X-API-AUTH": self.headers["X-API-AUTH"]}
        params = {"group": group_name}
        
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=params)
                if response.status_code == 404:
                    return {"error": f"Group '{group_name}' not found."}
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get members for group {group_name}: {e}")
            raise

    def health_check(self) -> dict:
        """
        Basic health check for the TTS system.
        """
        try:
            # Simple health check by trying to list tickets with minimal params
            result = self.list_tickets({"limit": 1})
            return {"status": "ok", "message": "TTS system is healthy"}
        except Exception as e:
            return {"status": "error", "message": f"TTS system health check failed: {e}"}

# Add more methods as needed for other TTS operations

# Example usage (for CLI):
# client = TTSClient(base_url="http://localhost:8000/tickets/api/v1/", api_token="your_token")
# tickets = client.list_tickets()
# print(tickets)
