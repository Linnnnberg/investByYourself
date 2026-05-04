#!/usr/bin/env bash
# restore_minio.sh - Mirror a backup snapshot directory back into MinIO.
#
# Usage:
#   ./scripts/backup/restore_minio.sh SNAPSHOT_DIR
#
# SNAPSHOT_DIR should contain one subdirectory per bucket, e.g.:
#   snapshot/
#     reports/
#     exports/
#
# Environment overrides:
#   MINIO_CONTAINER       - container name (default: investbyyourself-minio)
#   MINIO_ROOT_USER       - access key (default: read from container env)
#   MINIO_ROOT_PASSWORD   - secret key (default: read from container env)
#   FORCE                 - set to 1 to skip the confirmation prompt

set -euo pipefail

SRC="${1:-}"
if [ -z "${SRC}" ] || [ ! -d "${SRC}" ]; then
    echo "Usage: $0 SNAPSHOT_DIR" >&2
    exit 2
fi

MINIO_CONTAINER="${MINIO_CONTAINER:-investbyyourself-minio}"

if ! docker ps --format '{{.Names}}' | grep -qx "${MINIO_CONTAINER}"; then
    echo "[restore_minio] container ${MINIO_CONTAINER} is not running" >&2
    exit 1
fi

if [ -z "${MINIO_ROOT_USER:-}" ]; then
    MINIO_ROOT_USER="$(docker exec "${MINIO_CONTAINER}" sh -c 'echo "$MINIO_ROOT_USER"')"
fi
if [ -z "${MINIO_ROOT_PASSWORD:-}" ]; then
    MINIO_ROOT_PASSWORD="$(docker exec "${MINIO_CONTAINER}" sh -c 'echo "$MINIO_ROOT_PASSWORD"')"
fi

ABS_SRC="$(cd "${SRC}" && pwd)"

# List bucket subdirectories at the top level of the snapshot.
BUCKETS=$(find "${ABS_SRC}" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null || \
          ls -1 "${ABS_SRC}" | while read -r d; do [ -d "${ABS_SRC}/${d}" ] && echo "${d}"; done)

if [ -z "${BUCKETS}" ]; then
    echo "[restore_minio] no bucket directories found in ${ABS_SRC}" >&2
    exit 1
fi

if [ "${FORCE:-0}" != "1" ]; then
    echo "About to MIRROR (overwrite + remove extras) buckets in ${MINIO_CONTAINER}:"
    echo "${BUCKETS}" | sed 's/^/  - /'
    read -r -p "Type yes to confirm: " CONFIRM
    if [ "${CONFIRM}" != "yes" ]; then
        echo "[restore_minio] aborted" >&2
        exit 1
    fi
fi

MC_IMAGE="${MC_IMAGE:-minio/mc:latest}"
MINIO_NETWORK="${MINIO_NETWORK:-services_investbyyourself-network}"

if ! docker network ls --format '{{.Name}}' | grep -qx "${MINIO_NETWORK}"; then
    DETECTED=$(docker inspect "${MINIO_CONTAINER}" \
        --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}' \
        | head -1)
    if [ -n "${DETECTED}" ]; then
        MINIO_NETWORK="${DETECTED}"
    fi
fi

run_mc() {
    docker run --rm \
        --network "${MINIO_NETWORK}" \
        -v "${ABS_SRC}:/restore:ro" \
        -e MC_HOST_minio="http://${MINIO_ROOT_USER}:${MINIO_ROOT_PASSWORD}@${MINIO_CONTAINER}:9000" \
        "${MC_IMAGE}" "$@"
}

for BUCKET in ${BUCKETS}; do
    echo "[restore_minio] ensuring bucket exists: ${BUCKET}"
    run_mc mb --ignore-existing "minio/${BUCKET}" >/dev/null
    echo "[restore_minio] mirroring /restore/${BUCKET} -> minio/${BUCKET}"
    run_mc mirror --overwrite --remove "/restore/${BUCKET}" "minio/${BUCKET}"
done

echo "[restore_minio] OK"
