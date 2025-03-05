from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box
from getpass import getpass

class ConsoleManager:
    def __init__(self):
        self.console = Console()

    def print_package(self, message):
        text = Text()
        text.append("📦 ", style="")  # Database emoji
        text.append(message, style="bright_blue")
        self.console.print(text, end="")


    def print_warning_critical(self, text: str):
        error_msg = Text(text, style="bold red")
        self.console.print(Panel(error_msg, box=box.DOUBLE))

    def print_success(self, text: str):
        success_msg = Text(text, style="bold green")
        self.console.print(Panel(success_msg, box=box.DOUBLE))

    def print_error(self, e: str):
        self.console.print(f"[red]Error: {str(e)}[/]")

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

    def print_input(self, message: str):
        """Print progress message in blue with hammer emoji"""
        text = Text()
        text.append("📝 ", style="")  # Hammer emoji
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

    def print_step_progress(self, step_name: str, message: str)->None:
        text = Text()
        text.append("✅ ", style="") 
        text.append(f"{step_name}: {message}", style="green")
        self.console.print(text)


    def print_step_failure(self, step_name: str, message: str)->None:
        text = Text()
        text.append("❌ ", style="") 
        text.append(f"{step_name}: {message}", style="red")
        self.console.print(text)

    
    def input_profile(self) -> str:
        """Get profile input from user with styled prompt"""
        text = Text()
        text.append("👤 ", style="")
        text.append("Enter your profile name: ", style="bright_blue")
        self.console.print(text, end="")  # Using end="" to keep cursor on same line
        
        try:
            profile = input()
            if profile.strip():
                return profile
            else:
                self.print_step_failure("Profile", "Profile name cannot be empty")
                return self.input_profile()
        except Exception as e:
            self.print_error(str(e))
            return self.input_profile()

    def input_password(self, message="Enter your password: ") -> str:
        """Get password input from user with styled prompt"""
        text = Text()
        text.append("🔐 ", style="")
        text.append(message, style="bright_blue")
        self.console.print(text, end="")  # Using end="" to keep cursor on same line
        
        try:
            password = getpass(prompt="")  # Empty prompt since we already printed our styled one
            if password.strip():
                return password
            else:
                self.print_step_failure("Password", "Password cannot be empty")
                return self.input_password()
        except Exception as e:
            self.print_error(str(e))
            return self.input_password()





