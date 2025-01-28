#!/bin/bash
WEBHOOK_URL="http://localhost:9000/tickets/api/v1/create/"


while getopts "t:d:p:c:g:a:s:w:k:he" opt; do
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
    h )
      echo "Usage: cmd [-t title] [-d description] [-p priority] [-c category] [-g assigned_group] [-a assignee] [-s status]" 1>&2
      echo "Default values: priority=High, category=Support, assigned_group=staff, assignee=meirm" 1>&2
      exit 0
      ;;
    \? )
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
    echo "API_KEY is not set"
    exit 1
fi


# set default values
TITLE_TEMPLATE=${title:-"New ticket created"}
BODY_TEMPLATE=${description:-"A new ticket has been created by the user"}
PRIORITY=${priority:-"High"}
CATEGORY=${category:-"Support"}
ASSIGNED_GROUP=${assigned_group:-"staff"}
ASSIGNEE=${assignee:-"meirm"}
# Format the JSON payload
PAYLOAD=$(jq -n \
  --arg title "$TITLE_TEMPLATE" \
  --arg description "$BODY_TEMPLATE" \
  --arg priority "$PRIORITY" \
  --arg assigned_group "$ASSIGNED_GROUP" \
  --arg category "$CATEGORY" \
  --arg assignee "$ASSIGNEE" \
  '{title: $title, description: $description, priority: $priority, category: $category, assigned_group: $assigned_group, assignee: $assignee, status: "Open"}')

echo $PAYLOAD
# Send the data via curl to the webhook URL
curl -v -H "X-API-AUTH: $API_KEY" -H "Content-Type: application/json" --data "$PAYLOAD" "$WEBHOOK_URL" >/dev/null
