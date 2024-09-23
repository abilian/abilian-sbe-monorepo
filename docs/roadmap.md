# Roadmap for Abilian SBE

## Version 1.1 (Q1 2024)

- [x] Replace Celery with Dramatiq [DONE].
- [x] Make POC for SlapOS port of Abilian SBE (cf. [HyperOpen X](https://abilian.com/fr/recherche-developpement/hyper-open-x/) project) [DONE].
- [ ] Write doc [in progress]
- [ ] Upgrade core components: Flask, SQLAlchemy, WTForms, etc. [in progress]

## Version 1.2 (Q4 2024)

- [ ] Modernize UI: use [Flask-Vite](https://github.com/abilian/flask-vite), [Tailwind CSS](https://tailwindcss.com/), [Alpine.js](https://alpinejs.dev/), [htmx](https://htmx.org/).
  - see: [ADR 006](../notes/adrs/006-front-end.md)
- [ ] MVP for SlapOS port of Abilian SBE.
- [ ] Plugin architecture.
  - [ ] Pluggable search indexes (e.g. Typesense, ElasticSearch, etc.)
  - [ ] Pluggable file storage (e.g. S3, MinIO, etc.)
    - See: [ADR 005](../notes/adrs/005-storage.md)
- [ ] MVP for SlapOS port of Abilian SBE (update).

## Q1 2025

- [ ] Overhaul of the authentication and permissions system.
  - See: [ADR 001](../notes/adrs/001-oidc.md), [ADR 002](../notes/adrs/002-scim.md), [ADR 003](../notes/adrs/003-rbac.md), [ADR 004](../notes/adrs/004-permissions.md).
- ...

## See also:

A significant part of shaping the future of Abilian SBE involves participating in the creation and review of **[Architecture Decision Records](../notes/adrs) (ADRs)**. These documents capture major architectural decisions and guide the project’s long-term technical direction.
