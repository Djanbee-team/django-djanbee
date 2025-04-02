from pathlib import Path
from typing import Tuple, List, Dict, Optional
import textwrap
from ...os_manager import OSManager
from ...console_manager import ConsoleManager
from ...django_manager import DjangoManager
from ..base import BaseSocketManager


class GunicornSocketManager(BaseSocketManager):
    """
    Manages the Gunicorn socket configuration for Django deployments
    """

    def __init__(
        self,
        os_manager: OSManager,
        console_manager: ConsoleManager,
        django_manager: DjangoManager,
    ):
        """
        Initialize with OS manager for platform-specific operations

        Args:
            os_manager: OS manager for platform-specific operations
            console_manager: Console manager for output display
        """
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.django_manager = django_manager
        self.service_name = "gunicorn"

    def check_socket_service_exists(
        self, project_name: str
    ) -> Tuple[bool, Optional[Path]]:
        """
        Check if a Gunicorn socket service exists for the given project

        Args:
            project_name: Name of the project (used to identify the service)

        Returns:
            Tuple of (exists, service_file_path)
            If service doesn't exist, path will be None
        """
        try:
            # Construct the service name based on project name
            service_name = f"gunicorn-{project_name}.service"
            service_file_path = Path(f"/etc/systemd/system/{service_name}")

            # Check if the service file exists
            service_exists = self.os_manager.check_file_exists(service_file_path)

            if service_exists:
                self.console_manager.print_info(
                    f"Gunicorn service file found at {service_file_path}"
                )

                # Also check if the service is active
                active_service_name = f"gunicorn-{project_name}"
                service_active = self.os_manager.check_service_status(
                    active_service_name
                )

                if service_active:
                    self.console_manager.print_info(
                        f"Gunicorn service for {project_name} is active and running"
                    )
                else:
                    self.console_manager.print_error(
                        f"Gunicorn service file exists for {project_name} but service is not running"
                    )

                return service_exists, service_file_path
            else:
                self.console_manager.print_info(
                    f"No Gunicorn service file found for {project_name}"
                )
                return False, None

        except Exception as e:
            self.console_manager.print_error(
                f"Error checking Gunicorn socket service: {str(e)}"
            )
            return False, None

    def create_socket_service(
        self,
        project_path: Path,
        project_name: str,
        wsgi_app: str = None,
        use_sudo: bool = False,
    ) -> Tuple[bool, str]:
        """
        Create a systemd service file for Gunicorn that will create the socket

        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            wsgi_app: WSGI application path (e.g., 'myproject.wsgi:application')
            use_sudo: Whether to use sudo for file operations

        Returns:
            Tuple of (success, message or socket_path)
        """
        try:
            dir_success, dir_message = self.verify_run_gunicorn_directory()
            if not dir_success:
                return (
                    False,
                    f"Failed to verify or create /run/gunicorn directory: {dir_message}",
                )

            # Determine socket path

            socket_file_path = f"/run/gunicorn/{project_name}.sock"

            # Determine wsgi_app if not provided
            if not wsgi_app:
                wsgi_app = f"{project_name}.wsgi:application"

            # Get user information
            user = self.os_manager.get_username()

            # Create unique service name based on project name
            service_name = f"gunicorn-{project_name}"
            service_filename = f"{service_name}.service"

            # Create service file content with project-specific description
            service_content = (
                textwrap.dedent(
                    f"""
                [Unit]
                Description=Gunicorn daemon for {project_name}
                After=network.target

                [Service]
                User={user}
                Group={user}
                RuntimeDirectory=gunicorn
                WorkingDirectory={project_path}
                ExecStart={self.django_manager.state.active_venv_path}/bin/gunicorn \\
                        --access-logfile - \\
                        --workers 3 \\
                        --bind unix:{socket_file_path} \\
                        {wsgi_app}

                [Install]
                WantedBy=multi-user.target 
                """
                ).strip()
                + "\n"
            )

            # Write the service file with project-specific name
            service_file_path = Path(f"/etc/systemd/system/{service_filename}")
            success, message = self.os_manager.write_text_file(
                service_file_path, service_content, use_sudo=use_sudo
            )

            if not success:
                return False, f"Failed to create service file: {message}"

            # Reload systemd daemon
            reload_success, reload_message = self.os_manager.run_command(
                ["sudo", "systemctl", "daemon-reload"]
            )
            print(reload_message)
            if not reload_success:
                return False, f"Failed to reload systemd daemon: {reload_message}"

            # Enable the service
            enable_success, enable_message = self.os_manager.enable_service(
                service_name
            )
            if not enable_success:
                return False, f"Failed to enable service: {enable_message}"

            # Use start_socket_service to start the service
            start_success, start_message = self.start_socket_service(project_name)
            if not start_success:
                return False, f"Failed to start service: {start_message}"

            return True, str(socket_file_path)

        except Exception as e:
            return False, f"Error creating Gunicorn socket service: {str(e)}"

    def start_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Starts the Gunicorn socket service for the given project

        Args:
            project_name: Name of the project (used to identify the service)

        Returns:
            Tuple of (success, message)
        """
        try:
            # Create the service name based on project name
            service_name = f"gunicorn-{project_name}"

            # Check if the service exists before trying to start it
            exists, _ = self.check_socket_service_exists(project_name)
            if not exists:
                self.console_manager.print_error(
                    f"Socket service for project '{project_name}' does not exist"
                )
                return (
                    False,
                    f"Socket service for project '{project_name}' does not exist",
                )

            # Start the service using the OS manager
            success, message = self.os_manager.start_service(service_name)

            if success:
                self.console_manager.print_step_progress(
                    f"Socket service", f" '{service_name}' started successfully"
                )
                return True, f"Socket service started successfully"
            else:
                self.console_manager.print_error(
                    f"Failed to start socket service: {message}"
                )
                return False, f"Failed to start socket service: {message}"

        except Exception as e:
            error_msg = f"Error starting socket service: {str(e)}"
            self.console_manager.print_error(error_msg)
            return False, error_msg

    def verify_run_gunicorn_directory(self) -> Tuple[bool, str]:
        """
        Verifies that the /run/gunicorn directory exists and the current user has access to it.
        Creates the directory if it doesn't exist.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if /run/gunicorn directory exists
            run_gunicorn_path = Path("/run/gunicorn")

            # Check if directory exists using OS manager
            dir_exists = run_gunicorn_path.exists() and run_gunicorn_path.is_dir()

            if not dir_exists:
                self.console_manager.print_info(
                    "The /run/gunicorn directory does not exist. Attempting to create it..."
                )

                # We need to use sudo to create directory in /run
                create_result, create_message = self.os_manager.run_command(
                    ["sudo", "mkdir", "-p", "/run/gunicorn"]
                )

                if not create_result:
                    return (
                        False,
                        f"Failed to create /run/gunicorn directory: {create_message}",
                    )

                # Get current username
                username = self.os_manager.get_username()

                # Set ownership to current user
                chown_result, chown_message = self.os_manager.run_command(
                    ["sudo", "chown", f"{username}:{username}", "/run/gunicorn"]
                )

                if not chown_result:
                    return (
                        False,
                        f"Failed to set permissions on /run/gunicorn: {chown_message}",
                    )

                # Set directory permissions
                chmod_result, chmod_message = self.os_manager.run_command(
                    ["sudo", "chmod", "755", "/run/gunicorn"]
                )

                if not chmod_result:
                    return (
                        False,
                        f"Failed to set directory permissions: {chmod_message}",
                    )

                self.console_manager.print_info(
                    "Successfully created /run/gunicorn directory with proper permissions"
                )
                return True, "Directory created and configured successfully"

            # If directory exists, check if current user has write access
            username = self.os_manager.get_username()
            access_check, access_message = self.os_manager.run_command(
                ["test", "-w", "/run/gunicorn"]
            )

            if not access_check:
                self.console_manager.print_warning(
                    f"User '{username}' does not have write access to /run/gunicorn. Attempting to fix permissions..."
                )

                # Try to fix permissions
                fix_result, fix_message = self.os_manager.run_command(
                    ["sudo", "chown", f"{username}:{username}", "/run/gunicorn"]
                )

                if not fix_result:
                    return (
                        False,
                        f"Failed to set permissions on existing /run/gunicorn directory: {fix_message}",
                    )

                self.console_manager.print_info(
                    "Successfully updated permissions on /run/gunicorn directory"
                )
                return True, "Directory permissions updated successfully"

            self.console_manager.print_info(
                f"The /run/gunicorn directory exists and user '{username}' has proper access"
            )
            return True, "Directory exists with proper permissions"

        except Exception as e:
            error_msg = f"Error verifying /run/gunicorn directory: {str(e)}"
            self.console_manager.print_error(error_msg)
            return False, error_msg
