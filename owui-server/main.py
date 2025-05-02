# servers/ticket-tracking-system/main.py
# Import necessary libraries
from fastapi import FastAPI, HTTPException, Body, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, TypeVar, Generic
import os
import httpx  # Using httpx for async HTTP requests, recommended with FastAPI

# --- Configuration ---
# Load TTS connection details from environment variables for security
TTS_API_URL = os.getenv("TTS_API_URL")
TTS_API_TOKEN = os.getenv("TTS_API_TOKEN") # Or API Key, username/password etc.

# Basic check to ensure configuration is present
if not TTS_API_URL or not TTS_API_TOKEN:
    print("ERROR: TTS_API_URL and TTS_API_TOKEN environment variables must be set.")
    # You might want to raise an exception or exit here in a real application
    # raise ValueError("TTS_API_URL and TTS_API_TOKEN environment variables must be set.")

# --- ENFORCE CORRECT BASE URL ---
# Ensure TTS_API_URL ends with '/tickets/api/v1/' for correct proxy operation
REQUIRED_SUFFIX = "/tickets/api/v1/"
if not TTS_API_URL or not TTS_API_URL.rstrip("/").endswith(REQUIRED_SUFFIX.rstrip("/")):
    print(f"WARNING: TTS_API_URL should end with '{REQUIRED_SUFFIX}'. Current value: '{TTS_API_URL}'")
    # Optionally, you can raise an error to enforce strictness:
    # raise ValueError(f"TTS_API_URL must end with '{REQUIRED_SUFFIX}' (current: '{TTS_API_URL}')")

# --- FastAPI App Initialization ---
# Rename the original app to tts_app for clarity
# This app contains all the TTS endpoints

tts_app = FastAPI(
    title="Ticket Tracking System Proxy API",
    version="1.0.0",
    description="Provides an interface to interact with an external Ticket Tracking System.",
)

# --- CORS Middleware ---
# Allow requests from web frontends
origins = ["*"]  # Adjust in production for security
tts_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
# Define data structures for requests and responses
# NOTE: Adjust these models based on the *actual* fields your TTS uses!

class TicketBase(BaseModel):
    """Base model for core ticket fields. Uses IDs for relations."""
    title: str = Field(..., description="The title of the ticket.")
    description: Optional[str] = Field(None, description="Detailed description of the ticket.")
    # Use IDs based on script payload
    priority_id: Optional[int] = Field(None, description="ID of the priority level.")
    status_id: Optional[int] = Field(None, description="ID of the current status.")
    assignee_id: Optional[int] = Field(None, description="ID of the user assigned to the ticket.")
    category_id: Optional[int] = Field(None, description="ID of the ticket category.")
    # Add other common fields as needed: tags, project, due_date, etc.

# --- User Profile Models ---
class UserProfile(BaseModel):
    """Detailed response model for a user profile."""
    id: int
    username: str # Assuming username is part of profile and usually read-only
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True) # Ensure compatibility if using ORM

# --- ADD: Model for Profile Update Request ---
class ProfileUpdateRequest(BaseModel):
    """Request model for updating the user profile. Only allowed fields."""
    email: Optional[str] = Field(None, description="New email address.")
    first_name: Optional[str] = Field(None, description="New first name.")
    last_name: Optional[str] = Field(None, description="New last name.")

# --- Helper Models for Nested Data in TicketResponse --- START
# These models match the structure observed in the API response for nested objects
# within a ticket, preventing validation errors in TicketResponse.

class _NestedCategory(BaseModel):
    id: int
    name: str

class _NestedPriority(BaseModel):
    id: int
    name: str

class _NestedStatus(BaseModel):
    id: int
    name: str
    closed: Optional[bool] = None # Field observed in ticket list response

# --- Helper Models for Nested Data in TicketResponse --- END

class TicketCreateRequest(TicketBase):
    """Request model for creating a new ticket. Inherits ID fields.
       Requires description, assignee_id, category_id, priority_id, status_id as per script.
    """
    # Make fields required for creation as per script logic
    description: str = Field(..., description="Detailed description of the ticket.")
    assignee_id: int = Field(..., description="ID of the user assigned to the ticket.")
    category_id: int = Field(..., description="ID of the ticket category.")
    priority_id: int = Field(..., description="ID of the priority level.")
    status_id: int = Field(..., description="ID of the current status.")

