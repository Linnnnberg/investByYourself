# 🚀 Supabase Integration Setup Guide

## Overview
This guide will help you set up Supabase integration for the InvestByYourself platform, enabling real-time data synchronization and live prototyping capabilities.

## Prerequisites
- ✅ Supabase project created (Project ID: `ztxlcatckspsdtkepmwy`)
- ✅ Node.js and npm installed
- ✅ Frontend project running

## Step 1: Get Your Supabase Credentials

### 1.1 Access Your Supabase Dashboard
1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Sign in to your account
3. Select your project: **investByYourself**

### 1.2 Get API Keys
1. Navigate to **Settings** → **API**
2. Copy the following values:
   - **Project URL**: `https://ztxlcatckspsdtkepmwy.supabase.co`
   - **anon public key**: (starts with `eyJ...`)
   - **service_role key**: (starts with `eyJ...`)

## Step 2: Configure Environment Variables

### 2.1 Create Environment File
1. Copy `env.example` to `.env.local`:
   ```bash
   cp env.example .env.local
   ```

2. Update `.env.local` with your actual values:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://ztxlcatckspsdtkepmwy.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_actual_anon_key_here
   SUPABASE_SERVICE_ROLE_KEY=your_actual_service_role_key_here
   ```

### 2.2 Restart Your Development Server
```bash
npm run dev
```

## Step 3: Set Up Database Schema

### 3.1 Access SQL Editor
1. In your Supabase dashboard, go to **SQL Editor**
2. Click **New Query**

### 3.2 Create Tables
Run the following SQL to create the required tables:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies table
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  symbol VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  sector VARCHAR(100),
  industry VARCHAR(100),
  market_cap DECIMAL(20,2),
  pe_ratio DECIMAL(10,2),
  price DECIMAL(10,2),
  change DECIMAL(10,2),
  change_percent DECIMAL(5,2),
  volume BIGINT,
  avg_volume BIGINT,
  high_52_week DECIMAL(10,2),
  low_52_week DECIMAL(10,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolios table
CREATE TABLE portfolios (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  total_value DECIMAL(15,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio holdings table
CREATE TABLE portfolio_holdings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
  company_symbol VARCHAR(10) REFERENCES companies(symbol),
  shares INTEGER NOT NULL,
  average_price DECIMAL(10,2) NOT NULL,
  current_value DECIMAL(15,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Watchlist table
CREATE TABLE watchlist (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id VARCHAR(255) NOT NULL,
  company_symbol VARCHAR(10) REFERENCES companies(symbol),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_companies_symbol ON companies(symbol);
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
CREATE INDEX idx_portfolio_holdings_portfolio_id ON portfolio_holdings(portfolio_id);
CREATE INDEX idx_watchlist_user_id ON watchlist(user_id);

-- Create views for easier data access
CREATE VIEW company_overview AS
SELECT
  symbol,
  name,
  sector,
  industry,
  market_cap,
  pe_ratio,
  price,
  change,
  change_percent
FROM companies;

-- Enable Row Level Security (RLS)
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access to companies
CREATE POLICY "Companies are viewable by everyone" ON companies
  FOR SELECT USING (true);

-- Create policies for user-specific data
CREATE POLICY "Users can view their own portfolios" ON portfolios
  FOR SELECT USING (user_id = current_user);

CREATE POLICY "Users can insert their own portfolios" ON portfolios
  FOR INSERT WITH CHECK (user_id = current_user);

CREATE POLICY "Users can update their own portfolios" ON portfolios
  FOR UPDATE USING (user_id = current_user);

CREATE POLICY "Users can delete their own portfolios" ON portfolios
  FOR DELETE USING (user_id = current_user);

-- Similar policies for other tables...
```

## Step 4: Insert Sample Data

