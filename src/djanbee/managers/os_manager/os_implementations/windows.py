import subprocess
from pathlib import Path
from typing import List, Tuple

from ..base import BaseOSManager


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

    def check_service_status(self, service_name: str) -> bool:
        try:
            result = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            is_active = "RUNNING" in result.stdout
            return is_active
        except Exception:
            return False

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

    def is_venv_directory(self, path: Path) -> bool:
        """Check if a directory is a virtual environment on Windows systems"""
        cfg_exists = (path / "pyvenv.cfg").exists()
        scripts_exists = (path / "Scripts").exists()
        python_exists = (path / "Scripts" / "python.exe").exists()
        return cfg_exists and scripts_exists and python_exists
