# Architecture

- **Storage:** PostgreSQL 16 with pgvector extension for future semantic search over program descriptions.
- **Orchestration:** Dagster assets grouped by layer (ronze, silver, gold). Definitions live in carms/pipelines.
- **API:** FastAPI app in carms/api serving program and discipline endpoints plus a pipeline trigger.
- **Infrastructure:** Docker Compose runs Postgres, Dagster webserver (dagster dev), and the API with shared environment variables.

## Data Lineage
1. **Bronze (legacy ingestion):** direct load from the provided Excel/CSV extracts into ronze_* tables.
2. **Silver (modern standardized layer):** cleans column noise, normalizes types, adds provinces and validity flags, and unpivots description sections.
3. **Gold:** builds program profiles and geographic rollups for analytics.

## Environments
- Configure via .env (DB URL, secrets). Pydantic settings are centralized in carms/core/config.py.
- Alembic is scaffolded for migrations (lembic/env.py).
