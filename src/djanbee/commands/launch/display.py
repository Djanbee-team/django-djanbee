from rich.panel import Panel
from rich.text import Text
from rich import box
from ...managers import ConsoleManager


class LaunchDisplay:
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def display_splash_screen(self):
        title = Text("Djanbee deployment service", style="bold white", justify="center")
        warning = Text(
            "\nThe setup might require root privileges",
            style="yellow",
            justify="center",
        )
        content = Text.assemble(title, warning)

        self.console_manager.console.print(Panel(content, box=box.DOUBLE, style="blue"))
