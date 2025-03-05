from typing import Tuple, List
from pathlib import Path
from ....widgets.list_selector import ListSelector


class ProjectSearchDisplayMixin:
    """Mixin for project search display functionality.
    Requires:
    - self.console_manager
    """

    def show_project_not_found(self) -> None:
        self.console_manager.print_warning_critical(
            "Django project not found in this folder"
        )

    def show_project_opened(self, project) -> None:
        self.console_manager.print_success(
            f"Setting Django project as {project[0]} in {project[1]}"
        )

    def show_no_projects_found(self) -> None:
        self.console_manager.print_warning_critical("No Django projects found")

    def prompt_project_selection(
        self, projects: List[Tuple[str, Path]]
    ) -> Tuple[str, Path] | None:
        if not projects:
            return None

        choices = [(p[0], p[1]) for p in projects]
        self.console_manager.console.print("\nDid you mean one of these projects?")
        selector = ListSelector("Select Django Project", choices, self.console_manager)
        return selector.select()
