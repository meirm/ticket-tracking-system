# Ticket Tracking System (TTS) Proxy Server

This directory contains a FastAPI server (`main.py`) that acts as a proxy or intermediary for an external Ticket Tracking System (TTS).

It provides a standardized API interface for common TTS operations like creating, listing, getting, updating, closing tickets, and adding comments.

## Setup

1.  **Navigate to the directory:**
    ```bash
    cd servers/ticket-tracking-system
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables:**
    This server requires the URL and authentication credentials for your *actual* TTS API. Set the following environment variables:
    ```bash
    # The base URL of your actual TTS API (must end with /tickets/api/v1/)
    export TTS_API_URL="https://your-tts-api.com/tickets/api/v1/"
    
    # Your actual API token/key for the TTS
    export TTS_API_TOKEN="your_actual_api_token_or_key"
    ```
    **Note:** The proxy will warn you if TTS_API_URL does not end with `/tickets/api/v1/`.

## Running the Server

Once the setup is complete, run the server using Uvicorn:

```bash
# The --reload flag automatically restarts the server when code changes
# Use --port to specify a different port if needed (e.g., 8888)
uvicorn main:main_app --reload --port 8888
```

The API documentation will be available at `http://localhost:8888/tts/docs` (or your chosen port).

## Interacting with the API

You can use tools like `curl`, Postman, or build a frontend application to interact with the API endpoints provided by this server (e.g., `POST /tts/tickets`, `GET /tts/tickets/{ticket_id}`). Refer to the `/tts/docs` page for details on available endpoints and request/response schemas.

### Quickstart: Example cURL Commands

**Read a ticket:**
```bash
curl -H "X-API-AUTH: $TTS_API_TOKEN" http://localhost:8888/tts/tickets/811
```

**Update a ticket (e.g., change status):**
```bash
curl -X PUT -H "X-API-AUTH: $TTS_API_TOKEN" -H "Content-Type: application/x-www-form-urlencoded" \
  -d "status=Closed" \
  http://localhost:8888/tts/tickets/811
```

**Close a ticket (recommended way):**
```bash
curl -X POST -H "X-API-AUTH: $TTS_API_TOKEN" \
  http://localhost:8888/tts/tickets/811/close
```

- All update and close operations use form data (`application/x-www-form-urlencoded`).
- The `/close` endpoint will set the ticket status to `Closed` for you.

## Features
- Create, list, get, update, and close tickets
- Add comments to tickets
- All endpoints are under `/tts/` (e.g., `/tts/tickets`, `/tts/tickets/{id}`)
- `/tts/tickets/{ticket_id}/close` endpoint for easy closing
- Automatic mapping between proxy models and Django backend fields
- Robust error handling and normalization

## Notes
- The proxy expects the backend to accept status names (e.g., `Closed`) for status updates.
- If you encounter issues, check the logs for warnings about TTS_API_URL or backend responses.
- For advanced usage, see the FastAPI docs at `/tts/docs` after starting the server.
