from typing import Tuple
from ..managers import OSManager
import psycopg2
from psycopg2 import Error


class DatabaseManager:
    def __init__(self, os_manager: OSManager):
        self.os_manager = os_manager
        self._superuser = "postgres"
        self._superuser_password = ""
        self.host = ""
        self.database = "postgres"
        self.username = ""
        self._db_name = ""

    # Property getters/setters
    @property
    def superuser(self) -> str:
        return self._superuser

    @superuser.setter
    def superuser(self, value: str):
        self._superuser = value

    @property
    def superuser_password(self) -> str:
        return self._superuser_password

    @superuser_password.setter
    def superuser_password(self, value: str):
        self._superuser_password = value

    @property
    def db_name(self) -> str:
        return self._db_name

    @db_name.setter
    def db_name(self, value: str):
        self._db_name = value

    def create_database(self, db_name: str) -> Tuple[bool, str]:
        """Create a new database."""
        return self.execute_admin_command(f"CREATE DATABASE {db_name};")

    # Core database connection methods
    def _get_admin_connection(self):
        """Get connection with superuser privileges using peer authentication."""
        return psycopg2.connect(
            dbname=self.database,
            user=self.superuser,
            host="",  # Empty host forces Unix domain socket connection
        )

    def set_database_user(self, username):
        self.username = username

    def _get_connection(self):
        return psycopg2.connect(
            dbname=self.database,
            user=self.username,
            host=self.host,
        )

    def login_user(self, username):
        self.set_database_user(username)
        try:
            conn = self._get_connection()
            conn.close()
            return True, "Login successful"
        except psycopg2.Error as e:
            return False, f"Login failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during login: {str(e)}"

    def execute_admin_command(self, command: str, params=None) -> Tuple[bool, str]:
        """Execute a command with superuser privileges."""
        try:
            # Run the command as the postgres system user
            cmd = f'sudo -u postgres psql -c "{command}"'
            success, output = self.os_manager.run_command(cmd)
            if not success:
                return False, f"Command failed: {output}"
            return True, "Command executed successfully"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    # Database operations
    def create_database(self, db_name: str) -> Tuple[bool, str]:
        """Create a new database."""
        self.db_name = db_name.lower()
        return self.execute_admin_command(f"CREATE DATABASE {db_name};")

    def create_user(self, username: str) -> Tuple[bool, str]:
        """Create a new database user."""
        return self.execute_admin_command(f"CREATE USER {username};")

    # Installation and configuration methods
    def install_postgres(self):
        """
        Install PostgreSQL with progress updates.

        Yields:
            Tuple[str, bool, str]: (step_name, success, message)
        """

        # Install packages
        success, message = self.install_postgres_packages()
        if not success:
            yield "Package Installation", False, message
            return
        yield "Package Installation", True, "Packages installed successfully"

        # Configure service
        success, message = self.configure_postgres_service()
        if not success:
            yield "Service Configuration", False, message
            return
        yield "Service Configuration", True, "Service configured successfully"

        # Configure user
        success, message = self.configure_postgres_user()
        if not success:
            yield "User Configuration", False, message
            return
        yield "User Configuration", True, "User configured successfully"

        # Verify installation
        is_installed, location = self.check_postgres_installation()
        if not is_installed:
            yield "Installation Verification", False, "PostgreSQL installation could not be verified"
            return

        is_running = self.check_postgres_status()
        if not is_running:
            yield "Service Verification", False, "PostgreSQL service is not running"
            return

        yield "Installation Complete", True, f"PostgreSQL successfully installed at {location}"

    def install_postgres_packages(self):
        """
        Install PostgreSQL packages and dependencies.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        package_names = [
            "postgresql",
            "postgresql-contrib",
            "postgresql-client",
            "libpq-dev",
        ]

        for package in package_names:
            success, message = self.os_manager.install_package(package)
            if not success:
                return False, f"Failed to install {package}: {message}"

        return True, "PostgreSQL packages installed successfully"

    def configure_postgres_service(self):
        """
        Enable and start the PostgreSQL service.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Enable service
        success, message = self.os_manager.enable_service("postgresql")
        if not success:
            return False, f"Failed to enable PostgreSQL service: {message}"

        # Start service
        success, message = self.os_manager.start_service("postgresql")
        if not success:
            return False, f"Failed to start PostgreSQL service: {message}"

        return True, "PostgreSQL service started successfully"

    def configure_postgres_user(self):
        """
        Configure PostgreSQL user and initial database.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Create default user if doesn't exist
            if not self.os_manager.user_exists("postgres"):
                success, message = self.os_manager.run_command(
                    "sudo -u postgres createuser --superuser $USER"
                )
                if not success:
                    return False, f"Failed to create PostgreSQL user: {message}"

            return True, "PostgreSQL user configured successfully"
        except Exception as e:
            return False, f"Failed to configure PostgreSQL user: {str(e)}"

    # Status check methods

    def check_postgres_installation(self) -> Tuple[bool, str]:
        """
        Check if PostgreSQL is properly installed by verifying the client component.

        Returns:
            Tuple[bool, str]: (is_installed, message)
        """
        is_client_installed = self.os_manager._manager.check_package_installed("psql")

        if not is_client_installed:
            return False, "PostgreSQL client (psql) not found"

        return True, "PostgreSQL installed"

    def check_postgres_status(self) -> bool:
        is_active = self.os_manager._manager.check_service_status("postgresql")
        return is_active

    def get_all_databases(self) -> Tuple[bool, list | str]:
        """
        Get a list of all PostgreSQL databases, excluding system databases.

        Returns:
            Tuple[bool, Union[list, str]]: (success, list of databases or error message)
        """
        try:
            # Use psql to list databases
            cmd = "sudo -u postgres psql -t -c \"SELECT datname FROM pg_database WHERE datname NOT IN ('template0', 'template1', 'postgres');\""
            success, output = self.os_manager.run_command(cmd)

            if not success:
                return False, f"Failed to get databases: {output}"

            # Process the output - strip whitespace and empty lines
            databases = [db.strip() for db in output.split("\n") if db.strip()]
            return True, databases

        except Exception as e:
            return False, f"Error getting databases: {str(e)}"
