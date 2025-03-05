from rich.panel import Panel
from rich.text import Text
from rich import box
from ...managers import ConsoleManager
from typing import Protocol, Tuple, List
from ...managers.mixins.project_search import ProjectSearchDisplayMixin


class LaunchDisplayInterface(Protocol):
    def display_splash_screen(self) -> None: ...
    def prompt_project_selection(
        self, projects: List[Tuple[str, str]]
    ) -> Tuple[str, str]: ...
    def show_no_projects_found(self) -> None: ...
    def show_project_not_found(self) -> None: ...
    def show_project_opened(self, name: str, path: str) -> None: ...


class LaunchDisplay(ProjectSearchDisplayMixin):
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def display_splash_screen(self):
        title = Text("Djanbee deployment service", style="bold white", justify="center")
        warning = Text(
            "\nThe setup might require root privileges",
            style="yellow",
            justify="center",
        )
        content = Text.assemble(title, warning)

        self.console_manager.console.print(Panel(content, box=box.DOUBLE, style="blue"))

    def show_project_opened(self, name: str, path: str) -> None:
        self.console_manager.print_success(f"Opening {name} in {path}")
