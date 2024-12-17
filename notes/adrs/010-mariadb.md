# ADR: Adoption of MariaDB as a Tier-One Supported Database for Abilian SBE

**Status**: Draft

## Introduction
This ADR proposes adopting **MariaDB** as one of the **tier-one supported databases** for **Abilian SBE**, alongside PostgreSQL. MariaDB, as a fork of MySQL, offers high performance, compatibility, and scalability for relational database workloads while maintaining a strong commitment to open-source principles.

## Summary
MariaDB will be adopted as a **tier-one supported database** for Abilian SBE, ensuring compatibility with MySQL-based deployments, while benefiting from MariaDB’s performance improvements, extended features, and active development. MariaDB will provide a robust, scalable option for users alongside PostgreSQL.

## Status
Proposed

## Context and Goals

### Context
Abilian SBE historically supported MySQL as part of its relational database options. MariaDB, a community-driven fork of MySQL, has gained significant adoption due to its open governance, enhanced performance, and feature set. MariaDB retains high compatibility with MySQL while introducing improvements in performance, storage engines, and scalability.

By officially adopting MariaDB as a **tier-one supported database**, we align Abilian SBE with modern database trends, ensure compatibility for existing MySQL users, and provide a performant, reliable option for production deployments.

### Goals
1. **Tier-One Support**: Ensure MariaDB is fully supported, tested, and documented as a primary database option.
2. **Compatibility**: Maintain full compatibility with existing MySQL-based deployments.
3. **Performance**: Leverage MariaDB’s optimizations for query execution and storage engines.
4. **Scalability**: Provide a reliable and scalable relational database for enterprise-grade deployments.
5. **Open-Source Alignment**: Align with community-driven, open-source software principles.

## Tenets
- **Performance**: MariaDB must provide efficient query execution and indexing for typical Abilian SBE workloads.
- **Compatibility**: MariaDB will ensure seamless migration from MySQL with minimal effort.
- **Reliability**: MariaDB must deliver robust data integrity, ACID compliance, and high availability.
- **Community-Driven**: MariaDB’s open governance ensures long-term viability and active development.

## Decision
We will adopt **MariaDB** as a **tier-one supported database** for Abilian SBE, alongside PostgreSQL. MariaDB will receive full testing, documentation, and official support, ensuring it serves as a reliable and performant database option for Abilian SBE users.

### Why MariaDB?
1. **Compatibility with MySQL**:
   - MariaDB maintains drop-in compatibility with MySQL, ensuring a seamless migration path for existing MySQL users.
   - Compatibility extends to tools (e.g., MySQL Workbench, connectors, and ORMs) used with MySQL.

2. **Performance Enhancements**:
   - Improved query optimization, especially for complex queries.
   - Faster replication and parallel query execution for high-performance workloads.
   - Storage engine improvements such as **Aria** and **InnoDB** optimizations.

3. **Scalability**:
   - Better handling of large datasets through partitioning and optimized indexing.
   - Advanced replication options (e.g., multi-source replication, Galera Cluster) for scaling across distributed environments.

4. **Community-Driven Development**:
   - MariaDB remains fully open-source with an active community and foundation-led governance.
   - Transparent release cycles ensure predictable updates and long-term support.

5. **Extensibility**:
   - Support for plugins, virtual columns, dynamic columns, and JSON functions for semi-structured data.

## Detailed Design

### Database Configuration
MariaDB will be included as a **recommended database** option for production deployments.
Example configuration:
```yaml
database:
  backend: mariadb
  mariadb:
    host: localhost
    port: 3306
    database: abilian_sbe
    username: sbe_user
    password: secure_password
```

### Compatibility
- MariaDB will maintain full compatibility with existing MySQL-based migrations and tools.
- Abilian SBE ORM configurations (e.g., SQLAlchemy) will abstract database operations, ensuring minimal changes are required for MariaDB deployments.

### Performance Optimizations
- Use **InnoDB** as the default storage engine for transactional consistency and performance.
- Enable **query caching** and **parallel replication** for performance improvements on large datasets.
- Leverage **JSON functions** for managing semi-structured data.

### Migration Path
- Existing MySQL users can migrate seamlessly to MariaDB using standard tools (e.g., `mysqldump`, `mysql_upgrade`).
- Provide migration guides and best practices for transitioning MySQL-based deployments to MariaDB.

## Examples and Interactions

1. **JSON Data Support**
   Storing and querying JSON data:
   ```sql
   CREATE TABLE user_settings (
       id INT PRIMARY KEY AUTO_INCREMENT,
       preferences JSON
   );

   INSERT INTO user_settings (preferences) VALUES ('{"theme": "dark", "notifications": {"email": true}}');

   SELECT preferences->'$.theme' AS theme
   FROM user_settings;
   ```

2. **Parallel Replication Example**
   Improve replication performance for multi-node environments:
   ```sql
   SET GLOBAL slave_parallel_threads = 4;
   ```

3. **Partitioning for Large Tables**
   Partition a large table for efficient querying:
   ```sql
   CREATE TABLE logs (
       id INT,
       created_at DATETIME
   ) PARTITION BY RANGE (YEAR(created_at)) (
       PARTITION p2023 VALUES LESS THAN (2024),
       PARTITION p2024 VALUES LESS THAN MAXVALUE
   );
   ```

## Consequences

### Benefits
- **Compatibility**: Existing MySQL users can migrate seamlessly to MariaDB.
- **Performance**: MariaDB introduces performance improvements over MySQL, particularly for complex queries and replication.
- **Scalability**: MariaDB offers advanced replication, clustering, and partitioning for enterprise-grade deployments.
- **Open-Source Commitment**: MariaDB aligns with Abilian SBE’s commitment to open, community-driven software.

### Drawbacks
- **Migration Effort**: Users still running MySQL may need to test and validate migrations.
- **Resource Usage**: MariaDB, like MySQL, may consume more resources compared to lightweight alternatives like SQLite.

## Lessons Learned
MySQL has been widely used in the past, but MariaDB offers better performance, enhanced features, and an open governance model, making it a superior choice for future-proofing Abilian SBE deployments.

## Action Items
1. Include MariaDB as a **tier-one supported database** in Abilian SBE.
2. Test and validate MariaDB compatibility with all Abilian SBE features.
3. Provide migration guides for MySQL users to MariaDB.
4. Update documentation and examples to include MariaDB configuration and usage.

## Alternatives
- **MySQL**: While MySQL is compatible with MariaDB, it lacks MariaDB’s community-driven improvements and features.
- **PostgreSQL**: PostgreSQL is already supported as a tier-one database (see related ADR). Both databases serve complementary roles.
- **SQLite**: Suitable only for lightweight local development or testing, not scalable for production.

## Unresolved Questions
- Should MySQL support be deprecated in favor of MariaDB entirely in the long term?

## Future Work
- Investigate advanced MariaDB clustering solutions (e.g., **Galera Cluster**) for high-availability environments.
- Optimize Abilian SBE queries and schema to take advantage of MariaDB-specific performance features.

## Related
- ADR XXX: Adoption of PostgreSQL as a Tier-One Supported Database
- ADR XXX: Database Migration Strategy

## References
- **MariaDB Documentation**: https://mariadb.org/documentation/
- **Migration from MySQL to MariaDB**: https://mariadb.com/kb/en/upgrading-from-mysql-to-mariadb/
- **Performance Benchmarks**: https://mariadb.com/resources/
