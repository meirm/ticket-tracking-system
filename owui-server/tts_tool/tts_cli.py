#! /usr/bin/env python3

import typer
app = typer.Typer()
import dotenv
dotenv.load_dotenv()
import os
from models import TicketCreateRequest, TicketUpdateRequest
from tts_client import TTSClient
import json  # For pretty-printing JSON output
import requests
from urllib.parse import urljoin

TTS_API_URL = os.getenv("TTS_API_URL")
TTS_API_TOKEN = os.getenv("TTS_API_TOKEN")
client = TTSClient(TTS_API_URL, TTS_API_TOKEN)

@app.command()
def list_tickets(assignee: str = None, status: str = None):
    """List tickets, optionally filtered by assignee or status."""
    params = {}
    if assignee:
        params["assignee"] = assignee
    if status:
        params["status"] = status
    try:
        data = client.list_tickets(params)
        tickets = data.get("tickets", [])
        for t in tickets:
            typer.echo(f"#{t.get('id')}: {t.get('title')} (Status: {t.get('status')})")
    except Exception as e:
        typer.echo(f"Error listing tickets: {e}")

@app.command()
def create_ticket(
    title: str,
    description: str,
    assignee: str = typer.Option("meir", help="Assignee username (default: meir)"),
    category: str = typer.Option("Support", help="Category name (default: Support)"),
    priority: str = typer.Option("Medium", help="Priority name (default: Medium)"),
    status: str = typer.Option("Open", help="Status name (default: Open)"),
    group: str = typer.Option(..., help="Group name (required)")
):
    """
    Create a new ticket. Uses human-friendly names for assignee, category, priority, status, and group.
    Group is required.
    """
    # Helper to map names to IDs (case-insensitive)
    def get_id_by_name(list_func, name, key="name"):
        data = list_func()
        for item in data.get("results", []):
            if item[key].strip().lower() == name.strip().lower():
                return item["id"]
        typer.echo(f"[ERROR] No match for {name} in {key}s.")
        raise typer.Exit(1)

    # Validate assignee exists
    def validate_user(username):
        data = client.list_users()
        for user in data.get("results", []):
            if user["username"].strip().lower() == username.strip().lower():
                return user["username"]
        typer.echo(f"[ERROR] No user found with username: {username}")
        raise typer.Exit(1)

    # Map group name to ID (if provided)
    def get_group_id(groupname):
        data = client.list_groups()
        for g in data.get("results", []):
            if g["name"].strip().lower() == groupname.strip().lower():
                return g["id"]
        typer.echo(f"[ERROR] No group found with name: {groupname}")
        raise typer.Exit(1)

    assignee_validated = validate_user(assignee)

    group_id = get_group_id(group)

    payload = {
        "title": title,
        "description": description,
        "assignee": assignee_validated,  # Use the username directly
        "category": client.id_to_name("categories", get_id_by_name(client.list_categories, category)),
        "priority": client.id_to_name("priorities", get_id_by_name(client.list_priorities, priority)),
        "status": client.id_to_name("statuses", get_id_by_name(client.list_statuses, status)),
        "assigned_group": client.id_to_group_name(group_id),
    }
    typer.echo("[DEBUG] Payload to be sent:")
    typer.echo(payload)
    try:
        result = client.create_ticket(payload)
        typer.echo(f"Created ticket #{result.get('ticket_id')}")
    except Exception as e:
        typer.echo(f"Error creating ticket: {e}")

@app.command()
def get_ticket(ticket_id: int):
    """Get details for a ticket by ID."""
    try:
        ticket = client.get_ticket(ticket_id)
        # Pretty-print the ticket JSON for better readability
        typer.echo(json.dumps(ticket, indent=2))
    except Exception as e:
        typer.echo(f"Error getting ticket: {e}")

@app.command()
def update_ticket(ticket_id: int, title: str = None, description: str = None):
    """Update a ticket's title or description."""
    payload = {}
    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    # If no fields provided, warn the user and show available options
    if not payload:
        typer.echo("No fields provided to update. Please specify at least one field to change.")
        typer.echo("Available fields to update: --title, --description")
        typer.echo("Example: ./tts_cli.py update-ticket <ticket_id> --title 'New Title' --description 'New description'")
        return
    try:
        result = client.update_ticket(ticket_id, payload)
        typer.echo(f"Updated ticket #{ticket_id}")
    except Exception as e:
        typer.echo(f"Error updating ticket: {e}")

