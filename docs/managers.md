# Djanbee Manager Architecture

## What is a Manager?

A manager in Djanbee is a specialized component that handles one specific domain of functionality. Each manager is responsible for only its own abstraction level - it doesn't reach across boundaries or try to handle responsibilities outside its domain.

## Why Use Managers?

Managers provide several key benefits:

1. **Clear Responsibility Boundaries**: Each manager focuses on exactly one domain
2. **Simplified Code Maintenance**: When you need to fix OS-related code, you only need to look at the OS manager
3. **Easier Testing**: Managers can be tested independently without complex dependencies
4. **Platform Independence**: Specific implementations (Windows/Unix) can be swapped without changing other code
5. **Reusability**: Managers can be reused across different commands and features

## Manager Structure

Djanbee uses a consistent structure for all managers that consists of:

1. **Base Class** (usually in `base.py`)
   - Defines what operations the manager must support
   - Sets the contract that all implementations must follow
   - Example: `BaseOSManager` requires methods like `search_subfolders()` and `get_home_dir()`

2. **Implementation Classes** (in specific subdirectories)
   - Provide actual code for different platforms or scenarios
   - Handle the unique requirements of each environment
   - Example: `UnixOSManager` and `WindowsOSManager` implement OS operations differently

3. **Main Manager Class** (typically in `main.py`)
   - Acts as the entry point that other code interacts with
   - Automatically selects the right implementation based on the environment
   - Handles any common logic shared across implementations
   - Example: `OSManager` detects the operating system and uses the appropriate implementation

This structure allows Djanbee to work across different environments while keeping code organized and maintainable. When a Windows-specific operation is needed, only the Windows implementation needs to change, leaving all other code untouched.

## Manager Hierarchy

*IMPORTANT: The Python `subprocess` module should ONLY be used through the `CommandRunner` abstraction. Direct subprocess calls elsewhere in the codebase are strictly prohibited.*

Djanbee implements a clear hierarchy of responsibility for system-level operations:

### CommandRunner

All system-level functionality begins with the `CommandRunner` class, which serves as the foundation for executing external processes. This abstraction:

- Provides a uniform interface for running system commands
- Handles command string parsing, sudo elevation, and process execution
- Encapsulates subprocess functionality to prevent scattered implementations
- Returns standardized `CommandResult` objects with the following properties:

  ```python
  success: bool    # Whether the operation was successful
  stdout: str      # Standard output of the command
  stderr: str      # Standard error of the command  
  exit_code: int   # Process exit code
  ```

The `CommandRunner` is used by the `OSManager`, which then exposes higher-level operations to other managers in the system.

### Manager Communication Chain

System operations flow through this chain:
1. Command-specific managers request operations
2. These requests flow to the appropriate domain manager
3. Domain managers use the `OSManager` for system interactions
4. The `OSManager` utilizes `CommandRunner` for process execution

This structure ensures that subprocess calls are never scattered throughout the application but are always managed through the proper abstraction layers.

## Key Managers

Djanbee includes these specialized managers:

- **ConsoleManager**: Handles terminal output formatting and user interaction
- **OSManager**: Provides an abstraction over operating system operations
- **DjangoManager**: Manages Django project detection and configuration
- **DatabaseManager**: Handles database connectivity and configuration
- **ServerManager**: Manages web server configuration (e.g., Nginx)
- **SocketManager**: Manages WSGI server socket configuration (e.g., Gunicorn)
- **DotenvManager**: Manages environment variable loading from .env files
- **EnvManager**: Handles environment variables across the application

## How Managers Work Together

Managers collaborate through clear interfaces:

1. **Dependency Injection**: Managers receive other managers they need to work with
2. **Focused Communication**: Managers only request services through public interfaces
3. **Layered Dependencies**: Core managers (like OS) support higher-level managers (like Django)

For example, when deploying a Django application:
- The `DeployCommand` coordinates the overall process
- It uses the `DjangoManager` to handle project-specific tasks
- The `DjangoManager` uses the `OSManager` for file operations
- The `OSManager` handles the platform-specific details

Each manager stays focused on its specific job, creating a clean separation of responsibilities.

## Benefits of This Approach

By organizing code into managers with clear boundaries:

1. **Code stays organized** - Each component has a clear home
2. **Adding new features is simpler** - Just implement the required interfaces
3. **Debugging is easier** - Problems are isolated to specific managers
4. **Cross-platform support** - Implementations can vary without changing the interface
5. **Teams can work independently** - Different developers can work on different managers

This architecture allows Djanbee to remain maintainable as it grows in complexity and supports more features across different environments.