from .display import DeployDisplay
from ...core import AppContainer


class DeployManager:
    def __init__(self, display: DeployDisplay, app: "AppContainer"):
        self.display = display
        self.app = app

    def verify_venv(self):
        if not self.app.django_manager.environment_service.state.active_venv_path:
            if not self.app.django_manager.environment_service.get_active_venv():
                self.display.failure_verify_venv()
                return False
        return True

    def verify_packages(self):
        is_installed, response = self.app.server_manager.install_server()
        if is_installed:
            self.app.console_manager.print_step_progress(
                "Nginx", "Nginx installation found"
            )

        dependency_results = self.app.server_manager.verify_dependencies()

        # Check dependencies
        dependency_results = self.app.server_manager.verify_dependencies()
        self.display.report_dependency_check(dependency_results)

        # Install missing dependencies
        installation_results = []
        for dep_name, is_installed, message in dependency_results:
            if not is_installed:
                self.display.progress_install_dep(dep_name)
                success, install_msg = self.app.server_manager.install_dependency(
                    dep_name
                )
                installation_results.append((dep_name, success, install_msg))

        # Report installation results
        if installation_results:
            self.display.report_dependency_installation(installation_results)

        self.display.success_verify_dep()

    def verify_django_project(self):
        if not self.app.django_manager.project_service.state.current_project_path:
            if not self.app.django_manager.project_service.select_project():
                return False
        return True

    def find_and_create_socket_file(self):
        project_path = (
            self.app.django_manager.project_service.state.current_project_path
        )
        project_name = project_path.name

        socket_exists, service_path = (
            self.app.socket_manager.check_socket_service_exists(project_name)
        )

        if not socket_exists:

            result, path = self.app.socket_manager.create_socket_service(
                project_path, project_name, use_sudo=True
            )
            if result:
                self.display.success_create_socketservice(path)

        else:
            if self.display.prompt_override_socket(service_path, service_path.name):
                result, path = self.app.socket_manager.create_socket_service(
                    project_path, project_name, use_sudo=True
                )
                if result:
                    self.display.success_create_socketservice(path)
