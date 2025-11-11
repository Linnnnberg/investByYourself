-- =====================================================
-- TGA Liquidity Tracking Schema
-- Migration 002: Add TGA and comprehensive liquidity tracking
-- =====================================================

-- TGA (Treasury General Account) daily balances
CREATE TABLE IF NOT EXISTS tga_daily_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_date DATE NOT NULL UNIQUE,

    -- Raw TGA data (millions of USD)
    close_balance DECIMAL(20, 2) NOT NULL,
    open_balance DECIMAL(20, 2),
    open_month_balance DECIMAL(20, 2),

    -- Calculated metrics
    daily_change_billions DECIMAL(15, 6),
    liquidity_contribution DECIMAL(20, 6),

    -- Moving averages (millions USD)
    ma_7day DECIMAL(20, 2),
    ma_30day DECIMAL(20, 2),
    ma_90day DECIMAL(20, 2),

    -- Statistical metrics
    volatility_30d DECIMAL(15, 6),
    zscore_90d DECIMAL(10, 6),
    pct_change_7d DECIMAL(10, 4),
    liquidity_index_norm DECIMAL(10, 4),

    -- Stress indicators
    is_liquidity_stress BOOLEAN DEFAULT FALSE,

    -- Metadata
    source VARCHAR(50) DEFAULT 'treasury.gov',
    collected_at TIMESTAMP,
    calculated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comprehensive liquidity index (multi-factor)
CREATE TABLE IF NOT EXISTS liquidity_index_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    index_date DATE NOT NULL UNIQUE,

    -- Component balances (millions USD)
    tga_balance DECIMAL(20, 2),
    fed_balance_sheet DECIMAL(20, 2),
    reverse_repo DECIMAL(20, 2),
    bank_reserves DECIMAL(20, 2),

    -- Component changes (millions USD)
    tga_change DECIMAL(20, 2),
    fed_bs_change DECIMAL(20, 2),
    rrp_change DECIMAL(20, 2),
    reserves_change DECIMAL(20, 2),

    -- Composite metrics
    liquidity_daily DECIMAL(20, 2),
    liquidity_index DECIMAL(20, 2),
    liquidity_index_billions DECIMAL(15, 6),

    -- Smoothed indices
    liquidity_index_7d_ma DECIMAL(15, 6),
    liquidity_index_30d_ma DECIMAL(15, 6),

    -- Market context (optional)
    spy_market_cap DECIMAL(20, 2),
    liquidity_to_market_ratio DECIMAL(10, 6),

    -- Metadata
    calculation_method VARCHAR(50) DEFAULT 'multi_factor',
    data_completeness DECIMAL(3, 2),
    calculated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Liquidity events and alerts
CREATE TABLE IF NOT EXISTS liquidity_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- 'stress', 'spike', 'drain', 'surge'
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'

    -- Event details
    trigger_metric VARCHAR(50), -- 'tga_zscore', 'volatility', 'liquidity_index'
    trigger_value DECIMAL(15, 6),
    threshold_value DECIMAL(15, 6),

    -- Context
    tga_balance DECIMAL(20, 2),
    liquidity_index DECIMAL(20, 2),
    description TEXT,

    -- Market impact
    market_impact_expected VARCHAR(20), -- 'bullish', 'bearish', 'neutral'

    -- Alert status
    alert_sent BOOLEAN DEFAULT FALSE,
    alert_sent_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Liquidity correlation tracking
-- Tracks correlation between liquidity changes and market movements
CREATE TABLE IF NOT EXISTS liquidity_market_correlation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_date DATE NOT NULL,
    analysis_period VARCHAR(20) NOT NULL, -- '7d', '30d', '90d', '180d'

    -- Correlation coefficients
    tga_spy_correlation DECIMAL(6, 4),
    tga_qqq_correlation DECIMAL(6, 4),
    liquidity_index_spy_correlation DECIMAL(6, 4),
    liquidity_index_qqq_correlation DECIMAL(6, 4),

    -- Lead-lag analysis
    optimal_lag_days INTEGER,
    lagged_correlation DECIMAL(6, 4),

    -- Statistical significance
    p_value DECIMAL(10, 8),
    is_significant BOOLEAN,

    -- Metadata
    sample_size INTEGER,
    calculated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(analysis_date, analysis_period)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_tga_daily_balances_date ON tga_daily_balances(record_date DESC);
CREATE INDEX idx_tga_daily_balances_stress ON tga_daily_balances(is_liquidity_stress) WHERE is_liquidity_stress = TRUE;
CREATE INDEX idx_tga_daily_balances_date_range ON tga_daily_balances(record_date) WHERE record_date >= CURRENT_DATE - INTERVAL '2 years';

