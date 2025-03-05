from pathlib import Path
from .os_manager import OSManager
import re
from typing import Tuple


class DjangoManager:
    def __init__(self, os_manager: OSManager):
        self.os_manager = os_manager
        self._current_project_path = None

    @property
    def current_project_path(self):
        return self._current_project_path

    @current_project_path.setter
    def current_project_path(self, path):
        """Set the current Django project path"""
        if path is not None and not isinstance(path, Path):
            path = Path(path)
        self._current_project_path = path

    def find_django_project_in_current_dir(self) -> bool:
        """Check if current directory contains a Django project"""
        return self.os_manager.search_folder(self.is_django_project)

    def find_django_projects_in_tree(self):
        """Search for Django projects in subdirectories"""
        return self.os_manager.search_subfolders(self.is_django_project)

    @staticmethod
    def is_django_project(path: Path) -> bool:
        """Validate if directory is a Django project"""
        required_files = ["manage.py"]
        optional_files = ["requirements.txt", "Pipfile"]

        if not path.is_dir():
            return False

        has_manage_py = any(file.name == "manage.py" for file in path.iterdir())

        if not has_manage_py:
            return False

        manage_content = path.joinpath("manage.py").read_text()
        return "django" in manage_content.lower()

    def find_settings_file(self) -> Path:
        """Find the settings.py file in the Django project

        Returns:
            Path: Path to the settings.py file or None if not found
        """
        if not self.current_project_path:
            return None

        # Common patterns for settings file locations
        possible_locations = [
            # Standard Django project structure
            self.current_project_path / self.current_project_path.name / "settings.py",
            # Another common pattern (project/settings.py)
            self.current_project_path / "settings.py",
            # Project with config directory
            self.current_project_path / "config" / "settings.py",
            # Multiple settings files pattern
            self.current_project_path
            / self.current_project_path.name
            / "settings"
            / "base.py",
            self.current_project_path / "settings" / "base.py",
            self.current_project_path / "config" / "settings" / "base.py",
        ]

        # Check for settings module indicated in manage.py
        manage_path = self.current_project_path / "manage.py"
        if manage_path.exists():
            content = manage_path.read_text()
            # Look for DJANGO_SETTINGS_MODULE pattern
            import re

            settings_module_match = re.search(
                r'DJANGO_SETTINGS_MODULE["\']?\s*,\s*["\']([^"\']+)["\']', content
            )
            if settings_module_match:
                module_path = settings_module_match.group(1)
                # Convert module path (e.g. 'myproject.settings') to file path
                parts = module_path.split(".")
                file_path = self.current_project_path
                for part in parts[
                    :-1
                ]:  # All except the last part (which is the filename)
                    file_path = file_path / part
                file_path = file_path / f"{parts[-1]}.py"
                possible_locations.insert(0, file_path)  # Prioritize this path

        # Check each location
        for location in possible_locations:
            if location.exists() and location.is_file():
                return location

        # Search recursively as a fallback
        for path in self.current_project_path.rglob("settings.py"):
            return path

        return None

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

    def find_in_settings(self, setting_name, default=None):
        """
        Find a specific setting in the Django settings file

        Args:
            setting_name (str): The name of the setting to find (e.g., 'SECRET_KEY', 'ALLOWED_HOSTS', 'DATABASES')
            default: The default value to return if the setting is not found

        Returns:
            The value of the setting if found, or the default value if not found
        """
        settings_path = self.find_settings_file()
        if not settings_path or not settings_path.exists():
            return default

        # Create a temporary module to execute the settings file
        import importlib.util
        import sys

        # Create a temporary module name
        temp_module_name = f"_temp_settings_{hash(str(settings_path))}"

        try:
            # Create a new module spec
            spec = importlib.util.spec_from_file_location(
                temp_module_name, settings_path
            )
            if spec is None:
                return default

            # Create the module
            module = importlib.util.module_from_spec(spec)

            # Add the module to sys.modules
            sys.modules[temp_module_name] = module

            # Execute the module
            spec.loader.exec_module(module)

            # Try to get the setting
            return getattr(module, setting_name, default)
        except Exception as e:
            print(f"Error loading setting {setting_name}: {e}")
            return default
        finally:
            # Clean up
            if temp_module_name in sys.modules:
                del sys.modules[temp_module_name]

    def _parse_setting_value(self, value_str):
        """
        Parse a setting value string into the appropriate Python type

        Args:
            value_str (str): The string representation of the setting value

        Returns:
            The parsed value as the appropriate Python type
        """
        import ast

        # Remove trailing commas that might cause ast.literal_eval to fail
        value_str = value_str.rstrip(",")

        try:
            # Try to evaluate as a literal (handles strings, numbers, lists, tuples, dicts, etc.)
            return ast.literal_eval(value_str)
        except (SyntaxError, ValueError):
            # If it can't be parsed as a literal, return it as is
            return value_str

    def edit_settings(self, setting_name, new_value):
        """
        Update a specific setting in the Django settings file

        Args:
            setting_name (str): The name of the setting to update (e.g., 'SECRET_KEY', 'ALLOWED_HOSTS')
            new_value: The new value to set for the setting

        Returns:
            bool: True if the setting was successfully updated, False otherwise
        """
        import ast

        settings_path = self.find_settings_file()
        if not settings_path or not settings_path.exists():
            return False

        # Read the current content
        content = settings_path.read_text()

        # Prepare the string representation of the new value
        if isinstance(new_value, str):
            # For strings, ensure quotes are used
            value_str = f"'{new_value}'"
        elif new_value is None:
            value_str = "None"
        else:
            # For other types, use repr to get a string representation
            value_str = repr(new_value)

        # Check for different patterns and update appropriately
        updated = False
        new_content = content

        # Pattern for simple assignments: SETTING_NAME = value
        simple_pattern = rf"({setting_name}\s*=\s*)([^#\n]+)"
        simple_match = re.search(simple_pattern, content)

        if simple_match:
            # Preserve the assignment part (SETTING_NAME =) and replace the value part
            prefix = simple_match.group(1)
            new_content = re.sub(simple_pattern, f"{prefix}{value_str}", content)
            updated = True
        else:
            # Pattern for settings inside dictionaries
            dict_pattern = rf"(['\"]?{setting_name}['\"]?\s*:\s*)([^,}}]+)"
            dict_match = re.search(dict_pattern, content)

            if dict_match:
                prefix = dict_match.group(1)
                new_content = re.sub(dict_pattern, f"{prefix}{value_str}", content)
                updated = True
            else:
                # Pattern for commented settings
                commented_pattern = rf"(#\s*{setting_name}\s*=\s*)([^#\n]+)"
                commented_match = re.search(commented_pattern, content)

                if commented_match:
                    # Uncomment the setting and update its value
                    prefix = commented_match.group(1).lstrip("#").lstrip()
                    new_content = re.sub(
                        commented_pattern, f"{prefix}{value_str}", content
                    )
                    updated = True
                else:
                    # Setting not found, append it to the end of the file
                    new_content = f"{content}\n\n# Added by Django Manager\n{setting_name} = {value_str}\n"
                    updated = True

        # Write the updated content back to the file
        if updated:
            settings_path.write_text(new_content)
            return True

        return False

    def edit_database_settings(self, new_databases):
        """
        Update the DATABASES setting in the Django settings file

        Args:
            new_databases (dict): The new DATABASES configuration

        Returns:
            tuple: (bool success, str message)
        """
        # Validate that a default database is present
        if "default" not in new_databases:
            return False, "Error: The 'default' database configuration is required"

        settings_path = self.find_settings_file()
        if not settings_path or not settings_path.exists():
            return False, "Error: Settings file not found"

        # Read the current content
        content = settings_path.read_text()

        # Format the new databases dictionary with proper indentation
        from pprint import pformat

        formatted_databases = pformat(new_databases, indent=4)

        # Find the DATABASES definition in the file
        import re

        # First look for the start of the DATABASES assignment
        start_match = re.search(r"DATABASES\s*=\s*{", content)
        if not start_match:
            # DATABASES not found, append it to the end of the file
            new_content = f"{content}\n\n# Added by Django Manager\nDATABASES = {formatted_databases}\n"
            settings_path.write_text(new_content)
            return True, "DATABASES setting added successfully"

        # Find the entire DATABASES block by tracking braces
        start_pos = start_match.start()
        brace_count = 0
        end_pos = -1

        # Skip to the first opening brace
        first_brace_pos = content.find("{", start_pos)
        if first_brace_pos == -1:
            return False, "Error: Malformed DATABASES setting"

        # Count braces to find the matching closing brace
        for i in range(first_brace_pos, len(content)):
            char = content[i]
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break

        if end_pos == -1:
            return False, "Error: Could not find the end of DATABASES definition"

        # Replace the entire DATABASES block with the new configuration
        new_content = (
            content[:start_pos]
            + f"DATABASES = {str(formatted_databases)}"
            + content[end_pos:]
        )

        # Write the updated content back to the file
        settings_path.write_text(new_content)
        return True, "DATABASES setting updated successfully"

    def check_whitenoise_installed(self, venv_path: str | Path) -> Tuple[bool, str]:
        """
        Check if WhiteNoise is installed in the virtual environment.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Tuple of (is_installed: bool, message: str)
        """
        is_installed, message = self.os_manager.check_python_package_installed(
            venv_path, "whitenoise"
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
        pip_path = self.os_manager._manager.get_pip_path(Path(venv_path))
        try:
            result = self.os_manager.run_command(
                [str(pip_path), "install", "whitenoise"]
            )
            if result[0]:
                return True, "WhiteNoise installed successfully"
            else:
                return False, f"Failed to install WhiteNoise: {result[1]}"
        except Exception as e:
            return False, f"Error installing WhiteNoise: {str(e)}"

    def edit_middleware_settings(self, new_middleware):
        """
        Update the MIDDLEWARE setting in the Django settings file

        Args:
            new_middleware (list): The new MIDDLEWARE configuration

        Returns:
            tuple: (bool success, str message)
        """
        settings_path = self.find_settings_file()
        if not settings_path or not settings_path.exists():
            return False, "Error: Settings file not found"

        # Read the current content
        content = settings_path.read_text()

        # Format the new middleware list with proper indentation
        from pprint import pformat

        formatted_middleware = pformat(new_middleware, indent=4)

        # Find the MIDDLEWARE definition in the file
        import re

        # First look for the start of the MIDDLEWARE assignment
        start_match = re.search(r"MIDDLEWARE\s*=\s*\[", content)
        if not start_match:
            # MIDDLEWARE not found, append it to the end of the file
            new_content = f"{content}\n\n# Added by Django Manager\nMIDDLEWARE = {formatted_middleware}\n"
            settings_path.write_text(new_content)
            return True, "MIDDLEWARE setting added successfully"

        # Find the entire MIDDLEWARE block by tracking brackets
        start_pos = start_match.start()
        bracket_count = 0
        end_pos = -1

        # Skip to the first opening bracket
        first_bracket_pos = content.find("[", start_pos)
        if first_bracket_pos == -1:
            return False, "Error: Malformed MIDDLEWARE setting"

        # Count brackets to find the matching closing bracket
        for i in range(first_bracket_pos, len(content)):
            char = content[i]
            if char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    end_pos = i + 1
                    break

        if end_pos == -1:
            return False, "Error: Could not find the end of MIDDLEWARE definition"

        # Replace the entire MIDDLEWARE block with the new configuration
        new_content = (
            content[:start_pos]
            + f"MIDDLEWARE = {str(formatted_middleware)}"
            + content[end_pos:]
        )

        # Write the updated content back to the file
        settings_path.write_text(new_content)
        return True, "MIDDLEWARE setting updated successfully"

    def replace_settings(self, setting_name, new_value_raw):
        """
        Replace a setting in the Django settings file by directly modifying the text.
        This is useful for settings that include raw Python expressions (like os.path.join).

        Args:
            setting_name (str): The name of the setting to replace (e.g., 'STATIC_ROOT')
            new_value_raw (str): The raw value to set (e.g., "os.path.join(BASE_DIR, 'staticfiles')")

        Returns:
            tuple: (bool success, str message)
        """
        settings_path = self.find_settings_file()
        if not settings_path or not settings_path.exists():
            return False, f"Error: Settings file not found at {settings_path}"

        try:
            # Read the current content
            content = settings_path.read_text()

            # Pattern for finding the entire setting line or block
            pattern = rf"{setting_name}\s*=\s*[^\n]+"

            if re.search(pattern, content):
                # Replace existing setting
                new_content = re.sub(
                    pattern, f"{setting_name} = {new_value_raw}", content
                )
                settings_path.write_text(new_content)
                return True, f"{setting_name} replaced successfully"
            else:
                # Setting not found, append it to the end of the file
                new_content = f"{content}\n\n# Added by Django Manager\n{setting_name} = {new_value_raw}\n"
                settings_path.write_text(new_content)
                return True, f"{setting_name} added successfully"

        except Exception as e:
            return False, f"Error replacing setting {setting_name}: {str(e)}"

    def is_library_imported(self, library_name):
        """
        Check if a library is imported in the Django settings file.

        Args:
            library_name (str): The name of the library to check for (e.g., 'os', 'whitenoise')

        Returns:
            bool: True if the library is imported, False otherwise
        """
        settings_path = self.find_settings_file()
        if not settings_path or not settings_path.exists():
            return False

        try:
            # Read the content of the settings file
            content = settings_path.read_text()

            # Define patterns for different import styles
            import_patterns = [
                rf"import\s+{library_name}",  # import os
                rf"from\s+{library_name}\s+import",  # from os import path
                rf"import\s+.*,\s*{library_name}",  # import sys, os
                rf"import\s+{library_name}\s+as",  # import os as operating_system
            ]

            # Check if any pattern matches
            for pattern in import_patterns:
                if re.search(pattern, content):
                    return True

            return False

        except Exception as e:
            print(f"Error checking for library import: {e}")
            return False

    def add_library_import(
        self, library_name, import_from=None, import_as=None, import_what=None
    ):
        """
        Add a library import to the Django settings file if it's not already present.

        Args:
            library_name (str): The name of the library to import (e.g., 'os', 'whitenoise')
            import_from (str, optional): For 'from X import Y' style imports, the module to import from
            import_as (str, optional): For 'import X as Y' style imports, the alias to use
            import_what (str or list, optional): For 'from X import Y' style imports, what to import

        Returns:
            tuple: (bool success, str message)
        """
        # First check if the library is already imported
        if self.is_library_imported(library_name):
            return True, f"{library_name} is already imported"

        settings_path = self.find_settings_file()
        if not settings_path or not settings_path.exists():
            return False, "Settings file not found"

        try:
            # Read the content of the settings file
            content = settings_path.read_text()

            # Construct the import statement based on the parameters
            if import_from:
                if import_what:
                    if isinstance(import_what, list):
                        import_what_str = ", ".join(import_what)
                    else:
                        import_what_str = import_what
                    import_statement = f"from {import_from} import {import_what_str}"
                else:
                    return False, "import_what must be provided when using import_from"
            else:
                import_statement = f"import {library_name}"
                if import_as:
                    import_statement += f" as {import_as}"

            # Find the position to insert the import
            # Usually best to put new imports at the top, after any existing imports
            import_section_end = 0

            # Find the end of imports section (look for the first non-import, non-blank line)
            lines = content.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if (
                    line
                    and not line.startswith("#")
                    and not line.startswith("import")
                    and not line.startswith("from")
                ):
                    import_section_end = i
                    break

            # Insert the import statement
            new_lines = (
                lines[:import_section_end]
                + [import_statement]
                + lines[import_section_end:]
            )
            new_content = "\n".join(new_lines)

            # Write the modified content back to the file
            settings_path.write_text(new_content)

            return True, f"Added import for {library_name}"

        except Exception as e:
            return False, f"Error adding library import: {str(e)}"

    def get_raw_staticfiles_dirs(self):
        """
        Get the raw STATICFILES_DIRS expressions from the settings file,
        correctly handling nested parentheses.

        Returns:
            list: List of raw expressions in the STATICFILES_DIRS setting,
                or empty list if the setting doesn't exist
        """
        settings_path = self.find_settings_file()
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
