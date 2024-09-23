# Title: Pluggable Blob Storage with S3-like Services Support

Status: Draft

## Introduction

This ADR proposes the introduction of a **pluggable blob storage** system in **Abilian SBE** that can support various storage backends, including **S3-like services** (e.g., **Amazon S3**, **MinIO**, etc.). The goal is to provide flexible, scalable, and efficient storage for large binary files (blobs) such as documents, images, and media files. By making the blob storage pluggable, SBE can support multiple storage solutions, both on-premise and in the cloud, offering flexibility to adapt to different deployment environments and customer needs.

## Summary

We propose refactoring the current blob storage implementation to make it **pluggable**. This means that developers and system administrators can configure **Abilian SBE** to store files on various storage backends, including S3-compatible services. This would improve the scalability of the platform, particularly for handling large datasets and file storage in cloud environments, while allowing on-premise and hybrid solutions for organizations with specific needs.

## Status

Proposed

## Context and Goals

### Context

Currently, Abilian SBE uses a custom file storage system that is not optimized for handling large volumes of data or integrating with cloud storage providers. As the platform evolves and usage increases, especially in enterprise and cloud-based environments, a more scalable and flexible solution is needed. Many organizations are already using **S3-like services** for their storage needs, and the ability to integrate seamlessly with these services will improve deployment flexibility and scalability.

There is also a growing need for the platform to support multiple storage options, from cloud storage (Amazon S3, MinIO) to local file systems, depending on the deployment context (e.g., government, on-premise installations, or hybrid cloud).

### Goals

- Make the blob storage system **pluggable**, allowing administrators to choose and configure different storage backends.
- Provide **native support for S3-like services**, including **Amazon S3**, **MinIO**, and other compatible solutions.
- Maintain support for **local file storage** for on-premise deployments.
- Ensure scalability, especially for handling large files and datasets in cloud environments.
- Abstract the storage system to simplify the development of new backends or integration with existing services.

## Tenets

- **Modularity**: The storage system should be modular and pluggable, making it easy to add support for new storage backends.
- **Scalability**: The system must be able to scale with the growth in file storage needs, particularly for cloud environments.
- **Performance**: Blob storage and retrieval should be optimized for performance, especially when dealing with large datasets.
- **Simplicity**: The configuration and management of different storage backends should be simple and intuitive.
- **Security**: Ensure that data stored in blobs is secure, particularly when using third-party cloud providers, with encryption options for data at rest and in transit.

## Decision

We will implement a **pluggable blob storage system** that supports multiple backends, including:
- **S3-compatible services** (Amazon S3, MinIO, DigitalOcean Spaces, etc.).
- **Local file systems** for on-premise deployments.

The decision includes defining a **storage interface** that will abstract the interactions with different storage backends, enabling developers and administrators to switch between storage solutions with minimal configuration changes.

## Detailed Design

1. **Storage Interface**:
   - Define a standard storage interface (`BlobStorage`) that each storage backend must implement.
   - The interface will handle basic operations such as:
     - `store_blob(blob_data)`: Store a blob in the storage system.
     - `retrieve_blob(blob_id)`: Retrieve a blob from storage.
     - `delete_blob(blob_id)`: Delete a blob from storage.
     - `get_metadata(blob_id)`: Retrieve metadata about a blob (e.g., size, type, creation date).
   - The interface should be agnostic to the underlying storage technology, whether it’s an S3-like service or a local file system.

2. **S3-like Service Support**:
   - Implement a `S3BlobStorage` backend that interfaces with any S3-compatible service (e.g., Amazon S3, MinIO).
   - Use libraries such as **boto3** (for AWS S3) or other appropriate libraries for S3-like services to interact with the backend.
   - Features include:
     - Uploading blobs to the S3 bucket.
     - Retrieving blobs using secure, signed URLs.
     - Managing blob metadata and permissions.
     - Optional versioning and lifecycle management for blob storage.
   - Example Configuration:
     ```yaml
     storage:
       backend: s3
       s3:
         access_key: <AWS_ACCESS_KEY>
         secret_key: <AWS_SECRET_KEY>
         bucket: <BUCKET_NAME>
         region: <AWS_REGION>
     ```

3. **Local File System Storage**:
   - Implement a `LocalBlobStorage` backend that stores files on the local file system.
   - Features include:
     - Storing files in a specified directory.
     - Serving files directly from the local file system.
     - Managing file permissions and metadata.
   - Example Configuration:
     ```yaml
     storage:
       backend: local
       local:
         path: /var/abilian/storage/blobs
     ```

4. **Pluggable Architecture**:
   - The blob storage system should be designed as a plugin system, where different storage backends can be added or swapped without modifying the core platform.
   - Each storage backend (S3, local file system, etc.) will implement the `BlobStorage` interface.
   - Developers can create custom storage backends by implementing the same interface, making it easy to support other storage solutions.

5. **Configuration Management**:
   - The configuration system will allow administrators to switch between storage backends via a simple configuration file or environment variables.
   - Example:
     ```yaml
     storage:
       backend: s3
       s3:
         access_key: YOUR_ACCESS_KEY
         secret_key: YOUR_SECRET_KEY
         bucket: YOUR_BUCKET
         region: us-east-1
     ```


