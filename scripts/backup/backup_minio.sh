#!/usr/bin/env bash
# backup_minio.sh - Mirror MinIO buckets to a local directory using mc.
#
# Usage:
#   ./scripts/backup/backup_minio.sh OUTPUT_DIR
#
# Environment overrides:
#   MINIO_CONTAINER       - container name (default: investbyyourself-minio)
#   MINIO_ROOT_USER       - access key (default: read from container env)
#   MINIO_ROOT_PASSWORD   - secret key (default: read from container env)
#   MINIO_BUCKETS         - space-separated bucket list (default: all)

set -euo pipefail

OUT="${1:-}"
if [ -z "${OUT}" ]; then
    echo "Usage: $0 OUTPUT_DIR" >&2
    exit 2
fi

MINIO_CONTAINER="${MINIO_CONTAINER:-investbyyourself-minio}"

if ! docker ps --format '{{.Names}}' | grep -qx "${MINIO_CONTAINER}"; then
    echo "[backup_minio] container ${MINIO_CONTAINER} is not running" >&2
    exit 1
fi

# Read credentials from the running container if not supplied.
if [ -z "${MINIO_ROOT_USER:-}" ]; then
    MINIO_ROOT_USER="$(docker exec "${MINIO_CONTAINER}" sh -c 'echo "$MINIO_ROOT_USER"')"
fi
if [ -z "${MINIO_ROOT_PASSWORD:-}" ]; then
    MINIO_ROOT_PASSWORD="$(docker exec "${MINIO_CONTAINER}" sh -c 'echo "$MINIO_ROOT_PASSWORD"')"
fi

if [ -z "${MINIO_ROOT_USER}" ] || [ -z "${MINIO_ROOT_PASSWORD}" ]; then
    echo "[backup_minio] credentials are empty - check container env" >&2
    exit 1
fi

mkdir -p "${OUT}"
ABS_OUT="$(cd "${OUT}" && pwd)"

# Use the official mc image. It joins the same network as MinIO via --network.
MC_IMAGE="${MC_IMAGE:-minio/mc:latest}"
MINIO_NETWORK="${MINIO_NETWORK:-services_investbyyourself-network}"

# Resolve actual network name (compose may prefix with project name).
if ! docker network ls --format '{{.Name}}' | grep -qx "${MINIO_NETWORK}"; then
    DETECTED=$(docker inspect "${MINIO_CONTAINER}" \
        --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}' \
        | head -1)
    if [ -n "${DETECTED}" ]; then
        MINIO_NETWORK="${DETECTED}"
    fi
fi

echo "[backup_minio] mirroring buckets to ${ABS_OUT} via network ${MINIO_NETWORK}"

run_mc() {
    docker run --rm \
        --network "${MINIO_NETWORK}" \
        -v "${ABS_OUT}:/backup" \
        -e MC_HOST_minio="http://${MINIO_ROOT_USER}:${MINIO_ROOT_PASSWORD}@${MINIO_CONTAINER}:9000" \
        "${MC_IMAGE}" "$@"
}

if [ -z "${MINIO_BUCKETS:-}" ]; then
    BUCKETS=$(run_mc ls minio --json 2>/dev/null | \
        sed -n 's/.*"key":"\([^"/]*\)\/".*/\1/p' || true)
else
    BUCKETS="${MINIO_BUCKETS}"
fi

if [ -z "${BUCKETS}" ]; then
    echo "[backup_minio] no buckets found - creating empty marker"
    touch "${ABS_OUT}/.empty"
    echo "[backup_minio] OK - no buckets to back up"
    exit 0
fi

for BUCKET in ${BUCKETS}; do
    echo "[backup_minio]   mirroring bucket: ${BUCKET}"
    mkdir -p "${ABS_OUT}/${BUCKET}"
    run_mc mirror --overwrite --remove "minio/${BUCKET}" "/backup/${BUCKET}"
done

SIZE=$(du -sh "${ABS_OUT}" | awk '{print $1}')
echo "[backup_minio] OK - ${ABS_OUT} (${SIZE})"
