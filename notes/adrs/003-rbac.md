# Implement Role-Based Access Control (RBAC) and OAuth 2.0 Scopes for API Authorization

Status: Draft

## Introduction

This ADR proposes the implementation of **Role-Based Access Control (RBAC)** and **OAuth 2.0 Scopes** for managing API access and authorization in **Abilian SBE**. By using RBAC and OAuth 2.0 scopes, we can provide fine-grained control over user permissions and ensure that API requests are authorized based on the roles and scopes assigned to users and applications.

## Summary

We propose to implement RBAC in conjunction with **OAuth 2.0 scopes** to manage authorization for API access in Abilian SBE. This will provide a structured and scalable way to assign permissions to users based on their roles, and to grant specific access levels to third-party services or applications that interact with Abilian SBE via its APIs.

## Status

Proposed

## Context and Goals

### Context

Abilian SBE currently lacks a robust, scalable mechanism for controlling fine-grained access to its APIs. The current system relies on basic access control mechanisms that do not allow for the dynamic and granular management of permissions required by modern applications. Additionally, there is no easy way to differentiate between the access levels of different users or services interacting with the platform.

Introducing RBAC with OAuth 2.0 scopes will address these limitations by enabling role-specific access to different parts of the API and allowing third-party applications to request limited access based on predefined scopes. This is especially important for multi-tenant environments and integrations with external systems like **La Suite Numérique**.

### Goals

- Implement RBAC to define user and group roles with associated permissions.
- Use OAuth 2.0 scopes to provide fine-grained access control for third-party applications.
- Enable integration with identity providers (IDPs) that support OAuth 2.0 for scope-based access.
- Ensure compatibility with **La Suite Numérique**’s access management requirements.
- Provide a scalable and flexible access control model to support enterprise-level use cases.

## Tenets

- **Granularity**: Permissions must be fine-grained to provide the necessary control over user and application access.
- **Security**: API access must be controlled securely through token-based authorization.
- **Interoperability**: The implementation must align with OAuth 2.0 standards to ensure compatibility with external systems.
- **Scalability**: The solution must support large-scale deployments and multi-tenant environments.

## Decision

We will implement **RBAC** to manage user roles and permissions and use **OAuth 2.0 scopes** to control API access. Roles will define the actions a user can perform, while scopes will limit the API access available to third-party services or applications.

## Detailed Design

1. **RBAC Implementation**:
   - Roles will be defined for different types of users (e.g., admin, manager, user, guest), and each role will have specific permissions (e.g., read, write, delete) for various resources within Abilian SBE.
   - Roles will be assigned to users either directly or through groups, allowing for easier management of permissions.
   - Permissions will control which API endpoints and operations a user can access.

2. **OAuth 2.0 Scopes**:
   - Scopes will be used to define the level of access that a third-party application or service can request when interacting with Abilian SBE’s APIs.
   - Scopes will be associated with the API resources (e.g., `read:documents`, `write:users`), and applications will request access to these scopes as part of the OAuth authorization flow.
   - Abilian SBE will issue OAuth 2.0 tokens with the relevant scopes, allowing the API to enforce the appropriate access level.

3. **Token Validation**:
   - When a third-party application or user makes an API request, the OAuth 2.0 token will be validated against the roles and scopes associated with the request.
   - The API will check both the user’s role and the scopes embedded in the OAuth token to determine if the request is authorized.

4. **Role and Scope Assignment**:
   - Administrators will assign roles to users and groups, which will automatically grant the relevant permissions.
   - OAuth scopes will be assigned to third-party applications based on the type of access they require, limiting their interaction with the platform to specific endpoints.

5. **Configuration**:
   - A configuration panel will be provided to administrators, allowing them to manage roles, permissions, and OAuth scopes within the platform.

## Examples and Interactions

1. **User Role-Based Access**:
   - A user with the "manager" role has the ability to create, read, and update user profiles but cannot delete them. This is enforced by checking their role against the permissions when they make an API request.

2. **OAuth Scope-Based Access**:
   - A third-party application requests the `read:documents` scope as part of its OAuth 2.0 authorization.
   - The issued access token contains the `read:documents` scope, limiting the application’s access to document read operations and preventing it from modifying or deleting documents.

## Consequences

### Benefits

- **Fine-Grained Control**: RBAC and OAuth scopes enable fine-grained access control, ensuring that users and applications have only the permissions they need.
- **Scalability**: RBAC supports enterprise-level environments where managing permissions for large numbers of users and applications is necessary.
- **Security**: OAuth 2.0 scopes restrict third-party applications to specific areas of the API, reducing the risk of over-permissioned access.
- **Interoperability**: The use of OAuth 2.0 scopes aligns with industry standards, ensuring compatibility with external identity providers and systems.

### Drawbacks

- **Complexity**: Implementing RBAC and OAuth 2.0 scopes adds complexity to the authorization logic, particularly for administrators managing multiple roles and permissions.
- **Management Overhead**: The system requires ongoing management to ensure that roles and scopes are assigned correctly and that permissions remain up to date.

## Lessons Learned

Previous experiences with hardcoded or static permission systems in other platforms have shown that they do not scale well in multi-tenant environments or when supporting third-party integrations. Using RBAC with OAuth scopes provides the necessary flexibility and granularity for managing access in modern applications.

## Action Items

### Strategic Priorities

1. Define roles and permissions based on common use cases (e.g., admin, manager, user).
2. Implement OAuth 2.0 scopes for API endpoints and map them to relevant user roles.
3. Develop an interface for administrators to manage roles, permissions, and scopes.
4. Test the implementation with external identity providers that support OAuth 2.0.

## Alternatives

- **Flat Permissions Model**: A simpler permissions model could be implemented, where each API endpoint is directly linked to user permissions. However, this would lack the flexibility and scalability of RBAC and OAuth scopes.
- **Custom Token-Based System**: A custom token-based system could be used to manage access, but it would not adhere to standards and would likely introduce complexity in future integrations.

## Prior Art

Other platforms such as **Nextcloud** and **GitLab** have successfully implemented RBAC and OAuth 2.0 scopes to manage fine-grained access control. These platforms provide useful insights into how best to implement these features while maintaining security and flexibility.

## Unresolved Questions

- How should conflicts between roles and scopes be resolved (e.g., a user has a high-level role but a limited scope)?
- How will the system handle role inheritance, where one role inherits permissions from another?

## Future Work

- Extend RBAC and scopes to cover additional areas of the platform, such as integration with external services (e.g., CRM or ERP systems).
- Explore adding **Multi-Factor Authentication (MFA)** for additional security in high-risk environments.

## Related

- ADR 001: OIDC and OAuth 2.0 Integration for Authentication
- ADR 002: SCIM Integration for User Provisioning

## References

- **OAuth 2.0 Scopes**: https://oauth.net/2/scope/
- **RBAC**:
  - https://lab.abilian.com/Tech/Security/RBAC/
  - https://en.wikipedia.org/wiki/Role-based_access_control

## Notes

- The system must be designed with future extensibility in mind, allowing new roles and scopes to be added as the platform evolves.
