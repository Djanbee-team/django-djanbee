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

    def check_pip_package_installed(self, package_name: str) -> bool:
        """Checks if a Python package is installed via pip"""
        try:
            import sys

            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_pip_package(self, package_name: str) -> Tuple[bool, str]:
        """Installs a Python package via pip"""
        try:
            import sys

            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return True, f"Successfully installed {package_name}"
            else:
                return False, f"Failed to install {package_name}: {result.stderr}"

        except Exception as e:
            return False, f"Error installing package: {str(e)}"

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
        
    def run_python_command(self, command_args: List[str]) -> Tuple[bool, str]:
        """
        Runs a Python command using the system's Python version
        
        Args:
            command_args: Arguments to pass to Python (excluding the Python command itself)
            
        Returns:
            Tuple of (success, output/error message)
        """
        try:
            # Determine the Python executable to use
            python_exec_result = self.run_command("which python3 || which python")
            
            if not python_exec_result[0]:
                return False, "Could not find Python executable"
                
            python_exec = python_exec_result[1]
            
            # Build the full command with the determined Python executable
            full_command = [python_exec] + command_args
            
            # Use the existing run_command method to execute
            return self.run_command(full_command)
                
        except Exception as e:
            return False, f"Error running Python command: {str(e)}"

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
        
    def check_directory_exists(self, dir_path: str) -> bool:
        """Check if a directory exists"""
        try:
            path = Path(dir_path)
            return path.exists() and path.is_dir()
        except Exception:
            return False
            
    def check_file_exists(self, file_path: Path) -> bool:
        """Check if a file exists"""
        try:
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False

    def reload_daemon(self) -> Tuple[bool, str]:
        """
        Reloads the systemd daemon to recognize new or changed service files
        
        Returns:
            Tuple of (success, message)
        """
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "daemon-reload"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return True, "Systemd daemon reloaded successfully"
            else:
                return False, f"Failed to reload systemd daemon: {result.stderr.strip()}"
                
        except Exception as e:
            return False, f"Error reloading systemd daemon: {str(e)}"
            
    def user_exists(self, username: str) -> bool:
        """
        Check if a system user exists.
        
        Args:
            username: Username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            # Try to get user info using id command
            result = subprocess.run(
                ["id", username],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            # If any error occurs, assume user doesn't exist
            return False