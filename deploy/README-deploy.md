# Развёртывание на Timeweb VPS

Ниже описан минимальный продуктивный путь для Ubuntu 22.04/24.04 на VPS Timeweb. Перед запуском замените домен `crm.example.ru` в `nginx.conf` на рабочий домен.

## 1. Подготовка сервера

1. Создайте VPS с Ubuntu, минимум 2 vCPU, 4 ГБ ОЗУ и 40 ГБ NVMe.
2. Направьте A-запись домена на публичный IP сервера.
3. Установите Docker Engine и Compose plugin по официальной инструкции Docker.
4. Разрешите в firewall только SSH, HTTP и HTTPS.
5. Создайте отдельного пользователя для деплоя и добавьте его в группу `docker`.

## 2. Копирование и настройка

```bash
git clone https://github.com/OWNER/yurzil-avito-crm.git
cd yurzil-avito-crm
cp .env.example .env
```

Заполните `.env`: сгенерируйте `SECRET_KEY`, задайте сложный `POSTGRES_PASSWORD`, реальные реквизиты Avito, Bitrix24, Telegram и Hermes. Файл `.env` не должен попадать в Git.

## 3. Первый запуск

```bash
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml exec backend alembic upgrade head
curl http://127.0.0.1/health
```

Проверьте логи: `docker compose -f deploy/docker-compose.yml logs -f --tail=200`.

## 4. HTTPS

Поставьте Certbot на хосте либо используйте внешний reverse proxy. После выпуска сертификата настройте отдельный TLS server block, который проксирует запросы в контейнер Nginx на localhost, или добавьте Certbot-контейнер. Не публикуйте PostgreSQL и Redis наружу.

## 5. Обновление

```bash
git pull --ff-only
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml exec backend alembic upgrade head
```

Сделайте резервную копию PostgreSQL перед миграциями: `docker compose -f deploy/docker-compose.yml exec -T db pg_dump -U yurzil yurzil_crm > backup.sql`.
