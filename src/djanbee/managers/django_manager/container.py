from ..os_manager import OSManager
from ..console_manager import ConsoleManager
from .services.venv_service import DjangoEnvironmentService
from .services.project_service import DjangoProjectService
from .services.project_service_display import DjangoProjectServiceDisplay
from .services.requirements_service import DjangoRequirementsService


class DjangoManager:
    """Container for Django-related services with lazy loading"""

    def __init__(self, os_manager: OSManager, console_manager: ConsoleManager):
        """Initialize the Django manager with dependencies but not services"""
        self.os_manager = os_manager
        self.console_manager = console_manager

        # Initialize service placeholders
        self._project_service = None
        self._environment_service = None
        self._requirements_service = None

        # Cache values
        self._current_project_path = None

    @property
    def project_service(self):
        """Lazy load the project service when first accessed"""
        if self._project_service is None:
            self._project_service = DjangoProjectService(
                self.os_manager, DjangoProjectServiceDisplay(self.console_manager)
            )
        return self._project_service

    @property
    def environment_service(self):
        """Lazy load the project service when first accessed"""
        if self._environment_service is None:
            self._environment_service = DjangoEnvironmentService(self.os_manager)
        return self._environment_service

    @property
    def requirements_service(self):
        """Lazy load the project service when first accessed"""
        if self._requirements_service is None:
            self._requirements_service = DjangoRequirementsService(self.os_manager)
        return self._requirements_service
