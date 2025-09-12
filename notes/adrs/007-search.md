# Pluggable Search Index Architecture for Abilian SBE

Status: Draft

## Introduction

This ADR proposes transitioning from the current reliance on **Whoosh** as the sole search index to a **pluggable search index architecture** for **Abilian SBE**. The goal is to make the search system flexible and extensible, allowing different search backends (e.g., **Typesense**, **Tantivy**, **Sonic**, **Elasticsearch**, **Whoosh**...) to be integrated easily based on deployment requirements. This approach ensures that no single search engine is favored, keeping the system open to multiple solutions.

## Summary

We propose abstracting the search index system in **Abilian SBE**, allowing various search backends to be plugged in based on performance, scalability, and use case needs. While **Whoosh** will continue to be supported for lightweight local searches, additional options like **Typesense**, **Tantivy**, **Sonic**, and **Elasticsearch** will be made available for larger-scale, real-time, and distributed search needs.

## Status

Proposed

## Context and Goals

### Context

Currently, **Abilian SBE** relies solely on **Whoosh** for search indexing. While Whoosh is simple and suitable for small-scale, local deployments, it has significant limitations regarding performance, scalability, and advanced search features for larger datasets or complex queries.

As the platform evolves and integrates with larger datasets and diverse environments (e.g., distributed systems, cloud environments), we need a more flexible and scalable solution. Rather than committing to a single search engine like **Elasticsearch**, we will make the system pluggable to support multiple search solutions such as **Typesense**, **Tantivy**, and **Sonic**, in addition to Whoosh.

### Goals

- **Pluggable Search Architecture**: The system should allow administrators to choose and configure different search backends based on their deployment needs and scale.
- **Flexibility**: Support multiple backends, including local lightweight search engines like **Whoosh** and more scalable solutions like **Typesense**, **Elasticsearch**, or **Tantivy**.
- **Scalability**: Allow the system to scale as needed, supporting both small and large datasets, as well as distributed search operations when required.
- **Extensibility**: Ensure the search architecture can be extended to support new backends with minimal changes to the core system.

## Tenets

- **Flexibility**: The architecture must support seamless integration of various search backends without making drastic changes to the core system.
- **Scalability**: The system should be capable of scaling to support large datasets and multiple tenants, handling high traffic and search volume efficiently.
- **Modularity**: The architecture should be modular, allowing new search engines to be added or swapped out as needed.
- **Performance**: Search results should be delivered quickly and efficiently, regardless of the backend being used.

## Decision

We will implement a **pluggable search index architecture** for Abilian SBE, abstracting the search system so that multiple search backends can be integrated based on deployment needs. This will involve creating a **SearchBackend** interface that allows for easy swapping between different search engines such as **Whoosh**, **Typesense**, **Tantivy**, **Sonic**, **Elasticsearch**, and others in the future.

### Key Backends

1. **Whoosh**: A lightweight, file-based search index engine suitable for small, on-premise deployments. **Whoosh** will remain supported as the default search engine for lightweight use cases.

2. **Typesense**: A fast, open-source, typo-tolerant search engine that is simple to set up and optimized for small- to medium-sized datasets. Typesense will be a good alternative for users who need more scalability and advanced search features compared to Whoosh, but don't require the full complexity of distributed systems like Elasticsearch.

3. **Tantivy**: A high-performance, Rust-based search engine that offers speed and performance advantages for full-text search. It is suited for large datasets while maintaining simplicity.

4. **Sonic**: A fast, lightweight search backend optimized for fast indexing and real-time search of small to medium datasets.

5. **Elasticsearch**: A powerful, distributed search engine suitable for large-scale enterprise deployments where distributed indexing, full-text search, and real-time search are needed.

6. **Other Backends (Future Options)**: The pluggable architecture will allow support for additional search backends in the future, such as **MeiliSearch**, **OpenSearch**, or **Apache Solr**, depending on user needs.

## Detailed Design

1. **Search Abstraction Layer**:
   - Introduce a search abstraction layer (`SearchBackend`) to decouple the core logic of **Abilian SBE** from the underlying search engine.
   - Each backend will implement the `SearchBackend` interface, which will provide the following core methods:
     - `index_document(document)`: Add or update a document in the search index.
     - `delete_document(document_id)`: Remove a document from the index.
     - `search(query)`: Execute a search query and return results.
     - `reindex()`: Rebuild the search index for all documents.

2. **Pluggable Architecture**:
   - Administrators will configure the search backend via a configuration file or environment variables. The search backend can be swapped by simply modifying the configuration without making changes to the core system.
   - Example configuration:
     ```yaml
     search:
       backend: typesense
       typesense:
         api_key: <API_KEY>
         nodes:
           - host: <HOST>
             port: 8108
             protocol: http
     ```

