# DMF — Document Management Framework

DMF is a starter monorepo that demonstrates a simple document management
framework.  It contains two FastAPI services, infrastructure definitions and
database migrations so you can quickly spin up a working environment and begin
extending it for your own use cases.

## Repository Layout

| Path | Description |
| ---- | ----------- |
| `apps/gateway` | FastAPI gateway service exposing public endpoints |
| `apps/dms` | Core document management FastAPI service |
| `database/migrations` | SQL migration scripts executed via Alembic |
| `deploy/compose` | Docker Compose files used for local development |
| `libs` | Reusable library code (e.g. S3 client) |
| `tests` | Pytest test suite |

## Requirements

- Python 3.11+
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- `pip` for installing Python dependencies

## Installation

```bash
git clone <repo-url>
cd DMS
pip install -r requirements.txt
```

## Running the Stack with Docker

The Makefile wraps Docker Compose commands to simplify common tasks:

```bash
make dev-up       # build images and start containers in the background
make migrate      # apply database migrations

# available after the stack is up:
# Gateway service docs: http://localhost:8080/docs
# DMS service docs:     http://localhost:8081/docs

make dev-down     # stop and remove containers
```

## Running Services Directly

You can also run the services locally without Docker once dependencies are
installed:

```bash
# Start the DMS service on port 8081
uvicorn apps.dms.main:app --reload --port 8081

# In a separate terminal start the gateway on port 8080
uvicorn apps.gateway.main:app --reload --port 8080
```

## Database Migrations

Alembic migration scripts live under `database/migrations`.  To apply them
without Docker use:

```bash
python apps/dms/alembic_upgrade.py
```

## Tests and Formatting

Run the unit tests with:

```bash
pytest
# or use the Makefile: make test
```

Format the code using `ruff`:

```bash
make fmt
```

## Notes

This repository is intentionally lightweight and focuses on providing a basic
foundation for a document management platform.  Expand or replace components as
needed for your production environment.

