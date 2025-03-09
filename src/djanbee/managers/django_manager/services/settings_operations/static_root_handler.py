from ..settings_service import DjangoSettingsService
from .static_root_handler_display import StaticRootHandlerDisplay
from ..venv_service import DjangoEnvironmentService
from pathlib import Path
from typing import Tuple


class StaticRootHandler:
    def __init__(
        self,
        settings_service: DjangoSettingsService,
        display: StaticRootHandlerDisplay,
        venv_service: DjangoEnvironmentService,
    ):
        self.settings_service = settings_service
        self.display = display
        self.venv_service = venv_service

    def _handle_static_root(self):

        result = self.display.prompt_static_files_solution()

        handlers = {"Whitenoise": self._handle_whitenoise}

        if result in handlers:
            handlers[result]()

    def _handle_whitenoise(self):
        # Get the active virtual environment
        if not self.venv_service.state.active_venv_path:
            self.venv_service.get_active_venv()
        active_venv = self.venv_service.state.active_venv_path
        if not active_venv:
            print("No active virtual environment detected")
            # Handle error or create one
        else:
            venv_path = active_venv

            is_installed, message = self.check_whitenoise_installed(venv_path)
            if not is_installed:
                result = self.display.prompt_install_whitenoise()
                if result:
                    self.install_whitenoise(venv_path)

            middleware = self.settings_service.find_in_settings(
                "MIDDLEWARE", default={}
            )
            is_whitenoise = self.is_whitenoise_properly_configured(middleware)

            if not is_whitenoise:
                middleware = self.setup_whitenoise_middleware(middleware)
                self.display.print_progress_whitenoise()
                self.settings_service.edit_middleware_settings(middleware)
            self.display.success_progress_whitenoise()

            static_url = self.settings_service.find_in_settings("STATIC_URL")
            if static_url != "/static/":
                self.display.print_progress_static_url()
                self.settings_service.edit_settings("STATIC_URL", "/static/")
            self.display.success_progress_static_url()

            static_root = self.settings_service.find_in_settings("STATIC_ROOT")
            if static_root:
                self.display.print_progress_static_root()
                has_os = self.settings_service.is_library_imported("os")
                if not has_os:
                    self.settings_service.add_library_import("os")
                    self.display.print_progress_static_root_add_os()
                self.settings_service.replace_settings(
                    "STATIC_ROOT", "os.path.join(BASE_DIR, 'staticfiles')"
                )
            self.display.success_progress_static_root()

            staticfiles_dirs = self.get_raw_staticfiles_dirs()
            if not staticfiles_dirs:
                # STATICFILES_DIRS doesn't exist or is empty
                self.display.print_progress_static_file_dirs_create()
                self.settings_service.replace_settings(
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
                    self.settings_service.replace_settings(
                        "STATICFILES_DIRS", formatted_list
                    )
            self.display.success_progress_static_file_dirs_add()

            staticfiles_storage = self.settings_service.find_in_settings(
                "STATICFILES_STORAGE", default=""
            )
            if (
                staticfiles_storage
                != "whitenoise.storage.CompressedManifestStaticFilesStorage"
            ):
                self.display.progress_staticfiles_storage_add()
                self.settings_service.edit_settings(
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

    def check_whitenoise_installed(self, venv_path: str | Path) -> Tuple[bool, str]:
        """
        Check if WhiteNoise is installed in the virtual environment.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Tuple of (is_installed: bool, message: str)
        """
        is_installed, message = (
            self.settings_service.os_manager.check_python_package_installed(
                venv_path, "whitenoise"
            )
        )

        return is_installed, message

    def install_whitenoise(self, venv_path: str | Path) -> Tuple[bool, str]:
        """
        Install WhiteNoise in the virtual environment if not already installed.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check if already installed
        is_installed, _ = self.check_whitenoise_installed(venv_path)
        if is_installed:
            return True, "WhiteNoise is already installed"

        # Install WhiteNoise
        pip_path = self.settings_service.os_manager.get_pip_path(Path(venv_path))
        try:
            result = self.settings_service.os_manager.run_command(
                [str(pip_path), "install", "whitenoise"]
            )
            if result[0]:
                return True, "WhiteNoise installed successfully"
            else:
                return False, f"Failed to install WhiteNoise: {result[1]}"
        except Exception as e:
            return False, f"Error installing WhiteNoise: {str(e)}"

    def get_raw_staticfiles_dirs(self):
        """
        Get the raw STATICFILES_DIRS expressions from the settings file,
        correctly handling nested parentheses.

        Returns:
            list: List of raw expressions in the STATICFILES_DIRS setting,
                or empty list if the setting doesn't exist
        """
        settings_path = self.settings_service.find_settings_file()
        if not settings_path:
            return []

        try:
            content = settings_path.read_text()

            # Find the STATICFILES_DIRS declaration
            import re

            pattern = r"STATICFILES_DIRS\s*=\s*\[(.*?)\]"
            match = re.search(pattern, content, re.DOTALL)

            if not match:
                return []

            # Get the content inside the brackets
            raw_content = match.group(1).strip()

            if not raw_content:
                return []

            # Split by commas, respecting nested parentheses and brackets
            expressions = []
            current_expr = ""
            paren_level = 0
            bracket_level = 0

            for char in raw_content:
                if char == "," and paren_level == 0 and bracket_level == 0:
                    # Only split on commas at the top level
                    if current_expr.strip():
                        expressions.append(current_expr.strip())
                    current_expr = ""
                else:
                    current_expr += char
                    if char == "(":
                        paren_level += 1
                    elif char == ")":
                        paren_level -= 1
                    elif char == "[":
                        bracket_level += 1
                    elif char == "]":
                        bracket_level -= 1

            # Add the last expression if there is one
            if current_expr.strip():
                expressions.append(current_expr.strip())

            return expressions

        except Exception as e:
            print(f"Error getting raw STATICFILES_DIRS: {e}")
            return []
