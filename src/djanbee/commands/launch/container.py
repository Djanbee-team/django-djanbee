from dataclasses import dataclass
from .display import LaunchDisplay
from .manager import LaunchManager
from ...core import AppContainer


@dataclass
class LaunchContainer:

    display: LaunchDisplay
    manager: LaunchManager

    @classmethod
    def create(cls, app: "AppContainer") -> "LaunchContainer":
        display = LaunchDisplay(console_manager=app.console_manager)
        manager = LaunchManager(display, app)
        return cls(display=display, manager=manager)
