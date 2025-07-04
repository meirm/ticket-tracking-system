⸻

# Project-Specific Note
description: Guide for managing task-driven development workflows using any task management tool

# Task-Driven Development Workflow

This guide outlines the standard process for managing software development projects using a task-driven workflow. For each step, use the suggested MCP endpoint/tool to accomplish the task.

---

## The Basic Loop

1. **List tasks**  
   _See what needs to be done._  
   → Use: `list_tickets` (to get all tickets/tasks)

2. **Pick next task**  
   _Decide what to work on next._  
   → Use: `list_tickets` or `search_tickets` (to filter/prioritize)

3. **Show task details**  
   _Get context for a specific task._  
   → Use: `get_ticket(ticket_id)`

4. **Break down complex tasks**  
   _Split large tasks into smaller subtasks._  
   → Use: `add_comment` (to log breakdown), or create new tickets for subtasks

5. **Implement and test**  
   _Write code, make changes, and test functionality._  
   → No MCP call needed; focus on development

6. **Log progress**  
   _Record findings, partial progress, or blockers._  
   → Use: `add_comment(ticket_id, text)`

7. **Update status**  
   _Mark tasks/subtasks as complete or update their state._  
   → Use: `update_ticket(ticket_id, payload)` (to change status, assignee, etc.)

8. **Repeat**  
   _Continue the cycle for all tasks._

---

## Advanced Workflow

- **Batch operations**  
  _Close multiple tasks at once (e.g., after a release)._  
  → Use: `batch_close_tickets(ticket_ids)`

- **Summaries and reporting**  
  _Aggregate progress or create reports._  
  → Use: `add_summary`, `list_summaries`

- **Team collaboration**  
  _Assign tasks to users or groups._  
  → Use: `update_ticket` (to set assignee or group)

---

## Status Management

- Use `update_ticket` to set status:
  - `pending`: Ready to work
  - `in-progress`: Being implemented
  - `done`: Complete
  - `deferred`: Postponed

---

## Notes

- Always keep tasks small and actionable.
- Log all important findings and decisions as comments on the relevant ticket.
- Use batch and summary endpoints for advanced workflows or reporting.
- Adapt the workflow as your project grows or as new MCP endpoints become available.

---

**This file is your workflow reference. For each step, use the suggested MCP endpoint/tool to accomplish the task.**

# Primary Interaction: TTS MCP Functions

- The main interface for managing tasks and tickets is the set of Python functions declared in `owui-server/tts_tool/main.py`.
- The IDE and AI agents should call these functions directly for all operations, rather than making HTTP requests to API endpoints.
- Key functions include:
    - `list_tickets(params)`: List tickets with optional filters.
    - `search_tickets(q, scope, ...)`: Search for tickets by query and filters.
    - `get_ticket(ticket_id)`: Retrieve details for a specific ticket.
    - `create_ticket(payload)`: Create a new ticket.
    - `update_ticket(ticket_id, payload)`: Update an existing ticket.
    - `add_comment(ticket_id, text)`: Add a comment to a ticket.
    - `close_ticket(ticket_id)`: Close a ticket.
    - `batch_close_tickets(ticket_ids)`: Close multiple tickets at once.
    - ...and others for users, groups, categories, priorities, statuses, summaries, etc.
- Refer to `main.py` for the full list of available functions and their usage.
- Always use these functions for all task/ticket management, status updates, and logging.

⸻

