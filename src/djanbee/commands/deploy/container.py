from dataclasses import dataclass
from .display import DeployDisplay
from .manager import DeployManager
from ...core import AppContainer


@dataclass
class DeployContainer:

    display: DeployDisplay
    manager: DeployManager

    @classmethod
    def create(cls, app: "AppContainer") -> "DeployContainer":
        display = DeployDisplay(console_manager=app.console_manager)
        manager = DeployManager(display, app)
        return cls(display=display, manager=manager)

    def verify_packages(self):
        if not self.manager.verify_venv():
            return
        self.manager.verify_packages()

    def set_up_socket_file(self):
        if not self.manager.verify_django_project():
            return
        self.manager.find_and_create_socket_file()
