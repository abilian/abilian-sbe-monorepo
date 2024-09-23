# Integrate OpenID Connect (OIDC) and OAuth 2.0 for Authentication and Authorization

Status: Draft

## Introduction

This ADR addresses the integration of **OpenID Connect (OIDC)** and **OAuth 2.0** for authentication and authorization in **Abilian SBE**. OIDC is an identity layer built on top of OAuth 2.0 and allows the platform to authenticate users securely, leveraging industry standards. OAuth 2.0 will handle authorization, enabling third-party services to interact with the platform without exposing user credentials.

## Summary

We propose to integrate OpenID Connect (OIDC) and OAuth 2.0 into Abilian SBE to provide secure, scalable, and standard-based authentication and authorization. This will replace the current custom authentication mechanisms, enhancing security and interoperability, especially for clients integrating Abilian SBE into multi-tenant systems or government infrastructures like **La Suite Numérique**.

## Status

Proposed

## Context and Goals

### Context

Abilian SBE currently uses a custom-built authentication and authorization system that lacks integration with external identity providers (IDPs) like Keycloak, FranceConnect, or Google. This limits interoperability, especially when deploying the platform in environments requiring modern standards like OIDC and OAuth 2.0.

### Goals

- Enable OIDC for user authentication, supporting external IDPs such as Keycloak and FranceConnect.
- Implement OAuth 2.0 to manage token-based access control and API security.
- Ensure the solution aligns with **La Suite Numérique** and other government initiatives.
- Enhance security by removing the need for the platform to handle user credentials directly.

## Tenets

- **Security First**: User credentials must be securely handled via industry standards, reducing the risk of breaches.
- **Interoperability**: Enable seamless integration with external systems, both government and enterprise.
- **Compliance**: Align with security protocols such as GDPR and government authentication requirements (e.g., FranceConnect).

## Decision

We will integrate OIDC for authentication and OAuth 2.0 for authorization. Users will be authenticated via third-party identity providers, while API access will be managed using OAuth 2.0 tokens.

## Detailed Design

1. **OIDC Integration**:
   - Abilian SBE will allow users to authenticate through OIDC-compliant identity providers.
   - An OIDC library (e.g., **python-oauthlib** or **authlib**) will be integrated into the authentication flow.
   - Login and logout mechanisms will be delegated to external IDPs (e.g., Keycloak or FranceConnect).
   - User profile data will be fetched from IDPs and linked to Abilian SBE's internal user management system.

2. **OAuth 2.0 Implementation**:
   - OAuth 2.0 will be used to authorize third-party applications or services.
   - Access and refresh tokens will be issued for API access, allowing users or services to interact with Abilian SBE’s resources.
   - Role-based access control (RBAC) will be implemented using OAuth 2.0 scopes to grant or restrict access to specific API endpoints.

3. **Token Storage**:
   - Tokens will be stored securely in the database, with appropriate encryption.
   - OAuth tokens will be validated on each request to ensure session integrity.

4. **SSO Support**:
   - Single Sign-On (SSO) will be supported for environments using a centralized authentication service.

## Examples and Interactions

1. **Authentication Flow**:
   - A user attempting to log in to Abilian SBE is redirected to the external IDP (e.g., Keycloak).
   - The IDP handles the authentication and redirects the user back to Abilian SBE with an ID token.
   - The platform verifies the token, retrieves user profile information, and logs the user in.

2. **Authorization Flow**:
   - A third-party service requests access to Abilian SBE resources on behalf of the user.
   - OAuth 2.0 access tokens are issued to the service, allowing it to interact with the platform’s API while respecting the user's permissions.

## Consequences

### Benefits

- **Increased Security**: No need for Abilian SBE to store user credentials, reducing the attack surface.
- **Interoperability**: Seamless integration with external IDPs (Keycloak, FranceConnect, etc.).
- **Scalability**: OAuth 2.0 enables scalable API authorization with fine-grained control.
- **Compliance**: Aligns with industry standards and regulatory requirements (e.g., GDPR).

### Drawbacks

- **Implementation Complexity**: Integrating OIDC and OAuth 2.0 will require refactoring the current authentication system.
- **Learning Curve**: Administrators and developers need to understand OAuth 2.0 flows and OIDC configurations.

## Lessons Learned

In previous attempts to integrate third-party authentication systems, we encountered issues with token validation and user profile synchronization. This design proposal accounts for those challenges by standardizing the integration process using well-supported libraries.

## Action Items

### Strategic Priorities
1. Research and select an appropriate OAuth 2.0 and OIDC library (e.g., **Authlib**).
2. Develop OIDC and OAuth 2.0 workflows.
3. Configure and test integration with Keycloak and FranceConnect.
4. Implement secure token storage and validation.

## Alternatives

- **Custom OAuth-like Implementation**: Creating a custom token-based authentication system was considered, but it would not provide the same level of security and interoperability as industry standards.
- **Third-party OAuth Services**: We considered relying entirely on third-party OAuth services (e.g., AWS Cognito), but this would reduce the platform’s flexibility and autonomy.

## Prior Art

Previous discussions within the team have indicated a need to improve authentication security. Other open-source platforms like **Nextcloud** and **Mastodon** have successfully integrated OIDC and OAuth 2.0, offering useful insights into best practices.

## Unresolved Questions

- What fallback mechanisms should be implemented if the external IDP is unavailable?
- How will the platform handle token expiration and refresh cycles?

## Future Work

- Consider extending the authentication system to support **FIDO2/WebAuthn** for passwordless authentication.
- Evaluate additional security features such as **MFA** (Multi-Factor Authentication) or **device trust**.

## Related

TODO

## References

- **OAuth 2.0**: https://oauth.net/2/
- **OpenID Connect**: https://openid.net/connect/
- **Python OAuth Libraries**: https://authlib.org/

## Notes

- The implementation should follow best practices for secure token storage and encryption to protect user data.

## Appendix

- Comparative analysis of OAuth 2.0 and other authentication methods used in enterprise systems (TODO)
- SSO requirements from La Suite Numérique (TBC)
