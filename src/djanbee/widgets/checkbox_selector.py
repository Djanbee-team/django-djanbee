from typing import Optional, List, Set
from rich.panel import Panel
from rich.text import Text
from ..managers import ConsoleManager


class CheckboxSelector:
    def __init__(
        self, message: str, options: List[str], console_manager: ConsoleManager
    ):
        self.cursor_index = 0
        self.selected_indices = set()
        self.console_manager = console_manager
        self.message = message
        self.options = options

    def prepare_message(self):
        """Print question message in blue with checkbox emoji and border"""
        text = Text()
        text.append("✓ ", style="")  # Checkbox emoji
        text.append(self.message, style="blue")
        text.append("\n")
        return text

    def _render_options(self):
        """Render the checkbox selection options."""
        content = Text()

        for idx, option in enumerate(self.options):
            if idx > 0:
                content.append("\n")

            # Show checkbox status
            checkbox = "☑" if idx in self.selected_indices else "☐"

            if idx == self.cursor_index:
                content.append(f"→ {checkbox} {option}", style="reverse")
            else:
                content.append(f"  {checkbox} {option}", style="")

        instructions = Text(
            "Use ↑↓ to navigate, Space to toggle, Enter to confirm selection, Ctrl+C to cancel\n\n",
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

    def select(self) -> List[str]:
        """
        Interactive checkbox selection with arrow key navigation.

        Returns:
            List of selected option strings or empty list if canceled
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

            # Arrow key handling
            if key == "\x1b":
                next1, next2 = getch(), getch()
                if next1 == "[":
                    if next2 == "A":  # Up arrow
                        self.cursor_index = (self.cursor_index - 1) % len(self.options)
                    elif next2 == "B":  # Down arrow
                        self.cursor_index = (self.cursor_index + 1) % len(self.options)

            # Space key to toggle selection
            elif key == " ":
                if self.cursor_index in self.selected_indices:
                    self.selected_indices.remove(self.cursor_index)
                else:
                    self.selected_indices.add(self.cursor_index)

            # 'a' key to select all
            elif key.lower() == "a":
                if len(self.selected_indices) == len(self.options):
                    # If all are selected, deselect all
                    self.selected_indices.clear()
                else:
                    # Otherwise select all
                    self.selected_indices = set(range(len(self.options)))

            # Enter key to confirm selection
            elif key in ["\r", "\n"]:
                return [self.options[i] for i in self.selected_indices]

            # Ctrl+C to cancel
            elif key == "\x03":
                return []
