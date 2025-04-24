# Cyborg Ticketing System - API Backend

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is the API backend for a ticket tracking system built with Django and Django REST Framework.

## Features

*   **API Endpoints:** Provides RESTful API endpoints for managing:
    *   Tickets (CRUD, filtering)
    *   Comments (CRUD, filtering)
    *   API Keys (CRUD, activate/deactivate)
    *   Users, Groups, Categories, Statuses, Priorities (via related fields)
*   **Authentication:** Supports Token-based authentication (and Session for Browsable API).
*   **Permissions:** Basic permission handling (extensible).
*   **Filtering:** Allows filtering ticket lists via query parameters.
*   **Admin Interface:** Standard Django admin for backend management.

## Setup and Installation

### Prerequisites

*   Python 3.x
*   Pip
*   Virtualenv (Recommended)
*   PostgreSQL (Recommended for production) or another compatible database.

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ticket-tracking-system
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the project root directory (where `manage.py` is located) and add your database credentials:
    ```dotenv
    DB_ENGINE=postgresql
    DB_NAME=your_db_name
    DB_USERNAME=your_db_user
    DB_PASS=your_db_password
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    ```
    *(If you are using SQLite for local development, you can skip this step, but PostgreSQL is recommended for production.)*

5.  **Apply database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a superuser (for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create an admin account.

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API backend should now be running at `http://127.0.0.1:8000/`.

## API Usage

*   **Endpoints:** The main API endpoints are available under:
    *   `/tickets/api/v1/` (Tickets and Comments)
    *   `/accounts/api/v1/` (API Keys)
*   **Authentication:** Include your API token in the `Authorization` header: `Authorization: Token YOUR_API_TOKEN`.
*   **Browsable API:** Accessing the endpoints in a web browser while logged in via session authentication will show the DRF Browsable API for easier interaction during development.
*   **Examples:** (Use tools like `curl` or Postman)
    *   List Tickets: `GET /tickets/api/v1/tickets/`
    *   Create Ticket: `POST /tickets/api/v1/tickets/` with JSON data.
    *   Get API Keys: `GET /accounts/api/v1/keys/`
*   **Admin Panel:** Access the Django admin interface at `http://127.0.0.1:8000/admin/`.

## Contributing

Contributions are welcome! Please follow standard fork-and-pull-request workflows. Ensure code style follows Black formatting.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
