from .display import DeployDisplay
from ...core import AppContainer


class DeployManager:
    def __init__(self, display: DeployDisplay, app: "AppContainer"):
        self.display = display
        self.app = app

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
