from pathlib import Path
from ....managers.os_manager import OSManager
from ..state import DjangoManagerState
from collections import namedtuple
from typing import Tuple

Result = namedtuple("Result", ["valid", "object"])


class DjangoRequirementsService:
    """Service for managing virtual environment"""

    def __init__(self, os_manager: OSManager):
        self.os_manager = os_manager
        self.state = DjangoManagerState.get_instance()

    def find_requirements(self):
        requirements = self.os_manager.search_folder(self.has_requirements)
        if not requirements:
            requirements = self.os_manager.search_subfolders(self.has_requirements)

        if requirements:
            return Result(True, requirements.object / "requirements.txt")
        return None

    def has_requirements(self, path="."):
        """
        Check if directory has requirements file by verifying:
        1. requirements.txt exists
        Or alternative requirement files like:
        2. requirements-dev.txt
        3. requirements-prod.txt
        """
        # Common requirements file patterns
        requirement_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-prod.txt",
        ]

        # Check for any of the requirements files
        for req_file in requirement_files:
            if (path / req_file).exists():
                return True

        return False

    def extract_requirements(self, venv_path: str | Path) -> Tuple[bool, str]:
        """Extracts pip requirements from a virtual environment"""
        venv_path = Path(venv_path)

        requirements_filename = "requirements.txt"
        requirements_path = self.os_manager.get_dir() / requirements_filename

        # Run pip freeze using OS manager
        success, output = self.os_manager.run_pip_command(venv_path, ["freeze"])
        if not success:
            return False, output

        # Write requirements file using OS manager
        write_success, message = self.os_manager.write_text_file(
            requirements_path, output
        )
        if not write_success:
            return False, message

        return Result(True, requirements_path)

    def install_requirements(
        self, venv_path: str | Path, requirements_path: str | Path
    ) -> Tuple[bool, str]:
        """Installs pip requirements into a virtual environment"""

        venv_path = Path(venv_path)

        requirements_path = Path(requirements_path)

        # Check if requirements file exists
        if not self.os_manager.check_file_exists(requirements_path):
            return False, f"Requirements file not found: {requirements_path}"
        # Run pip install with requirements file
        success, output = self.os_manager.run_pip_command(
            venv_path, ["install", "-r", str(requirements_path)]
        )

        if success:
            return True, "Requirements installed successfully"
        else:
            return False, output
