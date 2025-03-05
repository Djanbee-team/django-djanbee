from ...managers import ConsoleManager
from ...widgets.checkbox_selector import CheckboxSelector
from ...managers.mixins.project_search import ProjectSearchDisplayMixin
from ...widgets.text_input import TextInputWidget
from ...widgets.create_delete_chekbox_selector import CreateDeleteCheckboxSelector
from ...widgets.list_selector import ListSelector
from ...widgets.question_selector import QuestionSelector


class ConfigureSettingsDisplay(ProjectSearchDisplayMixin):
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def print_lookup_settings(self):
        self.console_manager.print_lookup("Looking for settings.py")

    def error_found_settings(self):
        self.console_manager.print_error("Did not find settings.py")

    def success_found_settings(self, path):
        self.console_manager.print_step_progress(
            "Looking for settings.py", f"Found settings.py in {path}"
        )

    def progress_generate_secret_key(self):
        self.console_manager.print_progress("Generating secret key")

    def success_generate_secret_key(self, secret_key):
        self.console_manager.print_success(f"Secret key generated: {secret_key}")

    def prompt_configure_menu(self):
        options = [
            "Generate secret key",
            "Manage ALLOWED_HOSTS",
            "Manage databases",
            "Set up STATIC_ROOT",
            "Enable SSL settings (does not generate a certificate)",
            "Disable DEBUG",
        ]

        result = CheckboxSelector(
            "Select settings to configure:", options, self.console_manager
        )
        return result.select()

    def progress_set_secret_key(self, secret_key, old_key):
        self.console_manager.print_progress(
            f"Replacing old key {old_key} with {secret_key}"
        )

    def success_set_secret_key(self):
        self.console_manager.print_step_progress("Secret key", "set successfully")

    def warning_empty_hosts(self):
        self.console_manager.print_warning_critical(
            "No hosts set in ALLOWED_HOSTS. Django will reject all requests in production mode. "
            "Your website won't be accessible externally without properly configuring this setting."
        )

    def prompt_allowed_hosts_input(self, host=""):
        fields = [("Hostname", host)]
        input_widget = TextInputWidget(
            "Add an allowed host:", fields, self.console_manager
        )
        results = input_widget.get_result()
        if results is None:
            return None

        hostname = results.get("Hostname", "").strip()

        if not len(hostname):
            self.console_manager.print_warning_critical("Please fill in hostname")
            return self.prompt_allowed_hosts_input(host)

        return hostname

    def prompt_allowed_hosts_manager(self, hosts):
        result = CreateDeleteCheckboxSelector(
            "Delete hosts or create a new host", hosts, self.console_manager
        )

        return result.select()

    def success_host_created(self, host):
        self.console_manager.print_success(f"Host: {host} was successfully added")

    def success_hosts_removed(self, hosts):
        hosts_str = ", ".join(hosts)
        self.console_manager.print_success(
            f"Hosts: {hosts_str} were successfully deleted"
        )

    def prompt_postgresql_edit(self, database):
        # Create a list of tuples with field names and current values
        # Convert all values to strings to ensure .strip() will work
        fields = [
            ("ENGINE", str(database.get("ENGINE", "django.db.backends.postgresql"))),
            ("NAME", str(database.get("NAME", ""))),
            ("USER", str(database.get("USER", ""))),
            ("PASSWORD", str(database.get("PASSWORD", ""))),
            ("HOST", str(database.get("HOST", "localhost"))),
            ("PORT", str(database.get("PORT", "5432"))),
            ("CONN_MAX_AGE", str(database.get("CONN_MAX_AGE", "600"))),
        ]

        # Create the input widget
        input_widget = TextInputWidget(
            "Configure PostgreSQL database:",
            fields,
            self.console_manager,
        )

        # Get the results from the widget
        results = input_widget.get_result()
        if results is None:
            return None

        # Validate required fields
        required_fields = ["ENGINE", "NAME"]
        for field in required_fields:
            if not results.get(field, "").strip():
                self.console_manager.print_warning_critical(f"Please fill in {field}")
                return self.prompt_postgresql_edit(database)

        # Build the updated database configuration dictionary
        updated_database = {
            "ENGINE": results.get("ENGINE").strip(),
            "NAME": results.get("NAME").strip(),
        }

        # Add optional fields if they have values
        for field in ["USER", "PASSWORD", "HOST", "PORT", "CONN_MAX_AGE"]:
            value = results.get(field, "").strip()
            if value:
                # For PORT and CONN_MAX_AGE, try to convert to integer
                if field in ["PORT", "CONN_MAX_AGE"]:
                    try:
                        updated_database[field] = int(value)
                    except ValueError:
                        # Keep as string if not a valid integer
                        updated_database[field] = value
                else:
                    updated_database[field] = value

        # Add SSL options if host is not localhost
        if updated_database.get("HOST") and updated_database.get("HOST") != "localhost":
            ssl_option = self.prompt_for_ssl_mode()
            if ssl_option:
                updated_database["OPTIONS"] = {"sslmode": ssl_option}

        return updated_database

    def prompt_for_ssl_mode(self):
        """Prompt user to select an SSL mode for PostgreSQL connection"""
        ssl_modes = [
            "disable",
            "allow",
            "prefer",
            "require",
            "verify-ca",
            "verify-full",
        ]

        result = ListSelector(
            "Select SSL mode for database connection (if not sure leave allow):",
            ssl_modes,
            self.console_manager,
        )

        return result.select()

    def success_database_updated(self):
        self.console_manager.print_success("Database successfully updated")

    def print_lookup_database_dependencies(self):
        self.console_manager.print_lookup("Looking for database dependencies")

    def prompt_install_database_dependencies(self, dependencies):
        selector = QuestionSelector(
            f"Missing dependencies: {dependencies} \n Do you wish to install",
            self.console_manager,
        )
        return selector.select()

    def print_progress_database_dependencies_install(self):
        self.console_manager.print_progress("Installing dependencies")

    def print_database_dependencies_present(self):
        self.console_manager.print_step_progress(
            "Database dependencies", "All dependencies present"
        )

    def prompt_static_files_solution(self):

        selector = ListSelector(
            "Select static file handling solution:",
            ["Whitenoise", "Ngnix"],
            self.console_manager,
        )
        return selector.select()

    def prompt_install_whitenoise(self):
        selector = QuestionSelector(
            "Whitenoise not installed \n Do you wish to install it now:",
            self.console_manager,
        )
        return selector.select()

    def print_progress_whitenoise(self):
        self.console_manager.print_progress("Setting whitenoise in middleware")

    def success_progress_whitenoise(self):
        self.console_manager.print_step_progress(
            "Middleware", "Whitenoise added to middleware"
        )

    def print_progress_static_url(self):
        self.console_manager.print_progress("Setting static url")

    def success_progress_static_url(self):
        self.console_manager.print_step_progress(
            "STATIC_URL", "Static url set to /static/"
        )

    def print_progress_static_root(self):
        self.console_manager.print_progress("Setting static root")

    def success_progress_static_root(self):
        self.console_manager.print_step_progress(
            "STATIC_ROOT", "os.path.join(BASE_DIR, 'staticfiles')"
        )

    def print_progress_static_root_add_os(self):
        self.console_manager.print_progress("OS library missing, ading library")

    def print_progress_static_file_dirs_create(self):
        self.console_manager.print_progress("Creating STATICFILE_DIRS setting")

    def success_progress_static_file_dirs_add(self):
        self.console_manager.print_step_progress("STATICFILE_DIRS", "Whitenoise added")

    def progress_staticfiles_storage_add(self):
        self.console_manager.print_progress("Adding whitenoise to staticfile storage")

    def success_staticfiles_storage_add(self):
        self.console_manager.print_step_progress(
            "STATICFILES_STORAGE", "Whitenoise added"
        )
