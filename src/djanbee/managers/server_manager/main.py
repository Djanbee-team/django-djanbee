import os
import platform
import subprocess
from pathlib import Path
from typing import Callable, List, Tuple
from collections import namedtuple

from ..os_manager import OSManager
from ..console_manager import ConsoleManager
from .server_implementations import NginxServerManager

Result = namedtuple("Result", ["valid", "object"])


class ServerManager:
    def __init__(
        self,
        os_manager: OSManager,
        console_manager: ConsoleManager,
        server_type: str = "nginx",
    ):
        """Initializes server-specific manager"""
        self.os_manager = os_manager
        self.console_manager = console_manager

        if server_type.lower() == "nginx":
            self._manager = NginxServerManager(self.os_manager, self.console_manager)
        else:
            raise ValueError(f"Unsupported server type: {server_type}")

    def check_server_installed(self) -> bool:
        """Checks if the server is installed"""
        return self._manager.check_server_installed()

    def install_server(self) -> Tuple[bool, str]:
        """Installs the server if not already installed"""
        return self._manager.install_server()

    def start_server(self) -> Tuple[bool, str]:
        """Starts the server"""
        return self._manager.start_server()

    def stop_server(self) -> Tuple[bool, str]:
        """Stops the server"""
        return self._manager.stop_server()

    def restart_server(self) -> Tuple[bool, str]:
        """Restarts the server"""
        return self._manager.restart_server()

    def enable_server(self) -> Tuple[bool, str]:
        """Enables the server to start on boot"""
        return self._manager.enable_server()

    def check_server_status(self) -> bool:
        """Checks if the server is running"""
        return self._manager.check_server_status()

    def get_server_version(self) -> str:
        """Gets the server version"""
        return self._manager.get_server_version()

    def get_dependencies(self) -> List[str]:
        """Returns list of dependencies for the current server"""
        if hasattr(self._manager, "get_dependencies"):
            return self._manager.get_dependencies()
        return []

    def verify_dependencies(self) -> List[Tuple[str, bool, str]]:
        """Verifies all dependencies"""
        if hasattr(self._manager, "verify_dependencies"):
            return self._manager.verify_dependencies()
        return []

    def install_dependency(self, dependency: str) -> Tuple[bool, str]:
        """Installs a specific dependency"""
        if hasattr(self._manager, "install_dependency"):
            return self._manager.install_dependency(dependency)
        return False, "Server doesn't support dependency installation"
