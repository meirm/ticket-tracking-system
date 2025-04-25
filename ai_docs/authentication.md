
Okay, let's break down how Django REST Framework's built-in `TokenAuthentication` works. It's a common and relatively simple way to secure your API endpoints.

Here's the core idea:

1.  **Token Model:** It relies on an app called `rest_framework.authtoken`. When you add this to your `INSTALLED_APPS` (which we already have) and run migrations (`python manage.py migrate`), it creates a database table (usually named `authtoken_token`). This table stores authentication tokens.
2.  **One Token Per User:** Each token in this table is linked directly to a specific `User` via a one-to-one relationship. So, typically, each user has *one* unique, randomly generated token string associated with their account.
3.  **Client Sends Token:** When a client (like your `curl` command, a JavaScript frontend, or another application) wants to make an authenticated request, it must include the user's token in the HTTP `Authorization` header.
4.  **Header Format:** The header must follow a specific format: `Authorization: Token <the_actual_token_string>`. For example:
    ```
    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    ```
5.  **Server-Side Check:** When a request arrives at your Django application:
    *   DRF's authentication middleware kicks in.
    *   The `TokenAuthentication` class (which we have listed in `DEFAULT_AUTHENTICATION_CLASSES` in `settings.py`) checks the `Authorization` header.
    *   It looks specifically for the `Token` keyword at the beginning.
    *   If found, it extracts the `<the_actual_token_string>`.
    *   It then queries the `authtoken_token` table to find a token whose `key` field exactly matches the provided string.
    *   If it finds a matching, active token, it retrieves the `User` associated with that token.
    *   It then successfully authenticates the request *as that user*. `request.user` will be set to that user object, and `request.auth` will be set to the token object itself.
    *   If no matching token is found, or the header format is incorrect, this authentication method fails. DRF will then try the next authentication class listed in `settings.py` (like our `ApiKeyAuthentication` or `SessionAuthentication`).

**How Tokens are Generated/Obtained:**

*   **Management Command:** You can generate a token for a user via `python manage.py drf_create_token <username>`.
*   **Signals:** You can set up a Django signal to automatically create a token whenever a new user is created.
*   **API Endpoint:** A very common pattern is to provide a dedicated API endpoint (often using the `obtain_auth_token` view provided by `rest_framework.authtoken.views`) where a user can POST their username and password to receive their token in the response. They then store this token and use it for subsequent requests.

**Key Difference from Our `ApiKeyAuthentication`:**

*   `TokenAuthentication` uses the built-in `Token` model (one token per user) and the `Authorization: Token ...` header.
*   Our custom `ApiKeyAuthentication` uses our custom `ApiKey` model (potentially multiple keys per user, linked to applications) and the `Authorization: ApiKey ...` header.
