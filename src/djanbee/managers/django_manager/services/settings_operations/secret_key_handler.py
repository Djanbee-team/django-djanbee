from ..settings_service import DjangoSettingsService
from .secret_key_handler_display import SecretKeyHandlerDisplay


class SecretKeyHandler:
    """Handler for Django secret key operations"""

    def __init__(
        self, settings_service: DjangoSettingsService, display: SecretKeyHandlerDisplay
    ):
        self.settings_service = settings_service
        self.display = display

    def create_secret_key(self):
        self.display.progress_generate_secret_key()
        secret_key = self.generate_secret_key()
        self.display.success_generate_secret_key(secret_key)
        return secret_key

    def update_secret_key(self, secret_key: str):
        old_key = self.settings_service.find_in_settings("SECRET_KEY")
        self.display.progress_set_secret_key(secret_key, old_key)

        self.settings_service.edit_settings("SECRET_KEY", secret_key)
        self.display.success_set_secret_key()

    def generate_secret_key(self) -> str:
        """
        Generate a new Django-compatible secret key without depending on Django

        Returns:
            str: A new secure secret key suitable for Django
        """
        import secrets
        import string

        # Characters to use in the secret key - matching Django's pattern
        chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"

        # Generate a 50-character random string
        secret_key = "".join(secrets.choice(chars) for _ in range(50))

        return secret_key
