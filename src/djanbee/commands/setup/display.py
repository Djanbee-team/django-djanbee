from ...widgets.question_selector import QuestionSelector
from ...managers import ConsoleManager


class SetupDisplay:
    def __init__(self, console_manager: 'ConsoleManager'):
        self.console_manager = console_manager

    def prompt_create_environment(self):
        selector = QuestionSelector("Do you wish to create a virtual environment", self.console_manager)
        return selector.select()

    def prompt_extract_requirements(self):
        selector = QuestionSelector("Do you wish to extract requirements", self.console_manager)
        return selector.select()

    def prompt_install_requirements(self):
        selector = QuestionSelector("Do you wish to install requirements", self.console_manager)
        return selector.select()

