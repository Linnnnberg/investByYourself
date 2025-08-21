-- =====================================================
-- Migration: Tech-010 Schema Update
-- One Company = One Stock (Regardless of Exchange)
-- =====================================================

-- Migration metadata
-- Version: 1.1.0
-- Description: Update schema to support one company per symbol with preferred exchange
-- Dependencies: Existing schema from Tech-008
-- Rollback: Yes (see rollback section at bottom)

BEGIN;

-- =====================================================
-- STEP 1: Add new columns to companies table
-- =====================================================

-- Add preferred exchange and price source columns
ALTER TABLE companies
ADD COLUMN IF NOT EXISTS base_currency VARCHAR(3) DEFAULT 'USD',
ADD COLUMN IF NOT EXISTS preferred_exchange VARCHAR(20),
ADD COLUMN IF NOT EXISTS preferred_price_source VARCHAR(50) DEFAULT 'yfinance';

-- Update existing companies with default preferred exchange based on current exchange
UPDATE companies
SET preferred_exchange = COALESCE(exchange, 'NASDAQ')
WHERE preferred_exchange IS NULL;

-- Update existing companies with default base currency
UPDATE companies
SET base_currency = COALESCE(currency, 'USD')
WHERE base_currency IS NULL;

-- =====================================================
-- STEP 2: Create new user and portfolio tables
-- =====================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency_preference VARCHAR(3) DEFAULT 'USD',
    risk_tolerance VARCHAR(20) DEFAULT 'moderate',
    investment_goals TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    currency VARCHAR(3) DEFAULT 'USD',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);

-- Portfolio holdings table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    shares DECIMAL(15,6) NOT NULL,
    cost_basis DECIMAL(15,4) NOT NULL,
    purchase_date DATE NOT NULL,
    last_purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, company_id)
);

-- User watchlists table
CREATE TABLE IF NOT EXISTS user_watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    added_date DATE DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, company_id)
);

-- =====================================================
-- STEP 3: Update market_data table for multiple price sources
-- =====================================================

-- Add new columns for preferred price data
ALTER TABLE market_data
ADD COLUMN IF NOT EXISTS preferred_price DECIMAL(10,4),
ADD COLUMN IF NOT EXISTS preferred_volume BIGINT,
ADD COLUMN IF NOT EXISTS preferred_exchange VARCHAR(20),
ADD COLUMN IF NOT EXISTS preferred_source VARCHAR(50),
ADD COLUMN IF NOT EXISTS alternative_prices JSONB,
ADD COLUMN IF NOT EXISTS price_consistency_score DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS max_price_difference DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Initialize preferred price data from existing data
UPDATE market_data
SET
    preferred_price = COALESCE(adjusted_close, close_price),
    preferred_volume = volume,
    preferred_exchange = (SELECT preferred_exchange FROM companies WHERE id = market_data.company_id),
    preferred_source = source,
    updated_at = CURRENT_TIMESTAMP
WHERE preferred_price IS NULL;

-- =====================================================
-- STEP 4: Create schema migration and versioning tables
-- =====================================================

-- Schema version tracking table
CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    applied_by VARCHAR(100) DEFAULT 'system',
    migration_file VARCHAR(255),
    checksum VARCHAR(64)
);

-- Data migration logs table
CREATE TABLE IF NOT EXISTS data_migrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    migration_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    records_processed INTEGER DEFAULT 0,
    errors TEXT[],
    rollback_script TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- STEP 5: Create new indexes for performance
-- =====================================================

-- Companies indexes
CREATE INDEX IF NOT EXISTS idx_companies_preferred_exchange ON companies(preferred_exchange);

