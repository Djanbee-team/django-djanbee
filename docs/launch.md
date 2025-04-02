# Launch Command

## Overview
The `launch` command is the first step in the Djanbee deployment workflow. It initializes the deployment environment and locates your Django project for subsequent configuration and deployment steps.

## Basic Usage

```bash
# Basic usage
djanbee launch

# Specify project path explicitly
djanbee launch /path/to/your/django-project
```

## What It Does

When you run `djanbee launch`, Djanbee will:

1. Display a splash screen with deployment information
2. Scan for Django projects in the current directory (or specified path)
3. Select the Django project for deployment (with your input if multiple projects are found)
4. Prepare the environment for the next deployment steps

## Example Output

```bash
$ djanbee launch
🚀 Djanbee deployment service
  ⚠️ The setup might require root privileges

🔍 Searching for Django projects...
✅ Found Django project: myproject

Project is ready for setup!
```

## Common Scenarios

### Single Project
If there's only one Django project in the directory, Djanbee will automatically select it.

### Multiple Projects
If multiple projects are found, you'll see a selection prompt:

```
Multiple Django projects found:
1. project1
2. project2
3. project3

Please select a project (1-3):
```

### Custom Project Path
For deployments where your project isn't in the current directory:

```bash
djanbee launch /var/www/myproject
```

## Troubleshooting

- **No Django project found**: Verify you're in the correct directory or specify the path explicitly
- **Multiple projects without selection**: You must select one project to proceed
- **Missing system prerequisites**: Djanbee will notify you of any missing requirements

## Next Steps

After successfully running the launch command, proceed to:

```bash
djanbee setup      # Creates virtual environment and installs dependencies
djanbee configure  # Configures Django settings for production
djanbee deploy     # Deploys the application with Nginx and Gunicorn
```

---

## Technical Details

### Command Workflow

The detailed sequence when running `djanbee launch`:

1. Create an application container with all required services
2. Initialize the LaunchContainer with dependencies
3. Display the splash screen
4. Scan directories for Django projects
5. Select or prompt user to select a project
6. Initialize the deployment environment
7. Store project state for subsequent commands

### Architecture

The launch command follows a modular architecture with three components:

#### LaunchContainer (`container.py`)
The container component manages dependency injection and component lifecycle:

```python
@classmethod
def create(cls, app: AppContainer) -> "LaunchContainer":
    """Creates and wires launch components with required dependencies"""
    display = LaunchDisplay(console_manager=app.console_manager)
    manager = LaunchManager(display, app)
    return cls(display=display, manager=manager)
```

#### LaunchDisplay (`display.py`)
Handles all user interface and presentation concerns:

```python
def display_splash_screen(self) -> None:
    """Display welcome splash screen with service info"""
    title = Text("Djanbee deployment service", style="bold white", justify="center")
    warning = Text(
        "\nThe setup might require root privileges",
        style="yellow",
        justify="center",
    )
    content = Text.assemble(title, warning)
    self.console_manager.console.print(Panel(content, box=box.DOUBLE, style="blue"))
```

#### LaunchManager (`manager.py`)
Contains the business logic for project initialization:

```python
def launch_project(self, path: str = "") -> Optional[object]:
    """
    Initialize environment and select Django project.
    
    Args:
        path: Optional path to Django project directory
        
    Returns:
        Selected project object or None if no project found
        
    Raises:
        ProjectNotFoundError: If no Django project can be found in the path
        MultipleProjectsError: If multiple projects are found and user cancels selection
    """
    # Show splash screen
    self.display.display_splash_screen()

    # Initialize working directory
    self.app.django_manager.project_service.initialize_directory(path)

    # Find and select Django project
    return self.app.django_manager.project_service.select_project()
```

### Project Detection Implementation

Djanbee uses several strategies to locate valid Django projects:

1. Check for the presence of `manage.py`
2. Verify project structure for Django-specific files
3. Inspect settings files for Django configurations

When multiple projects are detected, the user is prompted with a selection interface backed by Djanbee's widget system.

### Environment Initialization

After a project is selected, Djanbee:

1. Creates necessary environment folders
2. Verifies system prerequisites 
3. Prepares for virtual environment creation (executed in the `setup` command)
4. Records project location for subsequent commands