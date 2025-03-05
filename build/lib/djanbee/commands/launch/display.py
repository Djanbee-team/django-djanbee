from rich.panel import Panel
from rich.text import Text
from rich import box
from ...utils.console import console_manager


def display_splash_screen():
    title = Text("Djanbee deployment service", style="bold white", justify="center")
    warning = Text("\nThe setup might require root privileges", style="yellow", justify="center")
    content = Text.assemble(title, warning)

    console_manager.console.print(Panel(content, box=box.DOUBLE, style="blue"))
