from typing import Optional, List, Dict, Tuple
from rich.panel import Panel
from rich.text import Text
from ..managers import ConsoleManager


class TextInputWidget:
    def __init__(
        self,
        title: str,
        fields: List[Tuple[str, str]],
        console_manager: ConsoleManager,
        create_button_text: str = "Create",
        cancel_button_text: str = "Cancel",
    ):
        """
        Initialize a text input widget with multiple fields.

        Args:
            title: Title for the input panel
            fields: List of tuples containing (field_name, default_value)
            console_manager: Console manager for rendering
            create_button_text: Text for the create/confirm button
            cancel_button_text: Text for the cancel button
        """
        self.title = title
        self.fields = fields
        self.console_manager = console_manager
        self.create_button_text = create_button_text
        self.cancel_button_text = cancel_button_text

        # Current state
        self.active_index = 0  # 0 to len(fields)-1 are fields, then buttons
        self.values = [default for _, default in fields]
        self.cursor_positions = [len(default) for _, default in fields]

        # Button indices
        self.create_button_index = len(fields)
        self.cancel_button_index = len(fields) + 1

    def prepare_title(self):
        """Prepare the title with an input emoji"""
        text = Text()
        text.append("✏️ ", style="")  # Input emoji
        text.append(self.title, style="blue")
        return text

    def _render_widget(self):
        """Render the text input widget with all fields and buttons"""
        content = Text()

        # Render fields
        for idx, (field_name, _) in enumerate(self.fields):
            if idx > 0:
                content.append("\n\n")

            # Field label
            content.append(f"{field_name}: ", style="bold")

            # Field input
            field_value = self.values[idx]
            cursor_pos = self.cursor_positions[idx]

            # Active field gets highlighted
            if idx == self.active_index:
                # Split the value at cursor position to show the cursor
                before_cursor = field_value[:cursor_pos]
                after_cursor = field_value[cursor_pos:]

                content.append(before_cursor)
                content.append("█", style="blink")  # Cursor
                content.append(after_cursor, style="")
            else:
                content.append(field_value)

        # Add spacing before buttons
        content.append("\n\n")

        # Render buttons
        create_text = (
            f"→ {self.create_button_text} ←"
            if self.active_index == self.create_button_index
            else f"  {self.create_button_text}  "
        )
        cancel_text = (
            f"→ {self.cancel_button_text} ←"
            if self.active_index == self.cancel_button_index
            else f"  {self.cancel_button_text}  "
        )

        content.append(
            Text(
                create_text,
                style=(
                    "reverse" if self.active_index == self.create_button_index else ""
                ),
            )
        )
        content.append("    ")  # Space between buttons
        content.append(
            Text(
                cancel_text,
                style=(
                    "reverse" if self.active_index == self.cancel_button_index else ""
                ),
            )
        )

        # Instructions
        instructions = Text(
            "Use Tab/↑↓/←→ to navigate, Enter to confirm, Ctrl+C to cancel\n\n",
            style="dim",
        )

        # Assemble the panel
        panel_content = Text.assemble(
            instructions, self.prepare_title(), "\n\n", content
        )

        panel = Panel(panel_content, border_style="blue")

        # Handle rendering and cursor positioning
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

    def _handle_text_input(self, key, field_idx):
        """Handle text input for a specific field"""
        # Current state
        current_value = self.values[field_idx]
        cursor_pos = self.cursor_positions[field_idx]

        # Handle backspace
        if key == "\x7f":  # Backspace
            if cursor_pos > 0:
                # Remove the character before the cursor
                self.values[field_idx] = (
                    current_value[: cursor_pos - 1] + current_value[cursor_pos:]
                )
                self.cursor_positions[field_idx] = cursor_pos - 1
        # Handle delete
        elif key == "\x1b":
            # This could be an arrow key or delete key sequence
            return "special"
        # Handle normal character input
        elif key.isprintable():
            # Insert the character at cursor position
            self.values[field_idx] = (
                current_value[:cursor_pos] + key + current_value[cursor_pos:]
            )
            self.cursor_positions[field_idx] = cursor_pos + 1

        return "handled"

    def get_result(self) -> Optional[Dict[str, str]]:
        """
        Run the text input widget and return the entered values.

        Returns:
            Dict mapping field names to values, or None if canceled
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
            self._render_widget()

            key = getch()

            # Ctrl+C to cancel
            if key == "\x03":
                return None

            # Tab key to move between fields
            elif key == "\t":
                self.active_index = (self.active_index + 1) % (len(self.fields) + 2)

            # Enter key
            elif key == "\r" or key == "\n":
                # If on a button
                if self.active_index == self.create_button_index:
                    # Return the field values
                    return {
                        field[0]: value
                        for field, value in zip(self.fields, self.values)
                    }
                elif self.active_index == self.cancel_button_index:
                    return None
                else:
                    # Move to next field or to create button
                    self.active_index = (self.active_index + 1) % (len(self.fields) + 2)

            # Arrow key or special key sequence
            elif key == "\x1b":
                seq = getch()
                if seq == "[":
                    direction = getch()

                    if direction in ["A", "D"]:  # Up arrow or Left arrow
                        # If we're at the Cancel button and want to go left
                        if (
                            self.active_index == self.cancel_button_index
                            and direction == "D"
                        ):
                            # Move to Create button
                            self.active_index = self.create_button_index
                        else:
                            # Normal backward navigation
                            self.active_index = (self.active_index - 1) % (
                                len(self.fields) + 2
                            )

                    elif direction in ["B", "C"]:  # Down arrow or Right arrow
                        # If we're at the Create button and want to go right
                        if (
                            self.active_index == self.create_button_index
                            and direction == "C"
                        ):
                            # Move to Cancel button
                            self.active_index = self.cancel_button_index
                        else:
                            # Normal forward navigation
                            self.active_index = (self.active_index + 1) % (
                                len(self.fields) + 2
                            )

                    # Handle cursor movement within text fields
                    if self.active_index < len(self.fields):
                        field_idx = self.active_index
                        if direction == "C" and self.cursor_positions[field_idx] < len(
                            self.values[field_idx]
                        ):
                            # Move cursor right
                            self.cursor_positions[field_idx] += 1
                        elif direction == "D" and self.cursor_positions[field_idx] > 0:
                            # Move cursor left
                            self.cursor_positions[field_idx] -= 1

            # Handle text input if we're on a field
            elif self.active_index < len(self.fields):
                self._handle_text_input(key, self.active_index)
