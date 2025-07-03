# servers/ticket-tracking-system/main.py
# Import necessary libraries
from fastapi import FastAPI, HTTPException, Body, Path, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, TypeVar, Generic
import os
import json
from tts_client import TTSClient
from models import TicketCreateRequest, TicketResponse, TicketUpdateRequest, CommentCreateRequest, CommentResponse, UserProfile, ProfileUpdateRequest, UserListItem, CategoryListItem, PriorityListItem, StatusListItem, PaginatedListResponse, SummaryCreateRequest, SummaryResponse, SummaryUpdateRequest
from fastapi.concurrency import run_in_threadpool

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

# --- HTTP Client Setup ---
# Setup headers for authentication (example using a Bearer Token)
# Adjust based on your TTS authentication method
headers = {
    "X-API-AUTH": f"{TTS_API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Instantiate the TTSClient for use in all endpoints
_tts_client = TTSClient(TTS_API_URL, TTS_API_TOKEN)

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
    url = f"{TTS_API_URL}assignees/"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        users = resp.json().get("results", [])
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
        items = resp.json().get("results", [])
        for item in items:
            if item.get("id") == obj_id:
                return item.get("name")
    raise HTTPException(status_code=400, detail=f"{model.title()} ID {obj_id} not found.")

# --- Helper: Map group ID to group name ---
async def id_to_group_name(group_id: int) -> str:
    """
    Helper to map group_id to group name by querying the Django API.
    Returns group name as string.
    """
    url = f"{TTS_API_URL}groups/"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        groups = resp.json().get("results", [])
        for group in groups:
            if group.get("id") == group_id:
                return group.get("name")
    raise HTTPException(status_code=400, detail=f"Group ID {group_id} not found.")

# --- API Endpoints ---

@tts_app.get("/tickets/search", summary="Search tickets by query, scope, and filters")
async def search_tickets(
    q: str = Query(..., description="Search query (title, description, or assignee username)"),
    scope: str = Query(None, description="Optional scope: my, hidden, closed"),
    status: str = Query(None, description="Comma-separated list of statuses to filter by (e.g. 'Open,In Progress')"),
    priority: str = Query(None, description="Comma-separated list of priorities to filter by (e.g. 'High,Medium')"),
    from_date: str = Query(None, description="Filter tickets created on or after this date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Filter tickets created on or before this date (YYYY-MM-DD)"),
    due_date: str = Query(None, description="Comma-separated list of due dates to filter by (YYYY-MM-DD)"),
    assignee: str = Query(None, description="Comma-separated list of assignee usernames to filter by"),
    issuer: str = Query(None, description="Comma-separated list of issuer usernames to filter by")
):
    """
    Proxies search requests to the TTS API's search endpoint using TTSClient.
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Missing search query (q)")
    try:
        data = await run_in_threadpool(_tts_client.search_tickets, q, scope, status, priority, from_date, to_date, due_date, assignee, issuer)
        tickets = data.get("tickets", [])
        return {"tickets": [normalize_ticket_fields(t) for t in tickets]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error searching tickets: {e}")

@tts_app.post("/tickets", response_model=TicketResponse, status_code=201, summary="Create a new ticket")
async def create_ticket(ticket_data: TicketCreateRequest):
    """
    Receives ticket details, maps to Django API fields, and forwards to TTSClient.
    """
    try:
        # Map IDs to names/usernames as required by Django API using TTSClient helpers
        assignee = await run_in_threadpool(_tts_client.id_to_username, ticket_data.assignee_id)
        category = await run_in_threadpool(_tts_client.id_to_name, "categories", ticket_data.category_id)
        priority = await run_in_threadpool(_tts_client.id_to_name, "priorities", ticket_data.priority_id)
        status = await run_in_threadpool(_tts_client.id_to_name, "statuses", ticket_data.status_id)
        assigned_group = await run_in_threadpool(_tts_client.id_to_group_name, ticket_data.assigned_group_id)
        payload = {
            "title": ticket_data.title,
            "description": ticket_data.description,
            "assignee": assignee,
            "category": category,
            "priority": priority,
            "status": status,
            "assigned_group": assigned_group,
        }
        # Create the ticket
        result = await run_in_threadpool(_tts_client.create_ticket, payload)
        ticket_id = result.get("ticket_id")
        if not ticket_id:
            raise HTTPException(status_code=500, detail="No ticket_id returned from TTS API.")
        # Fetch and return the full ticket details
        ticket = await run_in_threadpool(_tts_client.get_ticket, ticket_id)
        return normalize_ticket_fields(ticket)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error creating ticket: {e}")

@tts_app.get("/tickets")
async def list_tickets(
    status: str = Query(None, description="Comma-separated list of statuses to filter by (e.g. 'Open,In Progress')"),
    priority: str = Query(None, description="Comma-separated list of priorities to filter by (e.g. 'High,Medium')"),
    from_date: str = Query(None, description="Filter tickets created on or after this date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Filter tickets created on or before this date (YYYY-MM-DD)"),
    due_date: str = Query(None, description="Comma-separated list of due dates to filter by (YYYY-MM-DD)"),
    assignee: str = Query(None, description="Comma-separated list of assignee usernames to filter by"),
    issuer: str = Query(None, description="Comma-separated list of issuer usernames to filter by")
):
    """
    Retrieves a list of tickets from the TTS API using TTSClient. Accepts optional filter parameters.
    """
    params = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority
    if from_date:
        params["from_date"] = from_date
    if to_date:
        params["to_date"] = to_date
    if due_date:
        params["due_date"] = due_date
    if assignee:
        params["assignee"] = assignee
    if issuer:
        params["issuer"] = issuer
    try:
        # Call the sync TTSClient method in a threadpool to keep endpoint async
        data = await run_in_threadpool(_tts_client.list_tickets, params)
        tickets = data.get("tickets", [])
        # Normalize ticket fields for frontend compatibility
        return {"tickets": [normalize_ticket_fields(t) for t in tickets]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to TTS: {e}")

@tts_app.get("/tickets/{ticket_id}", response_model=TicketResponse, summary="Get a specific ticket by ID")
async def get_ticket(ticket_id: int = Path(..., description="The unique integer ID of the ticket to retrieve.")):
    """
    Retrieves details for a single ticket from the TTS API using TTSClient.
    """
    try:
        ticket_data = await run_in_threadpool(_tts_client.get_ticket, ticket_id)
        return normalize_ticket_fields(ticket_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS. {e}")

@tts_app.put("/tickets/{ticket_id}", response_model=TicketResponse, summary="Update an existing ticket")
async def update_ticket(
    ticket_data: TicketUpdateRequest,
    ticket_id: int = Path(..., description="The unique integer ID of the ticket to update.")
):
    # DEBUG: Print incoming request data
    print(f"[DEBUG] Incoming update_ticket request for ticket_id={ticket_id}")
    print(f"[DEBUG] ticket_data: {ticket_data}")

    payload = {}
    try:
        if ticket_data.title is not None:
            payload["title"] = ticket_data.title
        if ticket_data.description is not None:
            payload["description"] = ticket_data.description
        if ticket_data.assignee_id is not None:
            payload["assignee"] = await run_in_threadpool(_tts_client.id_to_username, ticket_data.assignee_id)
        if ticket_data.category_id is not None:
            payload["category"] = await run_in_threadpool(_tts_client.id_to_name, "categories", ticket_data.category_id)
        if ticket_data.priority_id is not None:
            payload["priority"] = await run_in_threadpool(_tts_client.id_to_name, "priorities", ticket_data.priority_id)
        if ticket_data.status_id is not None:
            payload["status"] = await run_in_threadpool(_tts_client.id_to_name, "statuses", ticket_data.status_id)
        if ticket_data.due_date is not None:
            payload["due_date"] = ticket_data.due_date
        if ticket_data.assigned_group_id is not None:
            payload["assigned_group"] = await run_in_threadpool(_tts_client.id_to_group_name, ticket_data.assigned_group_id)
        if not payload:
            print("[DEBUG] No update data provided.")
            raise HTTPException(status_code=400, detail="No update data provided.")
        print(f"[DEBUG] Payload to Django: {payload}")
        # Update the ticket
        result = await run_in_threadpool(_tts_client.update_ticket, ticket_id, payload)
        if not result.get("ticket_id"):
            print("[DEBUG] No ticket_id returned from TTS API.")
            raise HTTPException(status_code=500, detail="No ticket_id returned from TTS API.")
        # Fetch and return the full ticket details
        ticket = await run_in_threadpool(_tts_client.get_ticket, ticket_id)
        return normalize_ticket_fields(ticket)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error updating ticket: {e}")

@tts_app.delete("/tickets/{ticket_id}", status_code=204, summary="Delete a ticket by ID")
async def delete_ticket(ticket_id: int = Path(..., description="The unique integer ID of the ticket to delete.")):
    """
    Deletes a ticket from the TTS API using TTSClient.
    """
    try:
        await run_in_threadpool(_tts_client.delete_ticket, ticket_id)
        return None
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS.")
        raise HTTPException(status_code=503, detail=f"Error deleting ticket: {e}")

@tts_app.post("/tickets/{ticket_id}/comments", response_model=CommentResponse, status_code=201, summary="Add a comment to a ticket")
async def add_comment(
    comment_data: CommentCreateRequest,
    ticket_id: str = Path(..., description="The unique ID of the ticket to comment on.")
):
    """
    Adds a comment to a specific ticket using TTSClient.
    """
    try:
        result = await run_in_threadpool(_tts_client.add_comment, ticket_id, comment_data.text)
        return CommentResponse(id=str(result.get("ticket_id", "")), text=comment_data.text)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS.")
        raise HTTPException(status_code=503, detail=f"Error adding comment: {e}")

# --- Endpoints for Related Entities (Users, Categories, etc.) ---

async def _list_related_items(item_type: str, response_model: Any, limit: int = 50, offset: int = 0):
    """Helper function to list related items like users, categories, etc.
       Constructs the target URL by appending the item type to the base TTS_API_URL.
    """
    if not TTS_API_URL:
         raise HTTPException(status_code=500, detail="TTS_API_URL environment variable not set.")
    
    # Use the new /assignees/ endpoint for possible ticket assignees
    if item_type == "users":
        target_url = f"{TTS_API_URL}assignees/"
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
    limit: int = Query(50, ge=1, le=100, description="Maximum number of users to return."),
    offset: int = Query(0, ge=0, description="Number of users to skip for pagination.")
):
    """Retrieves a paginated list of users from the TTS API using TTSClient."""
    try:
        paginated_dict = await run_in_threadpool(_tts_client.list_users, limit, offset)
        return PaginatedListResponse[UserListItem](**paginated_dict)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error listing users: {e}")

@tts_app.get("/categories", response_model=PaginatedListResponse[CategoryListItem], summary="List all categories")
async def list_categories(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of categories to return."),
    offset: int = Query(0, ge=0, description="Number of categories to skip for pagination.")
):
    """Retrieves a paginated list of categories from the TTS API using TTSClient."""
    try:
        paginated_dict = await run_in_threadpool(_tts_client.list_categories, limit, offset)
        return PaginatedListResponse[CategoryListItem](**paginated_dict)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error listing categories: {e}")

@tts_app.get("/priorities", response_model=PaginatedListResponse[PriorityListItem], summary="List all priorities")
async def list_priorities(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of priorities to return."),
    offset: int = Query(0, ge=0, description="Number of priorities to skip for pagination.")
):
    """Retrieves a paginated list of priorities from the TTS API using TTSClient."""
    try:
        paginated_dict = await run_in_threadpool(_tts_client.list_priorities, limit, offset)
        return PaginatedListResponse[PriorityListItem](**paginated_dict)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error listing priorities: {e}")

@tts_app.get("/statuses", response_model=PaginatedListResponse[StatusListItem], summary="List all statuses")
async def list_statuses(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of statuses to return."),
    offset: int = Query(0, ge=0, description="Number of statuses to skip for pagination.")
):
    """Retrieves a paginated list of statuses from the TTS API using TTSClient."""
    try:
        paginated_dict = await run_in_threadpool(_tts_client.list_statuses, limit, offset)
        return PaginatedListResponse[StatusListItem](**paginated_dict)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error listing statuses: {e}")

# --- ADD: Profile Endpoints ---

@tts_app.get("/profile", response_model=UserProfile, summary="Get current user profile")
async def get_profile():
    """Retrieves the profile of the currently authenticated user from the TTS API using TTSClient."""
    try:
        profile_data = await run_in_threadpool(_tts_client.get_profile)
        return UserProfile(**profile_data)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error fetching profile: {e}")

@tts_app.put("/profile", response_model=UserProfile, summary="Update current user profile")
async def update_profile(update_data: ProfileUpdateRequest):
    """Updates the profile of the currently authenticated user using TTSClient."""
    payload = update_data.model_dump(exclude_unset=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No profile update data provided.")
    try:
        updated_profile_data = await run_in_threadpool(_tts_client.update_profile, payload)
        return UserProfile(**updated_profile_data)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error updating profile: {e}")

# --- ADD: User Detail Endpoint ---

@tts_app.get("/users/{user_id}", response_model=UserProfile, summary="Get user by ID")
async def get_user(user_id: int = Path(..., description="The ID of the user to retrieve.")):
    """Retrieves details for a specific user by their ID from the TTS API using TTSClient."""
    try:
        user_data = await run_in_threadpool(_tts_client.get_user, user_id)
        return UserProfile(**user_data)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")
        raise HTTPException(status_code=503, detail=f"Error fetching user: {e}")

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
    Sets the ticket's status to 'Closed' using TTSClient.
    """
    try:
        result = await run_in_threadpool(_tts_client.close_ticket, ticket_id)
        if not result.get("ticket_id"):
            raise HTTPException(status_code=500, detail="No ticket_id returned from TTS API.")
        ticket = await run_in_threadpool(_tts_client.get_ticket, ticket_id)
        return normalize_ticket_fields(ticket)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Ticket with ID '{ticket_id}' not found in TTS.")
        raise HTTPException(status_code=503, detail=f"Error closing ticket: {e}")

# --- Batch Close Request Model ---
class BatchCloseRequest(BaseModel):
    """
    Request model for batch closing tickets.
    """
    ticket_ids: List[int] = Field(..., description="List of ticket IDs to close.")

@tts_app.post("/tickets/batch_close", summary="Batch close tickets by IDs")
async def batch_close_tickets(request: BatchCloseRequest):
    """
    Closes multiple tickets by forwarding the list of IDs to the TTS API using TTSClient.
    Returns a summary of closed and failed ticket IDs.
    """
    try:
        result = await run_in_threadpool(_tts_client.batch_close_tickets, request.ticket_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error batch closing tickets: {e}")

# --- List Groups Endpoint ---
class GroupListItem(BaseModel):
    id: int = Field(..., description="Unique integer identifier for the group.")
    name: str = Field(..., description="Display name for the group.")

@tts_app.get("/groups", response_model=PaginatedListResponse[GroupListItem], summary="List all groups")
async def list_groups(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of groups to return."),
    offset: int = Query(0, ge=0, description="Number of groups to skip for pagination.")
):
    """Retrieves a paginated list of groups from the TTS API using TTSClient."""
    try:
        paginated_dict = await run_in_threadpool(_tts_client.list_groups, limit, offset)
        return PaginatedListResponse[GroupListItem](**paginated_dict)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error listing groups: {e}")

# API Endpoints for Summaries
@tts_app.get("/summaries", response_model=List[SummaryResponse], summary="List all summaries")
async def list_summaries(archived: Optional[bool] = Query(None, description="Filter summaries by archived status.")):
    """
    Retrieves a list of summaries from the TTS API using TTSClient.
    """
    try:
        data = await run_in_threadpool(_tts_client.list_summaries, archived)
        return data.get('summaries', [])
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error listing summaries: {e}")

@tts_app.post("/summaries", response_model=SummaryResponse, status_code=201, summary="Create a new summary")
async def create_summary(summary_data: SummaryCreateRequest):
    """
    Creates a new summary in the TTS API using TTSClient.
    """
    try:
        result = await run_in_threadpool(_tts_client.create_summary, summary_data.model_dump())
        summary_id = result.get("summary_id")
        if not summary_id:
            raise HTTPException(status_code=500, detail="Summary created but no ID returned.")
        summary = await run_in_threadpool(_tts_client.get_summary, summary_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error creating summary: {e}")

@tts_app.get("/summaries/{summary_id}", response_model=SummaryResponse, summary="Get a specific summary by ID")
async def get_summary(summary_id: int):
    """
    Retrieves details for a single summary from the TTS API using TTSClient.
    """
    try:
        summary = await run_in_threadpool(_tts_client.get_summary, summary_id)
        return summary
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Summary with ID '{summary_id}' not found in TTS.")
        raise HTTPException(status_code=503, detail=f"Error fetching summary: {e}")

@tts_app.put("/summaries/{summary_id}", response_model=SummaryResponse, summary="Update an existing summary")
async def update_summary(summary_id: int, summary_data: SummaryUpdateRequest):
    """
    Updates an existing summary in the TTS API using TTSClient.
    """
    payload = summary_data.model_dump(exclude_unset=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No update data provided.")
    try:
        await run_in_threadpool(_tts_client.update_summary, summary_id, payload)
        summary = await run_in_threadpool(_tts_client.get_summary, summary_id)
        return summary
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Summary with ID '{summary_id}' not found in TTS.")
        raise HTTPException(status_code=503, detail=f"Error updating summary: {e}")

@tts_app.delete("/summaries/{summary_id}", status_code=204, summary="Delete a summary by ID")
async def delete_summary(summary_id: int):
    """
    Deletes a summary by its ID using TTSClient.
    """
    try:
        await run_in_threadpool(_tts_client.delete_summary, summary_id)
        return None
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Summary with ID '{summary_id}' not found in TTS.")
        raise HTTPException(status_code=503, detail=f"Error deleting summary: {e}")

@tts_app.post("/summaries/archive_all", summary="Archive all unarchived summaries")
async def archive_all_summaries():
    """
    Sends a request to the TTS API to archive all summaries that are not currently archived using TTSClient.
    """
    try:
        result = await run_in_threadpool(_tts_client.archive_all_summaries)
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error archiving all summaries: {e}") 