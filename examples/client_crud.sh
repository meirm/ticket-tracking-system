#!/bin/bash

# Simple CRUD workflow demonstration script
# Requires jq to parse JSON output (for extracting the new ticket ID)

# resolve the path to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_CLIENT_SCRIPT="$SCRIPT_DIR/client_api_request.sh"

# --- Check for API Key ---
if [ -z "$1" ]; then
  echo "Usage: $0 <api_key>" >&2
  echo "Error: API Key argument is missing." >&2
  exit 1
fi
API_KEY="$1"

echo "--- CRUD Workflow Demo --- API Key: $API_KEY ---" >&2

# --- Prerequisites: Getting IDs ---
echo "" >&2
echo "Step 0: Get necessary IDs (Run these manually first if needed):" >&2
echo "  $API_CLIENT_SCRIPT -k $API_KEY -x list_users" >&2
echo "  $API_CLIENT_SCRIPT -k $API_KEY -x list_categories" >&2
echo "  $API_CLIENT_SCRIPT -k $API_KEY -x list_priorities" >&2
echo "  $API_CLIENT_SCRIPT -k $API_KEY -x list_statuses" >&2
echo "(Assuming default IDs exist for demo: User=1, Category=1, Priority=1, Status=1)" >&2

# Example IDs (replace with actual IDs obtained from list_* commands)
USER_ID=1    # Assuming user with ID 1 exists (Changed from ASSIGNEE_ID)
CATEGORY_ID=1    # Assuming category with ID 1 exists
PRIORITY_ID=1    # Assuming priority with ID 1 exists
STATUS_ID=1      # Assuming status with ID 1 exists

# --- CREATE ---
echo "" >&2
echo "Step 1: Creating a new ticket..." >&2
TICKET_TITLE="CRUD Demo Ticket $(date +%s)"
TICKET_DESCRIPTION="This ticket was created by the CRUD demo script."
# Use new single-character options for IDs: -u, -C, -P, -S
# Add required -d option
NEW_TICKET_JSON=$($API_CLIENT_SCRIPT -k "$API_KEY" -x create \
  -t "$TICKET_TITLE" \
  -d "$TICKET_DESCRIPTION" \
  -u "$USER_ID" \
  -C "$CATEGORY_ID" \
  -P "$PRIORITY_ID" \
  -S "$STATUS_ID")

# Check if jq is available and attempt to parse ID
if command -v jq &> /dev/null && [[ "$NEW_TICKET_JSON" == {* ]]; then
    NEW_TICKET_ID=$(echo "$NEW_TICKET_JSON" | jq -r '.id')
    echo "Created Ticket Response:" >&2
    echo "$NEW_TICKET_JSON"
    if [[ -z "$NEW_TICKET_ID" || "$NEW_TICKET_ID" == "null" ]]; then
      echo "Error: Could not extract ID from create response. Exiting." >&2
      exit 1
    fi
    echo "Extracted New Ticket ID: $NEW_TICKET_ID" >&2
else
    echo "jq not found or create failed. Cannot automatically extract ticket ID." >&2
    echo "Create Response:" >&2
    echo "$NEW_TICKET_JSON"
    echo "Please manually find the ticket ID and run subsequent steps." >&2
    exit 1
fi

# --- READ (GET) ---
echo "" >&2
echo "Step 2: Getting the created ticket (ID: $NEW_TICKET_ID)..." >&2
$API_CLIENT_SCRIPT -k "$API_KEY" -x get -i "$NEW_TICKET_ID"

# --- UPDATE ---
# Example: Change priority and status (Assuming Priority ID 2 and Status ID 2 exist)
NEW_PRIORITY_ID=2
NEW_STATUS_ID=2
echo "" >&2
echo "Step 3: Updating the ticket (ID: $NEW_TICKET_ID) to Priority=$NEW_PRIORITY_ID, Status=$NEW_STATUS_ID..." >&2
# Use new single-character options for IDs: -P, -S
$API_CLIENT_SCRIPT -k "$API_KEY" -x update -i "$NEW_TICKET_ID" \
  -P "$NEW_PRIORITY_ID" \
  -S "$NEW_STATUS_ID"

# --- READ (GET AGAIN) ---
echo "" >&2
echo "Step 4: Getting the updated ticket (ID: $NEW_TICKET_ID)..." >&2
$API_CLIENT_SCRIPT -k "$API_KEY" -x get -i "$NEW_TICKET_ID"

# --- DELETE ---
echo "" >&2
echo "Step 5: Deleting the ticket (ID: $NEW_TICKET_ID)..." >&2
$API_CLIENT_SCRIPT -k "$API_KEY" -x delete -i "$NEW_TICKET_ID"

# --- VERIFY DELETE (Optional) ---
echo "" >&2
echo "Step 6: Attempting to get the deleted ticket (should fail with 404)..." >&2
$API_CLIENT_SCRIPT -k "$API_KEY" -x get -i "$NEW_TICKET_ID"

echo "" >&2
echo "--- CRUD Workflow Demo Complete --- " >&2

exit 0
