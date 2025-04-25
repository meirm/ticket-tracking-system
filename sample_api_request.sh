#!/bin/bash
WEBHOOK_URL="http://localhost:8000/tickets/api/v1/tickets/"


# Added -i for ticket ID
# Use -x for action: create, list, get, update, delete
# Field options (-t, -d, -p, etc.) are used for 'create' and 'update'
# -i (ticket ID) is required for 'get', 'update', 'delete'
while getopts "x:i:t:d:p:c:g:a:s:w:k:he" opt; do
  case ${opt} in
      t )
        title=$OPTARG
        ;;
      d )
        description=$OPTARG
        ;;
      p )
        priority=$OPTARG
        ;;
      c )
        category=$OPTARG
        ;;
      g )
        assigned_group=$OPTARG
        ;;
      a )
        assignee=$OPTARG
        ;;
      s)
        status=$OPTARG
        ;;
      w )
        WEBHOOK_URL=$OPTARG
        ;;
      k )
        API_KEY=$OPTARG
        ;;
      i ) # Added for ticket ID
        TICKET_ID=$OPTARG
        ;;
      x )
        # action to perform
        ACTION=$OPTARG
        ;;
      h )
        # Updated usage message
        echo "Usage: cmd -k <api_key> -x <action> [options]"
        echo "Actions: create, list, get, update, delete"
        echo "Options for create/update: [-t title] [-d description] [-p priority] [-c category] [-g assigned_group] [-a assignee] [-s status]"
        echo "Options for get/update/delete: -i <ticket_id>"
        echo "Other options: [-w webhook_url]"
        echo ""
        echo "Default values for create: priority=High, category=Support, assigned_group=staff, assignee=meirm, status=Open"
        exit 0
        ;;
      \\? )
        echo "Invalid option: $OPTARG" 1>&2
        exit 1
        ;;
      * )
        echo "Invalid option: $OPTARG" 1>&2
        exit 1
        ;;
  esac
done


if [ -z "$API_KEY" ]; then
    echo "API_KEY (-k) is required." >&2
    exit 1
fi

if [ -z "$ACTION" ]; then
    echo "Action (-x) is required (create, list, get, update, delete)." >&2
    exit 1
fi


# set default values for create action
if [[ "$ACTION" == "create" ]]; then
  TITLE_TEMPLATE=${title:-"New ticket created"}
  BODY_TEMPLATE=${description:-"A new ticket has been created by the user"}
  PRIORITY=${priority:-"High"}
  CATEGORY=${category:-"Support"}
  ASSIGNED_GROUP=${assigned_group:-"staff"}
  ASSIGNEE=${assignee:-"meirm"}
  STATUS=${status:-"Open"} # Default status for creation
fi

function create_ticket() {
  # Format the JSON payload using defaults if not provided
  PAYLOAD=$(jq -n \
    --arg title "$TITLE_TEMPLATE" \
    --arg description "$BODY_TEMPLATE" \
    --arg priority "$PRIORITY" \
    --arg assigned_group "$ASSIGNED_GROUP" \
    --arg category "$CATEGORY" \
    --arg assignee "$ASSIGNEE" \
    --arg status "$STATUS" \
    '{title: $title, description: $description, priority: $priority, category: $category, assigned_group: $assigned_group, assignee: $assignee, status: $status}')

  echo "Creating ticket with payload:"
  echo "$PAYLOAD"
  # Send the data via curl to the webhook URL
  curl -H "Authorization: ApiKey $API_KEY" -H "Content-Type: application/json" --data "$PAYLOAD" "$WEBHOOK_URL"
}

function list_tickets() {
    echo "Listing tickets..."
    curl -H "Authorization: ApiKey $API_KEY" "$WEBHOOK_URL"
}

function get_ticket() {
    if [ -z "$TICKET_ID" ]; then
        echo "Ticket ID (-i) is required for the 'get' action." >&2
        exit 1
    fi
    echo "Getting ticket ID: $TICKET_ID..."
    # Ensure trailing slash for detail view
    curl -H "Authorization: ApiKey $API_KEY" "$WEBHOOK_URL$TICKET_ID/"
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
    [[ -n "$priority" ]]       && payload_json=$(echo "$payload_json" | jq --arg v "$priority" '.priority = $v') && field_provided=true
    [[ -n "$category" ]]       && payload_json=$(echo "$payload_json" | jq --arg v "$category" '.category = $v') && field_provided=true
    [[ -n "$assigned_group" ]] && payload_json=$(echo "$payload_json" | jq --arg v "$assigned_group" '.assigned_group = $v') && field_provided=true
    [[ -n "$assignee" ]]       && payload_json=$(echo "$payload_json" | jq --arg v "$assignee" '.assignee = $v') && field_provided=true
    [[ -n "$status" ]]         && payload_json=$(echo "$payload_json" | jq --arg v "$status" '.status = $v') && field_provided=true

    if ! $field_provided ; then
      echo "Update action requires at least one field to update (-t, -d, -p, etc.)." >&2
      exit 1
    fi

    PAYLOAD="$payload_json"

    echo "Updating ticket ID $TICKET_ID with payload:"
    echo "$PAYLOAD"
    # Send PUT request (as per dev-env rule)
    # Ensure trailing slash for detail view
    curl -X PUT -H "Authorization: ApiKey $API_KEY" -H "Content-Type: application/json" --data "$PAYLOAD" "$WEBHOOK_URL$TICKET_ID/"

}

# New function for deleting tickets
function delete_ticket() {
     if [ -z "$TICKET_ID" ]; then
        echo "Ticket ID (-i) is required for the 'delete' action." >&2
        exit 1
    fi
    echo "Deleting ticket ID: $TICKET_ID..."
    # Ensure trailing slash for detail view
    curl -X DELETE -H "Authorization: ApiKey $API_KEY" "$WEBHOOK_URL$TICKET_ID/"
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
    *)
        echo "Invalid action: $ACTION. Use 'create', 'list', 'get', 'update', or 'delete'." >&2
        exit 1
        ;;
esac

exit 0