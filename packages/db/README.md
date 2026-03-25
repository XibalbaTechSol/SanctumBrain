# Sanctum Brain: Shared DB (PARA Schema)

Shared database definitions for the Sanctum Brain ecosystem, ensuring consistency across the VPS backend and client synchronization.

## PARA v2 Schema

This package exports the core PostgreSQL schema and TypeScript definitions for:
- **Projects**: Active tasks with intent-based triggers.
- **Areas**: Long-term responsibilities and system status contexts.
- **Resources**: Vector-indexed knowledge base metadata.
- **Archives**: Historic state and cold-storage pointers.

## Usage

In the backend (Python):
The schema is used by the `para_manager` node to synchronize state.

In the frontend (TypeScript):
Type definitions are used for UI atoms like `ParaView` and `ActiveProjects`.

## Migrations

Manage database migrations using our unified script from the root:

```bash
./ops/db_migrate.sh
```
