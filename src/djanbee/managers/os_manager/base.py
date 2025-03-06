from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple


class BaseOSManager(ABC):
    @abstractmethod
    def get_dir(self) -> Path:
        """Returns current working directory"""
        pass

    @abstractmethod
    def get_pip_path(self, venv_path: Path) -> Path:
        """Gets platform-specific pip executable path"""
        pass

    @abstractmethod
    def check_package_installed(self, package_name: str) -> bool:
        """Checks if a system package is installed"""
        pass

    @abstractmethod
    def check_service_status(self, service_name: str) -> bool:
        """Checks if a system service is running"""
        pass

    @abstractmethod
    def install_package(self, package_name: str) -> Tuple[bool, str]:
        """Installs a system package"""
        pass

    @abstractmethod
    def start_service(self, service_name: str) -> Tuple[bool, str]:
        """Starts a system service"""
        pass

    @abstractmethod
    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        """Stops a system service"""
        pass

    @abstractmethod
    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        """Restarts a system service"""
        pass

    @abstractmethod
    def enable_service(self, service_name: str) -> Tuple[bool, str]:
        """Enables a service to start on boot"""
        pass

    @abstractmethod
    def run_command(self, command: str | List[str]) -> Tuple[bool, str]:
        """Runs a system command"""
        pass

    @abstractmethod
    def get_username(self) -> str:
        """Gets current user's username"""
        pass

    @abstractmethod
    def is_admin(self) -> bool:
        """Checks if current user has admin privileges"""
        pass