-- User and portfolio indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_portfolio_id ON portfolio_holdings(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_holdings_company_id ON portfolio_holdings(company_id);
CREATE INDEX IF NOT EXISTS idx_user_watchlists_user_id ON user_watchlists(user_id);

-- Migration indexes
CREATE INDEX IF NOT EXISTS idx_schema_versions_version ON schema_versions(version);
CREATE INDEX IF NOT EXISTS idx_data_migrations_status ON data_migrations(status);

-- =====================================================
-- STEP 6: Create new views
-- =====================================================

-- Portfolio summary view
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT
    p.id as portfolio_id,
    p.name as portfolio_name,
    u.username,
    COUNT(ph.company_id) as total_positions,
    SUM(ph.shares * md.preferred_price) as total_value,
    SUM(ph.shares * ph.cost_basis) as total_cost,
    CASE
        WHEN SUM(ph.shares * ph.cost_basis) > 0
        THEN ((SUM(ph.shares * md.preferred_price) - SUM(ph.shares * ph.cost_basis)) / SUM(ph.shares * ph.cost_basis) * 100
        ELSE 0
    END as total_return_percentage
FROM portfolios p
JOIN users u ON p.user_id = u.id
LEFT JOIN portfolio_holdings ph ON p.id = ph.portfolio_id
LEFT JOIN market_data md ON ph.company_id = md.company_id
WHERE md.data_date = (
    SELECT MAX(data_date)
    FROM market_data md2
    WHERE md2.company_id = ph.company_id
)
GROUP BY p.id, p.name, u.username;

-- =====================================================
-- STEP 7: Create new functions and triggers
-- =====================================================

-- Function to calculate portfolio position value
CREATE OR REPLACE FUNCTION calculate_position_value(
    shares DECIMAL,
    current_price DECIMAL
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN shares * current_price;
END;
$$ LANGUAGE plpgsql;

-- Function to validate company preferences
CREATE OR REPLACE FUNCTION validate_company_preferences()
RETURNS TABLE(company_symbol VARCHAR, has_preferred_exchange BOOLEAN, has_preferred_source BOOLEAN) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.symbol,
        c.preferred_exchange IS NOT NULL,
        c.preferred_price_source IS NOT NULL
    FROM companies c
    WHERE c.is_active = TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to validate portfolio holdings
CREATE OR REPLACE FUNCTION validate_portfolio_holdings()
RETURNS TABLE(portfolio_name VARCHAR, invalid_holdings INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.name,
        COUNT(ph.id) as invalid_holdings
    FROM portfolios p
    LEFT JOIN portfolio_holdings ph ON p.id = ph.portfolio_id
    LEFT JOIN companies c ON ph.company_id = c.id
    WHERE c.id IS NULL OR c.is_active = FALSE
    GROUP BY p.id, p.name;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- STEP 8: Update existing data and constraints
-- =====================================================

-- Ensure all companies have preferred exchange set
UPDATE companies
SET preferred_exchange = 'NASDAQ'
WHERE preferred_exchange IS NULL AND country = 'United States';

UPDATE companies
SET preferred_exchange = 'LSE'
WHERE preferred_exchange IS NULL AND country = 'United Kingdom';

UPDATE companies
SET preferred_exchange = 'XETR'
WHERE preferred_exchange IS NULL AND country = 'Germany';

-- Set default preferred price source for existing companies
UPDATE companies
SET preferred_price_source = 'yfinance'
WHERE preferred_price_source IS NULL;

-- =====================================================
-- STEP 9: Insert migration record
-- =====================================================

INSERT INTO schema_versions (version, description, migration_file, applied_by) VALUES
('1.1.0', 'Tech-010: Enhanced data models with user/portfolio entities and preferred exchange support', '001_tech010_schema_update.sql', 'system');

-- =====================================================
-- STEP 10: Validation and cleanup
-- =====================================================

-- Validate migration
DO $$
DECLARE
    company_count INTEGER;
    user_count INTEGER;
    portfolio_count INTEGER;
BEGIN
    -- Check companies table
    SELECT COUNT(*) INTO company_count FROM companies;
    RAISE NOTICE 'Companies table: % records', company_count;

    -- Check new tables
    SELECT COUNT(*) INTO user_count FROM users;
    RAISE NOTICE 'Users table: % records', user_count;

    SELECT COUNT(*) INTO portfolio_count FROM portfolios;
    RAISE NOTICE 'Portfolios table: % records', portfolio_count;

    -- Validate company preferences
    RAISE NOTICE 'Validating company preferences...';
    PERFORM * FROM validate_company_preferences();

    RAISE NOTICE 'Migration completed successfully!';
END $$;

COMMIT;

-- =====================================================
-- ROLLBACK SCRIPT (if needed)
-- =====================================================
/*
-- To rollback this migration, run:

BEGIN;

-- Drop new tables
DROP TABLE IF EXISTS user_watchlists CASCADE;
DROP TABLE IF EXISTS portfolio_holdings CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop new views
DROP VIEW IF EXISTS portfolio_summary;

-- Drop new functions
DROP FUNCTION IF EXISTS calculate_position_value(DECIMAL, DECIMAL);
DROP FUNCTION IF EXISTS validate_company_preferences();
DROP FUNCTION IF EXISTS validate_portfolio_holdings();

-- Remove new columns from market_data
ALTER TABLE market_data
DROP COLUMN IF EXISTS preferred_price,
DROP COLUMN IF EXISTS preferred_volume,
DROP COLUMN IF EXISTS preferred_exchange,
DROP COLUMN IF EXISTS preferred_source,
DROP COLUMN IF EXISTS alternative_prices,
DROP COLUMN IF EXISTS price_consistency_score,
DROP COLUMN IF EXISTS max_price_difference,
DROP COLUMN IF EXISTS updated_at;

-- Remove new columns from companies
ALTER TABLE companies
DROP COLUMN IF EXISTS base_currency,
DROP COLUMN IF EXISTS preferred_exchange,
DROP COLUMN IF EXISTS preferred_price_source;

-- Drop new indexes
DROP INDEX IF EXISTS idx_companies_preferred_exchange;
DROP INDEX IF EXISTS idx_users_username;
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_portfolios_user_id;
DROP INDEX IF EXISTS idx_portfolio_holdings_portfolio_id;
DROP INDEX IF EXISTS idx_portfolio_holdings_company_id;
DROP INDEX IF EXISTS idx_user_watchlists_user_id;
DROP INDEX IF EXISTS idx_schema_versions_version;
DROP INDEX IF EXISTS idx_data_migrations_status;

-- Drop migration tables
DROP TABLE IF EXISTS data_migrations CASCADE;
DROP TABLE IF EXISTS schema_versions CASCADE;

-- Remove migration record
DELETE FROM schema_versions WHERE version = '1.1.0';

COMMIT;
*/
