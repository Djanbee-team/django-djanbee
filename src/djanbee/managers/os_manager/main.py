import os
import platform
import subprocess
from pathlib import Path
from typing import Callable, List, Tuple
from collections import namedtuple

from .os_implementations import UnixOSManager, WindowsOSManager

Result = namedtuple("Result", ["valid", "object"])


class OSManager:
    def __init__(self):
        """Initializes platform-specific OS manager"""
        system = platform.system().lower()
        if system == "windows":
            self._manager = WindowsOSManager()
        else:
            self._manager = UnixOSManager()

    def set_dir(self, dir: str | Path = "."):
        """Sets OS directory"""
        try:
            dir_path = Path(dir)

            if not dir_path.exists():
                raise FileNotFoundError(f"Directory does not exist: {dir_path}")
            if not dir_path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {dir_path}")

            # Changes directory
            os.chdir(dir_path)

        except Exception as e:
            raise Exception(f"Failed to set directory: {str(e)}")

    def get_dir(self) -> Path:
        """Returns current working directory"""
        return self._manager.get_dir()

    def get_pip_path(self, venv_path: Path) -> Path:
        """Gets platform-specific pip executable path"""
        return self._manager.get_pip_path(venv_path)

    def check_package_installed(self, package_name: str) -> bool:
        """Checks if a system package is installed"""
        return self._manager.check_package_installed(package_name)

    def check_service_status(self, service_name: str) -> bool:
        """Checks if a system service is running"""
        return self._manager.check_service_status(service_name)

    def install_package(self, package_name: str) -> Tuple[bool, str]:
        """Installs a system package using appropriate package manager"""
        return self._manager.install_package(package_name)

    def start_service(self, service_name: str) -> Tuple[bool, str]:
        """Starts a system service"""
        return self._manager.start_service(service_name)

    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        """Stops a system service"""
        return self._manager.stop_service(service_name)

    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        """Restarts a system service"""
        return self._manager.restart_service(service_name)

    def enable_service(self, service_name: str) -> Tuple[bool, str]:
        """Enables a service to start on boot"""
        return self._manager.enable_service(service_name)

    def run_command(self, command: str | List[str]) -> Tuple[bool, str]:
        """Runs a system command"""
        return self._manager.run_command(command)

    def get_username(self) -> str:
        """Gets current user's username"""
        return self._manager.get_username()

    def is_admin(self) -> bool:
        """Checks if current user has admin privileges"""
        return self._manager.is_admin()

    def get_path_basename(self, path: str | Path) -> str:
        """Get the basename (final component) of a path"""
        path_obj = Path(path) if not isinstance(path, Path) else path
        return path_obj.name

    def search_subfolders(
        self, validator: Callable, max_depth: int = 1, search_path=""
    ):
        """Searches subfolders using a validator function"""
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
                        results.append(Result(valid=result, object=folder))

                    if depth < max_depth:
                        recursion(folder, depth + 1)
            except PermissionError:
                pass

        recursion(search_path, 1)
        return results

    def search_folder(self, validator: Callable, search_path=""):
        """Searches current folder using a validator function"""
        # If not path given searches current folder
        if not search_path:
            search_path = self.get_dir()

        search_path = Path(search_path)  # convert to path

        try:
            result = validator(search_path)
            if result:
                return Result(
                    valid=result,
                    object=search_path,
                )
        except PermissionError:
            pass

        return None

    def get_environment_variable(self, var_name: str) -> str:
        """Get an environment variable value"""
        return os.environ.get(var_name)

    def run_pip_command(self, venv_path: Path, pip_args: List[str]) -> Tuple[bool, str]:
        """Run a pip command in a virtual environment"""
        pip_path = self._manager.get_pip_path(venv_path)

        try:
            result = subprocess.run(
                [str(pip_path)] + pip_args, capture_output=True, text=True, check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Failed to run pip command: {e.stderr}"
        except Exception as e:
            return False, f"Error running pip command: {str(e)}"

    def check_file_exists(self, path: Path) -> bool:
        """Check if a file exists"""
        return path.exists() and path.is_file()

    def write_text_file(self, path: Path, content: str) -> Tuple[bool, str]:
        """Write text content to a file"""
        try:
            path.write_text(content)
            return True, "File written successfully"
        except Exception as e:
            return False, f"Error writing file: {str(e)}"

    def check_python_package_installed(
        self, venv_path: str | Path, package_name: str
    ) -> Tuple[bool, str]:
        """Checks if a Python package is installed in virtual environment"""
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
        """Checks for PostgreSQL dependencies in virtual environment"""
        required_packages = ["psycopg2", "psycopg2-binary"]
        missing_packages = []

        for package in required_packages:
            is_installed, _ = self.check_python_package_installed(venv_path, package)
            if not is_installed:
                missing_packages.append(package)

        return len(missing_packages) == 0, missing_packages

    def ensure_postgres_dependencies(self, venv_path: str | Path) -> Tuple[bool, str]:
        """Ensures PostgreSQL dependencies are installed in virtual environment"""
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

    def is_venv_directory(self, path: Path) -> bool:
        self._manager.is_venv_directory(path)
