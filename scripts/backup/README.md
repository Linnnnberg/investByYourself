# Backup & Restore Scripts

Operational scripts for the InvestByYourself production data tier.

See `docs/devops/BACKUP_STRATEGY.md` for the full strategy, retention policy,
RPO/RTO targets, and off-site replication guidance.

## Quick reference

```bash
# Daily backup (cron-friendly)
./scripts/backup/backup_all.sh ./backups

# Restore a snapshot
SNAP=./backups/2026-05-04T03-00-00Z
./scripts/backup/restore_postgres.sh "$SNAP/postgres.dump"
./scripts/backup/restore_redis.sh    "$SNAP/redis-dump.rdb"
./scripts/backup/restore_minio.sh    "$SNAP/minio"
```

## Make scripts executable

After cloning, run once:

```bash
chmod +x scripts/backup/*.sh
```

## Windows note

These scripts target Bash. On Windows, run them via Git Bash or WSL2. Docker
Desktop must be running with the Linux engine.
