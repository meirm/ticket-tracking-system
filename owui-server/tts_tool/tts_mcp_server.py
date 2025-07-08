#!/usr/bin/env python3
"""
TTS MCP Server
A Model Context Protocol server for the Ticket Tracking System using FastMCP.
Reuses the existing TTSClient class for API communication.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from tts_client import TTSClient
from models import TicketCreateRequest, TicketUpdateRequest, CommentCreateRequest, SummaryCreateRequest, SummaryUpdateRequest
import json

# Initialize FastMCP server
mcp = FastMCP("TTS")

# Initialize TTS client
TTS_API_URL = os.getenv("TTS_API_URL", "https://tts.cyborg.fi/tickets/api/v1/")
TTS_API_TOKEN = os.getenv("TTS_API_TOKEN", "")

if not TTS_API_URL or not TTS_API_TOKEN:
    raise ValueError("TTS_API_URL and TTS_API_TOKEN environment variables must be set")

# Global TTS client instance
tts_client = TTSClient(TTS_API_URL, TTS_API_TOKEN)

# --- Core Ticket Operations ---

@mcp.tool
def list_tickets(
    assignee: Optional[str] = None,
    status: Optional[str] = None, 
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List tickets with optional filtering.
    
    Args:
        assignee: Filter by assignee username
        status: Filter by status name
        category: Filter by category name
        priority: Filter by priority name
        limit: Maximum number of tickets to return
        offset: Number of tickets to skip
        
    Returns:
        Dictionary containing tickets list and metadata
    """
    params = {"limit": limit, "offset": offset}
    
    if assignee:
        params["assignee"] = assignee
    if status:
        params["status"] = status
    if category:
        params["category"] = category
    if priority:
        params["priority"] = priority
        
    return tts_client.list_tickets(params)

