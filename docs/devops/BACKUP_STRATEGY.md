# InvestByYourself Backup & Restore Strategy

Tech-020: Microservices Foundation - Production Readiness

This document describes how persistent data is backed up and restored for the
InvestByYourself stack.

## What is backed up

| Service  | Data                                | Volume          | Backup format                  |
| -------- | ----------------------------------- | --------------- | ------------------------------ |
| Postgres | Application database                | `postgres_data` | `pg_dump` custom format (`.dump`) |
| Redis    | Session/cache (RDB snapshot)        | `redis_data`    | `dump.rdb` copy                |
| MinIO    | Reports, exports, uploaded objects  | `minio_data`    | `mc mirror` to backup bucket   |

> Frontend, API, ETL, and analysis services are stateless containers - no
> backup needed beyond the source code in git.

## Retention policy

| Tier         | Frequency  | Retention | Location                          |
| ------------ | ---------- | --------- | --------------------------------- |
| Hot          | Daily      | 7 days    | Local disk (`./backups/`)         |
| Warm         | Weekly     | 4 weeks   | Local disk (`./backups/weekly/`)  |
| Cold         | Monthly    | 12 months | Off-site (S3-compatible bucket)   |

The provided scripts handle the hot tier. Wire them into cron / Task Scheduler
and add an off-site sync (e.g. `aws s3 sync`, `rclone copy`) for warm/cold.

## RPO / RTO targets

- **RPO** (Recovery Point Objective): 24 hours - daily backups acceptable
  for current scale. Tighten to hourly via WAL archiving once we have paying
  users.
- **RTO** (Recovery Time Objective): 1 hour - tested via the documented
  restore procedure below.

## Prerequisites

- Production stack running (`services/docker-compose.yml` +
  `services/docker-compose.prod.yml`).
- Bash shell on the host (Linux/macOS, or Git Bash / WSL2 on Windows).
- `docker` and `docker-compose` on PATH.
- Sufficient free disk space: budget at least 3x the size of `postgres_data`.

## Scripts

All scripts live in `scripts/backup/` and are idempotent and safe to re-run.

| Script                  | Purpose                                       |
| ----------------------- | --------------------------------------------- |
| `backup_all.sh`         | Run all three backups. Wire this into cron.   |
| `backup_postgres.sh`    | Postgres logical dump via `pg_dump -Fc`.      |
| `backup_redis.sh`       | Trigger `BGSAVE` and copy `dump.rdb`.         |
| `backup_minio.sh`       | Mirror MinIO buckets via `mc mirror`.         |
| `restore_postgres.sh`   | Restore from a `.dump` file via `pg_restore`. |
| `restore_redis.sh`      | Stop Redis, replace `dump.rdb`, start Redis.  |
| `restore_minio.sh`      | Mirror a backup snapshot back into MinIO.     |

Each script writes to `BACKUP_DIR` (default `./backups/`) with a timestamped
subdirectory like `backups/2026-05-04T03-00-00/`.

## Daily backup (production)

### Linux/macOS cron

```cron
# Daily at 03:00 local time
0 3 * * * cd /opt/investbyyourself && ./scripts/backup/backup_all.sh >> /var/log/ibyy-backup.log 2>&1
```

### Windows Task Scheduler

```powershell
# Run as Administrator
$action = New-ScheduledTaskAction -Execute "bash.exe" `
  -Argument "-c 'cd /d/Cursor\ Workspace/InvestByYourself && ./scripts/backup/backup_all.sh'"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -TaskName "InvestByYourself-Backup" -Action $action -Trigger $trigger
```

## Restore procedure

> ### Test restores quarterly. A backup that has never been restored is not a backup.

### 1. Identify the snapshot

```bash
ls -lah backups/
# e.g. backups/2026-05-04T03-00-00/
#        postgres.dump
#        redis-dump.rdb
#        minio/  (mirror tree)
#        manifest.json
```

The `manifest.json` records timestamps, file sizes, and checksums.

### 2. Stop application services (preserve infra services)

```bash
cd services
docker-compose --compatibility \
  -f docker-compose.yml -f docker-compose.prod.yml \
  stop etl-service financial-analysis-service data-service api-gateway
```

### 3. Restore each datastore

```bash
SNAPSHOT=backups/2026-05-04T03-00-00

./scripts/backup/restore_postgres.sh "$SNAPSHOT/postgres.dump"
./scripts/backup/restore_redis.sh    "$SNAPSHOT/redis-dump.rdb"
./scripts/backup/restore_minio.sh    "$SNAPSHOT/minio"
```

### 4. Restart application services and verify

```bash
docker-compose --compatibility \
  -f docker-compose.yml -f docker-compose.prod.yml \
  up -d

# Health checks
curl -f http://localhost/api/data/health
curl -f http://localhost/api/etl/health
curl -f http://localhost/api/analysis/health
```

### 5. Smoke test

- Log in to the frontend.
- Load a portfolio that existed before the incident.
- Run one analysis request.
- Spot-check 1-2 reports stored in MinIO.

## Verifying backup integrity

`backup_postgres.sh` runs `pg_restore --list` against each new dump to confirm
it is readable. `backup_redis.sh` checks the file header magic. `backup_minio.sh`
relies on `mc diff` for an empty diff. Failures cause non-zero exit codes
(picked up by cron logs).

For an end-to-end integrity test:

```bash
# Quarterly drill - run on a staging host, not production
./scripts/backup/restore_postgres.sh backups/<latest>/postgres.dump
docker exec investbyyourself-postgres psql -U postgres -d investbyyourself \
  -c "SELECT count(*) FROM companies;"
```

## Off-site replication (cold tier)

After `backup_all.sh` succeeds, replicate the snapshot directory off-site. Two
common options:

### S3 (or S3-compatible)

```bash
aws s3 sync ./backups/ s3://ibyy-backups/$(hostname)/ \
  --storage-class STANDARD_IA \
  --delete
```

### rclone (any cloud)

```bash
rclone copy ./backups/ remote:ibyy-backups --progress
```

Encrypt sensitive backups at rest. Use `gpg --symmetric` or rclone's `crypt`
backend for cold storage.

## Security

- Backup files contain real production data. Treat them as production secrets.
- Never check backups into git (covered by `.gitignore`: `*.dump`, `*.rdb`,
  `backups/`).
- Restrict filesystem permissions: `chmod 700 backups/` and `chown` to the
  backup user.
- Rotate database superuser passwords periodically; the scripts read
  credentials from the running container's environment so no hard-coded
  secrets are needed.

## See also

- `services/docker-compose.prod.yml` - production stack with resource limits
- `docs/devops/DOCKER_SETUP_GUIDE.md` - general Docker operations
- `docs/devops/DOCKER_INTEGRATION_IMPROVEMENTS.md` - tracking doc for this work
