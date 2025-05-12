#!/bin/bash

# Sample script to add, remove, or view a user's groups via the API
# Usage:
#   ./sample_user_groups.sh view <username>
#   ./sample_user_groups.sh add <username> <group>
#   ./sample_user_groups.sh remove <username> <group>
#
# Requires: curl, a valid superuser API key, and the API server running

# Set the API endpoint URL (change if your server is running elsewhere)
API_URL="http://localhost:8000/accounts/api_user_groups/"

# Set your superuser API key here
SUPERUSER_API_KEY="<SUPERUSER_API_KEY>"  # <-- Replace with your actual superuser API key

# Check arguments
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 view <username>"
  echo "       $0 add <username> <group>"
  echo "       $0 remove <username> <group>"
  exit 1
fi

ACTION="$1"
USERNAME="$2"
GROUP="$3"

case "$ACTION" in
  view)
    # View all groups for a user
    curl -X GET "$API_URL?username=$USERNAME" \
      -H "X-API-AUTH: $SUPERUSER_API_KEY"
    ;;
  add)
    # Add user to group
    if [ -z "$GROUP" ]; then
      echo "Group name required for add action."
      exit 1
    fi
    curl -X POST "$API_URL" \
      -H "X-API-AUTH: $SUPERUSER_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"username": "'$USERNAME'", "group": "'$GROUP'"}'
    ;;
  remove)
    # Remove user from group
    if [ -z "$GROUP" ]; then
      echo "Group name required for remove action."
      exit 1
    fi
    curl -X DELETE "$API_URL" \
      -H "X-API-AUTH: $SUPERUSER_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"username": "'$USERNAME'", "group": "'$GROUP'"}'
    ;;
  *)
    echo "Unknown action: $ACTION"
    echo "Valid actions: view, add, remove"
    exit 1
    ;;
esac

# Notes:
# - Replace <SUPERUSER_API_KEY> with your actual API key.
# - You can modify the API_URL if your server is running elsewhere.
# - The script prints the API response directly. 