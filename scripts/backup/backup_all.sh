#!/usr/bin/env bash
# backup_all.sh - Run all production backups (Postgres, Redis, MinIO).
#
# Usage:
#   ./scripts/backup/backup_all.sh [BACKUP_DIR]
#
# Environment:
#   BACKUP_DIR   - Root directory for snapshots (default: ./backups)
#   RETAIN_DAYS  - Days of hot snapshots to keep (default: 7)
#
# Exit codes:
#   0 - all backups succeeded
#   1 - at least one backup failed (check log)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${1:-${BACKUP_DIR:-./backups}}"
RETAIN_DAYS="${RETAIN_DAYS:-7}"

TIMESTAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
SNAPSHOT_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

mkdir -p "${SNAPSHOT_DIR}"
echo "[backup_all] snapshot dir: ${SNAPSHOT_DIR}"

FAILED=0

run_step() {
    local label="$1"
    shift
    echo "[backup_all] >>> ${label}"
    if "$@"; then
        echo "[backup_all] <<< ${label} OK"
    else
        echo "[backup_all] <<< ${label} FAILED" >&2
        FAILED=1
    fi
}

run_step "postgres" "${SCRIPT_DIR}/backup_postgres.sh" "${SNAPSHOT_DIR}/postgres.dump"
run_step "redis"    "${SCRIPT_DIR}/backup_redis.sh"    "${SNAPSHOT_DIR}/redis-dump.rdb"
run_step "minio"    "${SCRIPT_DIR}/backup_minio.sh"    "${SNAPSHOT_DIR}/minio"

cat > "${SNAPSHOT_DIR}/manifest.json" <<EOF
{
  "timestamp_utc": "${TIMESTAMP}",
  "host": "$(hostname)",
  "files": {
    "postgres": "postgres.dump",
    "redis": "redis-dump.rdb",
    "minio": "minio/"
  },
  "status": $( [ $FAILED -eq 0 ] && echo '"ok"' || echo '"partial_failure"' )
}
EOF

if command -v sha256sum >/dev/null 2>&1; then
    ( cd "${SNAPSHOT_DIR}" && \
      find . -type f ! -name 'checksums.sha256' -print0 | \
      xargs -0 sha256sum > checksums.sha256 )
fi

echo "[backup_all] pruning snapshots older than ${RETAIN_DAYS} days from ${BACKUP_ROOT}"
find "${BACKUP_ROOT}" -maxdepth 1 -type d -name '20*' -mtime +"${RETAIN_DAYS}" \
    -exec rm -rf {} \; 2>/dev/null || true

if [ $FAILED -eq 0 ]; then
    echo "[backup_all] SUCCESS - snapshot at ${SNAPSHOT_DIR}"
    exit 0
else
    echo "[backup_all] FAILURE - one or more steps failed (see above)" >&2
    exit 1
fi