class TicketUpdateRequest(BaseModel):
    """Request model for updating an existing ticket. All fields are optional.
       Uses ID fields for relations.
    """
    title: Optional[str] = Field(None, description="The updated title of the ticket.")
    description: Optional[str] = Field(None, description="Updated detailed description.")
    priority_id: Optional[int] = Field(None, description="Updated ID of the priority level.")
    status_id: Optional[int] = Field(None, description="Updated ID of the status.")
    assignee_id: Optional[int] = Field(None, description="Updated ID of the assignee.")
    category_id: Optional[int] = Field(None, description="Updated ID of the ticket category.")
    # Add other updatable fields

class TicketResponse(TicketBase):
    """Response model representing a ticket. Includes system fields like ID, timestamps, and nested objects.
       Inherits basic fields from TicketBase, but uses specific nested models for related entities.
    """
    id: int = Field(..., description="Unique integer identifier of the ticket (assigned by the TTS).")
    created_at: Optional[str] = Field(None, description="Timestamp when the ticket was created.")
    updated_at: Optional[str] = Field(None, description="Timestamp when the ticket was last updated.")
    due_date: Optional[str] = Field(None, description="Optional due date for the ticket.") # Added based on CLI output

    # --- FIX: Use renamed UserProfile model ---
    # Replace Optional[str] or potentially inherited fields from TicketBase with correct nested models
    issuer: Optional[UserProfile] = Field(None, description="User object who created the ticket.")
    assignee: Optional[UserProfile] = Field(None, description="User object assigned to the ticket.")
    category: Optional[_NestedCategory] = Field(None, description="Category object associated with the ticket.")
    priority: Optional[_NestedPriority] = Field(None, description="Priority object associated with the ticket.")
    status: Optional[_NestedStatus] = Field(None, description="Status object associated with the ticket.")

    # NOTE: We keep TicketBase inheritance for title, description.
    # The *_id fields from TicketBase are ignored by Pydantic during parsing
    # if fields with the base name (e.g., 'priority') are present and match incoming data.
    # No need to explicitly exclude them unless causing issues.

# Models for listing related entities (Users, Categories, etc.)
class ListItemBase(BaseModel):
    """Base model for items in list endpoints (e.g., User, Category)."""
    id: int = Field(..., description="Unique integer identifier.")
    name: Optional[str] = Field(None, description="Optional display name.")
    # Add other fields if provided by the TTS API (e.g., description, email for user)

class UserListItem(ListItemBase):
    """Response model for an item in the list_users response."""
    username: str = Field(..., description="User's unique username.")
    email: Optional[str] = Field(None, description="User's email address.")
    first_name: Optional[str] = Field(None, description="User's first name.")
    last_name: Optional[str] = Field(None, description="User's last name.")

class CategoryListItem(ListItemBase):
    """Response model for an item in the list_categories response."""
    name: str = Field(..., description="Display name for the category.")

class PriorityListItem(ListItemBase):
    """Response model for an item in the list_priorities response."""
    name: str = Field(..., description="Display name for the priority.")

class StatusListItem(ListItemBase):
    """Response model for an item in the list_statuses response."""
    name: str = Field(..., description="Display name for the status.")

class CommentCreateRequest(BaseModel):
    """Request model for adding a comment."""
    text: str = Field(..., description="The content of the comment.")

class CommentResponse(BaseModel):
    """Response model representing a comment."""
    id: str = Field(..., description="Unique identifier of the comment.")
    text: str = Field(..., description="The content of the comment.")
    author: Optional[str] = Field(None, description="User who posted the comment.")
    created_at: Optional[str] = Field(None, description="Timestamp when the comment was created.")

# --- ADD: Generic Model for Paginated Lists ---
ListItemType = TypeVar('ListItemType')

class PaginatedListResponse(Generic[ListItemType], BaseModel):
    """Generic response model for any paginated list result."""
    count: int = Field(..., description="Total number of items available.")
    next: Optional[str] = Field(None, description="URL for the next page of results, if any.")
    previous: Optional[str] = Field(None, description="URL for the previous page of results, if any.")
    results: List[ListItemType] = Field(..., description="List of items for the current page.")

