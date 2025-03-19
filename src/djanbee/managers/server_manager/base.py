from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple


class BaseServerManager(ABC):
    @abstractmethod
    def check_server_installed(self) -> bool:
        """Checks if the server is installed"""
        pass

    @abstractmethod
    def install_server(self) -> Tuple[bool, str]:
        """Installs the server if not already installed"""
        pass

    @abstractmethod
    def start_server(self) -> Tuple[bool, str]:
        """Starts the server"""
        pass

    @abstractmethod
    def stop_server(self) -> Tuple[bool, str]:
        """Stops the server"""
        pass

    @abstractmethod
    def restart_server(self) -> Tuple[bool, str]:
        """Restarts the server"""
        pass

    @abstractmethod
    def enable_server(self) -> Tuple[bool, str]:
        """Enables the server to start on boot"""
        pass

    @abstractmethod
    def check_server_status(self) -> bool:
        """Checks if the server is running"""
        pass

    @abstractmethod
    def get_server_version(self) -> str:
        """Gets the server version"""
        pass
