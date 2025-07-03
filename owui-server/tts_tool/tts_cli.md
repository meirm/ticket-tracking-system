# TTS CLI Manual

A command-line tool for interacting with the Ticket Tracking System (TTS).

---

## Table of Contents
- [Getting Started](#getting-started)
- [Basic Usage](#basic-usage)
- [Commands](#commands)
  - [list-tickets](#list-tickets)
  - [create-ticket](#create-ticket)
  - [get-ticket](#get-ticket)
  - [update-ticket](#update-ticket)
  - [delete-ticket](#delete-ticket)
  - [list-users](#list-users)
  - [list-categories](#list-categories)
  - [list-priorities](#list-priorities)
  - [list-statuses](#list-statuses)
  - [list-groups](#list-groups)
  - [get-user-groups](#get-user-groups)
  - [get-group-members](#get-group-members)
- [Bash Aliases](#bash-aliases)
- [Tips](#tips)

---

## Getting Started

1. Make sure you have Python 3 and the required dependencies installed.
2. Set up your environment variables (see `.env.example`).
3. Run the CLI using:
   ```bash
   python3 owui-server/tts_tool/tts_cli.py [COMMAND] [OPTIONS]
   ```

---

## Basic Usage

All commands are run as subcommands of the CLI script. Use `--help` with any command to see options.

Example:
```bash
python3 owui-server/tts_tool/tts_cli.py list-tickets --assignee meir
```

---

## Commands

### list-tickets
List tickets, optionally filtered by assignee or status.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py list-tickets [--assignee USERNAME] [--status STATUS]
```

**Examples:**
- List all tickets:
  ```bash
  python3 owui-server/tts_tool/tts_cli.py list-tickets
  ```
- List tickets assigned to you:
  ```bash
  python3 owui-server/tts_tool/tts_cli.py list-tickets --assignee meir
  ```
- List tickets with status 'Open':
  ```bash
  python3 owui-server/tts_tool/tts_cli.py list-tickets --status Open
  ```

### create-ticket
Create a new ticket. You can specify assignee, category, priority, status, and group by name (case-insensitive). Defaults are provided for all fields except title and description.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py create-ticket TITLE DESCRIPTION [--assignee USERNAME] [--category CATEGORY] [--priority PRIORITY] [--status STATUS] [--group GROUP]
```

**Defaults:**
- assignee: meir
- category: Support
- priority: Medium
- status: Open
- group: (none)

**Examples:**
- Create a ticket with all defaults:
  ```bash
  python3 owui-server/tts_tool/tts_cli.py create-ticket "Bug in login" "Login fails on Safari"
  ```
- Create a ticket with custom priority and category:
  ```bash
  python3 owui-server/tts_tool/tts_cli.py create-ticket "Bug in login" "Login fails on Safari" --priority high --category bug
  ```
- Create a ticket with custom assignee and status:
  ```bash
  python3 owui-server/tts_tool/tts_cli.py create-ticket "Bug in login" "Login fails on Safari" --assignee meir --status "in progress"
  ```

> **Note:**
> - All options are case-insensitive (e.g., `--priority High` or `--priority high` both work).
> - If you specify an invalid value, the CLI will show an error and list valid options.
> - You can see valid values for each field using the `list-users`, `list-categories`, `list-priorities`, `list-statuses`, and `list-groups` commands.

### get-ticket
Get details for a ticket by ID.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py get-ticket TICKET_ID
```

**Example:**
```bash
python3 owui-server/tts_tool/tts_cli.py get-ticket 123
```

### update-ticket
Update a ticket's title or description.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py update-ticket TICKET_ID [--title TITLE] [--description DESCRIPTION]
```

**Example:**
```bash
python3 owui-server/tts_tool/tts_cli.py update-ticket 123 --title "New Title" --description "Updated description"
```

> **Note:** If you do not provide any fields to update, the CLI will warn you and show available options.

### delete-ticket
Delete a ticket by ID.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py delete-ticket TICKET_ID
```

**Example:**
```bash
python3 owui-server/tts_tool/tts_cli.py delete-ticket 123
```

### list-users
List all users.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py list-users
```

### list-categories
List all categories.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py list-categories
```

### list-priorities
List all priorities.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py list-priorities
```

### list-statuses
List all statuses.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py list-statuses
```

### list-groups
List all groups.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py list-groups
```

### get-user-groups
Get all groups for a user by username.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py get-user-groups USERNAME
```

**Example:**
```bash
python3 owui-server/tts_tool/tts_cli.py get-user-groups meir
```

This will print all groups the user belongs to.

### get-group-members
List all users who are members of a given group.

**Usage:**
```bash
python3 owui-server/tts_tool/tts_cli.py get-group-members GROUPNAME
```

**Example:**
```bash
python3 owui-server/tts_tool/tts_cli.py get-group-members Admin
```

This will print all users in the 'Admin' group.

> **Note:**
> - If the group does not exist, you will see a friendly message: `Group '<groupname>' not found.`
> - If the group exists but has no members, you will see: `No members found for group '<groupname>'.`

---

## Bash Aliases

Add these to your `~/.bashrc` or `~/.zshrc` for convenience:

```bash
alias tts='python3 /full/path/to/owui-server/tts_tool/tts_cli.py'
alias tts-list='tts list-tickets'
alias tts-create='tts create-ticket'
alias tts-get='tts get-ticket'
alias tts-update='tts update-ticket'
alias tts-delete='tts delete-ticket'
alias tts-users='tts list-users'
alias tts-cats='tts list-categories'
alias tts-prios='tts list-priorities'
alias tts-statuses='tts list-statuses'
alias tts-groups='tts list-groups'
# List tickets assigned to you (replace 'meir' with your username if needed)
alias tts-mytickets='tts list-tickets --assignee meir'
```

---

## Tips

- Use `--help` with any command to see available options.
- Use `tts list-statuses` and `tts list-priorities` to see valid values for those fields.
- If you run `update-ticket` without any fields, the CLI will show you which fields you can update.
- For shell completion, use `--install-completion` or `--show-completion`.
- If you need to filter by other fields (like due date), you may need to extend the CLI and backend.

---

**For more information, see the project README or contact your system administrator.** 