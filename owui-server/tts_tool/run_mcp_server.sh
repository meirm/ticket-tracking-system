#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    for i in `cat .env`; do eval export $i; done
fi

# Set default values if not provided
export TTS_API_TOKEN=${TTS_API_TOKEN:-"my_test_token"}
export TTS_API_URL=${TTS_API_URL:-"https://tts.cyborg.fi/tickets/api/v1/"}

# Run the MCP server
echo "Starting TTS MCP Server..."
echo "TTS_API_URL: $TTS_API_URL"
echo "TTS_API_TOKEN: ${TTS_API_TOKEN:0:8}..."

python tts_mcp_server.py