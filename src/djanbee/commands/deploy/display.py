from ...managers import ConsoleManager
from ...widgets.question_selector import QuestionSelector


class DeployDisplay:
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def report_dependency_check(self, dependency_results):
        """Display initial dependency check results"""
        for dep_name, is_installed, message in dependency_results:
            if is_installed:
                self.console_manager.print_step_progress(
                    dep_name.capitalize(), f"{dep_name.capitalize()} found"
                )
            else:
                self.console_manager.print_step_failure(
                    dep_name.capitalize(), f"{dep_name.capitalize()} not found"
                )

    def report_dependency_installation(self, installation_results):
        """Display dependency installation results"""
        for dep_name, success, message in installation_results:
            if success:
                self.console_manager.print_step_progress(
                    dep_name.capitalize(),
                    f"{dep_name.capitalize()} installed successfully",
                )
            else:
                self.console_manager.print_step_failure(
                    dep_name.capitalize(), f"Failed: {message}"
                )

    def progress_install_dep(self, dep_name):
        self.console_manager.print_progress(f"Installing {dep_name.capitalize()}...")

    def success_verify_dep(self):
        self.console_manager.print_success("Server dependencies verified successfully!")

    def failure_verify_venv(self):
        self.console_manager.print_warning_critical("No venv found")

    def prompt_override_socket(self, service_path, service_name):
        selector = QuestionSelector(
            "Do you wish to override socketfile",
            self.console_manager,
            "yes",
            "no",
            f"This action will replace the current {service_name}",
        )
        return selector.select()

    def success_create_socketservice(self, path):
        self.console_manager.print_success(f"Socket service created at {path}")
<<<<<<< HEAD
=======

    def success_create_serverconfig(self, path):
        self.console_manager.print_success(f"Server config created at {path}")

    def prompt_override_server(self, config_path, config_name):
        selector = QuestionSelector(
            "Do you wish to override server configfile",
            self.console_manager,
            "yes",
            "no",
            f"This action will replace the current {config_name}",
        )
        return selector.select()
>>>>>>> ddfd42f (deploy command/recovered repo)