@mcp.tool
def search_tickets(
    q: str,
    scope: Optional[str] = None,
    assignee: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search tickets by query string with optional filtering.
    
    Args:
        q: Search query string
        scope: Search scope (e.g., 'title', 'description', 'all')
        assignee: Filter by assignee username
        status: Filter by status name
        category: Filter by category name
        priority: Filter by priority name
        limit: Maximum number of tickets to return
        offset: Number of tickets to skip
        
    Returns:
        Dictionary containing search results and metadata
    """
    params = {"q": q, "limit": limit, "offset": offset}
    
    if scope:
        params["scope"] = scope
    if assignee:
        params["assignee"] = assignee
    if status:
        params["status"] = status
    if category:
        params["category"] = category
    if priority:
        params["priority"] = priority
        
    return tts_client.search_tickets(params)

@mcp.tool
def get_ticket(ticket_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific ticket.
    
    Args:
        ticket_id: The unique integer ID of the ticket
        
    Returns:
        Dictionary containing ticket details
    """
    return tts_client.get_ticket(ticket_id)

@mcp.tool
def create_ticket(
    title: str,
    description: str,
    assignee_id: Optional[int] = None,
    category_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    status_id: Optional[int] = None,
    group_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a new ticket.
    
    Args:
        title: Ticket title
        description: Ticket description
        assignee_id: ID of the assigned user
        category_id: ID of the ticket category
        priority_id: ID of the ticket priority
        status_id: ID of the ticket status
        group_id: ID of the assigned group
        
    Returns:
        Dictionary containing created ticket details
    """
    ticket_data = {
        "title": title,
        "description": description
    }
    
    if assignee_id:
        ticket_data["assignee_id"] = assignee_id
    if category_id:
        ticket_data["category_id"] = category_id
    if priority_id:
        ticket_data["priority_id"] = priority_id
    if status_id:
        ticket_data["status_id"] = status_id
    if group_id:
        ticket_data["group_id"] = group_id
        
    return tts_client.create_ticket(ticket_data)

@mcp.tool
def update_ticket(
    ticket_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assignee_id: Optional[int] = None,
    category_id: Optional[int] = None,
    priority_id: Optional[int] = None,
    status_id: Optional[int] = None,
    group_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Update an existing ticket.
    
    Args:
        ticket_id: The unique integer ID of the ticket to update
        title: New ticket title
        description: New ticket description
        assignee_id: ID of the assigned user
        category_id: ID of the ticket category
        priority_id: ID of the ticket priority
        status_id: ID of the ticket status
        group_id: ID of the assigned group
        
    Returns:
        Dictionary containing updated ticket details
    """
    update_data = {}
    
    if title:
        update_data["title"] = title
    if description:
        update_data["description"] = description
    if assignee_id:
        update_data["assignee_id"] = assignee_id
    if category_id:
        update_data["category_id"] = category_id
    if priority_id:
        update_data["priority_id"] = priority_id
    if status_id:
        update_data["status_id"] = status_id
    if group_id:
        update_data["group_id"] = group_id
        
    return tts_client.update_ticket(ticket_id, update_data)

@mcp.tool
def delete_ticket(ticket_id: int) -> Dict[str, Any]:
    """
    Delete a ticket.
    
    Args:
        ticket_id: The unique integer ID of the ticket to delete
        
    Returns:
        Dictionary containing deletion result
    """
    return tts_client.delete_ticket(ticket_id)

@mcp.tool
def close_ticket(ticket_id: int) -> Dict[str, Any]:
    """
    Close a ticket by setting its status to 'Closed'.
    
    Args:
        ticket_id: The unique integer ID of the ticket to close
        
    Returns:
        Dictionary containing updated ticket details
    """
    return tts_client.close_ticket(ticket_id)

@mcp.tool
def batch_close_tickets(ticket_ids: List[int]) -> Dict[str, Any]:
    """
    Close multiple tickets at once.
    
    Args:
        ticket_ids: List of ticket IDs to close
        
    Returns:
        Dictionary containing batch operation results
    """
    return tts_client.batch_close_tickets(ticket_ids)

@mcp.tool
def add_comment(ticket_id: int, text: str) -> Dict[str, Any]:
    """
    Add a comment to a ticket.
    
    Args:
        ticket_id: The unique integer ID of the ticket
        text: Comment text
        
    Returns:
        Dictionary containing created comment details
    """
    return tts_client.add_comment(ticket_id, text)

# --- Reference Data Operations ---

@mcp.tool
def list_users(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    List all users in the system.
    
    Args:
        limit: Maximum number of users to return
        offset: Number of users to skip
        
    Returns:
        Dictionary containing users list and metadata
    """
    return tts_client.list_users(limit, offset)

@mcp.tool
def list_categories(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    List all ticket categories.
    
    Args:
        limit: Maximum number of categories to return
        offset: Number of categories to skip
        
    Returns:
        Dictionary containing categories list and metadata
    """
    return tts_client.list_categories(limit, offset)

@mcp.tool
def list_priorities(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    List all ticket priorities.
    
    Args:
        limit: Maximum number of priorities to return
        offset: Number of priorities to skip
        
    Returns:
        Dictionary containing priorities list and metadata
    """
    return tts_client.list_priorities(limit, offset)

@mcp.tool
def list_statuses(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    List all ticket statuses.
    
    Args:
        limit: Maximum number of statuses to return
        offset: Number of statuses to skip
        
    Returns:
        Dictionary containing statuses list and metadata
    """
    return tts_client.list_statuses(limit, offset)

@mcp.tool
def list_groups(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    List all groups in the system.
    
    Args:
        limit: Maximum number of groups to return
        offset: Number of groups to skip
        
    Returns:
        Dictionary containing groups list and metadata
    """
    return tts_client.list_groups(limit, offset)

# --- User and Group Operations ---

@mcp.tool
def get_user_groups(username: str) -> Dict[str, Any]:
    """
    Get all groups for a specific user.
    
    Args:
        username: Username to look up
        
    Returns:
        Dictionary containing user's groups
    """
    return tts_client.get_user_groups(username)

@mcp.tool
def get_group_members(group_name: str) -> Dict[str, Any]:
    """
    Get all members of a specific group.
    
    Args:
        group_name: Name of the group
        
    Returns:
        Dictionary containing group members
    """
    return tts_client.get_group_members(group_name)

# --- Summary Operations ---

@mcp.tool
def list_summaries(archived: Optional[bool] = None) -> Dict[str, Any]:
    """
    List summaries with optional filtering by archived status.
    
    Args:
        archived: Filter by archived status (True/False/None for all)
        
    Returns:
        Dictionary containing summaries list and metadata
    """
    params = {}
    if archived is not None:
        params["archived"] = archived
    return tts_client.list_summaries(params)

@mcp.tool
def create_summary(
    title: str,
    content: str,
    archived: bool = False
) -> Dict[str, Any]:
    """
    Create a new summary.
    
    Args:
        title: Summary title
        content: Summary content
        archived: Whether the summary is archived
        
    Returns:
        Dictionary containing created summary details
    """
    summary_data = {
        "title": title,
        "content": content,
        "archived": archived
    }
    return tts_client.create_summary(summary_data)

@mcp.tool
def get_summary(summary_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific summary.
    
    Args:
        summary_id: The unique integer ID of the summary
        
    Returns:
        Dictionary containing summary details
    """
    return tts_client.get_summary(summary_id)

@mcp.tool
def update_summary(
    summary_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    archived: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update an existing summary.
    
    Args:
        summary_id: The unique integer ID of the summary to update
        title: New summary title
        content: New summary content
        archived: New archived status
        
    Returns:
        Dictionary containing updated summary details
    """
    update_data = {}
    
    if title:
        update_data["title"] = title
    if content:
        update_data["content"] = content
    if archived is not None:
        update_data["archived"] = archived
        
    return tts_client.update_summary(summary_id, update_data)

@mcp.tool
def delete_summary(summary_id: int) -> Dict[str, Any]:
    """
    Delete a summary.
    
    Args:
        summary_id: The unique integer ID of the summary to delete
        
    Returns:
        Dictionary containing deletion result
    """
    return tts_client.delete_summary(summary_id)

@mcp.tool
def archive_all_summaries() -> Dict[str, Any]:
    """
    Archive all summaries in the system.
    
    Returns:
        Dictionary containing batch operation results
    """
    return tts_client.archive_all_summaries()

# --- Utility Functions ---

@mcp.tool
def health_check() -> Dict[str, Any]:
    """
    Check the health status of the TTS system.
    
    Returns:
        Dictionary containing health status
    """
    return tts_client.health_check()

@mcp.tool
def get_profile() -> Dict[str, Any]:
    """
    Get the current user's profile information.
    
    Returns:
        Dictionary containing user profile
    """
    return tts_client.get_profile()

# --- Helper Functions ---

def run_server():
    """Run the MCP server."""
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down TTS MCP server...")
    except Exception as e:
        print(f"Error running server: {e}")
        raise

if __name__ == "__main__":
    run_server()