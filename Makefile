COMPOSE = docker compose --project-directory docker --env-file .env -f docker/docker-compose.yaml
TEST_COMPOSE = docker compose --project-directory docker -p uptime-tests --env-file .env.test -f docker/docker-compose.test.yaml

.PHONY: up down restart logs ps test migrate revision

test:
	@echo "Starting test database..."
	$(TEST_COMPOSE) up -d --wait
	
	@echo "Running tests..."
	uv run pytest -v; status=$$?; \
		echo "Tearing down test database..."; \
		$(TEST_COMPOSE) down -v; \
		exit $$status

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

migrate:
	$(COMPOSE) exec -T api uv run alembic -c migrations/alembic.ini upgrade head
	
revision:
	uv run alembic -c migrations/alembic.ini revision --autogenerate