#! /usr/bin/env python3

import typer
app = typer.Typer()
import dotenv
dotenv.load_dotenv()
import os
from models import TicketCreateRequest, TicketUpdateRequest
from tts_client import TTSClient
import json  # For pretty-printing JSON output

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
def create_ticket(title: str, description: str, assignee_id: int, category_id: int, priority_id: int, status_id: int, assigned_group_id: int):
    """Create a new ticket."""
    payload = {
        "title": title,
        "description": description,
        "assignee": client.id_to_username(assignee_id),
        "category": client.id_to_name("categories", category_id),
        "priority": client.id_to_name("priorities", priority_id),
        "status": client.id_to_name("statuses", status_id),
        "assigned_group": client.id_to_group_name(assigned_group_id),
    }
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

if __name__ == "__main__":
    app()