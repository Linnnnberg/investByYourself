#!/usr/bin/env bash
# restore_postgres.sh - Restore the Postgres database from a custom-format dump.
#
# Usage:
#   ./scripts/backup/restore_postgres.sh DUMP_FILE
#
# WARNING: This DROPS and recreates the target database. Run only against a
# host that has been intentionally taken out of service for restore.
#
# Environment overrides:
#   PG_CONTAINER  - container name (default: investbyyourself-postgres)
#   PG_USER       - postgres user (default: postgres)
#   PG_DB         - database name (default: investbyyourself)
#   FORCE         - set to 1 to skip the confirmation prompt

set -euo pipefail

DUMP="${1:-}"
if [ -z "${DUMP}" ] || [ ! -f "${DUMP}" ]; then
    echo "Usage: $0 DUMP_FILE" >&2
    exit 2
fi

PG_CONTAINER="${PG_CONTAINER:-investbyyourself-postgres}"
PG_USER="${PG_USER:-postgres}"
PG_DB="${PG_DB:-investbyyourself}"

if ! docker ps --format '{{.Names}}' | grep -qx "${PG_CONTAINER}"; then
    echo "[restore_postgres] container ${PG_CONTAINER} is not running" >&2
    exit 1
fi

if [ "${FORCE:-0}" != "1" ]; then
    echo "About to DROP and recreate database '${PG_DB}' in ${PG_CONTAINER}."
    echo "Source dump: ${DUMP}"
    read -r -p "Type the database name to confirm: " CONFIRM
    if [ "${CONFIRM}" != "${PG_DB}" ]; then
        echo "[restore_postgres] aborted" >&2
        exit 1
    fi
fi

echo "[restore_postgres] terminating existing connections"
docker exec -i "${PG_CONTAINER}" psql -U "${PG_USER}" -d postgres -v ON_ERROR_STOP=1 <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${PG_DB}' AND pid <> pg_backend_pid();
SQL

echo "[restore_postgres] dropping and recreating database"
docker exec -i "${PG_CONTAINER}" psql -U "${PG_USER}" -d postgres -v ON_ERROR_STOP=1 <<SQL
DROP DATABASE IF EXISTS ${PG_DB};
CREATE DATABASE ${PG_DB};
SQL

echo "[restore_postgres] restoring dump"
docker exec -i "${PG_CONTAINER}" \
    pg_restore -U "${PG_USER}" -d "${PG_DB}" --no-owner --no-acl --exit-on-error \
    < "${DUMP}"

echo "[restore_postgres] running ANALYZE"
docker exec -i "${PG_CONTAINER}" psql -U "${PG_USER}" -d "${PG_DB}" -c "ANALYZE;"

echo "[restore_postgres] OK"