# --- END ADD ---

class PaginatedTicketResponse(BaseModel):
    """Response model for paginated ticket list results."""
    count: int = Field(..., description="Total number of tickets available.")
    next: Optional[str] = Field(None, description="URL for the next page of results, if any.")
    previous: Optional[str] = Field(None, description="URL for the previous page of results, if any.")
    results: List[TicketResponse] = Field(..., description="List of tickets for the current page.")

# --- HTTP Client Setup ---
# Setup headers for authentication (example using a Bearer Token)
# Adjust based on your TTS authentication method
headers = {
    "X-API-AUTH": f"{TTS_API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# --- Helper: Normalize ticket fields to match Pydantic models ---
def normalize_ticket_fields(ticket):
    """
    Convert string fields to dicts as expected by Pydantic models.
    - issuer, assignee: {"id": -1, "username": value, ...}
    - category, priority, status: {"id": -1, "name": value, ...}
    Use -1 for id if not available, to satisfy Pydantic integer requirements.
    """
    # Handle user fields
    for field in ["issuer", "assignee"]:
        if isinstance(ticket.get(field), str):
            # Provide minimal UserProfile structure with dummy id
            ticket[field] = {
                "id": -1,  # Use -1 to indicate unknown id
                "username": ticket[field],
                "email": None,
                "first_name": None,
                "last_name": None
            }
    # Handle related fields
    for field in ["category", "priority", "status"]:
        if isinstance(ticket.get(field), str):
            ticket[field] = {
                "id": -1,  # Use -1 to indicate unknown id
                "name": ticket[field]
            }
    # Comments: ensure it's a list (if present)
    if "comments" in ticket and not isinstance(ticket["comments"], list):
        ticket["comments"] = []
    return ticket

# --- Helper: Field Mapping for Django API ---
async def id_to_username(user_id: int) -> str:
    """
    Helper to map user_id to username by querying the Django API.
    Returns username as string.
    """
    # NOTE: This assumes the Django API provides a /users/ endpoint that returns user info by ID.
    # If not available, this should be replaced with a static mapping or cache.
    url = f"{TTS_API_URL}load-users/"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        users = resp.json().get("users", [])
        for user in users:
            if user.get("id") == user_id:
                return user.get("username")
    raise HTTPException(status_code=400, detail=f"User ID {user_id} not found.")

async def id_to_name(model: str, obj_id: int) -> str:
    """
    Helper to map an ID to a name for category, priority, or status.
    """
    url = f"{TTS_API_URL}{model}/"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        items = resp.json().get(model, [])
        for item in items:
            if item.get("id") == obj_id:
                return item.get("name")
    raise HTTPException(status_code=400, detail=f"{model.title()} ID {obj_id} not found.")

# --- API Endpoints ---

@tts_app.get("/tickets/search", summary="Search tickets by query and scope")
async def search_tickets(
    q: str = Query(..., description="Search query (title, description, or assignee username)"),
    scope: str = Query(None, description="Optional scope: my, hidden, closed")
):
    """
    Proxies search requests to the Django TTS API's search endpoint.
    Accepts 'q' (required) and 'scope' (optional) as query parameters.
    Returns a list of matching tickets as JSON.
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Missing search query (q)")
    # Build target URL and params
    target_url = f"{TTS_API_URL}search/"
    params = {"q": q}
    if scope:
        params["scope"] = scope
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            tickets = data.get("tickets", [])
            # Normalize ticket fields for frontend compatibility
            return {"tickets": [normalize_ticket_fields(t) for t in tickets]}
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
            raise HTTPException(status_code=exc.response.status_code, detail=detail)

@tts_app.post("/tickets", response_model=TicketResponse, status_code=201, summary="Create a new ticket")
async def create_ticket(ticket_data: TicketCreateRequest):
    """
    Receives ticket details (using IDs for relations), maps to Django API fields, and forwards to /tickets/api/v1/create/.
    """
    # Map IDs to names/usernames as required by Django API
    payload = {
        "title": ticket_data.title,
        "description": ticket_data.description,
        "assignee": await id_to_username(ticket_data.assignee_id),
        "category": await id_to_name("categories", ticket_data.category_id),
        "priority": await id_to_name("priorities", ticket_data.priority_id),
        "status": await id_to_name("statuses", ticket_data.status_id),
        # Add other fields as needed
    }
    # POST to Django API
    target_url = f"{TTS_API_URL}create/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            # Django returns only ticket_id; fetch full details
            ticket_id = result.get("ticket_id")
            if not ticket_id:
                raise HTTPException(status_code=500, detail="No ticket_id returned from Django API.")
            return await get_ticket(ticket_id)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
            raise HTTPException(status_code=exc.response.status_code, detail=detail)

@tts_app.get("/tickets")
async def list_tickets():
    """
    Retrieves a list of tickets from /tickets/api/v1/list/ and maps to expected output.
    """
    target_url = f"{TTS_API_URL}list/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Django returns {'tickets': [...]}
            tickets = data.get("tickets", [])
            # Map each ticket to expected output
            return {"tickets": [normalize_ticket_fields(t) for t in tickets]}
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
            raise HTTPException(status_code=exc.response.status_code, detail=detail)

@tts_app.get("/tickets/{ticket_id}", response_model=TicketResponse, summary="Get a specific ticket by ID")
async def get_ticket(ticket_id: int = Path(..., description="The unique integer ID of the ticket to retrieve.")):
    """
    Retrieves details for a single ticket from /tickets/api/v1/detail/{ticket_id}/.
    """
    target_url = f"{TTS_API_URL}detail/{ticket_id}/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, headers=headers)
            response.raise_for_status()
            ticket_data = response.json()
            return normalize_ticket_fields(ticket_data)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS.")
            else:
                detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
                raise HTTPException(status_code=exc.response.status_code, detail=detail)

@tts_app.put("/tickets/{ticket_id}", response_model=TicketResponse, summary="Update an existing ticket")
async def update_ticket(
    ticket_data: TicketUpdateRequest,
    ticket_id: int = Path(..., description="The unique integer ID of the ticket to update.")
):
    """
    Updates specified fields of an existing ticket in /tickets/api/v1/edit/{ticket_id}/.
    Uses ID fields for relations, maps to Django API fields.
    Sends data as application/x-www-form-urlencoded to match backend expectations.
    """
    payload = {}
    if ticket_data.title is not None:
        payload["title"] = ticket_data.title
    if ticket_data.description is not None:
        payload["description"] = ticket_data.description
    if ticket_data.assignee_id is not None:
        payload["assignee"] = await id_to_username(ticket_data.assignee_id)
    if ticket_data.category_id is not None:
        payload["category"] = await id_to_name("categories", ticket_data.category_id)
    if ticket_data.priority_id is not None:
        payload["priority"] = await id_to_name("priorities", ticket_data.priority_id)
    if ticket_data.status_id is not None:
        payload["status"] = await id_to_name("statuses", ticket_data.status_id)
    if not payload:
        raise HTTPException(status_code=400, detail="No update data provided.")
    target_url = f"{TTS_API_URL}edit/{ticket_id}/"
    # Use form data and set correct Content-Type
    form_headers = headers.copy()
    form_headers["Content-Type"] = "application/x-www-form-urlencoded"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, data=payload, headers=form_headers)
            response.raise_for_status()
            result = response.json()
            # Django returns ticket_id; fetch full details
            if not result.get("ticket_id"):
                raise HTTPException(status_code=500, detail="No ticket_id returned from Django API.")
            return await get_ticket(ticket_id)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS.")
            else:
                detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
                raise HTTPException(status_code=exc.response.status_code, detail=detail)

# Add DELETE endpoint based on script
@tts_app.delete("/tickets/{ticket_id}", status_code=204, summary="Delete a ticket by ID")
async def delete_ticket(ticket_id: int = Path(..., description="The unique integer ID of the ticket to delete.")):
    """
    Deletes a ticket from the external TTS (DELETE {TTS_API_URL}tickets/{id}/).
    """
    # Construct target URL by appending to the base TTS_API_URL
    target_url = f"{TTS_API_URL}tickets/{ticket_id}/"

    async with httpx.AsyncClient() as client:
        try:
            # Use DELETE method as per script
            response = await client.delete(target_url, headers=headers)
            response.raise_for_status() # Check for errors, handle 404 specifically
            # No content expected on success (204)
            return None # Return None for 204 response
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                 raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS.")
            else:
                detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
                raise HTTPException(status_code=exc.response.status_code, detail=detail)

@tts_app.post("/tickets/{ticket_id}/comments", response_model=CommentResponse, status_code=201, summary="Add a comment to a ticket")
async def add_comment(
    comment_data: CommentCreateRequest,
    ticket_id: str = Path(..., description="The unique ID of the ticket to comment on.")
):
    """
    Adds a comment to a specific ticket in /tickets/api/v1/add_comment/{ticket_id}/.
    """
    # Django expects 'comment' in POST data, not 'text'
    payload = {"comment": comment_data.text}
    target_url = f"{TTS_API_URL}add_comment/{ticket_id}/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, data=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            # Return a minimal comment response (Django does not return full comment)
            return CommentResponse(id=str(result.get("ticket_id", "")), text=comment_data.text)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS.")
            else:
                detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
                raise HTTPException(status_code=exc.response.status_code, detail=detail)

# --- Endpoints for Related Entities (Users, Categories, etc.) ---

async def _list_related_items(item_type: str, response_model: Any, limit: int = 50, offset: int = 0):
    """Helper function to list related items like users, categories, etc.
       Constructs the target URL by appending the item type to the base TTS_API_URL.
    """
    if not TTS_API_URL:
         raise HTTPException(status_code=500, detail="TTS_API_URL environment variable not set.")
    
    # Only append the action to TTS_API_URL for users
    if item_type == "users":
        target_url = f"{TTS_API_URL}load-users/"
    else:
        # Fallback to the old logic for other types
        base_api_path = TTS_API_URL if TTS_API_URL.endswith('/') else f"{TTS_API_URL}/"
        target_url = f"{base_api_path}{item_type}/"
    
    print(f"Constructed target URL for {item_type}: {target_url}") # Debugging print

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, headers=headers, params={"limit": limit, "offset": offset})
            response.raise_for_status()
            paginated_data = response.json()

            # --- MODIFIED: Validate structure and parse results ---
            if not isinstance(paginated_data, dict) or 'results' not in paginated_data or 'count' not in paginated_data:
                print(f"Error: Expected a paginated dict with 'count'/'results' from {target_url}, got {type(paginated_data)}")
                raise HTTPException(status_code=500, detail=f"Unexpected paginated response format from TTS listing {item_type}.")

            # Parse items within the 'results' list using the provided model
            try:
                parsed_results = [response_model(**item) for item in paginated_data['results']]
            except Exception as e: # Catch potential Pydantic validation errors during list parsing
                print(f"Error parsing items for {item_type}: {e}")
                raise HTTPException(status_code=500, detail=f"Error parsing item details for {item_type}.")

            # Replace raw results with parsed results in the dict to be returned
            paginated_data['results'] = parsed_results
            # Return the whole dict, let the endpoint handle final model instantiation
            return paginated_data
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            detail = f"TTS Error fetching {item_type}: {exc.response.status_code} - {exc.response.text}"
            raise HTTPException(status_code=exc.response.status_code, detail=detail)

@tts_app.get("/users", response_model=PaginatedListResponse[UserListItem], summary="List all users")
async def list_users(
    # Query parameters for pagination
    limit: int = Query(50, ge=1, le=100, description="Maximum number of users to return."),
    offset: int = Query(0, ge=0, description="Number of users to skip for pagination.")
):
    """Retrieves a paginated list of users from the external TTS (GET {TTS_API_URL}users/)."""
    paginated_dict = await _list_related_items("users", UserListItem, limit=limit, offset=offset)
    # Instantiate the generic response model using the processed dictionary
    return PaginatedListResponse[UserListItem](**paginated_dict)

@tts_app.get("/categories", response_model=PaginatedListResponse[CategoryListItem], summary="List all categories")
async def list_categories(
    # Query parameters for pagination
    limit: int = Query(50, ge=1, le=100, description="Maximum number of categories to return."),
    offset: int = Query(0, ge=0, description="Number of categories to skip for pagination.")
):
    """Retrieves a paginated list of categories from the external TTS (GET {TTS_API_URL}categories/)."""
    paginated_dict = await _list_related_items("categories", CategoryListItem, limit=limit, offset=offset)
    return PaginatedListResponse[CategoryListItem](**paginated_dict)

@tts_app.get("/priorities", response_model=PaginatedListResponse[PriorityListItem], summary="List all priorities")
async def list_priorities(
    # Query parameters for pagination
    limit: int = Query(50, ge=1, le=100, description="Maximum number of priorities to return."),
    offset: int = Query(0, ge=0, description="Number of priorities to skip for pagination.")
):
    """Retrieves a paginated list of priorities from the external TTS (GET {TTS_API_URL}priorities/)."""
    paginated_dict = await _list_related_items("priorities", PriorityListItem, limit=limit, offset=offset)
    return PaginatedListResponse[PriorityListItem](**paginated_dict)

@tts_app.get("/statuses", response_model=PaginatedListResponse[StatusListItem], summary="List all statuses")
async def list_statuses(
    # Query parameters for pagination
    limit: int = Query(50, ge=1, le=100, description="Maximum number of statuses to return."),
    offset: int = Query(0, ge=0, description="Number of statuses to skip for pagination.")
):
    """Retrieves a paginated list of statuses from the external TTS (GET {TTS_API_URL}statuses/)."""
    paginated_dict = await _list_related_items("statuses", StatusListItem, limit=limit, offset=offset)
    return PaginatedListResponse[StatusListItem](**paginated_dict)

# --- ADD: Profile Endpoints ---

@tts_app.get("/profile", response_model=UserProfile, summary="Get current user profile")
async def get_profile():
    """Retrieves the profile of the currently authenticated user from the TTS backend."""
    target_url = f"{TTS_API_URL}profile/" # Assuming API base URL ends with /v1/
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, headers=headers)
            response.raise_for_status()
            profile_data = response.json()
            return UserProfile(**profile_data)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            # Handle potential 401/403 if authentication fails
            detail = f"TTS Error fetching profile: {exc.response.status_code} - {exc.response.text}"
            raise HTTPException(status_code=exc.response.status_code, detail=detail)

@tts_app.put("/profile", response_model=UserProfile, summary="Update current user profile")
async def update_profile(update_data: ProfileUpdateRequest):
    """Updates the profile (email, first_name, last_name) of the currently authenticated user."""
    target_url = f"{TTS_API_URL}profile/" 
    payload = update_data.model_dump(exclude_unset=True)

    if not payload:
        raise HTTPException(status_code=400, detail="No profile update data provided.")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(target_url, json=payload, headers=headers)
            response.raise_for_status()
            updated_profile_data = response.json()
            return UserProfile(**updated_profile_data)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            # Handle potential 400 for bad data, 401/403 for auth
            detail = f"TTS Error updating profile: {exc.response.status_code} - {exc.response.text}"
            raise HTTPException(status_code=exc.response.status_code, detail=detail)

# --- ADD: User Detail Endpoint ---

@tts_app.get("/users/{user_id}", response_model=UserProfile, summary="Get user by ID")
async def get_user(user_id: int = Path(..., description="The ID of the user to retrieve.")):
    """Retrieves details for a specific user by their ID from the TTS backend."""
    target_url = f"{TTS_API_URL}users/{user_id}/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()
            return UserProfile(**user_data)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")
            else:
                detail = f"TTS Error fetching user {user_id}: {exc.response.status_code} - {exc.response.text}"
                raise HTTPException(status_code=exc.response.status_code, detail=detail)

# --- Health Check Endpoint ---
@tts_app.get("/health", status_code=200, summary="Health check")
async def health_check():
    """Basic health check endpoint."""
    # Optionally, you could add a simple check to the real TTS here
    return {"status": "ok"}

# --- Mount as Sub-Application ---
# Create the main FastAPI app and mount the TTS app under /tts
from fastapi import FastAPI as _FastAPI
main_app = _FastAPI(title="Main API Root")
# Mount the TTS app at /tts so all docs and endpoints are under /tts
main_app.mount("/tts", tts_app)

# For Uvicorn, use: uvicorn ticket-tracking-system.main:main_app --reload
# Now, all endpoints and docs are available under http://localhost:8000/tts
# Example: http://localhost:8000/tts/docs
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(main_app, host="0.0.0.0", port=8000) # Example port 

@tts_app.post("/tickets/{ticket_id}/close", response_model=TicketResponse, summary="Close a ticket by setting its status to 'Closed'")
async def close_ticket(ticket_id: int = Path(..., description="The unique integer ID of the ticket to close.")):
    """
    Sets the ticket's status to 'Closed' by updating the ticket with status name 'Closed'.
    Sends data as application/x-www-form-urlencoded to match backend expectations.
    """
    payload = {"status": "Closed"}
    target_url = f"{TTS_API_URL}edit/{ticket_id}/"
    form_headers = headers.copy()
    form_headers["Content-Type"] = "application/x-www-form-urlencoded"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, data=payload, headers=form_headers)
            response.raise_for_status()
            result = response.json()
            if not result.get("ticket_id"):
                raise HTTPException(status_code=500, detail="No ticket_id returned from Django API.")
            return await get_ticket(ticket_id)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS.")
            else:
                detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
                raise HTTPException(status_code=exc.response.status_code, detail=detail)

@tts_app.post("/tickets/batch_close", summary="Batch close tickets by IDs")
async def batch_close_tickets(request: Request):
    """
    Proxies batch close requests to the Django TTS API's batch close endpoint.
    Accepts POST with JSON: {"ticket_ids": [1,2,3]} from the client.
    Always sends JSON to Django.
    Returns a summary of closed and failed tickets.
    """
    target_url = f"{TTS_API_URL}batch_close/"
    # Print headers and raw body for debugging
    headers = dict(request.headers)
    raw_body = await request.body()
    print(f"[DEBUG] Request headers: {headers}")
    print(f"[DEBUG] Raw request body: {raw_body}")
    # Only accept JSON
    if not raw_body or raw_body.strip() == b'' or raw_body.strip() == b'{}':
        print("[DEBUG] Error: Request body is empty. Client did not send any data.")
        raise HTTPException(status_code=400, detail="Request body is empty. Please send JSON (e.g. {'ticket_ids': [1,2,3]}). Content-Type must be application/json.")
    if request.headers.get("content-type", "").split(";")[0].lower() != "application/json":
        print("[DEBUG] Error: Content-Type is not application/json.")
        raise HTTPException(status_code=415, detail="Content-Type must be application/json.")
    try:
        body = await request.json()
        print("[DEBUG] Received JSON body:", body)
        ticket_ids = body.get("ticket_ids", [])
        if not isinstance(ticket_ids, list) or not all(isinstance(i, int) for i in ticket_ids):
            print("[DEBUG] Error: ticket_ids is not a list of integers.")
            raise HTTPException(status_code=400, detail="ticket_ids must be a list of integers in JSON body.")
    except Exception as e:
        print(f"[DEBUG] Error parsing JSON body: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON body. Please send JSON with ticket_ids as a list of integers.")
    if not ticket_ids:
        print("[DEBUG] Error: No ticket_ids provided after parsing body.")
        raise HTTPException(status_code=400, detail="No ticket_ids provided. Please include ticket_ids as a list in JSON.")
    print(f"[DEBUG] Input type received from client: json")
    outgoing_json = {"ticket_ids": ticket_ids}
    print("[DEBUG] Sending JSON to Django:", outgoing_json)
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, json=outgoing_json, headers=json_headers)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            print(f"[DEBUG] RequestError: {exc}")
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            print(f"[DEBUG] HTTPStatusError: {exc.response.status_code} - {exc.response.text}")
            detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
            raise HTTPException(status_code=exc.response.status_code, detail=detail)

# --- Batch Close Request Model ---
class BatchCloseRequest(BaseModel):
    """
    Request model for batch closing tickets.
    """
    ticket_ids: List[int] = Field(..., description="List of ticket IDs to close.")

@tts_app.post("/tickets/batch_close", summary="Batch close tickets by IDs")
async def batch_close_tickets(request: BatchCloseRequest):
    """
    Closes multiple tickets by forwarding the list of IDs to the Django batch close API.
    Returns a summary of closed and failed ticket IDs.
    """
    target_url = f"{TTS_API_URL}batch_close/"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, json=request.dict(), headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {exc}")
        except httpx.HTTPStatusError as exc:
            detail = f"TTS Error: {exc.response.status_code} - {exc.response.text}"
            raise HTTPException(status_code=exc.response.status_code, detail=detail) 