### 4.1 Add Sample Companies
```sql
INSERT INTO companies (symbol, name, sector, industry, market_cap, pe_ratio, price, change, change_percent, volume, avg_volume, high_52_week, low_52_week) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 3000000000000, 25.5, 150.25, 2.15, 1.45, 50000000, 45000000, 180.50, 120.75),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 2800000000000, 30.2, 320.80, -1.20, -0.37, 30000000, 28000000, 350.00, 250.25),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Services', 1800000000000, 22.8, 140.50, 0.75, 0.54, 25000000, 22000000, 160.00, 100.50),
('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 'Internet Retail', 1600000000000, 45.3, 130.20, 1.80, 1.40, 40000000, 38000000, 150.00, 90.25),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 800000000000, 65.7, 180.90, -2.10, -1.15, 60000000, 55000000, 220.00, 140.00);
```

### 4.2 Add Sample Portfolio
```sql
INSERT INTO portfolios (user_id, name, description, total_value) VALUES
('demo-user-123', 'Growth Portfolio', 'Technology and growth stocks', 0);

INSERT INTO portfolio_holdings (portfolio_id, company_symbol, shares, average_price, current_value) VALUES
((SELECT id FROM portfolios WHERE user_id = 'demo-user-123' LIMIT 1), 'AAPL', 100, 120.00, 15025.00),
((SELECT id FROM portfolios WHERE user_id = 'demo-user-123' LIMIT 1), 'MSFT', 50, 280.00, 16040.00);
```

### 4.3 Add Sample Watchlist
```sql
INSERT INTO watchlist (user_id, company_symbol) VALUES
('demo-user-123', 'GOOGL'),
('demo-user-123', 'AMZN'),
('demo-user-123', 'TSLA');
```

## Step 5: Test the Integration

### 5.1 Start the Development Server
```bash
npm run dev
```

### 5.2 Navigate to Dashboard
1. Go to `http://localhost:3000/dashboard`
2. You should see real-time data loading
3. Check the connection status indicators

### 5.3 Test Real-time Updates
1. In Supabase dashboard, go to **Table Editor**
2. Select the `companies` table
3. Edit a company's price
4. Watch the dashboard update in real-time!

## Step 6: Enable Real-time Features

### 6.1 Database Replication
1. In Supabase dashboard, go to **Database** → **Replication**
2. Enable replication for all tables
3. Set up real-time subscriptions

### 6.2 Edge Functions (Optional)
1. Go to **Edge Functions**
2. Create functions for custom business logic
3. Deploy and test

## Troubleshooting

### Common Issues

#### 1. "Invalid API key" Error
- ✅ Check your `.env.local` file
- ✅ Verify the key in Supabase dashboard
- ✅ Restart your development server

#### 2. "Table doesn't exist" Error
- ✅ Run the SQL schema creation
- ✅ Check table names match exactly
- ✅ Verify RLS policies are set up

#### 3. Real-time Not Working
- ✅ Enable database replication
- ✅ Check network connectivity
- ✅ Verify subscription channels

#### 4. CORS Issues
- ✅ Add your domain to Supabase allowed origins
- ✅ Check browser console for errors

### Debug Mode
Enable debug logging in `.env.local`:
```env
NEXT_PUBLIC_DEBUG_MODE=true
NEXT_PUBLIC_LOG_LEVEL=debug
```

## Next Steps

### Phase 2 Complete! 🎉
- ✅ Supabase client configured
- ✅ Real-time subscriptions working
- ✅ Database schema created
- ✅ Sample data loaded

### Phase 3: Figma Integration
1. **Connect Figma to Supabase**
2. **Create interactive prototypes**
3. **Build user flow prototypes**
4. **Test with real data**

### Phase 4: Advanced Features
1. **Authentication system**
2. **Advanced analytics**
3. **Mobile optimization**
4. **Performance monitoring**

## Support

- 📚 [Supabase Documentation](https://supabase.com/docs)
- 🐛 [GitHub Issues](https://github.com/Linnnnberg/investByYourself/issues)
- 💬 [Community Forum](https://github.com/Linnnnberg/investByYourself/discussions)

---

**Happy coding! 🚀**
