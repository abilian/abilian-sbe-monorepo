# ADR: Continued Support for SQLite for Testing Environments in Abilian SBE

**Status**: Accepted

## Introduction
This ADR explains the rationale for maintaining **SQLite** support exclusively for **testing and development** purposes in Abilian SBE. While PostgreSQL and MariaDB are adopted as the tier-one databases for production deployments, SQLite offers simplicity, ease of setup, and minimal overhead, making it an ideal choice for local testing and automated test suites.

## Summary
SQLite will remain a supported database backend for **testing** and **local development** but will **not** be recommended or supported for production environments. Its lightweight nature and lack of configuration requirements make it an excellent tool for automated tests and developer workflows.

## Context and Goals

### Context
Abilian SBE currently supports multiple relational database systems, including SQLite, MySQL, and PostgreSQL. With the adoption of **PostgreSQL** and **MariaDB** as tier-one databases for production (see related ADRs), there is a need to clarify SQLite’s role within the system.

SQLite is widely used in development and testing workflows due to its simplicity, file-based storage, and zero-configuration nature. It eliminates the need for managing database servers in test environments, speeding up test execution and simplifying developer onboarding.

While SQLite lacks the scalability and advanced features required for production, its advantages for testing make it a valuable tool that should continue to be supported.

### Goals
1. **Testing Efficiency**: Use SQLite for lightweight and fast testing without requiring a database server.
2. **Developer Productivity**: Allow developers to set up local testing environments quickly and easily.
3. **Isolation**: Use a self-contained, file-based database to avoid external dependencies in CI/CD pipelines and local tests.
4. **Cost Efficiency**: Avoid the overhead of configuring and managing PostgreSQL or MariaDB for automated tests.

## Tenets
- **Simplicity**: SQLite requires no configuration or external dependencies, making it ideal for tests.
- **Speed**: SQLite offers fast setup and teardown times for automated test suites.
- **Isolation**: SQLite’s file-based nature ensures tests remain isolated and reproducible.
- **Consistency**: Developers and CI/CD systems can run tests reliably without external infrastructure.

## Decision
We will retain **SQLite** as the default database backend for **testing** and **local development** in Abilian SBE. SQLite will not be supported or recommended for production environments.

### Why SQLite for Testing?
1. **Zero Configuration**:
   - SQLite runs as a single library with file-based storage, requiring no database server, user management, or configuration.

2. **Speed**:
   - Tests execute faster with SQLite compared to server-based databases.
   - Database creation and teardown are near-instantaneous, which is ideal for unit tests and CI/CD pipelines.

3. **Self-Contained**:
   - SQLite operates as an embedded database, ensuring test environments remain isolated and reproducible.

4. **Ease of Use for Developers**:
   - Developers can run tests locally without installing or managing PostgreSQL or MariaDB.

5. **CI/CD Integration**:
   - SQLite simplifies test infrastructure, reducing overhead in CI/CD pipelines.

## Detailed Design

### Use Cases for SQLite
1. **Unit Tests**:
   - SQLite will serve as the default backend for running fast, isolated unit tests during development and CI/CD workflows.

2. **Local Development**:
   - Developers can use SQLite for quick local testing without needing a database server.

3. **Integration Tests**:
   - For isolated integration tests that do not rely on advanced database features, SQLite can provide lightweight, consistent behavior.

### Production Considerations
- SQLite will be **explicitly marked as unsupported for production** due to its limitations:
  - Lack of scalability for concurrent writes and large datasets.
  - Limited support for advanced features like JSONB, full-text search, and complex queries.
  - Potential issues with data integrity in multi-process environments.

### Configuration
The default testing configuration will use SQLite:
```yaml
database:
  backend: sqlite
  sqlite:
    filename: ":memory:"
```

For development, a local SQLite file can be used:
```yaml
database:
  backend: sqlite
  sqlite:
    filename: "./dev.db"
```

## Examples and Interactions

1. **In-Memory SQLite for Tests**
   Run unit tests with an ephemeral in-memory database:
   ```python
   from sqlalchemy import create_engine

   engine = create_engine("sqlite:///:memory:")
   # Initialize schema, run tests, and tear down automatically.
   ```

2. **Local Development Database**
   Use a file-based SQLite database for quick development:
   ```python
   engine = create_engine("sqlite:///local_dev.db")
   ```

3. **CI/CD Pipeline Example**
   Integrate SQLite into a CI pipeline for testing:
   ```yaml
   steps:
     - name: Run Unit Tests
       run: pytest --db-backend=sqlite
   ```

## Consequences

### Benefits
- **Simplified Testing**: No need for database servers in test environments, reducing setup time and resource consumption.
- **Faster Tests**: SQLite’s in-memory mode ensures rapid execution of test cases.
- **Developer Onboarding**: Developers can start testing without additional configuration or installations.
- **CI/CD Efficiency**: Reduces infrastructure complexity in CI/CD pipelines.

### Drawbacks
- **Feature Limitations**: SQLite does not support advanced features like JSONB, full-text search, or window functions used in PostgreSQL/MariaDB.
- **Behavior Differences**: Minor inconsistencies may arise between SQLite and production databases (e.g., stricter SQL compliance in PostgreSQL).
- **Not Suitable for Integration Tests with Complex Queries**: Some database-specific behaviors may require PostgreSQL or MariaDB for more robust integration testing.

## Lessons Learned
SQLite has consistently provided value as a lightweight, low-maintenance database for testing. However, its limitations make it unsuitable for production workloads. Retaining SQLite for testing ensures efficiency while avoiding unnecessary overhead.

## Action Items
1. Update Abilian SBE’s documentation to clarify SQLite’s role as a **testing-only** database.
2. Update default test configurations to use SQLite in in-memory mode.
3. Add warnings in documentation and logs when SQLite is used in production-like environments.
4. Ensure PostgreSQL and MariaDB remain the focus for production deployments.

## Alternatives
- **PostgreSQL for Testing**:
   - Running PostgreSQL in test environments ensures feature parity with production but increases setup complexity and slows down tests.

- **MariaDB for Testing**:
   - Similar to PostgreSQL, MariaDB introduces resource overhead for local tests and CI pipelines.

- **SQLite for Production**:
   - Not a viable option due to scalability and concurrency limitations.

## Unresolved Questions
- Should we include optional support for PostgreSQL or MariaDB-based testing in CI/CD pipelines for specific integration tests?

## Future Work
- Explore using PostgreSQL or MariaDB in automated integration tests where feature parity is critical.
- Provide tools for easy switching between SQLite and production databases for advanced testing workflows.

## Related
- ADR 009: Adoption of PostgreSQL as a Tier-One Supported Database
- ADR 010: Adoption of MariaDB as a Tier-One Supported Database

## References
- **SQLite Documentation**: https://sqlite.org/docs.html
- **Testing with SQLite**: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html
