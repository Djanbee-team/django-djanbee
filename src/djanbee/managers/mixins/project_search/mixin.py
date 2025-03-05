from typing import Tuple, List, Optional
from pathlib import Path


class ProjectSearchMixin:
    """Mixin for project search manager functionality.
    Requires:
    - self.app with django_manager and os_manager
    - self.display with ProjectSearchDisplayMixin methods
    """

    def find_django_project(self) -> Optional[Tuple[str, Path, bool]]:
        project = self.app.django_manager.find_django_project_in_current_dir()
        if not project:
            project = self._handle_project_search()
            if not project:
                return None
        return project

    def _handle_project_search(self) -> Optional[Tuple[str, Path, bool]]:
        projects = self.app.django_manager.find_django_projects_in_tree()
        if not projects:
            self.display.show_no_projects_found()
            return None

        project = self._select_and_set_project(projects)
        return project

    def _select_and_set_project(
        self, projects: List[Tuple[str, Path]]
    ) -> Optional[Tuple[str, Path, bool]]:
        self.display.show_project_not_found()
        selected_project = self.display.prompt_project_selection(projects)
        if not selected_project:
            return None

        project_name, project_path = selected_project
        self.app.os_manager.set_dir(project_path)
        return project_name, project_path, True
