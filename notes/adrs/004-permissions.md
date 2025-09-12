# Simplifying Permission Management in Abilian SBE

Status: Draft

## Introduction

This ADR proposes the simplification and refactoring of the permission management system in **Abilian SBE**. The current system has grown complex and difficult to maintain, making it challenging to manage permissions across various roles, resources, and use cases. This document outlines the rationale, goals, and proposed design for simplifying the permission management model to improve usability, maintainability, and scalability.

## Summary

The current permission management system in Abilian SBE is tightly coupled to the platform's core logic, making it inflexible and difficult to scale as new features and user roles are introduced. We propose refactoring the permission system to adopt a simpler, more modular approach that uses **Role-Based Access Control (RBAC)** and potentially **OAuth 2.0 scopes** to grant users and services specific levels of access based on their roles and activities.

## Status

Proposed

## Context and Goals

### Context

As Abilian SBE evolves, the current permission model has become increasingly difficult to manage, particularly as the platform integrates new features and third-party services. Permissions are currently handled in an ad-hoc manner, with many hardcoded checks throughout the codebase. This makes it difficult to extend or modify permission rules, especially for enterprise or government environments that require fine-grained access control and compliance with security standards.

Furthermore, as more services are integrated (e.g., cloud storage, social features, third-party applications), the need for a flexible, scalable permission model becomes critical to the platform's ability to manage user and service interactions securely.

### Goals

- **Simplification**: Refactor the existing permission system to simplify how permissions are assigned, managed, and validated.
- **Scalability**: Ensure the new model is scalable and can handle enterprise-level workloads, including multi-tenant environments.
- **Interoperability**: Align the system with industry standards such as **OAuth 2.0** scopes to enable secure API-based permissions for third-party services.
- **Security**: Maintain strict control over access to sensitive resources, with fine-grained permissions for different roles and services.
- **Flexibility**: Make it easier to extend the system as new roles and permissions are required, reducing the friction for future development.

## Tenets

- **Modularity**: The permission system should be modular, making it easy to update and extend without affecting the rest of the codebase.
- **Principle of Least Privilege**: Users and services should only be granted the minimum necessary permissions.
- **Consistency**: Permissions should be managed in a consistent way across all components of Abilian SBE, including both user-facing features and API interactions.

## Decision

We propose implementing a **Role-Based Access Control (RBAC)** system with optional support for **OAuth 2.0 scopes** to handle permissions for users and services in Abilian SBE. This approach will involve the following key changes:

- **Roles** will define a set of permissions that can be assigned to users or groups.
- **Permissions** will be defined at a resource level, specifying actions such as read, write, delete, etc.
- **Scopes** (optional) will be used to manage API access for third-party services, allowing them to interact with the platform with restricted permissions.
- **Role Hierarchy** may be implemented to allow more complex roles to inherit permissions from simpler roles.

## Detailed Design

1. **RBAC System**:
   - A new RBAC system will be designed where roles (e.g., admin, editor, viewer) are mapped to specific permissions for resources (e.g., documents, user profiles).
   - Each role will have a list of actions (create, read, update, delete) it is allowed to perform on specific resources.
   - Permissions will be checked dynamically at runtime when users or services attempt to perform actions within the system.
   - Administrators will be able to assign roles to users or groups through an administration interface.

2. **OAuth 2.0 Scopes for API Access**:
   - For API-based access, OAuth 2.0 scopes will be used to manage which API endpoints and resources a third-party service can access.
   - Scopes will be assigned when access tokens are generated, and each token will be checked against the API’s required scopes during requests.
   - Example scopes: `read:documents`, `write:profiles`, `manage:users`.

3. **Permission Assignment Interface**:
   - A graphical user interface will be developed to allow administrators to assign and revoke roles for users and groups.
   - This interface will provide visibility into which permissions are associated with each role, making it easier to manage permission sets for large user bases.

