from pathlib import Path
from ...core import AppContainer
from .display import RunDisplay


class RunManager:
    def __init__(self, display: "RunDisplay", app: "AppContainer"):
        self.display = display
        self.app = app
    
    def initialize_project(self, path=""):
        # Initialize working directory
        self.app.django_manager.project_service.initialize_directory(path)
    
    def migrate_database(self):
        self.app.os_manager.run_python_command(["manage.py", "makemigrations"])
        self.app.os_manager.run_python_command(["manage.py", "migrate"])

    def collect_static_files(self):
        self.app.os_manager.run_python_command(["manage.py", "collectstatic"])
