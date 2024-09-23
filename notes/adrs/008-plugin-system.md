# Plugin Architecture for Abilian SBE

Status: Draft

## Introduction

This ADR proposes the adoption of a **plugin architecture** for **Abilian SBE**, which will provide a modular and extensible system for integrating and managing pluggable services such as search, storage, and other customizable components. The architecture will allow dynamic addition, modification, or removal of plugins at runtime, ensuring flexibility, scalability, and ease of customization. Several Python-based libraries and architectures will be evaluated for this purpose.

## Summary

We propose creating a **pluggable architecture** for Abilian SBE to support modularization and extension of core services such as search, storage, and other components. The system will allow the addition and swapping of services at runtime, maintaining flexibility and scalability.

The plugin architecture should follow several core principles:

- **Extensibility**: Allow developers to easily add plugins to extend or modify core system behavior.
- **Modularity**: Core services (e.g., storage, search) should be separated from the main application logic and managed through a plugin system.
- **Isolation**: Plugins should operate independently, ensuring that failures or errors in one plugin do not affect others.
- **Dynamic Integration**: Plugins can be loaded, unloaded, or updated without requiring a system restart.

## Status

Proposed

## Context and Goals

### Context

Abilian SBE’s current architecture tightly couples certain services (such as search and storage) with the core system, making it difficult to replace or extend them without significant code changes. To support features like **pluggable search** and **pluggable storage**, as well as future services, we need a dynamic, flexible plugin system that decouples these components from the core application.

A plugin architecture would allow developers and administrators to choose, configure, and extend Abilian SBE’s services (e.g., switching between search engines such as **Whoosh**, **Elasticsearch**, or **Typesense**) without modifying the core codebase. Several Python libraries provide existing solutions for building plugin systems that are well-suited for Abilian SBE.

### Goals

- **Modularize core functionalities** such as search and storage using a pluggable system.
- **Implement a plugin interface** that ensures consistency across plugins, allowing seamless addition and removal of modules.
- **Enable dynamic loading and unloading** of plugins at runtime.
- **Ensure proper isolation** between plugins to prevent conflicts and maintain system stability.
- **Allow third-party integrations** and customizations via plugins, extending the capability of Abilian SBE without direct modification of the core code.

## Tenets

- **Extensibility**: The architecture should support seamless extension through third-party plugins.
- **Modularity**: Core services such as search and storage should be decoupled from the system and managed through plugins.
- **Isolation**: Plugins should be isolated from the core system and from each other, preventing conflicts or issues caused by one plugin from affecting others.
- **Simplicity**: The plugin system should be simple to configure, use, and maintain.
- **Scalability**: The system must scale to accommodate various levels of complexity, from small plugins to large, distributed services like search engines.

## Decision

We will implement a **plugin architecture** for Abilian SBE using either Pluggy (extended with some custom code) or something else TBD.

## Preliminary Detailed Design

Assuming Pluggy for now.

1. **Plugin Hooks and Interfaces**:
   - We will define a **plugin interface** using **Pluggy** that allows plugins to register for specific hooks. For instance, storage plugins can register for the "storage" hook and search plugins for the "search" hook.
   - Example hook definition:
     ```python
     @hookspec
     def get_storage_backend() -> StorageBackend:
         """Return the storage backend instance."""
     ```

2. **Plugin Discovery and Loading**:
   - Plugins will be discovered and loaded dynamically using either **Pluggy** or **Stevedore**, depending on the deployment environment.
   - **Pluggy** will manage runtime plugin execution, while **Stevedore** will handle plugins distributed as Python packages via entry points. Example configuration for Stevedore:
     ```yaml
     plugins:
       storage_backend: s3
       search_backend: typesense
     ```

3. **Isolation and Dependency Management**:
   - Each plugin will operate in isolation, with separate configuration and dependency management. We will ensure that plugins do not interfere with each other by using virtual environments or dependency sandboxing where necessary.

4. **Dynamic Integration**:
   - Plugins can be added or removed at runtime without requiring a restart. This will be facilitated by **Pluggy**’s hook system or by dynamically loading new entry points via **Stevedore**.

