from pathlib import Path
import venv
import os
from ...core import AppContainer
from .display import SetupDisplay

class SetupManager:
    def __init__(self, display: 'SetupDisplay', app: 'AppContainer'):
        self.display = display
        self.app = app
        self.os_manager = app.os_manager
        self.console_manager = app.console_manager

    def setup_project(self):
        """Main setup flow for the project"""
        # Handle virtual environment setup
        env = self._setup_virtual_environment()
        if not env:
            return
        
        # Handle requirements setup
        self._setup_requirements(env)
        
    def _setup_virtual_environment(self):
        """Handle virtual environment setup flow"""
        self.console_manager.print_lookup("Searching for virtual environment")
        
        active_venv = self.os_manager.get_active_venv()
        envs = [(*active_venv, True)] if active_venv else [None]

        if not envs[0]:
            self.console_manager.print_warning_critical("No active virtual environment")
            envs = self.os_manager.search_subfolders(self.is_venv)
            
            if not envs:
                self.console_manager.print_warning_critical("No virtual environments found")
                if self.display.prompt_create_environment():    
                    envs = [self.create_environment()]
                else:
                    print("setup cancelled")
                    return None
        else:
            self.console_manager.print_success("Virtual environment active")
        print(envs)
        env_name, env_path, _ = envs[0]
        self.console_manager.print_lookup(f"Found virtual environment: {env_name}")
        return env_path

    def _setup_requirements(self, env_path):
        """Handle requirements setup flow"""
        self.console_manager.print_lookup("Looking for requirements")
        requirements = self.os_manager.search_folder(self.has_requirements)

        if not requirements:
            requirements = self.os_manager.search_subfolders(self.has_requirements)
            
            if not requirements:
                self.console_manager.print_warning_critical("No requirements found")
                if self.display.prompt_extract_requirements():    
                    requirements = self.os_manager.extract_requirements(env_path)
                else:
                    print("setup cancelled")
                    return
        
        self.console_manager.print_success(f"{requirements[2][0]} file found")
        if self.display.prompt_install_requirements():
            self.console_manager.print_progress("Installing requirements")
            self.os_manager.install_requirements(env_path, requirements[1] / requirements[2][0])
        else:
            print("setup cancelled")


    def is_venv(self, path = "."):
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

    def has_requirements(self, path = "."):
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
                return req_file, True

        return False

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
            
            self.console_manager.print_success(f"Virtual environment created at {venv_path}")
            return (venv_path.name, venv_path, True)
            
        except Exception as e:
            self.console_manager.print_error(f"Failed to create virtual environment: {str(e)}")
            return False

