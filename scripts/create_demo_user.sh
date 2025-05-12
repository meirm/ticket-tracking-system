#!/bin/bash

# Script to create a user named 'demo' via the API
# Requires: curl, a valid superuser API key, and the API server running

API_URL="http://localhost:8000/accounts/api_create_user/"
SUPERUSER_API_KEY="43b098b8681dc116c143eda335f16c563758884c6f9056264e9d48a29599a7b5"

# User details
USERNAME="demo"
EMAIL="demo@example.com"
FIRST_NAME="Demo"
LAST_NAME="User"
ENABLED=true
GENERATE_API_KEY=true

# Make the API call
curl -X POST "$API_URL" \
  -H "X-API-AUTH: $SUPERUSER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "'$USERNAME'",
    "email": "'$EMAIL'",
    "first_name": "'$FIRST_NAME'",
    "last_name": "'$LAST_NAME'",
    "enabled": '$ENABLED',
    "generate_api_key": '$GENERATE_API_KEY'
  }'

# Notes:
# - The response will include the new user's details, a randomly generated password, and the API key.
# - You can modify the variables above to create different users as needed. 