@app.command()
def delete_ticket(ticket_id: int):
    """Delete a ticket by ID."""
    try:
        client.delete_ticket(ticket_id)
        typer.echo(f"Deleted ticket #{ticket_id}")
    except Exception as e:
        typer.echo(f"Error deleting ticket: {e}")

@app.command()
def list_users():
    """List all users."""
    try:
        data = client.list_users()
        for user in data.get("results", []):
            typer.echo(f"{user['id']}: {user['username']} ({user.get('email', '-')})")
    except Exception as e:
        typer.echo(f"Error listing users: {e}")

@app.command()
def list_categories():
    """List all categories."""
    try:
        data = client.list_categories()
        for cat in data.get("results", []):
            typer.echo(f"{cat['id']}: {cat['name']}")
    except Exception as e:
        typer.echo(f"Error listing categories: {e}")

@app.command()
def list_priorities():
    """List all priorities."""
    try:
        data = client.list_priorities()
        for p in data.get("results", []):
            typer.echo(f"{p['id']}: {p['name']}")
    except Exception as e:
        typer.echo(f"Error listing priorities: {e}")

@app.command()
def list_statuses():
    """List all statuses."""
    try:
        data = client.list_statuses()
        for s in data.get("results", []):
            typer.echo(f"{s['id']}: {s['name']}")
    except Exception as e:
        typer.echo(f"Error listing statuses: {e}")

@app.command()
def list_groups():
    """List all groups."""
    try:
        data = client.list_groups()
        for g in data.get("results", []):
            typer.echo(f"{g['id']}: {g['name']}")
    except Exception as e:
        typer.echo(f"Error listing groups: {e}")

def get_accounts_base_url():
    """Derive the accounts API base URL from TTS_API_URL."""
    if not TTS_API_URL:
        raise RuntimeError("TTS_API_URL must be set in the environment.")
    base_url = TTS_API_URL.split('/tickets')[0]
    return urljoin(base_url, '/accounts/')

@app.command()
def test_accounts_url():
    """Test and print the derived accounts API base URL."""
    try:
        url = get_accounts_base_url()
        typer.echo(f"Derived accounts API base URL: {url}")
    except Exception as e:
        typer.echo(f"Error: {e}")

@app.command()
def get_user_groups(username: str):
    """Get all groups for a user by username."""
    if not TTS_API_TOKEN:
        typer.echo("[ERROR] TTS_API_TOKEN must be set in the environment.")
        raise typer.Exit(1)
    url = get_accounts_base_url() + "api_user_groups/"
    headers = {"X-API-AUTH": TTS_API_TOKEN}
    params = {"username": username}
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        groups = data.get("groups", [])
        typer.echo(f"Groups for user '{username}':")
        for g in groups:
            typer.echo(f"- {g}")
    except Exception as e:
        typer.echo(f"Error fetching groups for user {username}: {e}")

@app.command()
def get_group_members(groupname: str):
    """List all users who are members of the given group."""
    import requests
    api_token = os.getenv("TTS_API_TOKEN")
    if not api_token:
        typer.echo("[ERROR] TTS_API_TOKEN must be set in the environment.")
        raise typer.Exit(1)
    url = get_accounts_base_url() + "api_group_members/"
    headers = {"X-API-AUTH": api_token}
    params = {"group": groupname}
    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 404:
            typer.echo(f"Group '{groupname}' not found.")
            return
        resp.raise_for_status()
        data = resp.json()
        members = data.get("members", [])
        if not members:
            typer.echo(f"No members found for group '{groupname}'.")
        else:
            typer.echo(f"Members of group '{groupname}':")
            for m in members:
                typer.echo(f"{m['username']} ({m.get('email', '-')})")
    except Exception as e:
        typer.echo(f"Error fetching members for group {groupname}: {e}")

if __name__ == "__main__":
    app()