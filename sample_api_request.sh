#!/bin/bash -v
WEBHOOK_URL="http://localhost:9000/tickets/api/v1/create/"
API_KEY="2b8263c9fa42c597bfe364288e59ace872bc8bd08a8b429dc393ce30f5b009bc"
TITLE_TEMPLATE="New ticket created"
BODY_TEMPLATE="A new ticket has been created by the user"
PRIORITY="High"

# Format the JSON payload
PAYLOAD=$(jq -n \
  --arg title "$TITLE_TEMPLATE" \
  --arg description "$BODY_TEMPLATE" \
  --arg priority "$PRIORITY" \
  --arg category "Support" \
  --arg assigned_group "staff" \
  --arg assignee "meirm" \
  '{title: $title, description: $description, priority: $priority, category: $category, assigned_group: $assigned_group, assignee: $assignee, status: "Open"}')

echo $PAYLOAD
# Send the data via curl to the webhook URL
curl -v -H "X-API-AUTH: $API_KEY" -H "Content-Type: application/json" --data "$PAYLOAD" "$WEBHOOK_URL" >/dev/null
