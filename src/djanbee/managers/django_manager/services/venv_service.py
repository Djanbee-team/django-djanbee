from pathlib import Path
from ....managers.os_manager import OSManager
from ..state import DjangoManagerState
import sys
from collections import namedtuple
import venv

Result = namedtuple("Result", ["valid", "object"])


class DjangoEnvironmentService:
    """Service for managing virtual environment"""

    def __init__(self, os_manager: OSManager):
        self.os_manager = os_manager
        self.state = DjangoManagerState.get_instance()

    def get_active_venv(self):
        """Detects active virtual environment"""

        # First check VIRTUAL_ENV environment variable
        virtual_env = self.os_manager.get_environment_variable("VIRTUAL_ENV")
        if not virtual_env:
            return None

        # If we have VIRTUAL_ENV, verify it with sys.prefix
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            venv_name = self.os_manager.get_path_basename(virtual_env)
            return Result(
                True, {"virtual_env": virtual_env, "virtual_env_name": venv_name}
            )

        return None

    def is_venv(self, path="."):
        """Check if path is a virtual environment"""
        print("HERE")
        path = Path(path) if not isinstance(path, Path) else path
        return self.os_manager.is_venv_directory(path)

    def find_envs(self):
        envs = self.os_manager.search_folder(self.is_venv)
        return envs

    def create_environment(self, path: str = ".venv") -> bool:
        """
        Create a new virtual environment

        Args:
            path: Path where to create the environment (default: .venv)
        Returns:
            bool: True if environment was created successfully
        """
        try:
            self.console_manager.print_progress("Creating virtual environment...")
            venv_path = Path(path)

            # Create the virtual environment
            venv.create(venv_path, with_pip=True)

            self.console_manager.print_success(
                f"Virtual environment created at {venv_path}"
            )
            return (venv_path.name, venv_path, True)

        except Exception as e:
            self.console_manager.print_error(
                f"Failed to create virtual environment: {str(e)}"
            )
            return False
