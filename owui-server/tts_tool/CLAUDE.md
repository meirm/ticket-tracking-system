# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the FastAPI server (preferred method)
./run_tts_tool.sh

# Alternative: Start with uvicorn directly
uvicorn main:main_app --port 8888 --reload

# Start the MCP server
./run_mcp_server.sh

# Alternative: Start MCP server directly
python tts_mcp_server.py
```

### Environment Configuration
- Copy `dot.env.example` to `.env` and configure:
  - `TTS_API_URL`: Base URL ending with `/tickets/api/v1/`
  - `TTS_API_TOKEN`: Authentication token for the TTS API

### CLI Usage
```bash
# Use the CLI tool for ticket management
python3 tts_cli.py [command] [options]

# Examples:
python3 tts_cli.py list-tickets --assignee meir
python3 tts_cli.py create-ticket "Title" "Description"
python3 tts_cli.py get-ticket 123
```

## Architecture Overview

### Core Components
- **main.py**: FastAPI application with two components:
  - `tts_app`: TTS proxy endpoints under `/tts/` prefix
  - `main_app`: Root application with MCP function endpoints
- **tts_client.py**: HTTP client for communicating with external TTS API
- **models.py**: Pydantic models for request/response validation
- **tts_cli.py**: Command-line interface for ticket management
- **tts_mcp_server.py**: FastMCP server implementation exposing TTS functions as MCP tools

### API Structure
The application provides multiple interfaces:
1. **REST API**: Traditional HTTP endpoints under `/tts/` prefix
2. **MCP Functions**: Direct Python function calls for IDE/AI integration
3. **MCP Server**: FastMCP server exposing TTS functions as MCP tools for AI agents

### Key MCP Functions
Located in `main.py`, these functions are the primary interface for task management:
- `list_tickets()`: List tickets with optional filtering
- `search_tickets()`: Search tickets by query and filters
- `get_ticket()`: Retrieve ticket details
- `create_ticket()`: Create new tickets
- `update_ticket()`: Update existing tickets
- `add_comment()`: Add comments to tickets
- `close_ticket()`: Close tickets
- `batch_close_tickets()`: Close multiple tickets

### Data Models
- Request/response models in `models.py` handle validation
- Automatic mapping between proxy models and Django backend fields
- Support for users, categories, priorities, statuses, and groups

## Task-Driven Development Workflow

This project follows a task-driven development approach:
1. Use `list_tickets()` to see available tasks
2. Use `get_ticket()` to understand specific tasks
3. Use `add_comment()` to log progress and findings
4. Use `update_ticket()` to change status or assignee
5. Use `close_ticket()` when tasks are complete

Always use the MCP functions rather than HTTP endpoints for task management operations.

## Configuration Requirements

- **TTS_API_URL**: Must end with `/tickets/api/v1/` (enforced with warnings)
- **TTS_API_TOKEN**: Required for authentication
- The application validates these on startup

## CLI Tools

### Primary CLI (`tts_cli.py`)
- Modern Python CLI with typer
- Supports all ticket operations with name-based lookups
- Case-insensitive input for categories, priorities, statuses
- Comprehensive help and error messages

### Legacy Shell Script (`tts_cli_sample.sh`)
- Bash-based CLI using curl
- Requires manual ID lookups
- More verbose but shows raw HTTP interactions

## Dependencies

- **FastAPI**: Web framework for API endpoints
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **httpx**: HTTP client for TTS API communication
- **typer**: CLI framework (for tts_cli.py)
- **fastmcp**: FastMCP framework for MCP server implementation

## MCP Server Usage

The TTS MCP Server (`tts_mcp_server.py`) exposes all TTS functionality as MCP tools:

### Available MCP Tools
- **Ticket Operations**: `list_tickets`, `search_tickets`, `get_ticket`, `create_ticket`, `update_ticket`, `delete_ticket`, `close_ticket`, `batch_close_tickets`
- **Comments**: `add_comment`
- **Reference Data**: `list_users`, `list_categories`, `list_priorities`, `list_statuses`, `list_groups`
- **User/Group Management**: `get_user_groups`, `get_group_members`
- **Summaries**: `list_summaries`, `create_summary`, `get_summary`, `update_summary`, `delete_summary`, `archive_all_summaries`
- **Utilities**: `health_check`, `get_profile`

### Running the MCP Server
```bash
# Using the run script
./run_mcp_server.sh

# Or directly
python tts_mcp_server.py
```

### Testing the MCP Server
```bash
# Run the test suite
python test_mcp_server.py
```

### Claude Configuration for MCP Server
To configure Claude to use the TTS MCP server, add this configuration to your Claude settings:

```json
{
  "mcpServers": {
    "tts": {
      "command": "python",
      "args": ["/path/to/tts_tool/tts_mcp_server.py"],
      "env": {
        "TTS_API_URL": "https://your-tts-api-url/tickets/api/v1/",
        "TTS_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

**Configuration Notes:**
- Replace `/path/to/tts_tool/tts_mcp_server.py` with the full absolute path to your tts_mcp_server.py file
- Replace `https://your-tts-api-url/tickets/api/v1/` with your actual TTS API URL
- Replace `your-api-token` with your actual API token
- Ensure the TTS API URL ends with `/tickets/api/v1/`
- The MCP server will automatically load environment variables from `.env` file if present
- Use absolute paths in the args array rather than relative paths with cwd