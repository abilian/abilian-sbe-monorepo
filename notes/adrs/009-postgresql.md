# ADR: Adoption of PostgreSQL as a Tier-One Supported Database for Abilian SBE

**Status**: Accepted

## Introduction
This ADR proposes adopting **PostgreSQL** as one of the **tier-one supported databases** for **Abilian SBE**. PostgreSQL will serve as a primary database choice alongside MariaDB (to be addressed in a separate ADR), ensuring Abilian SBE supports modern, scalable, and open-source relational database systems.

## Summary
PostgreSQL will be adopted as a **tier-one supported database**, meaning it will receive first-class support, testing, and documentation in Abilian SBE. PostgreSQL's feature set, scalability, and adherence to modern SQL standards make it a robust choice for production environments and future growth.

## Context and Goals

### Context
Abilian SBE currently supports multiple relational database systems, including SQLite and MySQL. However, to better align with modern use cases, scalability requirements, and advanced database features, we aim to prioritize two database systems: PostgreSQL and MariaDB.

PostgreSQL has become the preferred choice for many open-source and enterprise-grade applications due to its advanced capabilities such as **JSONB storage**, **full-text search**, **window functions**, and extensibility. This ADR focuses on formally adopting PostgreSQL as a **tier-one supported database** for Abilian SBE.

### Goals
1. **Tier-One Support**: Ensure PostgreSQL is fully supported, tested, and documented in Abilian SBE.
2. **Advanced Features**: Leverage PostgreSQL’s capabilities such as JSONB, full-text search, and advanced indexing.
3. **Scalability**: Provide a robust and scalable solution for multi-tenant, enterprise-grade deployments.
4. **Compatibility**: Maintain SQLite for development/testing while ensuring seamless PostgreSQL deployment for production.

## Tenets
- **Reliability**: PostgreSQL must offer robust data integrity, ACID compliance, and high availability for production.
- **Performance**: PostgreSQL will serve complex queries efficiently while scaling for larger datasets.
- **Extensibility**: PostgreSQL’s features like JSONB, custom extensions, and advanced indexing will enhance Abilian SBE’s capabilities.
- **Compliance**: PostgreSQL’s adherence to SQL standards ensures compatibility and portability.

## Decision
We will adopt **PostgreSQL** as a **tier-one supported database** for Abilian SBE. PostgreSQL will be supported alongside MariaDB, with equal focus on stability, features, and performance.

### Why PostgreSQL?
1. **Advanced Features**:
   - **JSONB Support**: Enables semi-structured data storage, reducing the need for external NoSQL solutions.
   - **Full-Text Search**: Integrated full-text search capabilities without external dependencies.
   - **Window Functions and CTEs**: Simplifies complex queries for analytics and reporting.
   - **Advanced Indexing**: Supports GIN, BRIN, and GiST indexes for optimized query performance.

2. **Scalability and Performance**:
   - Multi-Version Concurrency Control (MVCC) ensures fast, concurrent reads and writes.
   - Optimized query planner for efficient handling of large datasets.
   - Vertical and horizontal scalability to support growing workloads.

3. **Extensibility**:
   - PostgreSQL supports user-defined functions, procedural languages (e.g., PL/pgSQL), and extensions like **PostGIS** for geospatial data.
   - Native support for custom data types and indexing strategies.

4. **Open-Source and Community-Driven**:
   - PostgreSQL is a mature, open-source solution with an active and supportive community.

## Detailed Design

### Database Configuration
1. PostgreSQL will become a **recommended option** in Abilian SBE’s configuration files.
2. Default production settings will prioritize PostgreSQL for new deployments.
3. Example configuration:
   ```yaml
   database:
     backend: postgresql
     postgresql:
       host: localhost
       port: 5432
       database: abilian_sbe
       username: sbe_user
       password: secure_password
   ```

### PostgreSQL-Specific Features
- Enable **JSONB** columns for semi-structured data such as user settings or metadata.
- Implement **full-text search** features for indexed document content.
- Optimize query performance using **GIN** and **BRIN** indexes where applicable.

### Compatibility
- SQLite will remain supported for local development and lightweight testing environments.
- MariaDB (see upcoming ADR) will serve as the other **tier-one supported database**.
- Existing deployments using MySQL will be provided with migration scripts for PostgreSQL compatibility.

## Examples and Interactions

1. **JSONB Example**
   Storing semi-structured user preferences:
   ```sql
   CREATE TABLE user_settings (
       user_id SERIAL PRIMARY KEY,
       preferences JSONB
   );

   INSERT INTO user_settings (preferences) VALUES ('{"theme": "dark", "notifications": {"email": true}}');
   ```

2. **Full-Text Search**
   Example of querying indexed text content:
   ```sql
   CREATE TABLE documents (
       id SERIAL PRIMARY KEY,
       content TEXT
   );

   CREATE INDEX idx_content_search ON documents USING gin(to_tsvector('english', content));

   SELECT * FROM documents WHERE to_tsvector('english', content) @@ to_tsquery('search_term');
   ```

3. **Complex Query with Window Functions**
   Retrieve user login counts using window functions:
   ```sql
   SELECT user_id, COUNT(*) OVER (PARTITION BY user_id) AS login_count
   FROM user_logins;
   ```

## Consequences

### Benefits
- **Advanced Features**: PostgreSQL’s feature set, including JSONB and full-text search, enhances Abilian SBE’s capabilities.
- **Performance**: Improved scalability and query optimization for enterprise-grade deployments.
- **Extensibility**: Support for extensions and customizations provides flexibility for diverse use cases.
- **Long-Term Viability**: PostgreSQL’s maturity and open-source nature ensure long-term support and growth.

### Drawbacks
- **Migration Effort**: Existing MySQL-based deployments will need to migrate their data.
- **Resource Consumption**: PostgreSQL may require more memory and storage compared to lightweight options like SQLite.

## Lessons Learned
Past experience with MySQL and SQLite has highlighted the limitations of these systems for modern, enterprise-grade requirements. PostgreSQL’s robust feature set and scalability make it a natural choice for handling complex, high-volume data in Abilian SBE.

## Action Items
1. Update Abilian SBE to prioritize PostgreSQL as a tier-one supported database.
2. Write migration scripts and tools for MySQL users.
3. Document PostgreSQL installation, setup, and advanced configuration.
4. Optimize database queries and models to leverage PostgreSQL features.

## Alternatives
- **SQLite**: Suitable for development and testing but not scalable for production.
- **MariaDB**: Will be supported as a tier-one database (addressed in a separate ADR).
- **MySQL**: While widely used, it lacks PostgreSQL’s advanced indexing and JSONB support.

## Unresolved Questions
- How will migrations between MySQL and PostgreSQL be handled for legacy installations?
- Should PostgreSQL be the default option in production environments, or remain user-configurable?

## Future Work
- Implement advanced PostgreSQL features such as **table partitioning** and **row-level security** for multi-tenant deployments.
- Explore the use of extensions like **PostGIS** for geospatial data support.

## Related
- ADR XXX: Adoption of MariaDB as a Tier-One Supported Database
- ADR XXX: Database Migration Strategy

## References
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **JSONB and Indexing**: https://www.postgresql.org/docs/current/datatype-json.html
- **PostgreSQL Full-Text Search**: https://www.postgresql.org/docs/current/textsearch.html
