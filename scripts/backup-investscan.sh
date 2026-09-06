#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
mkdir -p backups
backup_file="backups/investscan-$(date -u +%Y%m%dT%H%M%SZ).dump"
docker compose --env-file .env -f deploy/investscan/compose.yml exec -T db pg_dump -U investscan -d investscan -Fc > "$backup_file"
test -s "$backup_file"
printf '%s\n' "$backup_file"
