#!/bin/bash
WEBHOOK_URL="http://localhost:8000/tickets/api/v1/tickets/"


# Field options (-t, -d)
# -i (ticket ID) is required for 'get', 'update', 'delete'
# ID options (-u, -C, -P, -S) are used for create/update relationship fields
while getopts "x:i:t:d:w:k:h:u:C:P:S:" opt; do # Changed ID options to single char (u, C, P, S), removed a, c, p, s, g
  case ${opt} in
      t )
        title=$OPTARG
        ;;
      d )
        description=$OPTARG
        ;;
      # Removed p, c, g, a, s (name options)

      # ID options using single uppercase letters or 'u'
      u)
        user_id=$OPTARG # Assignee ID
        ;;
      C)
        category_id=$OPTARG # Category ID (Uppercase C)
        ;;
      P)
        priority_id=$OPTARG # Priority ID (Uppercase P)
        ;;
      S)
        status_id=$OPTARG # Status ID (Uppercase S)
        ;;
      w )
        WEBHOOK_URL=$OPTARG
        ;;
      k )
        API_KEY=$OPTARG
        ;;
      i ) # For ticket ID
        TICKET_ID=$OPTARG
        ;;
      x )
        # action to perform
        ACTION=$OPTARG
        ;;
      h )
        # Updated usage message with new options
        echo "Usage: cmd -k <api_key> -x <action> [options]"
        echo "Actions: create, list, get, update, delete, list_categories, list_priorities, list_statuses, list_users"
        echo ""
        echo "CREATE action options:"
        echo "  Required: -t <title> | -d <description> | -u <assignee_user_id> | -C <category_id> | -P <priority_id> | -S <status_id>"
        echo ""
        echo "UPDATE action options:"
        echo "  Required: -i <ticket_id>"
        echo "  Optional: [-t title] [-d description] [-u assignee_user_id] [-C category_id] [-P priority_id] [-S status_id]"
        echo "  Note: Only provide fields you want to change."
        echo ""
        echo "GET/DELETE action options:"
        echo "  Required: -i <ticket_id>"
        echo ""
        echo "LIST actions require no other options."
        echo ""
        echo "Other options: [-w webhook_url]"
        echo ""
        echo "Use list_* actions first to get the required IDs."
        exit 0
        ;;
      \\? )
        echo "Invalid option: -$OPTARG" 1>&2
        exit 1
        ;;
      * )
        # This case might not be reached with standard getopts usage
        echo "Invalid option processing." 1>&2
        exit 1
        ;;
  esac
done


if [ -z "$API_KEY" ]; then
    echo "API_KEY (-k) is required." >&2
    exit 1
fi

if [ -z "$ACTION" ]; then
    echo "Action (-x) is required (create, list, get, update, delete, list_categories, list_priorities, list_statuses, list_users)." >&2
    exit 1
fi


# TITLE_TEMPLATE still used
if [[ "$ACTION" == "create" ]]; then
  TITLE_TEMPLATE=${title:-"New ticket created via script"} # Title still needs a default or check
  # Check required fields for create using new variable names
  if [ -z "$title" ] || [ -z "$description" ] || [ -z "$user_id" ] || [ -z "$category_id" ] || [ -z "$priority_id" ] || [ -z "$status_id" ]; then
      echo "Error: For 'create' action, all required fields must be provided: -t, -d, -u, -C, -P, -S" >&2
      exit 1
  fi
fi

function create_ticket() {
  # Use required ID fields (new names) and REQUIRED description.
  # Revert back to using jq for safer JSON creation, use -c for compact output
  PAYLOAD=$(jq -c -n \
    --arg title "$TITLE_TEMPLATE" \
    --arg description "$description" \
    --argjson assignee_id "$user_id" \
    --argjson category_id "$category_id" \
    --argjson priority_id "$priority_id" \
    --argjson status_id "$status_id" \
    '{title: $title, description: $description, assignee_id: $assignee_id, category_id: $category_id, priority_id: $priority_id, status_id: $status_id}')

  # Informational message to stderr
  echo "Creating ticket with payload:" >&2

  # Send the data via curl to the webhook URL using JSON
  output=$(curl -s -w "\\n%{http_code}" -X POST \
    -H "Authorization: ApiKey $API_KEY" \
    -H "Content-Type: application/json" \
    --data-raw "$PAYLOAD" \
    "$WEBHOOK_URL" 2>/dev/null)
  http_code=$(printf "%s" "$output" | tail -n 1)
  body=$(printf "%s" "$output" | sed '$d')
  printf "%s" "$body" # Print body to stdout
  printf "%s\\n" "$http_code" >&2 # Print status code to stderr
}

