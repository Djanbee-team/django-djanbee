import os
import subprocess
from pathlib import Path
from typing import List, Tuple

from ..base import BaseOSManager


class UnixOSManager(BaseOSManager):
    def get_dir(self) -> Path:
        """Returns current working directory"""
        return Path.cwd().resolve()

    def get_pip_path(self, venv_path: Path) -> Path:
        """Gets platform-specific pip executable path"""
        return venv_path / "bin" / "pip"

    def check_package_installed(self, package_name: str) -> bool:
        """Checks if a system package is installed"""
        try:
            result = subprocess.run(
                ["which", package_name], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_service_status(self, service_name: str) -> bool:
        """Checks if a system service is running"""
        try:
            result = subprocess.run(
                ["systemctl", "status", service_name], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_package(self, package_name: str) -> Tuple[bool, str]:
        """Installs a system package"""
        try:
            # First update package list
            update_result = subprocess.run(
                ["sudo", "apt-get", "update"], capture_output=True, text=True
            )
            if update_result.returncode != 0:
                return False, f"Failed to update package list: {update_result.stderr}"

            # Then install the package
            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", package_name],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return True, f"Successfully installed {package_name}"
            else:
                return False, f"Failed to install {package_name}: {result.stderr}"

        except Exception as e:
            return False, f"Error installing package: {str(e)}"

    def start_service(self, service_name: str) -> Tuple[bool, str]:
        """Starts a system service"""
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", service_name],
                capture_output=True,
                text=True,
            )
            return (
                result.returncode == 0,
                result.stdout if result.returncode == 0 else result.stderr,
            )
        except Exception as e:
            return False, str(e)

    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        """Stops a system service"""
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "stop", service_name],
                capture_output=True,
                text=True,
            )
            return (
                result.returncode == 0,
                result.stdout if result.returncode == 0 else result.stderr,
            )
        except Exception as e:
            return False, str(e)

    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        """Restarts a system service"""
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "restart", service_name],
                capture_output=True,
                text=True,
            )
            return (
                result.returncode == 0,
                result.stdout if result.returncode == 0 else result.stderr,
            )
        except Exception as e:
            return False, str(e)

    def enable_service(self, service_name: str) -> Tuple[bool, str]:
        """Enables a service to start on boot"""
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "enable", service_name],
                capture_output=True,
                text=True,
            )
            return (
                result.returncode == 0,
                result.stdout if result.returncode == 0 else result.stderr,
            )
        except Exception as e:
            return False, str(e)

    def run_command(self, command: str | List[str]) -> Tuple[bool, str]:
        """Runs a system command"""
        try:
            # Convert string command to list if necessary
            if isinstance(command, str):
                import shlex

                command_list = shlex.split(command)
            else:
                command_list = command

            result = subprocess.run(command_list, capture_output=True, text=True)

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()

        except Exception as e:
            return False, str(e)

    def get_username(self) -> str:
        """Gets current user's username"""
        try:
            result = subprocess.run(["whoami"], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return ""

    def is_admin(self) -> bool:
        """Checks if current user has admin privileges"""
        try:
            return os.geteuid() == 0
        except Exception:
            return False

    def is_venv_directory(self, path: Path) -> bool:
        """Check if a directory is a virtual environment on Unix systems"""
        cfg_exists = (path / "pyvenv.cfg").exists()
        bin_exists = (path / "bin").exists()
        python_exists = (path / "bin" / "python").exists()
        return cfg_exists and bin_exists and python_exists
