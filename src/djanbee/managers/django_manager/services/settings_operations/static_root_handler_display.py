from ....console_manager import ConsoleManager
from .....widgets.list_selector import ListSelector
from .....widgets.question_selector import QuestionSelector


class StaticRootHandlerDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def prompt_static_files_solution(self):

        selector = ListSelector(
            "Select static file handling solution:",
            ["Whitenoise", "Ngnix"],
            self.console_manager,
        )
        return selector.select()

    def prompt_install_whitenoise(self):
        selector = QuestionSelector(
            "Whitenoise not installed \n Do you wish to install it now:",
            self.console_manager,
        )
        return selector.select()

    def print_progress_whitenoise(self):
        self.console_manager.print_progress("Setting whitenoise in middleware")

    def success_progress_whitenoise(self):
        self.console_manager.print_step_progress(
            "Middleware", "Whitenoise added to middleware"
        )

    def print_progress_static_url(self):
        self.console_manager.print_progress("Setting static url")

    def success_progress_static_url(self):
        self.console_manager.print_step_progress(
            "STATIC_URL", "Static url set to /static/"
        )

    def print_progress_static_root(self):
        self.console_manager.print_progress("Setting static root")

    def success_progress_static_root(self):
        self.console_manager.print_step_progress(
            "STATIC_ROOT", "os.path.join(BASE_DIR, 'staticfiles')"
        )

    def print_progress_static_root_add_os(self):
        self.console_manager.print_progress("OS library missing, ading library")

    def print_progress_static_file_dirs_create(self):
        self.console_manager.print_progress("Creating STATICFILE_DIRS setting")

    def success_progress_static_file_dirs_add(self):
        self.console_manager.print_step_progress("STATICFILE_DIRS", "Whitenoise added")

    def progress_staticfiles_storage_add(self):
        self.console_manager.print_progress("Adding whitenoise to staticfile storage")

    def success_staticfiles_storage_add(self):
        self.console_manager.print_step_progress(
            "STATICFILES_STORAGE", "Whitenoise added"
        )
