# ЮрЖил Avito CRM

Open-source скелет инвестиционной CRM для строительной компании **ЮрЖилСервис** (Домодедово, Московская область). Проект помогает находить земельные участки на Авито ниже рыночной цены, оценивать их, вести полуавтоматические переговоры и передавать подтверждённые сделки в Bitrix24.

> Важно: это рабочая инженерная основа, а не инструмент массовой рассылки. Юридические, финансовые решения и обещания продавцу всегда остаются за человеком.

## Возможности

- FastAPI API, SQLModel-модели и PostgreSQL-схема инвестиционной воронки.
- Скоринг по медиане цены за сотку и формуле с весами скидки, ликвидности, локации, документов, коммуникаций и срочности продавца.
- Стейт-машина переговоров с обязательной эскалацией менеджеру по критическим условиям.
- Клиенты Avito Business API, Bitrix24, Telegram и Hermes Agent с безопасной обработкой незаполненных секретов.
- React/Vite интерфейс: обзор, участки, карточка лота, сделки и вход.
- Docker Compose, Nginx, CI и пример деплоя на Timeweb VPS.

## Архитектура

```text
Браузер → Nginx → React SPA
                └→ FastAPI → PostgreSQL
                            → Redis / воркер
                            → Avito / Bitrix24 / Telegram / Hermes
```

Полное описание: [docs/architecture.md](docs/architecture.md). Модель данных: [docs/data-model.md](docs/data-model.md).

## Быстрый старт локально

### Вариант 1: Docker

```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml up --build
docker compose -f deploy/docker-compose.yml exec backend alembic upgrade head
```

Откройте интерфейс на `http://localhost:5173`, Swagger на `http://localhost:8000/docs`, проверку процесса на `http://localhost:8000/health`.

### Вариант 2: локальный Python и Node.js

Нужны Python 3.11+, Node.js 22+ и доступный PostgreSQL. Для минимальной проверки можно оставить SQLite по умолчанию.

```bash
python3.11 -m venv .venv-crm
source .venv-crm/bin/activate
pip install -r backend/requirements.txt
cd backend
pytest tests -q
uvicorn app.main:app --reload
```

Во втором терминале:

```bash
cd frontend
npm install
npm run dev
```

## Конфигурация

Скопируйте `.env.example` в `.env`. Обязательны для безопасного продуктивного запуска: `DATABASE_URL`, уникальный `SECRET_KEY` и пароль PostgreSQL. Интеграции подключаются только после указания соответствующих ключей:

- `AVITO_CLIENT_ID`, `AVITO_CLIENT_SECRET`
- `BITRIX24_WEBHOOK_URL`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `HERMES_API_URL`, при необходимости `HERMES_API_KEY`

Никогда не коммитьте `.env`.

## VPS Timeweb

Подробная последовательность — в [deploy/README-deploy.md](deploy/README-deploy.md). Кратко: подготовьте Ubuntu VPS, DNS, Docker, `.env`, затем запустите `docker compose -f deploy/docker-compose.yml up -d --build` и примените миграции.

## Команды Make

```bash
make up       # собрать и поднять контейнеры
make down     # остановить контейнеры
make logs     # показать логи
make migrate  # применить миграции
make test     # выполнить pytest
make fmt      # исправить стиль Python-кода
```

## Статус интеграции Авито

Методы API в `backend/app/services/avito.py` реализуют OAuth2, авторизацию, частотное ограничение и запросы. Перед продуктивным включением обязательно подтвердите доступные конкретному приложению пути и поля в кабинете Avito Business API — они зависят от подключённого продукта. Правила безопасной автоматизации приведены в [docs/avito-compliance.md](docs/avito-compliance.md).

## Roadmap

- **0.1:** доменная модель, API, интерфейс, скоринг, переговоры, Docker.
- **0.2:** подтверждённая интеграция Avito, очередь задач, ручная передача в Bitrix24.
- **0.3:** карта кластеров, роли, аудит и аналитика качества.
- **1.0:** резервные копии, мониторинг, безопасность и эксплуатационные регламенты.

Детали: [docs/roadmap.md](docs/roadmap.md).

## Лицензия

Проект распространяется по [MIT License](LICENSE).