function list_tickets() {
    # Informational message to stderr
    echo "Listing tickets..." >&2
    # curl -H "Authorization: ApiKey $API_KEY" "$WEBHOOK_URL"
    output=$(curl -s -w "\\n%{http_code}" -H "Authorization: ApiKey $API_KEY" "$WEBHOOK_URL" 2>/dev/null)
    http_code=$(printf "%s" "$output" | tail -n 1)
    body=$(printf "%s" "$output" | sed '$d')
    printf "%s" "$body"
    printf "%s\\n" "$http_code" >&2
}

function get_ticket() {
    if [ -z "$TICKET_ID" ]; then
        echo "Ticket ID (-i) is required for the 'get' action." >&2
        exit 1
    fi
    # Informational message to stderr
    echo "Getting ticket ID: $TICKET_ID..." >&2
    # Ensure trailing slash for detail view
    # curl -H "Authorization: ApiKey $API_KEY" "$WEBHOOK_URL$TICKET_ID/"
    local target_url="$WEBHOOK_URL$TICKET_ID/"
    output=$(curl -s -w "\\n%{http_code}" -H "Authorization: ApiKey $API_KEY" "$target_url" 2>/dev/null)
    http_code=$(printf "%s" "$output" | tail -n 1)
    body=$(printf "%s" "$output" | sed '$d')
    printf "%s" "$body"
    printf "%s\\n" "$http_code" >&2
}

# Function to list categories
function list_categories() {
    local url="${WEBHOOK_URL%tickets/*}categories/" # Construct URL relative to base tickets URL
    # Informational message to stderr
    echo "Listing categories from $url ..." >&2
    # curl -H "Authorization: ApiKey $API_KEY" "$url"
    output=$(curl -s -w "\\n%{http_code}" -H "Authorization: ApiKey $API_KEY" "$url" 2>/dev/null)
    http_code=$(printf "%s" "$output" | tail -n 1)
    body=$(printf "%s" "$output" | sed '$d')
    printf "%s" "$body"
    printf "%s\\n" "$http_code" >&2
}

# Function to list priorities
function list_priorities() {
    local url="${WEBHOOK_URL%tickets/*}priorities/" # Construct URL relative to base tickets URL
    # Informational message to stderr
    echo "Listing priorities from $url ..." >&2
    # curl -H "Authorization: ApiKey $API_KEY" "$url"
    output=$(curl -s -w "\\n%{http_code}" -H "Authorization: ApiKey $API_KEY" "$url" 2>/dev/null)
    http_code=$(printf "%s" "$output" | tail -n 1)
    body=$(printf "%s" "$output" | sed '$d')
    printf "%s" "$body"
    printf "%s\\n" "$http_code" >&2
}

# Function to list statuses
function list_statuses() {
    local url="${WEBHOOK_URL%tickets/*}statuses/" # Construct URL relative to base tickets URL
    # Informational message to stderr
    echo "Listing statuses from $url ..." >&2
    # curl -H "Authorization: ApiKey $API_KEY" "$url"
    output=$(curl -s -w "\\n%{http_code}" -H "Authorization: ApiKey $API_KEY" "$url" 2>/dev/null)
    http_code=$(printf "%s" "$output" | tail -n 1)
    body=$(printf "%s" "$output" | sed '$d')
    printf "%s" "$body"
    printf "%s\\n" "$http_code" >&2
}

# Function to list users
function list_users() {
    local url="${WEBHOOK_URL%tickets/*}users/" # Construct URL relative to base tickets URL
    # Informational message to stderr
    echo "Listing users from $url ..." >&2
    # curl -H "Authorization: ApiKey $API_KEY" "$url"
    output=$(curl -s -w "\\n%{http_code}" -H "Authorization: ApiKey $API_KEY" "$url" 2>/dev/null)
    http_code=$(printf "%s" "$output" | tail -n 1)
    body=$(printf "%s" "$output" | sed '$d')
    printf "%s" "$body"
    printf "%s\\n" "$http_code" >&2
}

