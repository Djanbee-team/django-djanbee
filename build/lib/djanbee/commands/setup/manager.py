from ...managers import os_manager
from ...utils.console import console_manager
from pathlib import Path
import venv
import os

def is_venv(path = "."):
    """
    Check if current directory is a virtual environment by verifying:
    1. pyvenv.cfg exists
    2. bin/Scripts directory exists
    3. python executable exists in bin/Scripts
    """
    print("SEARCHING IN", path)

    cfg_exists = (path / "pyvenv.cfg").exists()

    bin_dir = "Scripts" if os.name == "nt" else "bin"
    bin_exists = (path / bin_dir).exists()

    python_exec = "python.exe" if os.name == "nt" else "python"
    python_exists = (path / bin_dir / python_exec).exists()

    return cfg_exists and bin_exists and python_exists

def has_requirements(path = "."):
    """
    Check if directory has requirements file by verifying:
    1. requirements.txt exists
    Or alternative requirement files like:
    2. requirements-dev.txt
    3. requirements-prod.txt
    """
    print("CHECKING REQUIREMENTS IN", path)

    # Common requirements file patterns
    requirement_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-prod.txt"
    ]

    # Check for any of the requirements files
    for req_file in requirement_files:
        if (path / req_file).exists():
            print(f"Found {req_file}")
            return True

    return False

def create_environment(path: str = ".venv") -> bool:
    """
    Create a new virtual environment
    
    Args:
        path: Path where to create the environment (default: .venv)
    Returns:
        bool: True if environment was created successfully
    """
    try:
        console_manager.print_progress("Creating virtual environment...")
        venv_path = Path(path)
        
        # Create the virtual environment
        venv.create(venv_path, with_pip=True)
        
        console_manager.print_success(f"Virtual environment created at {venv_path}")
        return (venv_path.name, venv_path, True)
        
    except Exception as e:
        console_manager.print_error(f"Failed to create virtual environment: {str(e)}")
        return False

