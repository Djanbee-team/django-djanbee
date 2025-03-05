from ...core import AppContainer
from .configure_settings_display import ConfigureSettingsDisplay
from ...managers.mixins.project_search import ProjectSearchMixin
from typing import Optional


class ConfigureSettingsManager(ProjectSearchMixin):
    def __init__(self, display: ConfigureSettingsDisplay, app: AppContainer):
        self.display = display
        self.app = app

    def _configure_settings(self, path="") -> Optional[tuple]:
        """Handle searching for Django projects in subdirectories"""
        # Find and validate project
        project = self.find_django_project()
        if not project:
            return None

        # Set up project path
        self.app.django_manager.current_project_path = project[1]
        self.display.show_project_opened(project)

        # Find settings file
        self.display.print_lookup_settings()
        settings_file = self.app.django_manager.find_settings_file()
        if not settings_file:
            self.display.error_found_settings()
            return None
        self.display.success_found_settings(settings_file)

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
            "Manage ALLOWED_HOSTS": self._handle_allowed_hosts,
            "Manage databases": self._handle_databases,
            "Set up STATIC_ROOT": self._handle_static_root,
            # "Enable SSL settings (does not generate a certificate)": self._handle_ssl,
            # "Disable DEBUG": self._handle_debug,
        }

        if setting in handlers:
            handlers[setting]()

    def _handle_secret_key(self):
        """Handle generating and setting a new secret key"""
        self.display.progress_generate_secret_key()
        secret_key = self.app.django_manager.generate_secret_key()
        self.display.success_generate_secret_key(secret_key)

        old_key = self.app.django_manager.find_in_settings("SECRET_KEY")
        self.display.progress_set_secret_key(secret_key, old_key)

        self.app.django_manager.edit_settings("SECRET_KEY", secret_key)
        self.display.success_set_secret_key()

    def _handle_allowed_hosts(self):
        allowed_hosts = self.app.django_manager.find_in_settings("ALLOWED_HOSTS")
        if not allowed_hosts:
            self.display.warning_empty_hosts()
            return self._add_new_host()

        allowed_hosts = self.app.django_manager.find_in_settings("ALLOWED_HOSTS")
        response, hosts = self.display.prompt_allowed_hosts_manager(allowed_hosts)
        if response == "create":
            return self._add_new_host()
        elif response == "delete":
            return self._remove_host(hosts)

    def _add_new_host(self):
        try:
            host = self.display.prompt_allowed_hosts_input()
            self.edit_allowed_hosts(host)
        except:
            # TODO: if edit_allowed_hosts is cancelled there it returns None and crashes
            pass
        self.display.success_host_created(host)
        return self._handle_allowed_hosts()

    def _remove_host(self, hosts_to_remove):
        self.edit_allowed_hosts(hosts_to_remove, operation="remove")
        self.display.success_hosts_removed(hosts_to_remove)
        return self._handle_allowed_hosts()

    def edit_allowed_hosts(self, host, operation="add"):
        """
        Modify the ALLOWED_HOSTS setting by adding or removing hosts

        Args:
            host (str or list): The host(s) to add or remove
            operation (str): The operation to perform ('add' or 'remove')

        Returns:
            tuple: (bool - success, list - current hosts)
        """
        # Get the current ALLOWED_HOSTS
        current_hosts = self.app.django_manager.find_in_settings(
            "ALLOWED_HOSTS", default=[]
        )

        # If it's a string (like "*"), convert to a list
        if isinstance(current_hosts, str):
            current_hosts = [current_hosts]
        elif current_hosts is None:
            current_hosts = []

        # Convert single host to list for consistent processing
        hosts_to_process = [host] if isinstance(host, str) else host

        if operation == "add":
            # Add hosts that aren't already in the list
            updated_hosts = current_hosts.copy()
            for h in hosts_to_process:
                if h not in current_hosts:
                    updated_hosts.append(h)
        elif operation == "remove":
            # Remove hosts that are in the list
            updated_hosts = [h for h in current_hosts if h not in hosts_to_process]
        else:
            return False, current_hosts  # Invalid operation

        # Update the setting
        success = self.app.django_manager.edit_settings("ALLOWED_HOSTS", updated_hosts)

        return success, updated_hosts

    def _handle_databases(self):
        database = self.app.django_manager.find_in_settings("DATABASES", default=[])
        default_db = database.get("default", {})

        # Create a copy without the OPTIONS field
        db_without_options = {k: v for k, v in default_db.items() if k != "OPTIONS"}

        updated_db = self.display.prompt_postgresql_edit(db_without_options)
        if not updated_db:
            return
        # Wrap the updated database configuration in the "default" key
        updated_database_config = {"default": updated_db}

        # Update the settings file
        self.app.django_manager.edit_database_settings(updated_database_config)

        # Confirm to the user
        self.display.success_database_updated()

        self.display.print_lookup_database_dependencies()

        # Get the active virtual environment
        active_venv = self.app.os_manager.get_active_venv()
        if not active_venv:
            print("No active virtual environment detected")
            # Handle error or create one
        else:
            venv_name, venv_path = active_venv

            # Check if PostgreSQL dependencies are installed
            all_installed, missing_packages = (
                self.app.os_manager.check_postgres_dependencies(venv_path)
            )

            if not all_installed:
                result = self.display.prompt_install_database_dependencies(
                    missing_packages
                )
                if result:
                    self.display.print_progress_database_dependencies_install()
                    success, message = self.app.os_manager.ensure_postgres_dependencies(
                        venv_path
                    )
                    print(message)
            else:
                self.display.print_database_dependencies_present()

    def _handle_static_root(self):

        result = self.display.prompt_static_files_solution()

        handlers = {"Whitenoise": self._handle_whitenoise}

        if result in handlers:
            handlers[result]()

    def _handle_whitenoise(self):
        # Get the active virtual environment
        active_venv = self.app.os_manager.get_active_venv()
        if not active_venv:
            print("No active virtual environment detected")
            # Handle error or create one
        else:
            venv_name, venv_path = active_venv

            is_installed, message = self.app.django_manager.check_whitenoise_installed(
                venv_path
            )
            if not is_installed:
                result = self.display.prompt_install_whitenoise()
                if result:
                    self.app.django_manager.install_whitenoise(venv_path)

            middleware = self.app.django_manager.find_in_settings(
                "MIDDLEWARE", default={}
            )
            is_whitenoise = self.is_whitenoise_properly_configured(middleware)
            if not is_whitenoise:
                middleware = self.setup_whitenoise_middleware(middleware)
                self.display.print_progress_whitenoise()
                self.app.django_manager.edit_middleware_settings(middleware)
            self.display.success_progress_whitenoise()

            static_url = self.app.django_manager.find_in_settings("STATIC_URL")
            if static_url != "/static/":
                self.display.print_progress_static_url()
                self.app.django_manager.edit_settings("STATIC_URL", "/static/")
            self.display.success_progress_static_url()

            static_root = self.app.django_manager.find_in_settings("STATIC_ROOT")
            if static_root:
                self.display.print_progress_static_root()
                has_os = self.app.django_manager.is_library_imported("os")
                if not has_os:
                    self.app.django_manager.add_library_import("os")
                    self.display.print_progress_static_root_add_os()
                self.app.django_manager.replace_settings(
                    "STATIC_ROOT", "os.path.join(BASE_DIR, 'staticfiles')"
                )
            self.display.success_progress_static_root()

            staticfiles_dirs = self.app.django_manager.get_raw_staticfiles_dirs()
            if not staticfiles_dirs:
                # STATICFILES_DIRS doesn't exist or is empty
                self.display.print_progress_static_file_dirs_create()
                self.app.django_manager.replace_settings(
                    "STATICFILES_DIRS", "[os.path.join(BASE_DIR, 'static')]"
                )
            else:
                # Check if our expression is already in the list
                target_expr = "os.path.join(BASE_DIR, 'static')"

                # Look for the exact expression or similar ones (may have different spacing)
                has_path = any(
                    "os.path.join(BASE_DIR" in expr and "'static'" in expr
                    for expr in staticfiles_dirs
                )

                if not has_path:
                    # Add our path to the list
                    staticfiles_dirs.append(target_expr)

                    # Format the list correctly for the settings file
                    formatted_list = (
                        "[\n    " + ",\n    ".join(staticfiles_dirs) + "\n]"
                    )

                    # Update the setting
                    self.app.django_manager.replace_settings(
                        "STATICFILES_DIRS", formatted_list
                    )
                    print("ALERT - Added static path to STATICFILES_DIRS")
            self.display.success_progress_static_file_dirs_add()

            staticfiles_storage = self.app.django_manager.find_in_settings(
                "STATICFILES_STORAGE", default=""
            )
            if (
                staticfiles_storage
                != "whitenoise.storage.CompressedManifestStaticFilesStorage"
            ):
                self.display.progress_staticfiles_storage_add()
                self.app.django_manager.edit_settings(
                    "STATICFILES_STORAGE",
                    "whitenoise.storage.CompressedManifestStaticFilesStorage",
                )
            self.display.success_staticfiles_storage_add()

    def is_whitenoise_properly_configured(self, middleware_list):
        """
        Check if WhiteNoise middleware is present and properly placed after
        SecurityMiddleware in the MIDDLEWARE setting.

        Args:
            middleware_list: List of middleware from settings

        Returns:
            bool: True if WhiteNoise middleware is present and properly placed, False otherwise
        """
        # Check if middleware_list is empty or None
        if not middleware_list:
            return False

        # The exact strings to look for
        security_middleware = "django.middleware.security.SecurityMiddleware"
        whitenoise_middleware = "whitenoise.middleware.WhiteNoiseMiddleware"

        # Check if both middlewares are in the list
        if (
            security_middleware not in middleware_list
            or whitenoise_middleware not in middleware_list
        ):
            return False

        # Check their relative positions
        security_index = middleware_list.index(security_middleware)
        whitenoise_index = middleware_list.index(whitenoise_middleware)

        # WhiteNoise should come directly after SecurityMiddleware
        return whitenoise_index == security_index + 1

    def setup_whitenoise_middleware(self, middleware_list):
        """
        Configure the middleware list to include WhiteNoise in the correct position
        (immediately after SecurityMiddleware).

        Args:
            middleware_list: List of middleware from settings

        Returns:
            list: Updated middleware list with WhiteNoise properly positioned
        """
        if not middleware_list:
            # If middleware_list is empty, create a list with the basic middlewares
            return [
                "django.middleware.security.SecurityMiddleware",
                "whitenoise.middleware.WhiteNoiseMiddleware",
                # Add other essential middlewares
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.middleware.clickjacking.XFrameOptionsMiddleware",
            ]

        # The middlewares we're working with
        security_middleware = "django.middleware.security.SecurityMiddleware"
        whitenoise_middleware = "whitenoise.middleware.WhiteNoiseMiddleware"

        # Remove WhiteNoise if it's already in the list (to reposition it)
        if whitenoise_middleware in middleware_list:
            middleware_list.remove(whitenoise_middleware)

        # If SecurityMiddleware exists, insert WhiteNoise after it
        if security_middleware in middleware_list:
            security_index = middleware_list.index(security_middleware)
            middleware_list.insert(security_index + 1, whitenoise_middleware)
        else:
            # If SecurityMiddleware doesn't exist, add both at the beginning
            middleware_list.insert(0, whitenoise_middleware)
            middleware_list.insert(0, security_middleware)

        return middleware_list