4. **Role Hierarchy**:
   - If required, roles can be structured hierarchically. For example, an "admin" role might inherit all permissions from the "editor" and "viewer" roles, making it easier to manage complex permission structures.

5. **Resource-Specific Permissions**:
   - Each resource type (e.g., documents, profiles, projects) will have associated permissions that define what actions can be performed on that resource.
   - These permissions will be linked to the roles, ensuring that only users or services with the correct roles can access or modify the resource.

## Examples and Interactions

1. **User with Role-Based Permissions**:
   - A user with the "editor" role is allowed to create and update documents but cannot delete them.
   - When the user attempts to delete a document, the system checks their role and denies the request.

2. **Service with OAuth Scopes**:
   - A third-party service is granted the `read:documents` and `write:profiles` scopes.
   - The service is able to retrieve documents from the API but is prevented from creating or deleting them. Similarly, it can update user profiles but cannot access sensitive admin functionality.

## Consequences

### Benefits

- **Simplicity**: The RBAC system will be simpler to manage, reducing the need for hardcoded permission checks scattered across the codebase.
- **Scalability**: The model will scale more easily as new features, roles, and resources are added, providing flexibility for enterprise or multi-tenant environments.
- **Security**: Permissions will be centrally managed, ensuring consistent enforcement of security policies across all features and APIs.
- **Modularity**: By using OAuth 2.0 scopes for API-based access, the system will be more modular, making it easier to integrate with external services.

### Drawbacks

- **Implementation Complexity**: Refactoring the current system will require careful planning to avoid breaking existing functionality.
- **Learning Curve**: Developers and administrators will need to familiarize themselves with the new RBAC and OAuth 2.0 scope models.

## Lessons Learned

Previous attempts to manually manage permissions for various features have led to complex, error-prone code that is difficult to extend. Moving to an RBAC model will centralize permission management, making it easier to extend and maintain.

## Action Items

### Strategic Priorities

1. Develop the RBAC system with role-based permissions for key resources (documents, users, projects).
2. Implement OAuth 2.0 scope-based access control for API endpoints.
3. Build a management interface for role and permission assignment.
4. Test the system with different user and role configurations to ensure proper permission enforcement.

## Alternatives

- **Flat Permissions Model**: A simpler permissions model could be considered, but this would lack the flexibility and scalability needed for enterprise use cases.
- **Custom Permissions Framework**: A custom-built permissions system could be created, but this would result in higher development and maintenance costs without providing the benefits of standard RBAC and OAuth 2.0 scopes.

## Prior Art

Platforms like **GitLab** and **Nextcloud** have successfully implemented RBAC and OAuth 2.0 scopes to manage permissions for both users and third-party services. These examples show how well these models can scale and provide flexibility in real-world applications.

## Unresolved Questions

- How should the system handle permissions conflicts when a user has multiple roles with overlapping permissions?
- Will certain actions (e.g., sensitive admin actions) require special roles that cannot be delegated?

## Future Work

- Investigate the possibility of adding **attribute-based access control (ABAC)** in the future for more complex permission models.
- Consider integrating **Multi-Factor Authentication (MFA)** for additional security in high-risk environments.

## Related

- ADR 001: OAuth 2.0 and RBAC for API Authorization
- ADR 002: SCIM Integration for User Provisioning
- ADR 003: RBAC

## References


## Notes

- Ensure the permission management system is extensible, allowing for easy addition of new roles, resources, and permissions as the platform evolves.

## Appendix

### Example role and permission configurations for common use cases (admin, editor, viewer).

Here are example role and permission configurations for common use cases such as **admin**, **editor**, and **viewer**. These examples show how roles can be assigned to users and the specific permissions that each role grants for different resources within **Abilian SBE**.

### Example Role and Permission Configurations


#### Admin Role

The **admin** role has full access to all resources in the system, including administrative functions like user management and system configuration.

