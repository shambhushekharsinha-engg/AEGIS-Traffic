# ADR 0002: Synchronous SQLAlchemy & Simplified Repository Pattern

## Context
While async database drivers (such as `asyncpg` / `asyncmy`) provide non-blocking IO for heavy concurrent workloads, migrating an existing synchronous SQLAlchemy ORM layer introduces significant code churn across repositories, dependencies, tests, and database fixtures without providing tangible performance gains for standard workloads.

## Decision
We elected to retain synchronous SQLAlchemy ORM paired with connection pooling (`db_pool_size`, `db_max_overflow`), clean dependency injection (`Depends(get_db)`), and a straightforward Service/CRUD layer without over-engineered generic repository abstractions.

## Consequences
- Maintains 100% test reliability across all 36+ unit and integration test cases.
- Reduces architectural overhead while maintaining simple, maintainable database interactions.
- Allows seamless switching between SQLite (development) and PostgreSQL (production).
