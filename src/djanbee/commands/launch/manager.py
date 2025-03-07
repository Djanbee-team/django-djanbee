from .display import LaunchDisplay
from ...core import AppContainer


class LaunchManager:
    def __init__(self, display: LaunchDisplay, app: "AppContainer"):
        self.display = display
        self.app = app

    def launch_project(self, path: str = "") -> None:
        """
        Main method to handle Django project launch logic

        Args:
            path (str): Optional path to Django project
        """
        self.display.display_splash_screen()

        # Initialize directory
        self.app.django_manager.project_service.initialize_directory(path)

        # Find and launch Django project
        project = self.app.django_manager.project_service.select_project()
