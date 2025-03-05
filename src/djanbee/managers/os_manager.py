from pathlib import Path
import platform
from abc import ABC, abstractmethod
from typing import Callable, TypeVar, List, Tuple, Optional
import os
import subprocess


class BaseOSManager(ABC):
    @abstractmethod
    def get_dir(self) -> Path:
        pass

    @abstractmethod
    def get_pip_path(self, venv_path: Path) -> Path:
        """Get platform-specific pip executable path"""
        pass

    @abstractmethod
    def check_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed on the system"""
        pass

    @abstractmethod
    def check_service_status(self, service_name: str) -> bool:
        """Check if service is running"""
        pass

    @abstractmethod
    def install_package(self, package_name: str) -> Tuple[bool, str]:
        """Install a system package

        Returns:
            Tuple[bool, str]: (success, message)
        """
        pass

    @abstractmethod
    def start_service(self, service_name: str) -> Tuple[bool, str]:
        """Start a system service"""
        pass

    @abstractmethod
    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        """Stop a system service"""
        pass

    @abstractmethod
    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        """Restart a system service"""
        pass

    @abstractmethod
    def enable_service(self, service_name: str) -> Tuple[bool, str]:
        """Enable a service to start on boot"""
        pass

    @abstractmethod
    def run_command(self, command: str | List[str]) -> Tuple[bool, str]:
        """Run a system command

        Args:
            command: Command to run (string or list of arguments)

        Returns:
            Tuple[bool, str]: (success, output or error message)
        """
        pass

    @abstractmethod
    def get_username(self) -> str:
        """Get current user's username"""
        pass

    @abstractmethod
    def is_admin(self) -> bool:
        """Check if current user has admin privileges"""
        pass


