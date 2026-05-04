#!/usr/bin/env bash
# restore_redis.sh - Restore Redis from an RDB dump file.
#
# Usage:
#   ./scripts/backup/restore_redis.sh DUMP_FILE
#
# WARNING: This stops Redis, replaces dump.rdb on the data volume, and
# starts Redis again. All current data is replaced.
#
# Environment overrides:
#   REDIS_CONTAINER  - container name (default: investbyyourself-redis)
#   FORCE            - set to 1 to skip the confirmation prompt

set -euo pipefail

DUMP="${1:-}"
if [ -z "${DUMP}" ] || [ ! -f "${DUMP}" ]; then
    echo "Usage: $0 DUMP_FILE" >&2
    exit 2
fi

REDIS_CONTAINER="${REDIS_CONTAINER:-investbyyourself-redis}"

if ! docker ps -a --format '{{.Names}}' | grep -qx "${REDIS_CONTAINER}"; then
    echo "[restore_redis] container ${REDIS_CONTAINER} not found" >&2
    exit 1
fi

# Verify input is a real RDB file.
HEADER=$(head -c 5 "${DUMP}" | tr -d '\0' || true)
if [ "${HEADER}" != "REDIS" ]; then
    echo "[restore_redis] input file lacks REDIS magic header: ${DUMP}" >&2
    exit 1
fi

if [ "${FORCE:-0}" != "1" ]; then
    echo "About to REPLACE Redis data in ${REDIS_CONTAINER} with ${DUMP}."
    read -r -p "Type yes to confirm: " CONFIRM
    if [ "${CONFIRM}" != "yes" ]; then
        echo "[restore_redis] aborted" >&2
        exit 1
    fi
fi

echo "[restore_redis] stopping ${REDIS_CONTAINER}"
docker stop "${REDIS_CONTAINER}" >/dev/null

echo "[restore_redis] copying dump.rdb into container volume"
# Start a temporary container to write into the redis_data volume.
VOLUME=$(docker inspect "${REDIS_CONTAINER}" \
    --format '{{range .Mounts}}{{if eq .Destination "/data"}}{{.Name}}{{end}}{{end}}')

if [ -z "${VOLUME}" ]; then
    echo "[restore_redis] could not find /data mount on ${REDIS_CONTAINER}" >&2
    docker start "${REDIS_CONTAINER}" >/dev/null || true
    exit 1
fi

docker run --rm \
    -v "${VOLUME}:/data" \
    -v "$(cd "$(dirname "${DUMP}")" && pwd):/restore:ro" \
    alpine:3 \
    sh -c "cp /restore/$(basename "${DUMP}") /data/dump.rdb && chmod 600 /data/dump.rdb"

echo "[restore_redis] starting ${REDIS_CONTAINER}"
docker start "${REDIS_CONTAINER}" >/dev/null

# Wait for Redis to come back.
for _ in $(seq 1 30); do
    if docker exec "${REDIS_CONTAINER}" redis-cli ping >/dev/null 2>&1 || \
       docker exec "${REDIS_CONTAINER}" sh -c \
           'redis-cli -a "$REDIS_PASSWORD" --no-auth-warning ping' >/dev/null 2>&1; then
        echo "[restore_redis] OK - Redis responding"
        exit 0
    fi
    sleep 1
done

echo "[restore_redis] Redis did not respond after restore" >&2
exit 1
