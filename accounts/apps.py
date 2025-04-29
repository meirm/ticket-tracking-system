from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    # Import signals when the app is ready
    def ready(self):
        # Import signals to ensure they are registered
        import accounts.signals
