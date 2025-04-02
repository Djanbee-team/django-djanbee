from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple


class BaseSocketManager(ABC):
    """
    Abstract base class for socket managers used in web server deployments
    """

    @abstractmethod
    def check_socket_service_exists(self, project_name: str) -> bool:
        """
        Check if a socket file exists for the given project

        Args:
            project_name: Name of the project (used as part of socket filename)

        Returns:
            True if socket file exists, False otherwise
        """
        pass

    @abstractmethod
    def create_socket_service(
        self, project_path: Path, project_name: str
    ) -> Tuple[bool, str]:
        """
        Create a socket file for the given project

        Args:
            project_path: Path to the project directory
            project_name: Name of the project

        Returns:
            Tuple of (success, message or socket_path)
        """
        pass
