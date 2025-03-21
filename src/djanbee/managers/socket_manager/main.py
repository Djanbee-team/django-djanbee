from pathlib import Path
from typing import Tuple, Optional

from ..os_manager import OSManager
from ..console_manager import ConsoleManager
from ..django_manager import DjangoManager
from .socket_implementations import GunicornSocketManager
from .base import BaseSocketManager


class SocketManager:
    """
    Factory class for creating and managing different socket implementations
    """

    def __init__(
        self,
        os_manager: OSManager,
        console_manager: ConsoleManager,
        django_manager: DjangoManager,
        socket_type: str = "gunicorn",
    ):
        """
        Initialize socket manager with dependencies

        Args:
            os_manager: OS manager for platform-specific operations
            console_manager: Console manager for output display
            django_manager: Django manager for project information
            socket_type: Type of socket implementation to use
        """
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.django_manager = django_manager

        # Initialize the appropriate socket manager based on type
        if socket_type.lower() == "gunicorn":
            self._manager = GunicornSocketManager(
                self.os_manager, self.console_manager, self.django_manager
            )
        else:
            raise ValueError(f"Unsupported socket type: {socket_type}")

    def check_socket_service_exists(self, project_name: str) -> bool:
        """
        Check if a socket file exists for the given project

        Args:
            project_name: Name of the project (used as part of socket filename)

        Returns:
            True if socket file exists, False otherwise
        """
        return self._manager.check_socket_service_exists(project_name)

    def create_socket_service(
        self, project_path: Path, project_name: str, use_sudo: bool = False
    ) -> Tuple[bool, str]:
        """
        Create a socket file for the given project

        Args:
            project_path: Path to the project directory
            project_name: Name of the project

        Returns:
            Tuple of (success, message or socket_path)
        """
        return self._manager.create_socket_service(
            project_path, project_name, use_sudo=use_sudo
        )
