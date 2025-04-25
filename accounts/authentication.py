from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from .models import ApiKey
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class ApiKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API keys.

    Clients should authenticate by passing the token key in the 'Authorization'
    HTTP header, prepended with the string 'ApiKey '. For example:

        Authorization: ApiKey 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'ApiKey'

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token) or None.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None # No ApiKey header found

        if len(auth) == 1:
            msg = 'Invalid ApiKey header. No credentials provided.'
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid ApiKey header. Key string should not contain spaces.'
            raise AuthenticationFailed(msg)

        try:
            key = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid ApiKey header. Key string should not contain invalid characters.'
            raise AuthenticationFailed(msg)

        try:
            api_key = ApiKey.objects.select_related('user').get(key=key, active=True)
        except ApiKey.DoesNotExist:
            logger.warning(f"ApiKeyAuthentication: Invalid key presented: {key[:10]}...") # Log invalid key attempt
            raise AuthenticationFailed('Invalid or inactive API key.')
        except Exception as e:
            # Log unexpected errors during lookup
            logger.error(f"ApiKeyAuthentication: Error during key lookup: {e}")
            raise AuthenticationFailed('Error authenticating API key.')


        if not api_key.user.is_active:
            raise AuthenticationFailed('User inactive or deleted.')
        
        logger.info(f"ApiKeyAuthentication: User {api_key.user.username} authenticated successfully using API Key for application '{api_key.application}'")
        # Return the user and the api_key object itself as the 'auth' token
        return (api_key.user, api_key)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a 401 Unauthenticated response.
        """
        return self.keyword 