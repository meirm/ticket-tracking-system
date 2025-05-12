#!/bin/bash

# Sample script to create a new user via the API
# This script demonstrates how to call the api_create_user endpoint
# Requires: curl, a valid superuser API key, and the API server running

# Set the API endpoint URL (change if your server is running elsewhere)
API_URL="http://localhost:8000/accounts/api_create_user/"

# Set your superuser API key here
SUPERUSER_API_KEY="<SUPERUSER_API_KEY>"  # <-- Replace with your actual superuser API key

# Set the new user's details
NEW_USERNAME="newuser"           # Required: Username for the new user
NEW_EMAIL="newuser@example.com"  # Required: Email for the new user
FIRST_NAME="New"                 # Optional: First name
LAST_NAME="User"                 # Optional: Last name
ENABLED=true                      # Optional: Set to true (enabled) or false (disabled), default is true
GENERATE_API_KEY=true             # Optional: Set to true to generate an API key for the new user

# Make the API call using curl
curl -X POST "$API_URL" \
  -H "X-API-AUTH: $SUPERUSER_API_KEY" \  # API key for authentication (must be a superuser)
  -H "Content-Type: application/json" \  # Specify JSON payload
  -d '{
    "username": "'$NEW_USERNAME'",
    "email": "'$NEW_EMAIL'",
    "first_name": "'$FIRST_NAME'",
    "last_name": "'$LAST_NAME'",
    "enabled": '$ENABLED',
    "generate_api_key": '$GENERATE_API_KEY'
  }'

# Notes:
# - The response will include the new user's details, a randomly generated password, and the API key if requested.
# - Make sure to replace <SUPERUSER_API_KEY> with your actual API key.
# - You can modify the variables above to create different users as needed. 