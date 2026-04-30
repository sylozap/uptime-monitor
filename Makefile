.PHONY: test

test:
	@echo "Starting test database..."
	docker compose -p uptime-tests --env-file .env.test -f docker-compose.test.yaml up -d --wait
	
	@echo "Running tests..."
	pytest -v || true 
	
	@echo "Tearing down test database..."
	docker compose -p uptime-tests --env-file .env.test -f docker-compose.test.yaml down -v