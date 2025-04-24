# Ticket Tracking System - API Integration Guide

## Overview
The Ticket Tracking System provides a comprehensive REST API that enables AI agents to interact with the ticketing system programmatically. This document outlines the available endpoints, authentication method, and example usage for AI agent integration.

## Authentication
All API endpoints require authentication using an API key.

### API Key Header
Include the API key in the request header:
```
X-API-AUTH: your_api_key_here
```

### Alternative Query Parameter
Alternatively, include the API key as a query parameter:
```
?api_key=your_api_key_here
```

## Available Endpoints

### 1. List Tickets
**Endpoint:** `GET /tickets/api/v1/list/`

Lists all non-hidden and non-closed tickets.

**Query Parameters:**
- `status`: Filter by status (comma-separated)
- `priority`: Filter by priority (comma-separated)
- `from_date`: Filter by creation date (start)
- `to_date`: Filter by creation date (end)
- `due_date`: Filter by due date (comma-separated)
- `assignee`: Filter by assignee username (comma-separated)
- `issuer`: Filter by issuer username (comma-separated)

**Response Example:**
```json
{
  "tickets": [
    {
      "id": 1,
      "issuer": "username",
      "title": "Ticket Title",
      "status": "Open",
      "priority": "High",
      "category": "Support",
      "assignee": "assignee_username",
      "created_at": "2024-03-21T10:00:00Z",
      "updated_at": "2024-03-21T10:30:00Z",
      "due_date": "2024-03-28T10:00:00Z"
    }
  ]
}
```

### 2. Get Ticket Details
**Endpoint:** `GET /tickets/api/v1/detail/<ticket_id>/`

Retrieves detailed information about a specific ticket, including comments.

**Response Example:**
```json
{
  "id": 1,
  "title": "Ticket Title",
  "description": "Ticket Description",
  "status": "Open",
  "priority": "High",
  "category": "Support",
  "assignee": "username",
  "created_at": "2024-03-21T10:00:00Z",
  "updated_at": "2024-03-21T10:30:00Z",
  "comments": [
    {
      "id": 1,
      "author": "username",
      "comment": "Comment text",
      "created_at": "2024-03-21T10:15:00Z",
      "upvotes": 0,
      "downvotes": 0
    }
  ]
}
```

### 3. Create Ticket
**Endpoint:** `POST /tickets/api/v1/create/`

Creates a new ticket.

**Request Body (JSON):**
```json
{
  "title": "Ticket Title",
  "description": "Ticket Description",
  "priority": "Low",
  "status": "Open",
  "category": "Support",
  "assigned_group": "Group Name",
  "assignee": "username",
  "due_date": "2024-03-28T10:00:00Z"
}
```

**Response:**
```json
{
  "ticket_id": 1
}
```

### 4. Edit Ticket
**Endpoint:** `POST /tickets/api/v1/edit/<ticket_id>/`

Updates an existing ticket.

**Request Body (Form Data):**
- `title`: New title
- `description`: New description
- `status`: New status
- `priority`: New priority
- `category`: New category
- `assignee`: New assignee ID
- `due_date`: New due date

**Response:**
```json
{
  "ticket_id": 1,
  "actions": ["Title: Old Title -> New Title", "Status: Open -> In Progress"],
  "success": true
}
```

### 5. Add Comment
**Endpoint:** `POST /tickets/api/v1/add_comment/<ticket_id>/`

Adds a comment to an existing ticket.

**Request Body (Form Data):**
- `comment`: Comment text

**Response:**
```json
{
  "ticket_id": 1
}
```

## Error Handling
All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 401: Unauthorized (invalid or missing API key)
- 404: Not Found (ticket doesn't exist)

Error responses include a JSON object with an error message:
```json
{
  "error": "Error message description"
}
```

## AI Agent Integration Tips

1. **Authentication Flow**
   - Generate an API key through the web interface
   - Store the API key securely
   - Include the API key in all requests

2. **Common Operations**
   - Monitor tickets: Poll the list endpoint with appropriate filters
   - Update tickets: Use the edit endpoint to update status/priority
   - Communicate: Add comments through the comment endpoint

3. **Best Practices**
   - Implement rate limiting in your agent
   - Handle errors gracefully
   - Log all API interactions
   - Validate input before sending requests

4. **Example Python Code**
```python
import requests

API_BASE_URL = "http://your-tts-instance/tickets/api/v1"
API_KEY = "your_api_key_here"

headers = {
    "X-API-AUTH": API_KEY,
    "Content-Type": "application/json"
}

# List tickets
response = requests.get(f"{API_BASE_URL}/list/", headers=headers)
tickets = response.json()["tickets"]

# Create ticket
ticket_data = {
    "title": "AI Generated Ticket",
    "description": "This ticket was created by an AI agent",
    "priority": "Medium",
    "status": "Open",
    "category": "Support"
}
response = requests.post(f"{API_BASE_URL}/create/", 
                        json=ticket_data, 
                        headers=headers)
```

## Limitations and Considerations
1. PATCH operations are not supported - use PUT/POST instead
2. All dates should be in ISO 8601 format
3. The API is rate-limited (limits not specified)
4. Some operations may require specific user permissions
5. File attachments are not supported through the API 