# New function for updating tickets
function update_ticket() {
    if [ -z "$TICKET_ID" ]; then
        echo "Ticket ID (-i) is required for the 'update' action." >&2
        exit 1
    fi

    # Build JSON payload dynamically only with provided fields
    local payload_json="{}"
    local field_provided=false
    [[ -n "$title" ]]          && payload_json=$(echo "$payload_json" | jq --arg v "$title" '.title = $v') && field_provided=true
    [[ -n "$description" ]]    && payload_json=$(echo "$payload_json" | jq --arg v "$description" '.description = $v') && field_provided=true
    # Update payload building for IDs (new names) - use --argjson since IDs should be numbers
    [[ -n "$user_id" ]]        && payload_json=$(echo "$payload_json" | jq --argjson v "$user_id" '.assignee_id = $v') && field_provided=true
    [[ -n "$category_id" ]]    && payload_json=$(echo "$payload_json" | jq --argjson v "$category_id" '.category_id = $v') && field_provided=true
    [[ -n "$priority_id" ]]    && payload_json=$(echo "$payload_json" | jq --argjson v "$priority_id" '.priority_id = $v') && field_provided=true
    [[ -n "$status_id" ]]      && payload_json=$(echo "$payload_json" | jq --argjson v "$status_id" '.status_id = $v') && field_provided=true

    if ! $field_provided ; then
      # Update error message with new options
      echo "Update action requires at least one field to update (-t, -d, -u, -C, -P, -S)." >&2
      exit 1
    fi

    PAYLOAD="$payload_json"

    # Informational message to stderr
    echo "Updating ticket ID $TICKET_ID with payload:" >&2
    local target_url="$WEBHOOK_URL$TICKET_ID/"
    # Send PUT request
    output=$(curl -s -w "\\n%{http_code}" -X PUT -H "Authorization: ApiKey $API_KEY" -H "Content-Type: application/json" --data "$PAYLOAD" "$target_url" 2>/dev/null)
    http_code=$(printf "%s" "$output" | tail -n 1)
    body=$(printf "%s" "$output" | sed '$d')
    printf "%s" "$body"
    printf "%s\\n" "$http_code" >&2
}

# New function for deleting tickets
function delete_ticket() {
     if [ -z "$TICKET_ID" ]; then
        echo "Ticket ID (-i) is required for the 'delete' action." >&2
        exit 1
    fi
    # Informational message to stderr
    echo "Deleting ticket ID: $TICKET_ID..." >&2
    # Ensure trailing slash for detail view
    # curl -X DELETE -H "Authorization: ApiKey $API_KEY" "$WEBHOOK_URL$TICKET_ID/"
    local target_url="$WEBHOOK_URL$TICKET_ID/"
    output=$(curl -s -w "\\n%{http_code}" -X DELETE -H "Authorization: ApiKey $API_KEY" "$target_url" 2>/dev/null)
    http_code=$(printf "%s" "$output" | tail -n 1)
    body=$(printf "%s" "$output" | sed '$d')
    # For DELETE, the body is often empty (204 No Content), but print it anyway
    printf "%s" "$body"
    printf "%s\\n" "$http_code" >&2
}


case $ACTION in
    create)
        create_ticket
        ;;
    list)
        list_tickets
        ;;
    get)
        get_ticket
        ;;
    update) # Added update case
        update_ticket
        ;;
    delete) # Added delete case
        delete_ticket
        ;;
    # Add cases for new list actions
    list_categories)
        list_categories
        ;;
    list_priorities)
        list_priorities
        ;;
    list_statuses)
        list_statuses
        ;;
    list_users)
        list_users
        ;;
    *)
        # Updated invalid action message
        echo "Invalid action: $ACTION. Use 'create', 'list', 'get', 'update', 'delete', 'list_categories', 'list_priorities', 'list_statuses', or 'list_users'." >&2
        exit 1
        ;;
esac

exit 0