#!/usr/bin/env bash
# backup_postgres.sh - Dump the Postgres database to a custom-format file.
#
# Usage:
#   ./scripts/backup/backup_postgres.sh OUTPUT_FILE
#
# Environment overrides:
#   PG_CONTAINER  - container name (default: investbyyourself-postgres)
#   PG_USER       - postgres user (default: postgres)
#   PG_DB         - database name (default: investbyyourself)

set -euo pipefail

OUT="${1:-}"
if [ -z "${OUT}" ]; then
    echo "Usage: $0 OUTPUT_FILE" >&2
    exit 2
fi

PG_CONTAINER="${PG_CONTAINER:-investbyyourself-postgres}"
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-investbyyourself}"

if ! docker ps --format '{{.Names}}' | grep -qx "${PG_CONTAINER}"; then
    echo "[backup_postgres] container ${PG_CONTAINER} is not running" >&2
    exit 1
fi

mkdir -p "$(dirname "${OUT}")"

echo "[backup_postgres] dumping ${PG_DB} from ${PG_CONTAINER} to ${OUT}"

# pg_dump in custom format: compressed, supports parallel restore, sortable.
docker exec -i "${PG_CONTAINER}" \
    pg_dump -U "${PG_USER}" -d "${PG_DB}" -Fc --no-owner --no-acl \
    > "${OUT}"

if [ ! -s "${OUT}" ]; then
    echo "[backup_postgres] dump file is empty" >&2
    exit 1
fi

echo "[backup_postgres] verifying dump integrity (pg_restore --list)"
docker exec -i "${PG_CONTAINER}" pg_restore --list < "${OUT}" >/dev/null

SIZE=$(wc -c < "${OUT}")
echo "[backup_postgres] OK - ${OUT} (${SIZE} bytes)"
