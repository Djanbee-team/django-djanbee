from ...widgets.question_selector import QuestionSelector
from ...managers import ConsoleManager


class SetupDisplay:
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def prompt_create_environment(self):
        selector = QuestionSelector(
            "Do you wish to create a virtual environment", self.console_manager
        )
        return selector.select()

    def prompt_extract_requirements(self):
        selector = QuestionSelector(
            "Do you wish to extract requirements", self.console_manager
        )
        return selector.select()

    def prompt_install_requirements(self):
        selector = QuestionSelector(
            "Do you wish to install requirements", self.console_manager
        )
        return selector.select()

    def lookup_venv(self):
        self.console_manager.print_lookup("Searching for virtual environment")

    def failure_lookup_venv(self):
        self.console_manager.print_warning_critical("No active virtual environment")

    def failure_lookup_venvs(self):
        self.console_manager.print_warning_critical("No virtual environments found")

    def success_lookup_venv(self):
        self.console_manager.print_success("Virtual environment active")

    def success_locate_env(self, env_name, env_path):
        self.console_manager.print_step_progress(
            f"Found virtual environment {env_name}", env_path
        )

    def lookup_requirements(self):
        self.console_manager.print_lookup("Looking for requirements")

    def failure_lookup_requirements(self):
        self.console_manager.print_error("No requirements file found")

    def success_lookup_requirements(self, path):
        self.console_manager.print_step_progress("Found requirements.txt", path)

    def progress_install_requirements(self):
        self.console_manager.print_progress("Installing requirements")

    def success_install_requirements(self, requirements, env):
        self.console_manager.print_success(
            f"Requirements {requirements} installed ito {env}"
        )
