SHELL := /bin/bash

.PHONY: dev-up dev-down build migrate fmt test e2e

dev-up:
	docker compose -f deploy/compose/docker-compose.dev.yml up -d --build

dev-down:
	docker compose -f deploy/compose/docker-compose.dev.yml down -v

build:
	docker compose -f deploy/compose/docker-compose.dev.yml build

migrate:
	docker compose -f deploy/compose/docker-compose.dev.yml exec dms alembic upgrade head

fmt:
	docker compose -f deploy/compose/docker-compose.dev.yml exec dms ruff format || true

test:
	docker compose -f deploy/compose/docker-compose.dev.yml exec dms pytest -q || true

e2e:
	@echo "Add Playwright tests under tests/e2e and wire here."
