# Database Quick Reference Guide
## InvestByYourself Financial Platform

**Database**: `investbyyourself`
**Schema**: `public`
**Total Tables**: 13

---

## 📊 **Table Overview**

| Table | Purpose | Key Fields | Relationships |
|-------|---------|------------|---------------|
| `companies` | Company master data | `id`, `symbol`, `name`, `sector` | Referenced by all financial tables |
| `company_profiles` | Extended company info | `company_id`, `profile_date`, `business_summary` | → `companies.id` |
| `financial_ratios` | Financial metrics | `company_id`, `ratio_date`, `ratio_type`, `ratio_value` | → `companies.id` |
| `financial_statements` | Financial statements | `company_id`, `statement_date`, `statement_type` | → `companies.id` |
| `market_data` | Stock prices & volume | `company_id`, `data_date`, `close_price`, `volume` | → `companies.id` |
| `economic_indicators` | Economic data | `indicator_name`, `value`, `date` | Standalone |
| `data_collection_logs` | ETL tracking | `operation`, `status`, `timestamp` | Standalone |
| `data_quality` | Quality metrics | `table_name`, `quality_score`, `date` | Standalone |
| `schema_versions` | Migration tracking | `version`, `description`, `applied_date` | Standalone |
| `users` | User accounts | `id`, `username`, `email`, `risk_tolerance` | Referenced by portfolio tables |
| `portfolios` | Investment portfolios | `id`, `user_id`, `name`, `currency` | → `users.id` |
| `portfolio_holdings` | Stock positions | `portfolio_id`, `company_id`, `shares`, `cost_basis` | → `portfolios.id`, `companies.id` |
| `user_watchlists` | User watchlists | `user_id`, `company_id`, `added_date` | → `users.id`, `companies.id` |

---

## 🔗 **Key Relationships**

### **Core Business Data Flow**
```
companies ← financial_ratios
     ↓           ↓
financial_statements ← market_data
     ↓           ↓
company_profiles ← economic_indicators
```

### **User Management Flow**
```
users → portfolios → portfolio_holdings → companies
  ↓           ↓
user_watchlists → companies
```

---

## 🎯 **Common Queries**

### **Get Company with Financial Data**
```sql
SELECT
    c.symbol, c.name, c.sector,
    fr.ratio_type, fr.ratio_value,
    md.close_price, md.volume
FROM companies c
LEFT JOIN financial_ratios fr ON c.id = fr.company_id
LEFT JOIN market_data md ON c.id = md.company_id
WHERE c.symbol = 'AAPL';
```

### **Get User Portfolio Summary**
```sql
SELECT
    u.username,
    p.name as portfolio_name,
    COUNT(ph.company_id) as holdings_count,
    SUM(ph.shares * ph.cost_basis) as total_value
FROM users u
JOIN portfolios p ON u.id = p.user_id
LEFT JOIN portfolio_holdings ph ON p.id = ph.portfolio_id
GROUP BY u.username, p.name;
```

### **Get Data Quality Status**
```sql
SELECT
    table_name,
    quality_score,
    date
FROM data_quality
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date DESC, quality_score;
```

---

## 🚀 **Performance Tips**

### **Indexes Available**
- `companies`: `symbol`, `sector`, `industry`
- `financial_ratios`: `company_id`, `ratio_date`, `ratio_type`
- `market_data`: `company_id`, `data_date`
- `users`: `username`, `email`
- `portfolios`: `user_id`
- `portfolio_holdings`: `portfolio_id`, `company_id`

### **Query Optimization**
- Use `company_id` for joins (not `symbol`)
- Filter by `data_date` for time-series data
- Use `LIMIT` for large result sets
- Leverage JSONB for flexible data in `market_data.alternative_prices`

---

## 🔧 **Maintenance Queries**

### **Check Table Sizes**
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### **Check Recent Activity**
```sql
SELECT
    schemaname,
    relname,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as current_rows
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC;
```

### **Check Foreign Key Constraints**
```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
```

---

## 📝 **Data Types Reference**

| Field Type | Examples | Use Case |
|------------|----------|----------|
| `UUID` | Primary keys, foreign keys | Unique identifiers |
| `VARCHAR(n)` | Company names, symbols | Text with length limits |
| `DECIMAL(p,s)` | Prices, ratios, amounts | Financial calculations |
| `DATE` | Financial dates, birthdays | Date-only values |
| `TIMESTAMP` | Created/updated times | Precise time tracking |
| `BOOLEAN` | Active flags, defaults | True/false values |
| `TEXT` | Descriptions, summaries | Long text content |
| `JSONB` | Alternative prices, metadata | Flexible structured data |
| `INTEGER` | Counts, years, IDs | Whole numbers |
| `BIGINT` | Volume, large counts | Very large numbers |

---

## 🚨 **Important Notes**

1. **UUID Primary Keys**: All tables use UUIDs for scalability
2. **Timestamps**: All tables track `created_at` and `updated_at`
3. **Foreign Keys**: Proper referential integrity enforced
4. **Data Validation**: Quality scoring and validation in place
5. **Multi-currency**: Support for USD and other currencies
6. **Exchange Support**: Multiple exchanges per company supported

---

**Last Updated**: August 24, 2025
**Database Version**: PostgreSQL 17.6
**Schema Version**: 1.1.0 (Tech-010)
