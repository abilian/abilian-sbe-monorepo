# Integrate SCIM for Automated User Provisioning and Management

Status: Draft

## Introduction

This ADR proposes the integration of **System for Cross-domain Identity Management (SCIM)** to automate user provisioning and management within **Abilian SBE**. SCIM is a standard for automating the exchange of user identity information between identity domains or IT systems, which will significantly simplify the process of managing user accounts and groups.

## Summary

The proposed change involves implementing SCIM to automate the provisioning, updating, and deprovisioning of users and groups in Abilian SBE. This will enhance the platform's ability to integrate with external identity providers and directory services, such as **Keycloak**, **Azure AD**, or **LDAP**, and improve the management of user lifecycles in enterprise and government settings, particularly for **La Suite Numérique**.

## Status

Proposed

## Context and Goals

### Context

Currently, user provisioning and deprovisioning in Abilian SBE are handled manually or via custom scripts, which is inefficient and prone to errors. Additionally, managing user information across multiple systems is time-consuming and may lead to inconsistencies, especially in environments with large numbers of users, such as government agencies or enterprise deployments.

Without SCIM, organizations need to manually sync user data, leading to delays and potential security vulnerabilities when users are not provisioned or deactivated promptly.

### Goals

- Automate user and group management by leveraging SCIM 2.0.
- Enable external systems to create, update, and delete users and groups in Abilian SBE automatically.
- Reduce manual errors and increase efficiency in managing users and permissions.
- Improve integration with government and enterprise identity management systems such as **Keycloak**, **Azure AD**, and **LDAP**.

## Tenets

- **Automation**: User provisioning and management must be automated to reduce administrative overhead and improve accuracy.
- **Security**: The integration must ensure that all user data is securely synchronized and that permissions are managed appropriately across systems.
- **Interoperability**: Abilian SBE must seamlessly integrate with existing identity management platforms.
- **Efficiency**: The system must minimize administrative effort and maximize the speed of provisioning and deprovisioning.

## Decision

Abilian SBE will implement **SCIM 2.0** for user provisioning and management. This will enable the platform to:
- Automatically sync user accounts and groups with external identity providers.
- Manage the full user lifecycle, including creation, update, and deletion, as well as group management.
- Ensure that user attributes, roles, and permissions are up-to-date across all systems.

## Detailed Design

1. **SCIM Protocol Support**:
   - Abilian SBE will implement a SCIM 2.0-compliant API endpoint that supports operations for managing users and groups.
   - The API will handle requests for **Create**, **Read**, **Update**, and **Delete** (CRUD) operations on user accounts and groups.

2. **User Provisioning**:
   - External identity providers (IDPs) or systems will send requests to the SCIM endpoint to create or update users in Abilian SBE.
   - User attributes such as name, email, department, and roles will be synced automatically between the IDP and Abilian SBE.
   - Deactivated users in the external system will automatically be deprovisioned in Abilian SBE.

3. **Group Management**:
   - SCIM will also manage user groups, ensuring that any group memberships updated in the external system are reflected in Abilian SBE.
   - Group roles and permissions within Abilian SBE will be updated in real-time based on SCIM data.

4. **Authentication**:
   - Secure authentication methods such as OAuth 2.0 will be used to ensure that only authorized systems can interact with the SCIM API.

5. **Error Handling**:
   - The SCIM API will include detailed error responses and logging to ensure that administrators can resolve issues quickly if the sync fails.

## Examples and Interactions

1. **User Creation**:
   - A new user is added in the external IDP (e.g., Keycloak or Azure AD).
   - A SCIM request is automatically sent to Abilian SBE’s SCIM API, and the user is created in the platform with all the necessary attributes and roles.

2. **User Update**:
   - The external IDP updates the user’s email or department.
   - A SCIM update request is sent to Abilian SBE, which updates the user’s profile accordingly.

3. **User Deprovisioning**:
   - A user is deactivated in the external IDP.
   - SCIM sends a delete request to Abilian SBE, automatically removing the user from the platform.

## Consequences

### Benefits

- **Automation**: Reduces manual labor in managing user accounts and groups.
- **Consistency**: Ensures that user data is consistently managed across multiple systems.
- **Scalability**: SCIM is designed to handle large numbers of users and groups, making it ideal for enterprise and government deployments.
- **Security**: Ensures timely deprovisioning of users, minimizing security risks associated with inactive accounts.

### Drawbacks

- **Implementation Complexity**: Integrating SCIM requires setting up the necessary API endpoints and testing for all possible user lifecycle scenarios.
- **Dependency on External Systems**: Abilian SBE will rely on the external IDP to manage user data, which could introduce issues if the IDP becomes unavailable or fails to sync properly.

## Lessons Learned

Previous attempts at integrating external identity providers manually have shown that manual synchronization is error-prone and inefficient. SCIM solves these problems by offering a standardized, automated approach.

## Action Items

### Strategic Priorities

1. Research and select a SCIM 2.0 library or framework compatible with Abilian SBE’s existing architecture (e.g., **python-scim**).
2. Develop and implement SCIM 2.0-compliant API endpoints for user and group management.
3. Test the integration with commonly used IDPs (e.g., Keycloak, Azure AD).
4. Implement detailed logging and error handling to ensure smooth operation.

## Alternatives

- **Manual Syncing**: Continue using the existing custom scripts or manual processes for syncing users, but this introduces more potential for error and does not scale well.
- **Custom API for User Provisioning**: Build a custom API instead of SCIM, but this would lack the flexibility and standardization of SCIM, making future integrations more difficult.

## Prior Art

Previous discussions about automating user provisioning led to attempts at creating a custom solution, but the lack of standardization resulted in inconsistent behavior across different environments. SCIM provides a well-established solution adopted by many enterprise systems.

## Unresolved Questions

- How will the platform handle partial sync failures (e.g., when only some attributes are updated successfully)?
- What are the fallback mechanisms if the external IDP is temporarily unavailable?

## Future Work

- Investigate adding support for additional SCIM features, such as advanced user schema management or extended attributes.
- Consider integrating SCIM with other external systems that require user data (e.g., CRM or ERP systems).

## Related

- ADR 001: OIDC and OAuth 2.0 Integration for Authentication
- ADR 003: Role-Based Access Control (RBAC) and OAuth 2.0 Scopes

## References

- **SCIM 2.0 Specification**: https://tools.ietf.org/html/rfc7644
- **SCIM Overview**: https://scim.cloud/
- Flask demo: https://github.com/oktadev/okta-scim-flask-example

## Notes

- Ensure that the SCIM implementation follows security best practices, including proper authentication, validation, and logging.
- SCIM is an open standard, which aligns with Abilian SBE’s principle of supporting interoperability and open protocols.

## Appendix

- SCIM integration diagrams and flowcharts for user lifecycle management (TODO).
- Example SCIM requests for user creation, update, and deletion (TODO).
