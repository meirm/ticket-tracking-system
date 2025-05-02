#!/bin/bash
# This script lists tickets from the ticket tracking system using optional filters.
# It sends a GET request to the API and prints the result.

# Default API endpoint for listing tickets
# You can override this by setting the API_URL environment variable before running the script
API_URL=${API_URL:-"https://tts.cyborg.fi/tickets/api/v1/"}
API_KEY=${API_KEY:-"1234567890"}

# Initialize filter variables
status=""
priority=""
assignee=""
issuer=""
from_date=""
to_date=""
due_date=""

# Parse command-line options for filters
while getopts "s:p:a:i:f:t:d:w:k:h" opt; do
  case ${opt} in
    s )
      status=$OPTARG
      ;;
    p )
      priority=$OPTARG
      ;;
    a )
      assignee=$OPTARG
      ;;
    i )
      issuer=$OPTARG
      ;;
    f )
      from_date=$OPTARG
      ;;
    t )
      to_date=$OPTARG
      ;;
    d )
      due_date=$OPTARG
      ;;
    w )
      API_URL=$OPTARG
      ;;
    k )
      API_KEY=$OPTARG
      ;;
    h )
      echo "Usage: $0 [-s status] [-p priority] [-a assignee] [-i issuer] [-f from_date] [-t to_date] [-d due_date] [-w api_url] [-k api_key]" 1>&2
      echo "Example: $0 -s Open -p High -a meirm -k YOUR_API_KEY" 1>&2
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

# Check for API key
if [ -z "$API_KEY" ]; then
    echo "API_KEY is not set"
    exit 1
fi

# Build query string from provided filters
query_params=""
[ -n "$status" ] && query_params+="status=$status&"
[ -n "$priority" ] && query_params+="priority=$priority&"
[ -n "$assignee" ] && query_params+="assignee=$assignee&"
[ -n "$issuer" ] && query_params+="issuer=$issuer&"
[ -n "$from_date" ] && query_params+="from_date=$from_date&"
[ -n "$to_date" ] && query_params+="to_date=$to_date&"
[ -n "$due_date" ] && query_params+="due_date=$due_date&"

# Remove trailing '&' if present
query_params=${query_params%&}

# Construct full URL
if [ -n "$query_params" ]; then
    FULL_URL="$API_URL/list/?$query_params"
else
    FULL_URL="$API_URL/list/"
fi

# Print the URL for debugging
# echo "Requesting: $FULL_URL"

# Send GET request to list tickets
curl -v -H "X-API-AUTH: $API_KEY" "$FULL_URL"

# End of script
