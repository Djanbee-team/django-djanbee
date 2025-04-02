from rich.panel import Panel
from rich.text import Text
from rich import box
from ...managers import ConsoleManager


class LaunchDisplay:
    """Handles display output for the launch command."""
    
    def __init__(self, console_manager: ConsoleManager) -> None:
        self.console_manager = console_manager

    def display_splash_screen(self) -> None:
        """Display welcome splash screen with service info."""
        # Display bee logo
        self.console_manager.print_logo()
        
        # Display warning about privileges
        warning = Text(
            "The setup might require root privileges",
            style="yellow",
            justify="center",
        )
        
        self.console_manager.console.print(Panel(warning, box=box.SIMPLE, style="blue"))
