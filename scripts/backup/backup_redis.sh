#!/usr/bin/env bash
# backup_redis.sh - Trigger a Redis BGSAVE and copy the RDB file out.
#
# Usage:
#   ./scripts/backup/backup_redis.sh OUTPUT_FILE
#
# Environment overrides:
#   REDIS_CONTAINER  - container name (default: investbyyourself-redis)
#   REDIS_PASSWORD   - auth password (default: read from container env)

set -euo pipefail

OUT="${1:-}"
if [ -z "${OUT}" ]; then
    echo "Usage: $0 OUTPUT_FILE" >&2
    exit 2
fi

REDIS_CONTAINER="${REDIS_CONTAINER:-investbyyourself-redis}"

if ! docker ps --format '{{.Names}}' | grep -qx "${REDIS_CONTAINER}"; then
    echo "[backup_redis] container ${REDIS_CONTAINER} is not running" >&2
    exit 1
fi

if [ -z "${REDIS_PASSWORD:-}" ]; then
    REDIS_PASSWORD="$(docker exec "${REDIS_CONTAINER}" \
        sh -c 'echo "$REDIS_PASSWORD"' 2>/dev/null || true)"
fi

mkdir -p "$(dirname "${OUT}")"

echo "[backup_redis] triggering BGSAVE in ${REDIS_CONTAINER}"

# Capture the LASTSAVE timestamp before BGSAVE so we can poll for completion.
auth_args=()
if [ -n "${REDIS_PASSWORD:-}" ]; then
    auth_args=(-a "${REDIS_PASSWORD}" --no-auth-warning)
fi

PRE_SAVE=$(docker exec "${REDIS_CONTAINER}" redis-cli "${auth_args[@]}" LASTSAVE)
docker exec "${REDIS_CONTAINER}" redis-cli "${auth_args[@]}" BGSAVE >/dev/null

# Wait up to 60s for the save to complete.
for _ in $(seq 1 60); do
    NEW_SAVE=$(docker exec "${REDIS_CONTAINER}" redis-cli "${auth_args[@]}" LASTSAVE)
    if [ "${NEW_SAVE}" != "${PRE_SAVE}" ]; then
        break
    fi
    sleep 1
done

if [ "${NEW_SAVE}" = "${PRE_SAVE}" ]; then
    echo "[backup_redis] BGSAVE did not complete within 60s" >&2
    exit 1
fi

echo "[backup_redis] copying dump.rdb to ${OUT}"
docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "${OUT}"

# Sanity check the RDB magic header.
HEADER=$(head -c 5 "${OUT}" | tr -d '\0' || true)
if [ "${HEADER}" != "REDIS" ]; then
    echo "[backup_redis] file does not start with REDIS magic header" >&2
    exit 1
fi

SIZE=$(wc -c < "${OUT}")
echo "[backup_redis] OK - ${OUT} (${SIZE} bytes)"
