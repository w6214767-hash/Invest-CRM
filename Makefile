COMPOSE=docker compose -f deploy/docker-compose.yml

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
