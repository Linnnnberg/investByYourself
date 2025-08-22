# Tech-010 Database Migration Guide

## Overview
This migration updates your existing database to implement the new **"One Company = One Stock"** approach.

## What This Migration Does

### ✅ **Adds New Columns to Existing Tables**
- `companies` table: Adds `preferred_exchange`, `preferred_price_source`, `base_currency`
- `market_data` table: Adds preferred price fields and alternative price storage

### 🆕 **Creates New Tables**
- `users` - User accounts and preferences
- `portfolios` - User investment portfolios
- `portfolio_holdings` - Individual positions in portfolios
- `user_watchlists` - Companies users are monitoring
- `schema_versions` - Track database schema changes
- `data_migrations` - Log migration execution

### 🔧 **Adds New Features**
- Portfolio management system
- User authentication framework
- Multiple price source support
- Schema versioning and migration tracking

## How to Apply

### **Option 1: Run Migration Script (Recommended)**
```bash
# Connect to your PostgreSQL database
psql -h localhost -U your_username -d investbyyourself -f database/migrations/001_tech010_schema_update.sql
```

### **Option 2: Use Python Script**
```python
# Run the migration through your ETL system
python scripts/run_migration.py --migration 001_tech010_schema_update.sql
```

## What Happens After Migration

1. **Your existing data is preserved**
2. **New tables are created for users and portfolios**
3. **Existing companies get default preferred exchanges**
4. **Market data gets enhanced with preferred price fields**

## Rollback (If Needed)
The migration script includes a complete rollback section at the bottom (commented out).

## Benefits of This Approach
- ✅ **No data loss** - preserves your existing ETL data
- ✅ **Incremental** - adds new features without rebuilding
- ✅ **Safe** - includes validation and rollback options
- ✅ **Professional** - follows database migration best practices

## Next Steps After Migration
1. Test the new portfolio functionality
2. Create test users and portfolios
3. Verify data integrity
4. Update your ETL pipeline to use preferred exchanges
