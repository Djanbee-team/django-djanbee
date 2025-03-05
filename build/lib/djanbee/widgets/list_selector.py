from typing import List, Tuple
from pathlib import Path
from ..utils.console import console_manager
from rich.panel import Panel
from rich.text import Text
from typing import Optional

class ListSelector:
    def __init__(self, projects: List[Tuple[str, Path]]):
        self.console_manager = console_manager
        self.projects = projects
        self.selected_index = 0

    def _render_menu(self):
        """Render the project selection menu."""
        panel_content = []
        print(self.projects)

        for idx, (name, path) in enumerate(self.projects):
            # Highlight the current selection
            if idx == self.selected_index:
                line = Text(f"> {name} ({path})", style="reverse")
            else:
                line = Text(f"  {name} ({path})")
            panel_content.append(line)

        # Add navigation instructions
        instructions = Text("\nUse ↑ and ↓ to navigate, Enter to select, Ctrl+C to cancel", style="dim")
        
        panel = Panel(
            "\n".join(str(line) for line in panel_content + [instructions]),
            title="Select Django Project",
            border_style="blue"
        )
        
        self.console_manager.console.print(panel)

    def select(self) -> Optional[Tuple[str, Path]]:
        """
        Interactive project selection with arrow key navigation.
        
        Returns:
            Optional tuple of (project_name, project_path)
        """
        if not self.projects:
            return None

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
            self._render_menu()

            key = getch()
            
            # Arrow key handling (works for most terminals)
            if key == '\x1b':
                next1, next2 = getch(), getch()
                if next1 == '[':
                    if next2 == 'A':  # Up arrow
                        self.selected_index = max(0, self.selected_index - 1)
                    elif next2 == 'B':  # Down arrow
                        self.selected_index = min(len(self.projects) - 1, self.selected_index + 1)
            
            # Enter key
            elif key == '\r' or key == '\n':
                return self.projects[self.selected_index]
            
            # Ctrl+C
            elif key == '\x03':
                return None

