# Djanbee Widget Architecture

## What is a Widget?

A widget in Djanbee is a self-contained UI component that handles a specific type of user interaction. Each widget encapsulates everything needed for a particular type of terminal user interface element - from rendering to keyboard handling to state management.

Widgets operate at a single abstraction level: user interaction. They don't handle business logic or application state beyond what's needed for their specific interaction.

## Core Widget Principles

Widgets in Djanbee follow these key principles:

1. **Self-contained**: A widget can be created anywhere in the codebase just by importing its class
2. **Single responsibility**: Each widget handles exactly one type of interaction pattern
3. **Dependency injection**: The ConsoleManager is provided to widgets rather than created internally
4. **Abstraction boundaries**: Widgets handle UI concerns only, not application logic

## Widget Base Class 

All widgets inherit from a common base class that handles:

- Terminal input/output management
- Keyboard event handling
- Screen clearing and redrawing
- Common rendering patterns
- Cursor management

This approach eliminates code duplication and ensures consistent behavior across all interactive elements.

## Widget Organization

The widget architecture separates concerns in several ways:

1. **Input separation**: Keyboard handling is separated from business logic
2. **Output separation**: Rendering is handled independently from state management
3. **State encapsulation**: Each widget maintains only its own internal state

## Widget Lifecycle

Widgets follow a consistent lifecycle pattern:

1. **Initialization**
   - Widget is created with required parameters: message, console_manager, and widget-specific data
   - Initial state is set (selected_index, cursor_index, etc.)
   - Pre-selected values or configuration options are applied

2. **Rendering**
   - The prepare_message method formats the widget title/message
   - The _render_options method displays all interaction elements
   - First render measures panel height for future redrawing
   - Instructions for navigation are displayed to guide the user

3. **Interaction Loop**
   - The select or get_result method initiates the interaction
   - Widget enters a continuous loop of:
     - Render current state
     - Capture keyboard input via getch
     - Process input and update internal state
     - Redraw the widget with updated state
   - Loop continues until user makes a selection or cancels

4. **Redrawing**
   - Previous output is cleared using terminal control sequences
   - Widget is redrawn at the same position to create the illusion of in-place updates
   - State changes (like selection highlighting) are reflected in the redraw

5. **Result Return**
   - When user completes interaction (via Enter key or similar)
   - The select or get_result method returns the appropriate data type
   - Different widgets return different data: string, boolean, list, index, etc.
   - If canceled (via Ctrl+C), typically returns None

This consistent lifecycle makes widgets predictable for both users and developers.

## Widget Types

Djanbee includes specialized widgets for different interaction patterns:

- **ListSelector**: Single-choice selection from a list of options
- **CheckboxSelector**: Multi-choice selection with checkboxes
- **TextInput**: Free-form text input with validation
- **QuestionSelector**: Yes/No question selection
- **CreateDeleteCheckboxSelector**: Special checkbox selector with create/delete actions

## Best Practices for Widgets

When working with or creating widgets:

1. **Keep widgets focused**: A widget should do one thing well
2. **Inject dependencies**: Pass in the ConsoleManager rather than creating it
3. **Respect abstraction boundaries**: Widgets should not reach into other system components
4. **Consistent interfaces**: Maintain common patterns across widgets
5. **Self-documentation**: Widget method names should clearly indicate their purpose
6. **Avoid side effects**: Widgets should not modify application state directly

## Widget-Command Relationship

Widgets serve as the building blocks for command interfaces:

- Commands use widgets to gather user input
- Widgets return structured data to commands
- Commands interpret widget results and take appropriate actions
- Multiple widgets can be combined to create complex interactions

## Benefits of the Widget Architecture

This widget architecture provides several advantages:

1. **Consistent UI**: All interactive elements share the same look and feel
2. **Reduced code duplication**: Common functionality lives in the base class
3. **Improved testability**: Widgets can be tested in isolation
4. **Easy to extend**: New interaction patterns can be added as new widget types
5. **Better user experience**: Users learn interaction patterns once and apply them across all commands

By organizing terminal interactions into well-defined widgets, Djanbee maintains a clean, consistent, and intuitive user interface.