class UnixOSManager(BaseOSManager):
    def get_dir(self) -> Path:
        return Path.cwd().resolve()

    def get_pip_path(self, venv_path: Path) -> Path:
        return venv_path / "bin" / "pip"

    def check_package_installed(self, package_name: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["which", package_name], capture_output=True, text=True
            )
            return (result.returncode == 0, result)
        except Exception:
            return False

    def check_service_status(self, service_name: str) -> bool:
        try:
            result = subprocess.run(
                ["systemctl", "status", service_name], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_package(self, package_name: str) -> Tuple[bool, str]:
        """Install a package using apt-get on Debian/Ubuntu systems"""
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
        try:
            result = subprocess.run(["whoami"], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return ""

    def is_admin(self) -> bool:
        try:
            return os.geteuid() == 0
        except Exception:
            return False


class WindowsOSManager(BaseOSManager):
    def get_dir(self) -> Path:
        return Path.cwd().resolve()

    def get_pip_path(self, venv_path: Path) -> Path:
        return venv_path / "Scripts" / "pip.exe"

    def check_package_installed(self, package_name: str) -> bool:
        try:
            result = subprocess.run(
                ["where", package_name], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_package(self, package_name: str) -> Tuple[bool, str]:
        """Install a package using winget"""
        try:
            result = subprocess.run(
                [
                    "winget",
                    "install",
                    "--exact",
                    package_name,
                    "--accept-source-agreements",
                    "--accept-package-agreements",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return True, f"Successfully installed {package_name}"
            else:
                return False, f"Failed to install {package_name}: {result.stderr}"

        except Exception as e:
            return False, f"Error installing package: {str(e)}"

    def check_service_status(self, service_name: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            is_active = "RUNNING" in result.stdout
            return is_active, result.stdout
        except Exception as e:
            return False, f"Error checking service status: {str(e)}"

    def start_service(self, service_name: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["sc", "start", service_name], capture_output=True, text=True
            )
            return (
                "START_PENDING" in result.stdout or "RUNNING" in result.stdout,
                result.stdout,
            )
        except Exception as e:
            return False, str(e)

    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["sc", "stop", service_name], capture_output=True, text=True
            )
            return (
                "STOP_PENDING" in result.stdout or "STOPPED" in result.stdout,
                result.stdout,
            )
        except Exception as e:
            return False, str(e)

    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        stop_success, stop_msg = self.stop_service(service_name)
        if not stop_success:
            return False, f"Failed to stop service: {stop_msg}"

        start_success, start_msg = self.start_service(service_name)
        if not start_success:
            return False, f"Failed to start service: {start_msg}"

        return True, "Service restarted successfully"

    def enable_service(self, service_name: str) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["sc", "config", service_name, "start=auto"],
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
        try:
            # For Windows, we'll use shell=True for string commands
            if isinstance(command, str):
                result = subprocess.run(
                    command, capture_output=True, text=True, shell=True
                )
            else:
                result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()

        except Exception as e:
            return False, str(e)

    def get_username(self) -> str:
        try:
            result = subprocess.run(["whoami"], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return ""

    def is_admin(self) -> bool:
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False


class OSManager:
    def __init__(self):
        system = platform.system().lower()
        if system == "windows":
            self._manager = WindowsOSManager()
        else:
            self._manager = UnixOSManager()
        self._current_project_path: Optional[Path] = None

    @property
    def project_path(self) -> Optional[Path]:
        return self._current_project_path

    def set_project_path(self, path: Path) -> None:
        """Set and validate project path"""
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")
        self._current_project_path = path

    def set_dir(self, dir: str | Path = "."):
        try:
            # Convert to Path object if string
            dir_path = Path(dir)

            # Check if directory exists
            if not dir_path.exists():
                raise FileNotFoundError(f"Directory does not exist: {dir_path}")

            if not dir_path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {dir_path}")

            # Change to directory
            os.chdir(dir_path)

        except Exception as e:
            raise Exception(f"Failed to set directory: {str(e)}")

    def get_dir(self) -> Path:
        return self._manager.get_dir()

    def search_subfolders(
        self, validator: Callable, max_depth: int = 1, search_path=""
    ):
        """
        Search subfolders using a validator function

        Args:
            search_path: Directory to search in
            validator: Function that validates each folder and returns a value
            max_depth: Maximum depth to search (default: 1 level deep)

        Returns:
            List of tuples containing (folder_name, folder_path, validator_result)
            for each folder where validator returns a truthy value
        """
        if not search_path:
            search_path = self.get_dir()

        search_path = Path(search_path)
        results = []

        def recursion(path, depth):
            if depth > max_depth:
                return

            try:
                for folder in path.iterdir():
                    if path.name.startswith("."):
                        return
                    result = validator(folder)
                    if result:
                        results.append((folder.name, folder, result))

                    if depth < max_depth:
                        recursion(folder, depth + 1)
            except PermissionError:
                pass

        recursion(search_path, 1)
        return results

    def search_folder(self, validator: Callable, search_path=""):
        """
        Search current folder using a validator function

        Args:
            validator: Function that validates each item and returns a value
            search_path: Directory to search in (default: current directory)

        Returns:
            List of tuples containing (item_name, item_path, validator_result)
            for each item where validator returns a truthy value
        """
        if not search_path:
            search_path = self.get_dir()

        search_path = Path(search_path)

        try:
            result = validator(search_path)
            if result:
                return (search_path.name, search_path, result)
        except PermissionError:
            pass

        return None

    def get_active_venv(self):
        """
        Detects if there is currently an active virtual environment.
        Returns (name, path) if an environment is active, None otherwise.
        """
        import sys
        import os

        # First check VIRTUAL_ENV environment variable
        virtual_env = os.environ.get("VIRTUAL_ENV")
        if not virtual_env:
            return None

        # If we have VIRTUAL_ENV, verify it with sys.prefix
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            venv_path = virtual_env
            venv_name = os.path.basename(venv_path)
            return venv_name, venv_path

        return None

    def extract_requirements(self, venv_path: str | Path) -> Tuple[bool, str]:
        """
        Extract requirements from a virtual environment using pip freeze.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Tuple of (success: bool, result: str) where result is either
            the path to requirements file or error message
        """
        import subprocess

        venv_path = Path(venv_path)
        pip_path = self._manager.get_pip_path(venv_path)

        requirements_filename = "requirements.txt"
        requirements_path = self.get_dir() / requirements_filename

        try:
            # Run pip freeze to get requirements
            result = subprocess.run(
                [str(pip_path), "freeze"], capture_output=True, text=True, check=True
            )

            # Write requirements to file
            requirements_path.write_text(result.stdout)
            return requirements_filename, self.get_dir(), (requirements_filename, True)
        except subprocess.CalledProcessError as e:
            return False, f"Failed to run pip freeze: {e.stderr}"
        except Exception as e:
            return False, f"Error extracting requirements: {str(e)}"

    def install_requirements(
        self, venv_path: str | Path, requirements_path: str | Path
    ) -> Tuple[bool, str]:
        """
        Install requirements into a virtual environment using pip.

        Args:
            venv_path: Path to the virtual environment
            requirements_path: Path to the requirements.txt file

        Returns:
            Tuple of (success: bool, result: str) where result is either
            success message or error message
        """
        venv_path = Path(venv_path)
        requirements_path = Path(requirements_path)
        pip_path = self._manager.get_pip_path(venv_path)

        if not requirements_path.exists():
            return False, f"Requirements file not found: {requirements_path}"

        try:
            # Run pip install with requirements file
            result = subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            return True, "Requirements installed successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to install requirements: {e.stderr}"
        except Exception as e:
            return False, f"Error installing requirements: {str(e)}"

    def install_package(self, package_name: str) -> Tuple[bool, str]:
        """Install a system package using the appropriate package manager"""
        return self._manager.install_package(package_name)

    def start_service(self, service_name: str) -> Tuple[bool, str]:
        return self._manager.start_service(service_name)

    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        return self._manager.stop_service(service_name)

    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        return self._manager.restart_service(service_name)

    def enable_service(self, service_name: str) -> Tuple[bool, str]:
        return self._manager.enable_service(service_name)

    def run_command(self, command: str | List[str]) -> Tuple[bool, str]:
        """Run a system command using the appropriate OS manager"""
        return self._manager.run_command(command)

    def get_username(self) -> str:
        return self._manager.get_username()

    def is_admin(self) -> bool:
        return self._manager.is_admin()

    def check_python_package_installed(
        self, venv_path: str | Path, package_name: str
    ) -> Tuple[bool, str]:
        """
        Check if a Python package is installed in the specified virtual environment.

        Args:
            venv_path: Path to the virtual environment
            package_name: Name of the package to check

        Returns:
            Tuple of (installed: bool, message: str)
        """
        venv_path = Path(venv_path)
        pip_path = self._manager.get_pip_path(venv_path)

        try:
            # Run pip list to check if the package is installed
            result = subprocess.run(
                [str(pip_path), "list"], capture_output=True, text=True, check=True
            )

            # Check if the package is in the output
            if (
                f"{package_name} " in result.stdout
                or f"\n{package_name} " in result.stdout
            ):
                return True, f"{package_name} is installed"
            else:
                return False, f"{package_name} is not installed"

        except subprocess.CalledProcessError as e:
            return False, f"Failed to check if {package_name} is installed: {e.stderr}"
        except Exception as e:
            return False, f"Error checking package installation: {str(e)}"

    def check_postgres_dependencies(
        self, venv_path: str | Path
    ) -> Tuple[bool, List[str]]:
        """
        Check if PostgreSQL dependencies are installed in the virtual environment.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Tuple of (all_installed: bool, missing_packages: List[str])
        """
        required_packages = ["psycopg2", "psycopg2-binary"]
        missing_packages = []

        for package in required_packages:
            is_installed, _ = self.check_python_package_installed(venv_path, package)
            if not is_installed:
                missing_packages.append(package)

        return len(missing_packages) == 0, missing_packages

    def ensure_postgres_dependencies(self, venv_path: str | Path) -> Tuple[bool, str]:
        """
        Ensure PostgreSQL dependencies are installed in the virtual environment.
        This will check if the packages are installed and install them if missing.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Tuple of (success: bool, message: str)
        """
        venv_path = Path(venv_path)
        pip_path = self._manager.get_pip_path(venv_path)

        # Check if dependencies are already installed
        all_installed, missing_packages = self.check_postgres_dependencies(venv_path)

        if all_installed:
            return True, "PostgreSQL dependencies are already installed"

        # Install missing packages
        for package in missing_packages:
            try:
                result = subprocess.run(
                    [str(pip_path), "install", package],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                return False, f"Failed to install {package}: {e.stderr}"
            except Exception as e:
                return False, f"Error installing {package}: {str(e)}"

        return True, "PostgreSQL dependencies were successfully installed"