6. **Caching strategies** will be implemented to optimize blob retrieval performance in **distributed environments**, especially where latency can become a bottleneck. These strategies include:

  1. **Local Disk Caching**: Frequently accessed blobs can be cached on local storage disks to reduce retrieval times from the S3-compatible backend. This is particularly useful for high-read environments where the same files are accessed repeatedly.

  2. **In-Memory Caching**: Leveraging in-memory cache solutions (e.g., **Redis** or **Memcached**) to store metadata or small objects that are frequently requested, allowing quick retrieval without hitting the S3-compatible backend.

  3. **CDN Integration**: For large files or media assets, integrating with **Content Delivery Networks (CDNs)** to cache and distribute blobs closer to the end users, reducing the load on the backend and improving download times across geographically distributed regions.

  4. **HTTP Caching with ETags**: Use **ETags** and **cache-control** headers to allow clients to cache responses locally or via intermediate proxies, avoiding unnecessary retrievals when the content has not changed.

  5. **Blob Prefetching**: Implement a prefetching strategy where blobs that are likely to be requested soon are proactively cached based on user behavior or access patterns.

  The caching layer will be designed to work in conjunction with the **S3 API**, ensuring that cached objects remain consistent with the source, while maintaining proper **cache invalidation** mechanisms (e.g., via object versioning or cache expiration policies).


7. **Testing and Performance Considerations**:
   - Each backend will be tested for performance and scalability, particularly when handling large datasets or high-frequency storage/retrieval operations.
   - **Local testing** environments should be supported via mock S3 services (e.g., MinIO or moto for AWS S3).

8. **Security**:
   - Support encryption of data at rest (e.g., server-side encryption for S3).
   - Implement HTTPS for all data in transit, ensuring secure upload and download operations.
   - Ensure that access control policies (e.g., read-only vs. read-write) are enforced for both S3-like services and local storage.

## Examples and Interactions

1. **Storing a Blob (S3)**:
   - A user uploads a document through the Abilian SBE interface.
   - The document is passed to the `S3BlobStorage` backend, which uploads the file to the configured S3 bucket.
   - The backend returns a unique blob ID for later retrieval.

2. **Retrieving a Blob (Local File System)**:
   - A user requests to download a document.
   - The `LocalBlobStorage` backend retrieves the file from the local file system and returns the file stream to the user.

3. **Switching Backends**:
   - The system is configured to use the local file system for blob storage.
   - The administrator switches to S3 by updating the configuration file and restarting the service. No code changes are required.

## Consequences

### Benefits

- **Flexibility**: By supporting multiple storage backends, Abilian SBE can be deployed in various environments, from cloud-based to on-premise installations.
- **Scalability**: S3-like services are highly scalable, making them ideal for handling large datasets and high-traffic environments.
- **Modularity**: The pluggable architecture makes it easy to add or replace storage backends without modifying the core application.
- **Performance**: S3-like services provide optimized storage solutions that are both performant and cost-effective for large datasets.
- **Security**: Supporting S3 encryption and HTTPS ensures data is secure at rest and in transit.

### Drawbacks

- **Increased Complexity**: Introducing a pluggable architecture adds some complexity to the system configuration and deployment process.
- **Dependency Management**: Managing dependencies like boto3 for AWS S3 or other storage libraries may require additional effort in keeping the system up to date.

## Lessons Learned

Previous attempts to manually manage file storage across different environments have led to fragmented and inefficient solutions. A pluggable architecture, where backends are abstracted via a common interface, will ensure consistency and flexibility in the future.

## Action Items

### Strategic Priorities

1. Design and implement the `BlobStorage` interface for multiple storage backends.
2. Develop and test the `S3BlobStorage` and `LocalBlobStorage` backends.
3. Ensure smooth configuration management for switching between backends.
4. Integrate secure storage options (encryption, secure URLs) into the storage solutions.

## Alternatives

- **Single Backend (S3 Only)**: The alternative would be to only support S3-like services, but this would reduce flexibility for customers who need local storage solutions.
- **Custom Storage Implementation**: Developing a custom storage system without relying on S3 or other services would be more complex and less scalable.

## Prior Art

Other platforms like **Nuxeo CPS**, **Nextcloud** and **Django** have implemented pluggable storage systems that support

 S3, local storage, and other cloud providers. These implementations serve as a useful reference for best practices and lessons learned in managing blob storage.

## Unresolved Questions

- How should the system handle migrating data from one storage backend to another (e.g., moving from local storage to S3)?
- How will we support versioning for blobs across different storage backends?

## Future Work

- Explore caching strategies to optimize blob retrieval performance in distributed environments.

## Related

- ADR 004: Simplifying Permission Management (for access control of blobs)

## References

- Cloud providers:
  - **Amazon S3**: https://aws.amazon.com/s3/
  - **Scaleway Object Storage**: https://www.scaleway.com/en/object-storage/
  - **OVH Cloud Storage**: https://www.ovhcloud.com/en/public-cloud/object-storage/
- Self-hosted / open source:
  - **MinIO**: https://min.io/
- **Boto3 Documentation**: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

## Notes

- The pluggable storage system will be designed for **extensibility**, allowing easy addition of new storage backends that implement the **S3 API** (e.g., **MinIO**, **DigitalOcean Spaces**, or **Wasabi**), as well as custom or on-premise storage solutions.

- **Security**: Data security, particularly in caching layers, will be emphasized, ensuring that only authorized users can access cached blobs and that sensitive data is encrypted at rest in the cache (where applicable).

- **Future-proofing**: The architecture should remain adaptable for additional enhancements, such as **tiered storage** strategies (e.g., moving less-frequently accessed data to cold storage) and **automatic blob replication** across multiple regions for high availability and disaster recovery.
