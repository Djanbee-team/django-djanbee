# Djanbee Core Module

## What is the Core Module?

The core module provides a central access point for all managers in Djanbee. It uses the **Service Locator** pattern combined with a **Singleton** pattern to make managers available throughout the application without manually passing them through multiple layers of code.

## The AppContainer

The heart of the core module is the `AppContainer`, which:

1. Stores all application managers in one place
2. Creates managers in the correct order with proper dependencies 
3. Makes managers available through a single access point
4. Uses lazy loading to initialize managers only when needed

## Why We Use Service Locator

The Service Locator pattern solves a common problem in complex applications:

1. Without it, managers would need to be passed through multiple layers of code
2. This creates lengthy parameter lists and tight coupling between components
3. The Service Locator provides a simpler way to access services wherever they're needed

Think of the AppContainer as a central registry where all managers are stored and can be retrieved as needed.

## How It Works

The container implements both Service Locator and Singleton patterns:

1. A single instance is created the first time it's accessed (`get_instance()`)
2. This instance contains all properly initialized managers
3. The same instance is returned on all subsequent access
4. Managers are wired together with their dependencies automatically

## Current Implementation

The current implementation is straightforward:

1. The `AppContainer` class is defined as a dataclass with fields for each manager
2. A private `_instance` class variable holds the singleton instance
3. The `get_instance()` method creates the instance on first access
4. All managers are created in the correct dependency order

This approach might be refined in the future as the application grows more complex, but it provides a practical solution for the current needs.

## Using the Core Container

The container is typically used in two ways:

1. At the entry point of commands to access required managers
2. Passed to command containers to make managers available to command components

For example:
- The launch command container receives the AppContainer
- It uses the container to access ConsoleManager, DjangoManager, etc.
- This avoids having to pass individual managers through numerous method calls

## Best Practices

When working with the core container:

1. Access the container at the highest appropriate level (typically in command containers)
2. Only use the managers you actually need
3. Don't create new instances of managers outside the container
4. Don't modify managers obtained from the container