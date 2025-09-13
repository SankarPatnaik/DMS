# DMF — Document Management Framework (Starter Repo)

This is a starter monorepo scaffolding for a Document Management Framework (DMF).  
It includes:
- **Docker Compose** stack (PostgreSQL, MinIO, OpenSearch, RabbitMQ, Redis) + services.
- **FastAPI** service stubs (`gateway`, `dms`).
- **Alembic** migrations for core tables.
- **OpenSearch** index mapping.
- **Makefile** helpers.
- **GitHub Actions** CI workflow.

## Quickstart

```bash
make dev-up       # start infra + build services
make migrate      # run Alembic migrations
# visit gateway docs: http://localhost:8080/docs
# visit dms docs:     http://localhost:8081/docs
```

> **Note**: This is a minimal scaffold to get you running locally. Extend per your architecture.