5. **Standardized Plugin Interface**:
   - A common plugin interface will be provided to ensure that all plugins (e.g., for search or storage) implement the required methods and interact with the core system in a predictable manner. This will ensure that plugins are easily swappable.

6. **Lifecycle Management**:
   - We will incorporate lifecycle management for plugins, allowing plugins to be initialized, updated, and gracefully shut down as necessary.

## Examples and Interactions

1. **Adding a New Search Plugin**:
   - A developer writes a plugin for **Typesense** and registers it through the appropriate plugin hook:
     ```python
     @hookimpl
     def get_search_backend() -> TypesenseSearchBackend:
         return TypesenseSearchBackend()
     ```
   - The plugin is installed and activated via the plugin configuration. Abilian SBE now uses **Typesense** for search without modifying the core code.

2. **Switching Storage Backends**:
   - An administrator switches from a local file system storage backend to an **S3-compatible** storage system by updating the configuration file. The plugin system ensures the correct storage plugin is loaded, and all operations are routed through the new backend.

## Consequences

### Benefits

- **Extensibility**: The plugin system will allow Abilian SBE to grow and evolve with new functionalities without requiring core code changes.
- **Modularity**: By decoupling services such as search and storage, the system will be easier to maintain and extend.
- **Isolation**: Plugins will operate in isolation, ensuring that errors or failures in one plugin do not impact others or the core system.
- **Dynamic Customization**: Plugins can be added, removed, or updated at runtime, providing maximum flexibility for customization and deployment.

### Drawbacks

- **Increased Complexity**: Introducing a plugin system adds complexity, particularly in terms of managing dependencies and ensuring compatibility between plugins.
- **Testing Overhead**: Each plugin will need to be tested thoroughly to ensure it does not break the core system or cause conflicts with other plugins.

## Lessons Learned

Plugin systems such as those in **Datasette** and **Pytest** have shown the value of modular, pluggable architectures in increasing the flexibility and maintainability of a system. However, they also demonstrate the need for careful attention to isolation and dependency management to avoid conflicts and instability.

## Action Items

1. Develop the core plugin system using **Pluggy**.
2. Define hooks for pluggable services such as **search** and **storage**.
3. Implement **Stevedore** for plugin discovery via **setuptools entry points**.
4. Test the system with multiple plugins and ensure isolation and performance.
5. Provide detailed documentation on how to create and manage plugins.

## Alternatives

- **Hardcoded Services**: Continuing with hardcoded services would simplify development but limit flexibility and extensibility in the long term.
- **Custom Plugin System**: Building a custom plugin system from scratch could offer more control but would require significantly more effort compared to adopting existing libraries.

## Prior Art

- **Datasette**: Uses **Pluggy** for extensibility, demonstrating how a plugin architecture can support a highly modular system.
- **Pytest**: Implements a plugin architecture with hooks to extend and modify core functionality.
- **Trac**: Uses a comprehensive plugin system to manage its modular components, allowing deep customization. See: https://trac.edgewall.org/wiki/TracDev/ComponentArchitecture
- **Beets**: See https://beets.readthedocs.io/en/stable/dev/plugins.html
- ...


## Future Work

- Extend the plugin architecture to handle additional services such as authentication, notifications, or analytics.

## Related

- ADR 007: Pluggable Search Index
- ADR 005: Pluggable Blob Storage

## References

- [Plugins on lab.abilian.com](https://lab.abilian.com/Tech/Programming%20Techniques/Plugins/)
- This includes (list not exhaustive):
  - **Pluggy**: https://pluggy.readthedocs.io/
  - **Stevedore**: https://docs.openstack.org/stevedore/latest/
  - **Yapsy**: https://yapsy.readthedocs.io/
  - **Zope Component Architecture**: https://zope.readthedocs.io/en/latest/
  - **Trac Component Architecture**: https://trac.edgewall.org/wiki/TracDev/ComponentArchitecture
  - **Setuptools Entry Points**: https://setuptools.pypa.io/en/latest/userguide/entry_point.html
