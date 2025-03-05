from pathlib import Path
import platform
from abc import ABC, abstractmethod
from typing import Callable, TypeVar, List, Tuple
import os
import sys

class BaseOSManager(ABC):
    @abstractmethod
    def get_dir(self) -> Path:
        pass

class UnixOSManager(BaseOSManager):
    def get_dir(self) -> Path:
        return Path.cwd().resolve()

class WindowsOSManager(BaseOSManager):
    def get_dir(self) -> Path:
        return Path.cwd().resolve()

class OSManager:
    def __init__(self):
        system = platform.system().lower()
        if system == 'windows':
            self._manager = WindowsOSManager()
        else:
            self._manager = UnixOSManager()

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
    
    def search_subfolders(self, validator: Callable, max_depth: int = 1, search_path = ""):
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
                    if path.name.startswith('.'):
                        return
                    result = validator(folder)
                    if result:
                            results.append((folder.name, folder, result))

                    if depth< max_depth:
                        recursion(folder, depth+1)
            except PermissionError:
                pass
        
        recursion(search_path, 1)
        return results
    
    def search_folder(self, validator: Callable, search_path = ""):
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
        virtual_env = os.environ.get('VIRTUAL_ENV')
        if not virtual_env:
            return None
            
        # If we have VIRTUAL_ENV, verify it with sys.prefix
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            venv_path = virtual_env
            venv_name = os.path.basename(venv_path)
            return venv_name, venv_path
        
        return None



