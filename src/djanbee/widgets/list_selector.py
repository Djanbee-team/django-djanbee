from typing import Optional, List
from rich.panel import Panel
from rich.text import Text
from ..managers import ConsoleManager


class ListSelector:
    def __init__(
        self, message: str, options: List[str], console_manager: ConsoleManager
    ):
        self.selected_index = 0
        self.console_manager = console_manager
        self.message = message
        self.options = options

    def prepare_message(self):
        """Print question message in blue with list emoji and border"""
        text = Text()
        text.append("📋 ", style="")  # List emoji
        text.append(self.message, style="blue")
        text.append("\n")
        return text

    def _render_options(self):
        """Render the list selection options."""
        content = Text()

        for idx, option in enumerate(self.options):
            if idx > 0:
                content.append("\n")

            if idx == self.selected_index:
                content.append(f"→ {option} ←", style="reverse")
            else:
                content.append(f"  {option}  ", style="")

        instructions = Text(
            "Use ↑↓ to navigate, Enter to select, number keys for direct choice, Ctrl+C to cancel\n\n",
            style="dim",
        )

        panel_content = Text.assemble(
            instructions, self.prepare_message(), "\n", content
        )

        panel = Panel(panel_content, border_style="blue")

        if not hasattr(self, "_first_render"):
            # First time rendering
            with self.console_manager.console.capture() as capture:
                self.console_manager.console.print(panel)
            # Count actual rendered lines
            self._panel_lines = len(capture.get().split("\n")) - 1
            # Print the actual panel
            self.console_manager.console.print(panel)
            self._first_render = True
        else:
            # Move cursor up by the number of lines in the panel
            print(f"\033[{self._panel_lines}A", end="")
            # Clear from cursor to end of screen
            print("\033[J", end="")
            self.console_manager.console.print(panel)

    def select(self) -> Optional[int]:
        """
        Interactive list selection with arrow key navigation.

        Returns:
            Selected index (0-based) or None for cancel
        """
        import sys
        import termios
        import tty

        def getch():
            """Read a single character from stdin."""
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        while True:
            self._render_options()

            key = getch()

            # Handle number key input for direct selection
            if key.isdigit():
                num = int(key)
                if 1 <= num <= len(self.options):
                    return num - 1

            # Arrow key handling
            elif key == "\x1b":
                next1, next2 = getch(), getch()
                if next1 == "[":
                    if next2 == "A":  # Up arrow
                        self.selected_index = (self.selected_index - 1) % len(
                            self.options
                        )
                    elif next2 == "B":  # Down arrow
                        self.selected_index = (self.selected_index + 1) % len(
                            self.options
                        )

            # Enter key
            elif key in ["\r", "\n"]:
                return self.options[self.selected_index]

            # Ctrl+C
            elif key == "\x03":
                return None
