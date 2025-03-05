from typing import Optional
from rich.panel import Panel
from rich.text import Text
from ..managers import ConsoleManager

class QuestionSelector:
    def __init__(self, message: str, console_manager: ConsoleManager, positive_command = "yes", negative_command = "no", warning = ""):
        self.selected_index = 0  # 0 for Yes, 1 for No
        self.console_manager = console_manager
        self.message = message
        self.positive_command = positive_command
        self.negative_command = negative_command
        self.warning = warning


    def prepare_question(self):
        """Print question message in blue with question mark emoji and border"""
        text = Text()
        text.append("❓ ", style="")  # Question mark emoji
        text.append(self.message, style="blue")
        text.append("\n")
        return text
    
    def prepare_warning(self):
        text = Text()
        if self.warning:
            text.append("!!! ", style="yellow") 
            text.append(self.warning, style="yellow")
            text.append("\n")
            text.append("\n")
        return text

    
                
    def _render_options(self):
        """Render the Yes/No selection options."""
        yes_text = f"→ {self.positive_command} ←" if self.selected_index == 0 else f"  {self.positive_command}  "
        no_text = f"→ {self.negative_command} ←" if self.selected_index == 1 else f"  {self.negative_command}  "
        
        content = Text.assemble(
            Text(yes_text, style="reverse" if self.selected_index == 0 else ""),
            "    ",
            Text(no_text, style="reverse" if self.selected_index == 1 else "")
        )
        
        instructions = Text("Use ←→ or ↑↓ to navigate, Enter to select, Y/N for direct choice, Ctrl+C to cancel\n\n", style="dim")

        panel_content = Text.assemble(
            instructions,
            self.prepare_warning(),
            self.prepare_question(),
            "\n",
            content
        )
        
        panel = Panel(
            panel_content,
            border_style="blue"
        )
        
        if not hasattr(self, '_first_render'):
            # First time rendering
            with self.console_manager.console.capture() as capture:
                self.console_manager.console.print(panel)
            # Count actual rendered lines
            self._panel_lines = len(capture.get().split('\n'))-1
            # Print the actual panel
            self.console_manager.console.print(panel)
            self._first_render = True

        else:
            # Move cursor up by the number of lines in the panel
            print(f"\033[{self._panel_lines}A", end="")
            # Clear from cursor to end of screen
            print("\033[J", end="")
            self.console_manager.console.print(panel)
    def select(self) -> Optional[bool]:
        """
        Interactive Yes/No selection with arrow key navigation.
        
        Returns:
            True for Yes, False for No, None for cancel
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
            
            # Handle direct Y/N input
            if key.lower() == 'y':
                return True
            elif key.lower() == 'n':
                return False
            
            # Arrow key handling
            elif key == '\x1b':
                next1, next2 = getch(), getch()
                if next1 == '[':
                    if next2 in ['D', 'A']:  # Left arrow or Up arrow
                        self.selected_index = 0
                    elif next2 in ['C', 'B']:  # Right arrow or Down arrow
                        self.selected_index = 1
            
            # Enter key
            elif key in ['\r', '\n']:
                return self.selected_index == 0
            
            # Ctrl+C
            elif key == '\x03':
                return None
        