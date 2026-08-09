COMPOSE=docker compose -f deploy/docker-compose.yml
PLAYWRIGHT_VERSION=1.55.0

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

migrate:
	$(COMPOSE) exec backend alembic upgrade head

test:
	cd backend && python -m pytest tests -q

fmt:
	cd backend && python -m ruff check app tests --fix && python -m ruff format app tests

browser-setup:
	npx -y playwright@$(PLAYWRIGHT_VERSION) install-deps chromium
	npx -y playwright@$(PLAYWRIGHT_VERSION) install chromium
