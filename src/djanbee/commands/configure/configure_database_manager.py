from ...core import AppContainer
from .configure_database_display import ConfigureDatabaseDisplay
from pathlib import Path
from typing import Tuple, Optional


class ConfigureDatabaseManager:

    def __init__(self, display: ConfigureDatabaseDisplay, app: AppContainer):
        self.display = display
        self.app = app

    def _configure_database(self, path: str) -> None:
        """Main entry point for database configuration."""
        self.display.show_lookup_database()

        if not self._ensure_installation():
            return
        print("TEST")
        if not self._ensure_service_running():
            return

        self.display.success_database_running()

        user = self._handle_user()
        if not user:
            return

        self.display.success_login_user(user)

        self._handle_database_create_or_connect()

    def _ensure_installation(self) -> bool:
        """Ensure PostgreSQL is installed, install if needed."""
        is_installed, location = self.app.database_manager.check_postgres_installation()

        if not is_installed:
            return self._handle_installation()

        self.display.success_database_installed(location)
        return True

    def _ensure_service_running(self) -> bool:
        """Ensure PostgreSQL service is running, start if needed."""
        is_running = self.app.database_manager.check_postgres_status()

        if not is_running:
            return self._handle_service_start()

        return True

    def _handle_installation(self) -> bool:
        """Handle PostgreSQL installation process."""
        self.display.error_database_installed()

        if not self.display.prompt_install_database():
            return False

        try:
            if not self._run_installation():
                return False

            # Verify installation
            is_installed, location = (
                self.app.database_manager.check_postgres_installation()
            )
            if is_installed:
                self.display.success_database_installed(location)
                return True
            else:
                self.display.error_database_installed()
                return False

        except Exception as e:
            self.display.print_installation_failure(
                "Installation", f"Unexpected error: {e}"
            )
            return False

    def _run_installation(self) -> bool:
        """Run the actual installation process."""
        installation = self.app.database_manager.install_postgres()

        try:
            for step_name, success, message in installation:
                if success:
                    self.display.print_installation_progress(step_name, message)
                else:
                    self.display.print_installation_failure(step_name, message)
                    return False

            return True
        except Exception as e:
            self.display.print_installation_failure(
                "Installation", f"Installation error: {e}"
            )
            return False

    def _handle_service_start(self) -> bool:
        """Handle starting PostgreSQL service."""
        self.display.error_database_running()

        if not self.display.prompt_enable_database():
            return False

        enabled, message = self.app.database_manager.configure_postgres_service()
        if not enabled:
            self.display.error_database_running()
            return False

        is_running = self.app.database_manager.check_postgres_status()
        return is_running

    def _handle_user(self):
        user = self.app.os_manager.get_username()
        is_admin = self.app.os_manager.is_admin()

        login = self.display.prompt_user_create_or_login(is_admin)
        if login is not None:
            if not login:
                flag, response = self.app.database_manager.create_user(user)
                if not flag:
                    self.display.error_create_user(response)
                    return False
                self.display.success_create_user(user)

            flag, response = self.app.database_manager.login_user(user)
            if not flag:
                self.display.error_login_user(response)
                return False
            return user

    def _handle_database_create_or_connect(self):
        create = self.display.prompt_database_create_or_connect()

        if create:
            db_name = self.display.input_database_name()
            self.app.database_manager.create_database(db_name)
        else:
            flag, databases = self.app.database_manager.get_all_databases()
            database = self.display.prompt_select_database(databases)
            self.app.database_manager.db_name = database

        self.display.print_progress_database(self.app.database_manager.db_name)

    def find_settings_file(self, project_path: Path) -> Tuple[bool, Optional[Path]]:
        """
        Find the settings file for a Django project.

        Args:
            project_path: Path to the Django project directory

        Returns:
            Tuple[bool, Optional[Path]]:
                - True and the path if settings file is found
                - False and None if settings file is not found
        """
        # Save the project path
        self.current_project_path = project_path

        # Common patterns for Django settings files
        settings_patterns = [
            # Standard Django layout: project_name/settings.py
            project_path / "settings.py",
            # Project with inner module: project_name/project_name/settings.py
            *[
                project_path / inner_dir.name / "settings.py"
                for inner_dir in project_path.iterdir()
                if inner_dir.is_dir() and not inner_dir.name.startswith(".")
            ],
            # Settings in config directory: project_name/config/settings.py
            project_path / "config" / "settings.py",
            # Settings as a package: project_name/settings/__init__.py
            project_path / "settings" / "__init__.py",
            # Common Django project layout with app name matching project folder
            project_path / project_path.name / "settings.py",
        ]

        # Check each pattern
        for settings_path in settings_patterns:
            if settings_path.exists() and settings_path.is_file():
                return True, settings_path

        # If no common pattern matches, do a more thorough search (limited depth)
        try:
            # Search for settings.py files (limit to 3 levels deep to avoid excessive searching)
            for settings_file in list(project_path.glob("**/settings.py"))[:5]:
                # Verify it's a Django settings file by checking content
                content = settings_file.read_text(encoding="utf-8", errors="ignore")
                if any(
                    marker in content
                    for marker in [
                        "DJANGO_SETTINGS_MODULE",
                        "SECRET_KEY",
                        "INSTALLED_APPS",
                    ]
                ):
                    return True, settings_file
        except Exception:
            # Handle potential errors during file reading
            pass

        # No settings file found
        return False, None