3. **Integration of Multiple Backends**:
   - **Typesense**, **Tantivy**, and **Sonic** will be considered for immediate integration, offering various benefits for different types of deployments.
   - For distributed environments or larger datasets, **Elasticsearch** or similar engines (e.g., **OpenSearch**) will also be available.
   - The system should also include appropriate error handling and logging for cases where specific backends fail or are misconfigured.

4. **Migration and Compatibility**:
   - For installations currently using **Whoosh**, migration scripts will be provided to move data from Whoosh to another search backend (e.g., **Typesense** or **Elasticsearch**) if desired.
   - The system will maintain backward compatibility with Whoosh to ensure minimal disruption for smaller-scale users who wish to continue using local search.

5. **Testing and Performance**:
   - Each search backend will be tested for performance under various conditions, ensuring the system functions efficiently with both small and large datasets.
   - Performance benchmarks will focus on indexing speed, search query execution time, and the ability to handle concurrent search operations.

## Examples and Interactions

1. **Switching from Whoosh to Typesense**:
   - An administrator can switch from **Whoosh** to **Typesense** by updating the configuration file. Once the switch is made, the system will reindex existing documents in Typesense, making them available for real-time search.

2. **Search Query**:
   - A user submits a search query. The configured search backend (Whoosh, Typesense, or another) processes the query and returns relevant results.

3. **Pluggable Backend Configuration**:
   - The system allows for easy switching between different backends. For example, an organization with a small dataset can use **Sonic**, while a larger enterprise might use **Elasticsearch** or **Tantivy** for faster, distributed search capabilities.

## Consequences

### Benefits

- **Flexibility**: The pluggable architecture allows **Abilian SBE** to be deployed in environments with varying search needs, from small, local installations to large, distributed environments.
- **Extensibility**: Adding new search backends in the future will be simple, as the search layer is decoupled from the rest of the system.
- **Performance**: Search backends such as **Tantivy** and **Typesense** offer performance optimizations, while more complex engines like **Elasticsearch** or **OpenSearch** provide real-time indexing and advanced search features for enterprise use.

### Drawbacks

- **Increased Complexity**: The introduction of a pluggable search system adds some complexity to the configuration and management of the system.
- **Migration Effort**: Users wishing to switch from **Whoosh** to another backend may need to invest time and effort in migrating their data and reconfiguring their systems.

## Lessons Learned

Previous reliance on a single search backend (Whoosh) limited **Abilian SBE**'s ability to scale and adapt to diverse environments. Moving to a pluggable architecture provides flexibility and future-proofing.

## Action Items

### Strategic Priorities

1. Implement the `SearchBackend` abstraction layer.
2. Integrate and test **Typesense**, **Tantivy**, **Sonic**, and other backends as viable alternatives to **Whoosh**.
3. Provide migration tools for users to move from **Whoosh** to other backends.
4. Develop comprehensive testing and benchmarking frameworks for each backend.

## Alternatives

- **Single Search Engine (e.g., Typesense-only)**: Committing to a single search engine could simplify development but would limit flexibility and scalability for certain environments.
- **Custom Search Engine**: Building a custom search engine would require significant effort and would not match the performance and features of existing solutions.

## Prior Art

Many platforms such as **Nextcloud**, **Django**, and **

Mattermost** have implemented pluggable search systems, allowing users to choose between lightweight and scalable search backends depending on their needs.

## Unresolved Questions

- How will we manage search engine configuration and ensure backward compatibility when new backends are added?
- Should we prioritize adding a broader range of backends (e.g., **MeiliSearch**, **OpenSearch**), or focus on optimizing a smaller number of high-performing ones?

## Future Work

- Investigate additional backends (e.g., **MeiliSearch**, **Solr**) to extend the flexibility of the pluggable search system.
- Explore query caching and distributed search mechanisms for larger deployments.


## References

- Open source search engines:
  - **Whoosh**: https://whoosh.readthedocs.io/
  - **Typesense**: https://typesense.org/
  - **Tantivy**: https://tantivy-search.github.io/
  - **Sonic**: https://crates.io/crates/sonic
  - **Elasticsearch**: https://www.elastic.co/elasticsearch/
- [Search on lab.abilian.com](https://lab.abilian.com/Tech/Search/Search/)
  - And also: [Comparison of open source search engines](https://lab.abilian.com/Tech/Search/Comparison%20of%20open%20source%20search%20engines/)
