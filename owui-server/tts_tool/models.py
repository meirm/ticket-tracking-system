
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, TypeVar, Generic

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
    assigned_group_id: Optional[int] = Field(None, description="ID of the assigned group.")
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
       Requires description, assignee_id, category_id, priority_id, status_id, assigned_group_id as per script.
    """
    # Make fields required for creation as per script logic
    description: str = Field(..., description="Detailed description of the ticket.")
    assignee_id: int = Field(..., description="ID of the user assigned to the ticket.")
    category_id: int = Field(..., description="ID of the ticket category.")
    priority_id: int = Field(..., description="ID of the priority level.")
    status_id: int = Field(..., description="ID of the current status.")
    assigned_group_id: int = Field(..., description="ID of the assigned group.")

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
    due_date: Optional[str] = Field(None, description="Updated due date for the ticket.")
    assigned_group_id: Optional[int] = Field(None, description="Updated ID of the assigned group.")
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

# FIX: Inherit from BaseModel before Generic[ListItemType]
class PaginatedListResponse(BaseModel, Generic[ListItemType]):
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

# Pydantic Models for Summaries
class SummaryBase(BaseModel):
    task_id: str = Field(..., description="Unique task identifier for the summary.")
    title: str = Field(..., description="The title of the summary.")
    description: str = Field(..., description="Detailed description for the summary task.")
    related_tickets: List[int] = Field([], description="A list of related ticket IDs.")
    archived: bool = Field(False, description="Whether the summary is archived.")

class SummaryCreateRequest(SummaryBase):
    pass

class SummaryUpdateRequest(BaseModel):
    task_id: Optional[str] = Field(None, description="Updated task identifier.")
    title: Optional[str] = Field(None, description="Updated title.")
    description: Optional[str] = Field(None, description="Updated description.")
    related_tickets: Optional[List[int]] = Field(None, description="Updated list of related ticket IDs.")
    archived: Optional[bool] = Field(None, description="Updated archived status.")

class SummaryResponse(SummaryBase):
    id: int = Field(..., description="Unique integer identifier of the summary (assigned by the TTS).")
