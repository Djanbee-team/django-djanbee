from typing import Optional
from .display import LaunchDisplay
from ...core import AppContainer


class LaunchManager:
    """Manages Django project initialization and selection."""
    
    def __init__(self, display: LaunchDisplay, app: AppContainer) -> None:
        self.display = display
        self.app = app

    def launch_project(self, path: str = "") -> Optional[object]:
        """Initialize environment and select Django project.
        
        Args:
            path: Optional path to Django project directory
            
        Returns:
            Selected project object or None if no project found
        """
        # Show splash screen
        self.display.display_splash_screen()

        # Initialize working directory
        self.app.django_manager.project_service.initialize_directory(path)

        # Find and select Django project
        return self.app.django_manager.project_service.select_project()
