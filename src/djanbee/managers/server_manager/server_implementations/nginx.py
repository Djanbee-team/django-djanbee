import os
import subprocess
from pathlib import Path
from typing import List, Tuple

from ..base import BaseServerManager
from ...os_manager import OSManager
from ...console_manager import ConsoleManager


class NginxServerManager(BaseServerManager):
    def __init__(self, os_manager: OSManager, console_manager: ConsoleManager):
        """Initialize with OS manager for platform-specific operations"""
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.server_name = "nginx"
        self.dependencies = ["gunicorn"]

    def check_server_installed(self) -> bool:
        """Checks if Nginx is installed"""
        return self.os_manager.check_package_installed(self.server_name)

    def install_server(self) -> Tuple[bool, str]:
        """Installs Nginx if not already installed"""
        if self.check_server_installed():
            return True, "Nginx is already installed"

        return self.os_manager.install_package(self.server_name)

    def start_server(self) -> Tuple[bool, str]:
        """Starts the Nginx server"""
        return self.os_manager.start_service(self.server_name)

    def stop_server(self) -> Tuple[bool, str]:
        """Stops the Nginx server"""
        return self.os_manager.stop_service(self.server_name)

    def restart_server(self) -> Tuple[bool, str]:
        """Restarts the Nginx server"""
        return self.os_manager.restart_service(self.server_name)

    def enable_server(self) -> Tuple[bool, str]:
        """Enables Nginx to start on boot"""
        return self.os_manager.enable_service(self.server_name)

    def check_server_status(self) -> bool:
        """Checks if Nginx is running"""
        return self.os_manager.check_service_status(self.server_name)

    def get_server_version(self) -> str:
        """Gets the Nginx version"""
        success, output = self.os_manager.run_command([self.server_name, "-v"])
        if success:
            return output
        else:
            return "Unknown version"

    # Additional methods for dependency management
    def get_dependencies(self) -> List[str]:
        """Returns the list of dependencies required by this server"""
        return self.dependencies

    def check_gunicorn_installed(self) -> bool:
        """Checks if Gunicorn is installed via pip"""
        return self.os_manager.check_pip_package_installed("gunicorn")

    def install_gunicorn(self) -> Tuple[bool, str]:
        """Installs Gunicorn if not already installed"""
        if self.check_gunicorn_installed():
            return True, "Gunicorn is already installed"
        return self.os_manager.install_pip_package("gunicorn")

    def verify_dependencies(self) -> List[Tuple[str, bool, str]]:
        """Verifies all dependencies and returns results"""
        results = []
        for dependency in self.dependencies:
            check_method = getattr(self, f"check_{dependency}_installed", None)
            if check_method and callable(check_method):
                is_installed = check_method()
                status_msg = f"{dependency} is {'installed' if is_installed else 'not installed'}"
                results.append((dependency, is_installed, status_msg))
            else:
                results.append((dependency, False, f"Cannot check {dependency}"))
        return results

    def install_dependency(self, dependency: str) -> Tuple[bool, str]:
        """Install a specific dependency"""
        if dependency not in self.dependencies:
            return False, f"{dependency} is not a recognized dependency"

        install_method = getattr(self, f"install_{dependency}", None)
        if install_method and callable(install_method):
            return install_method()
        else:
            return False, f"No installation method for {dependency}"
