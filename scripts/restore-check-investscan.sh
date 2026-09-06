#!/usr/bin/env bash
# Restores into a NEW disposable database, never over the working database.
set -euo pipefail
cd "$(dirname "$0")/.."
backup_file="${1:?Pass the path to a backup dump}"
test -s "$backup_file"
restore_db="investscan_restore_$(date -u +%Y%m%d%H%M%S)"
docker compose --env-file .env -f deploy/investscan/compose.yml exec -T db createdb -U investscan "$restore_db"
docker compose --env-file .env -f deploy/investscan/compose.yml exec -T db pg_restore -U investscan --exit-on-error --no-owner -d "$restore_db" < "$backup_file"
docker compose --env-file .env -f deploy/investscan/compose.yml exec -T db psql -U investscan -d "$restore_db" -c 'SELECT count(*) AS objects FROM is_objects;'
printf 'Restore verified in database %s. Working database unchanged.\n' "$restore_db"