**Role: Admin**
- **Permissions**:
  - **Users**:
    - Create users
    - Read users
    - Update users
    - Delete users
  - **Documents**:
    - Create documents
    - Read documents
    - Update documents
    - Delete documents
  - **Projects**:
    - Create projects
    - Read projects
    - Update projects
    - Delete projects
  - **System**:
    - Configure system settings
    - Manage permissions
    - View audit logs
    - Backup and restore data
  - **API**:
    - Full access to all API endpoints, including admin functions

#### Editor Role

The **editor** role has permission to create, read, and modify documents and projects, but lacks the ability to delete sensitive resources or access administrative functionality.

**Role: Editor**
- **Permissions**:
  - **Users**:
    - Read users (limited to viewing profiles and basic info)
  - **Documents**:
    - Create documents
    - Read documents
    - Update documents
    - Cannot delete documents
  - **Projects**:
    - Create projects
    - Read projects
    - Update projects
    - Cannot delete projects
  - **System**:
    - No system-level access or configuration permissions
  - **API**:
    - Access limited to document and project management APIs
    - Example API scopes: `read:documents`, `write:documents`, `read:projects`, `write:projects`

#### Viewer Role

The **viewer** role has read-only access to resources, allowing users to view documents and project details, but not modify or delete them.

**Role: Viewer**
- **Permissions**:
  - **Users**:
    - Read users (view profile info, no editing)
  - **Documents**:
    - Read documents only (cannot create, update, or delete)
  - **Projects**:
    - Read project details (cannot create, update, or delete)
  - **System**:
    - No system-level access
  - **API**:
    - Access limited to read-only API operations
    - Example API scopes: `read:documents`, `read:projects`

#### Detailed Permission Matrix

The following table shows a matrix that describes which actions are available to each role:

| **Resource**       | **Action**        | **Admin** | **Editor** | **Viewer** |
|--------------------|-------------------|-----------|------------|------------|
| **Users**          | Create            | Yes       | No         | No         |
|                    | Read              | Yes       | Yes        | Yes        |
|                    | Update            | Yes       | No         | No         |
|                    | Delete            | Yes       | No         | No         |
| **Documents**      | Create            | Yes       | Yes        | No         |
|                    | Read              | Yes       | Yes        | Yes        |
|                    | Update            | Yes       | Yes        | No         |
|                    | Delete            | Yes       | No         | No         |
| **Projects**       | Create            | Yes       | Yes        | No         |
|                    | Read              | Yes       | Yes        | Yes        |
|                    | Update            | Yes       | Yes        | No         |
|                    | Delete            | Yes       | No         | No         |
| **System Settings**| Configure         | Yes       | No         | No         |
| **Audit Logs**     | View              | Yes       | No         | No         |
| **Permissions**    | Manage            | Yes       | No         | No         |
| **API Access**     | Full Access       | Yes       | No         | No         |
|                    | Limited Access    | No        | Yes        | Yes        |


#### Role Assignment Examples

1. **Admin User**:
   - Assigned the "Admin" role.
   - Has full access to user management, document creation and deletion, system configuration, and API calls.

2. **Content Manager** (Editor role):
   - Assigned the "Editor" role.
   - Can create and update content (documents and projects), but cannot delete documents or access admin-level functionality.

3. **Read-Only User**:
   - Assigned the "Viewer" role.
   - Can view content (documents and projects) but cannot make any changes or access sensitive user data.


#### API Scopes Example

Here’s how OAuth 2.0 scopes would be mapped to these roles for API access:

1. **Admin Scope**:
   - API Scopes: `admin:all`, `write:documents`, `read:projects`, `manage:users`
   - Access: Full API access, including admin and system settings endpoints.

2. **Editor Scope**:
   - API Scopes: `write:documents`, `read:projects`, `write:projects`
   - Access: Limited to document and project CRUD (Create, Read, Update, Delete) operations but no administrative privileges.

3. **Viewer Scope**:
   - API Scopes: `read:documents`, `read:projects`
   - Access: Read-only access to documents and projects via API.
