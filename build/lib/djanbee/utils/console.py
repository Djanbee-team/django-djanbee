from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box

class ConsoleManager:
    def __init__(self, console: Console):
        self.console = console

    def print_warning_critical(self, text: str):
        error_msg = Text(text, style="bold red")
        self.console.print(Panel(error_msg, box=box.DOUBLE))

    def print_success(self, text: str):
        success_msg = Text(text, style="bold green")
        self.console.print(Panel(success_msg, box=box.DOUBLE))

    def print_error(self, e: str):
        console_manager.console.print(f"[red]Error: {str(e)}[/]")

    def print_lookup(self, message: str):
        """Print progress message in blue with hammer emoji"""
        text = Text()
        text.append("🔍 ", style="")  # Hammer emoji
        text.append(message, style="blue")
        
        self.console.print(text)

    def print_progress(self, message: str):
        """Print progress message in blue with hammer emoji"""
        text = Text()
        text.append("🔨 ", style="")  # Hammer emoji
        text.append(message, style="blue")
        
        self.console.print(text)

    def print_question(self, message: str):
        """Print question message in blue with question mark emoji and border"""
        text = Text()
        text.append("❓ ", style="")  # Question mark emoji
        text.append(message, style="blue")
        
        panel = Panel(
            text,
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        



# Create single instance at app startup
console = Console()
console_manager = ConsoleManager(console)