CREATE INDEX idx_liquidity_index_daily_date ON liquidity_index_daily(index_date DESC);
CREATE INDEX idx_liquidity_index_daily_recent ON liquidity_index_daily(index_date) WHERE index_date >= CURRENT_DATE - INTERVAL '1 year';

CREATE INDEX idx_liquidity_events_date ON liquidity_events(event_date DESC);
CREATE INDEX idx_liquidity_events_type ON liquidity_events(event_type);
CREATE INDEX idx_liquidity_events_severity ON liquidity_events(severity);
CREATE INDEX idx_liquidity_events_pending_alerts ON liquidity_events(alert_sent) WHERE alert_sent = FALSE;

CREATE INDEX idx_liquidity_correlation_date ON liquidity_market_correlation(analysis_date DESC);
CREATE INDEX idx_liquidity_correlation_period ON liquidity_market_correlation(analysis_period);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Latest TGA status view
CREATE OR REPLACE VIEW v_tga_latest_status AS
SELECT
    record_date,
    close_balance / 1000 AS balance_billions,
    daily_change_billions,
    ma_7day / 1000 AS ma_7day_billions,
    ma_30day / 1000 AS ma_30day_billions,
    volatility_30d AS volatility_billions,
    zscore_90d,
    is_liquidity_stress,
    liquidity_contribution AS liquidity_index
FROM tga_daily_balances
WHERE record_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY record_date DESC;

-- Liquidity summary view
CREATE OR REPLACE VIEW v_liquidity_summary AS
SELECT
    l.index_date,
    l.tga_balance / 1000 AS tga_billions,
    l.fed_balance_sheet / 1000 AS fed_bs_billions,
    l.reverse_repo / 1000 AS rrp_billions,
    l.liquidity_index_billions,
    l.liquidity_index_7d_ma,
    l.liquidity_index_30d_ma,
    t.is_liquidity_stress,
    t.zscore_90d AS tga_zscore
FROM liquidity_index_daily l
LEFT JOIN tga_daily_balances t ON l.index_date = t.record_date
WHERE l.index_date >= CURRENT_DATE - INTERVAL '1 year'
ORDER BY l.index_date DESC;

-- Active liquidity events view
CREATE OR REPLACE VIEW v_active_liquidity_events AS
SELECT
    event_date,
    event_type,
    severity,
    trigger_metric,
    trigger_value,
    tga_balance / 1000 AS tga_billions,
    liquidity_index / 1000 AS liquidity_index_billions,
    market_impact_expected,
    description,
    alert_sent
FROM liquidity_events
WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY event_date DESC, severity DESC;

-- Recent correlation analysis view
CREATE OR REPLACE VIEW v_liquidity_correlation_recent AS
SELECT
    analysis_date,
    analysis_period,
    tga_spy_correlation,
    liquidity_index_spy_correlation,
    optimal_lag_days,
    lagged_correlation,
    is_significant,
    sample_size
FROM liquidity_market_correlation
WHERE analysis_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY analysis_date DESC, analysis_period;

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE tga_daily_balances IS 'Daily Treasury General Account balances with calculated liquidity metrics';
COMMENT ON TABLE liquidity_index_daily IS 'Comprehensive multi-factor liquidity index combining TGA, Fed balance sheet, RRP, and reserves';
COMMENT ON TABLE liquidity_events IS 'Liquidity stress events and market alerts';
COMMENT ON TABLE liquidity_market_correlation IS 'Statistical correlation between liquidity metrics and market movements';

COMMENT ON COLUMN tga_daily_balances.close_balance IS 'TGA closing balance in millions USD';
COMMENT ON COLUMN tga_daily_balances.daily_change_billions IS 'Daily change in billions (positive = drain, negative = add)';
COMMENT ON COLUMN tga_daily_balances.liquidity_contribution IS 'Cumulative liquidity contribution to markets (-1 * cumsum of daily change)';
COMMENT ON COLUMN tga_daily_balances.zscore_90d IS 'Z-score vs 90-day rolling mean (values >2 indicate stress)';
COMMENT ON COLUMN tga_daily_balances.is_liquidity_stress IS 'True if TGA shows liquidity stress conditions';

COMMENT ON COLUMN liquidity_index_daily.liquidity_index IS 'Cumulative liquidity index: -ΔTGA + ΔFed_BS - ΔRRP + ΔReserves';
COMMENT ON COLUMN liquidity_index_daily.liquidity_to_market_ratio IS 'Liquidity index normalized by S&P 500 market cap';

-- =====================================================
-- TRIGGERS FOR UPDATED_AT
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tga_daily_balances_updated_at
    BEFORE UPDATE ON tga_daily_balances
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_liquidity_index_daily_updated_at
    BEFORE UPDATE ON liquidity_index_daily
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
