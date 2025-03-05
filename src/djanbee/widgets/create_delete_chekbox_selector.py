from typing import Optional, List, Set, Tuple, Union
from rich.panel import Panel
from rich.text import Text
from ..managers import ConsoleManager


class CreateDeleteCheckboxSelector:
    """
    A checkbox selector with delete, create, and done action buttons.

    This component allows users to:
    - Navigate through options using arrow keys
    - Toggle checkboxes using Space
    - Navigate to action buttons using down arrow from the last item
    - Delete selected items using a Delete button or 'd' key
    - Create new items using a Create button or 'c' key
    - Confirm selection and continue using Done button or Enter key
    """

    ACTION_CREATE = "create"
    ACTION_DELETE = "delete"
    ACTION_SELECT = "select"
    ACTION_CANCEL = "cancel"
    ACTION_DONE = "done"

    def __init__(
        self, message: str, options: List[str], console_manager: ConsoleManager
    ):
        self.cursor_index = 0
        self.selected_indices = set()
        self.console_manager = console_manager
        self.message = message
        self.options = options
        self.button_index = (
            -1
        )  # -1 for no button, 0 for Delete, 1 for Create, 2 for Done
        self._first_render = False
        self._panel_lines = 0

    def prepare_message(self):
        """Print question message in blue with checkbox emoji and border"""
        text = Text()
        text.append("✓ ", style="")  # Checkbox emoji
        text.append(self.message, style="blue")
        text.append("\n")
        return text

    def _render_options(self):
        """Render the checkbox selection options and action buttons."""
        content = Text()

        # Render list options with checkboxes
        for idx, option in enumerate(self.options):
            if idx > 0:
                content.append("\n")

            # Show checkbox status
            checkbox = "☑" if idx in self.selected_indices else "☐"

            if idx == self.cursor_index and self.button_index == -1:
                content.append(f"→ {checkbox} {option}", style="reverse")
            else:
                content.append(f"  {checkbox} {option}", style="")

        # Add spacer
        content.append("\n\n")

        # Add action buttons
        delete_style = "reverse" if self.button_index == 0 else ""
        create_style = "reverse" if self.button_index == 1 else ""
        done_style = "reverse" if self.button_index == 2 else ""

        content.append("  [Delete]  ", style=f"red {delete_style}")
        content.append("   ")
        content.append("  [Create]  ", style=f"green {create_style}")
        content.append("   ")
        content.append("  [Done]  ", style=f"blue {done_style}")

        # Add instructions
        instructions = Text(
            "Use ↑↓ to navigate, Space to toggle selection, 'a' to select all, "
            "Enter to confirm, 'd' to delete, 'c' to create, 's' for done, Ctrl+C to cancel\n\n",
            style="dim",
        )

        panel_content = Text.assemble(
            instructions, self.prepare_message(), "\n", content
        )

        panel = Panel(panel_content, border_style="blue")

        if not self._first_render:
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

    def select(self) -> Tuple[str, Union[List[str], None]]:
        """
        Interactive checkbox selection with action buttons.

        Returns:
            Tuple containing (action, selection) where:
            - action: One of ACTION_CREATE, ACTION_DELETE, ACTION_SELECT, ACTION_CANCEL, ACTION_DONE
            - selection: Either a list of selected items or None
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

            # Delete key
            if key == "d" or key == "D":
                if not self.selected_indices:
                    # If nothing explicitly selected, use current highlighted item
                    return (self.ACTION_DELETE, [self.options[self.cursor_index]])
                return (
                    self.ACTION_DELETE,
                    [self.options[i] for i in self.selected_indices],
                )

            # Create key
            elif key == "c" or key == "C":
                return (self.ACTION_CREATE, None)

            # Done key (using 's' for "save and continue")
            elif key == "s" or key == "S":
                return (
                    self.ACTION_DONE,
                    [self.options[i] for i in self.selected_indices],
                )

            # Arrow key handling
            elif key == "\x1b":
                next1, next2 = getch(), getch()
                if next1 == "[":
                    if next2 == "A":  # Up arrow
                        if self.button_index != -1:
                            # Move focus back to the list
                            self.button_index = -1
                        else:
                            # Navigate up within the list
                            self.cursor_index = (self.cursor_index - 1) % len(
                                self.options
                            )
                    elif next2 == "B":  # Down arrow
                        if self.button_index == -1:
                            if self.cursor_index == len(self.options) - 1:
                                # Move from last list item to the Delete button
                                self.button_index = 0
                            else:
                                # Navigate down within the list
                                self.cursor_index = (self.cursor_index + 1) % len(
                                    self.options
                                )
                    elif next2 == "C":  # Right arrow
                        if self.button_index == 0:
                            self.button_index = 1  # Move from Delete to Create
                        elif self.button_index == 1:
                            self.button_index = 2  # Move from Create to Done
                    elif next2 == "D":  # Left arrow
                        if self.button_index == 1:
                            self.button_index = 0  # Move from Create to Delete
                        elif self.button_index == 2:
                            self.button_index = 1  # Move from Done to Create

            # Space key to toggle selection
            elif key == " " and self.button_index == -1:
                if self.cursor_index in self.selected_indices:
                    self.selected_indices.remove(self.cursor_index)
                else:
                    self.selected_indices.add(self.cursor_index)

            # 'a' key to select all or clear all
            elif key.lower() == "a":
                if len(self.selected_indices) == len(self.options):
                    # If all are selected, deselect all
                    self.selected_indices.clear()
                else:
                    # Otherwise select all
                    self.selected_indices = set(range(len(self.options)))

            # Tab key to switch focus
            elif key == "\t":
                if self.button_index == -1:
                    self.button_index = 0  # Focus on Delete button
                elif self.button_index == 0:
                    self.button_index = 1  # Focus on Create button
                elif self.button_index == 1:
                    self.button_index = 2  # Focus on Done button
                else:
                    self.button_index = -1  # Focus back on list

            # Enter key
            elif key in ["\r", "\n"]:
                if self.button_index == 0:  # Delete button
                    if not self.selected_indices:
                        # If nothing explicitly selected, use current highlighted item
                        return (self.ACTION_DELETE, [self.options[self.cursor_index]])
                    return (
                        self.ACTION_DELETE,
                        [self.options[i] for i in self.selected_indices],
                    )
                elif self.button_index == 1:  # Create button
                    return (self.ACTION_CREATE, True)
                elif self.button_index == 2:  # Done button
                    return (
                        self.ACTION_DONE,
                        [self.options[i] for i in self.selected_indices],
                    )
                else:  # List item
                    # Return all selected items, or the current item if none are selected
                    if not self.selected_indices:
                        return (self.ACTION_SELECT, [self.options[self.cursor_index]])
                    return (
                        self.ACTION_SELECT,
                        [self.options[i] for i in self.selected_indices],
                    )

            # Ctrl+C
            elif key == "\x03":
                return (self.ACTION_CANCEL, None)
