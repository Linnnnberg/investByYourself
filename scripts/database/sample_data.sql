
-- Sample Companies Data
INSERT INTO companies (symbol, name, sector, industry, exchange, country, website, description, employee_count, market_cap, enterprise_value, ceo, headquarters, founded_year, is_active) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 'NASDAQ', 'United States', 'https://www.apple.com', 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables and accessories worldwide.', 164000, 3000000000000, 3200000000000, 'Tim Cook', 'Cupertino, CA', 1976, true),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 'NASDAQ', 'United States', 'https://www.microsoft.com', 'Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.', 221000, 2800000000000, 3000000000000, 'Satya Nadella', 'Redmond, WA', 1975, true),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Content & Information', 'NASDAQ', 'United States', 'https://www.abc.xyz', 'Alphabet Inc. is an American multinational technology conglomerate holding company.', 156500, 1800000000000, 1900000000000, 'Sundar Pichai', 'Mountain View, CA', 2015, true),
('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 'Internet Retail', 'NASDAQ', 'United States', 'https://www.amazon.com', 'Amazon.com Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally.', 1608000, 1700000000000, 1800000000000, 'Andy Jassy', 'Seattle, WA', 1994, true),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 'NASDAQ', 'United States', 'https://www.tesla.com', 'Tesla Inc. designs, develops, manufactures, leases and sells electric vehicles, and energy generation and storage systems.', 127855, 800000000000, 900000000000, 'Elon Musk', 'Austin, TX', 2003, true),
('JNJ', 'Johnson & Johnson', 'Healthcare', 'Drug Manufacturers', 'NYSE', 'United States', 'https://www.jnj.com', 'Johnson & Johnson researches, develops, manufactures and sells various products in the healthcare field worldwide.', 134000, 450000000000, 480000000000, 'Joaquin Duato', 'New Brunswick, NJ', 1886, true),
('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 'Banks', 'NYSE', 'United States', 'https://www.jpmorganchase.com', 'JPMorgan Chase & Co. operates as a financial services company worldwide.', 256105, 400000000000, 450000000000, 'Jamie Dimon', 'New York, NY', 1799, true),
('PG', 'Procter & Gamble Co.', 'Consumer Defensive', 'Household & Personal Products', 'NYSE', 'United States', 'https://www.pg.com', 'The Procter & Gamble Company provides branded consumer packaged goods to consumers through mass merchandisers.', 101000, 350000000000, 380000000000, 'Jon Moeller', 'Cincinnati, OH', 1837, true),
('XOM', 'Exxon Mobil Corp.', 'Energy', 'Oil & Gas Integrated', 'NYSE', 'United States', 'https://www.exxonmobil.com', 'Exxon Mobil Corporation explores for and produces crude oil and natural gas in the United States and internationally.', 63000, 450000000000, 480000000000, 'Darren Woods', 'Irving, TX', 1999, true)
ON CONFLICT (symbol) DO UPDATE SET
    name = EXCLUDED.name,
    sector = EXCLUDED.sector,
    industry = EXCLUDED.industry,
    market_cap = EXCLUDED.market_cap,
    enterprise_value = EXCLUDED.enterprise_value,
    updated_at = CURRENT_TIMESTAMP;

-- Sample Market Data (last 30 days)
INSERT INTO market_data (company_id, data_date, open_price, high_price, low_price, close_price, adjusted_close, volume, market_cap, pe_ratio, pb_ratio, ps_ratio, dividend_yield, beta, source)
SELECT
    c.id,
    CURRENT_DATE - INTERVAL '1 day' * generate_series(0, 29),
    150.00 + (random() * 50 - 25),  -- Open price with variation
    150.00 + (random() * 50 - 25) + (random() * 10),  -- High price
    150.00 + (random() * 50 - 25) - (random() * 10),  -- Low price
    150.00 + (random() * 50 - 25),  -- Close price
    150.00 + (random() * 50 - 25),  -- Adjusted close
    1000000 + (random() * 5000000),  -- Volume
    c.market_cap,
    15.0 + (random() * 20),  -- P/E ratio
    2.0 + (random() * 3),    -- P/B ratio
    3.0 + (random() * 5),    -- P/S ratio
    0.01 + (random() * 0.04), -- Dividend yield
    0.8 + (random() * 0.8),   -- Beta
    'sample_data'
FROM companies c
WHERE c.symbol IN ('AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA')
ON CONFLICT (company_id, data_date) DO UPDATE SET
    open_price = EXCLUDED.open_price,
    high_price = EXCLUDED.high_price,
    low_price = EXCLUDED.low_price,
    close_price = EXCLUDED.close_price,
    adjusted_close = EXCLUDED.adjusted_close,
    volume = EXCLUDED.volume,
    pe_ratio = EXCLUDED.pe_ratio,
    pb_ratio = EXCLUDED.pb_ratio,
    ps_ratio = EXCLUDED.ps_ratio,
    dividend_yield = EXCLUDED.dividend_yield,
    beta = EXCLUDED.beta;

-- Sample Financial Ratios
INSERT INTO financial_ratios (company_id, ratio_date, ratio_type, ratio_value, ratio_unit, source, confidence_score)
SELECT
    c.id,
    CURRENT_DATE - INTERVAL '1 month' * generate_series(0, 11),
    'pe_ratio',
    15.0 + (random() * 20),
    'ratio',
    'sample_data',
    0.9 + (random() * 0.1)
FROM companies c
WHERE c.symbol IN ('AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA')
ON CONFLICT (company_id, ratio_date, ratio_type) DO UPDATE SET
    ratio_value = EXCLUDED.ratio_value,
    confidence_score = EXCLUDED.confidence_score;

-- Sample Economic Indicators
INSERT INTO economic_indicators (indicator_date, indicator_type, indicator_value, indicator_unit, period_type, source)
VALUES
(CURRENT_DATE - INTERVAL '1 month', 'CPI', 300.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
(CURRENT_DATE - INTERVAL '2 months', 'CPI', 299.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
(CURRENT_DATE - INTERVAL '3 months', 'CPI', 298.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
(CURRENT_DATE - INTERVAL '1 month', 'GDP', 20.0 + (random() * 2), 'trillions', 'quarterly', 'sample_data'),
(CURRENT_DATE - INTERVAL '2 months', 'GDP', 19.8 + (random() * 2), 'trillions', 'quarterly', 'sample_data'),
(CURRENT_DATE - INTERVAL '3 months', 'GDP', 19.6 + (random() * 2), 'trillions', 'quarterly', 'sample_data')
ON CONFLICT (indicator_date, indicator_type) DO UPDATE SET
    indicator_value = EXCLUDED.indicator_value;
