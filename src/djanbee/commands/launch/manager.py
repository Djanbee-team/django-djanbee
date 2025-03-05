from .display import LaunchDisplayInterface
from ...core import AppContainer
from ...managers.mixins.project_search import ProjectSearchMixin


class LaunchManager(ProjectSearchMixin):
    def __init__(self, display: LaunchDisplayInterface, app: "AppContainer"):
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
        self._initialize_directory(path)

        # Find and launch Django project
        project = self.find_django_project()
        if project:
            self.display.show_project_opened(project[0], project[1])

    def _initialize_directory(self, path: str) -> None:
        """Set up the working directory"""
        if not path:
            self.app.os_manager.get_dir()
        else:
            self.app.os_manager.set_dir(path)
