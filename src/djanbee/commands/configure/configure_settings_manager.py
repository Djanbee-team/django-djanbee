from ...core import AppContainer
from .configure_settings_display import ConfigureSettingsDisplay
from typing import Optional
from collections import namedtuple

Result = namedtuple("Result", ["valid", "object"])


class ConfigureSettingsManager:
    def __init__(self, display: ConfigureSettingsDisplay, app: AppContainer):
        self.display = display
        self.app = app

    def _configure_settings(self, path="") -> Optional[tuple]:
        """Handle searching for Django projects in subdirectories"""
        # Find and validate project
        if not self.app.django_manager.project_service.state.current_project_path:
            project = self.app.django_manager.project_service.select_project()
        if not project:
            return None

        # Find settings file
        settings_file = self.app.django_manager.settings_service.find_settings()

        # Get user's configuration choices
        selected_settings = self.display.prompt_configure_menu()

        # Process each selected setting
        for setting in selected_settings:
            self._process_setting(setting)

        return project

    def _process_setting(self, setting):
        """Process a single selected setting"""
        handlers = {
            "Generate secret key": self._handle_secret_key,
            "Manage ALLOWED_HOSTS": self.app.django_manager.allowed_hosts_handler.handle_allowed_hosts,
            "Manage databases": self.app.django_manager.databases_handler.handle_databases,
            "Set up STATIC_ROOT": self.app.django_manager.static_root_handler._handle_static_root,
            # "Enable SSL settings (does not generate a certificate)": self._handle_ssl,
            # "Disable DEBUG": self._handle_debug,
        }

        if setting in handlers:
            handlers[setting]()

    def _handle_secret_key(self):
        """Handle generating and setting a new secret key"""
        secret_key = self.app.django_manager.secret_key_handler.create_secret_key()
        self.app.django_manager.secret_key_handler.update_secret_key(secret_key)
