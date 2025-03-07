from pathlib import Path
from ...core import AppContainer
from .display import SetupDisplay


class SetupManager:
    def __init__(self, display: "SetupDisplay", app: "AppContainer"):
        self.display = display
        self.app = app

    def setup_project(self):
        """Main setup flow for the project"""
        # Handle virtual environment setup
        env = self._handle_virtual_environment()
        self.app.django_manager.environment_service.state.active_venv_path = env[
            "virtual_env"
        ]

        if not env:
            return

        # Handle requirements setup
        self._handle_requirements(env)

    def _handle_virtual_environment(self):
        """Handle virtual environment setup flow"""
        self.display.lookup_venv()

        active_venv = self.app.django_manager.environment_service.get_active_venv()

        if not active_venv:
            self.display.failure_lookup_venv("No active virtual environment")
            envs = self.app.django_manager.environment_service.find_envs()

            if not envs:
                self.display.failure_lookup_venvs()
                if self.display.prompt_create_environment():
                    envs = [self.create_environment()]
                else:
                    print("setup cancelled")
                    return None

        self.display.success_lookup_venv()
        is_active, venv = active_venv
        self.display.success_locate_env(venv["virtual_env_name"], venv["virtual_env"])
        return venv

    def _handle_requirements(self, env_path):
        """Handle requirements setup flow"""
        self.display.lookup_requirements()
        requirements = self.app.django_manager.requirements_service.find_requirements()

        if not requirements:
            self.display.failure_lookup_requirements()
            if self.display.prompt_extract_requirements():
                # This should verify whether a venv path exists
                # will throw error if run without previously setting up venv
                env_path = {
                    "virtual_env": self.app.django_manager.requirements_service.state.active_venv_path
                }
                requirements = (
                    self.app.django_manager.requirements_service.extract_requirements(
                        env_path["virtual_env"]
                    )
                )

            else:
                print("setup cancelled")
                return

        self.display.success_lookup_requirements(requirements.object)
        if self.display.prompt_install_requirements():
            self.display.progress_install_requirements()

            self.app.django_manager.requirements_service.install_requirements(
                env_path["virtual_env"], requirements.object
            )
            self.display.success_install_requirements(
                requirements.object, env_path["virtual_env"]
            )

        else:
            print("setup cancelled")
