# Historical Price Data & Technical Indicators Implementation Plan
## InvestByYourself Financial Platform

**Date**: January 21, 2025
**Priority**: High (Story-038)
**Timeline**: Weeks 26-28
**Status**: Planning Phase

---

## 🎯 **Overview**

This plan outlines the implementation of comprehensive historical price data collection and technical indicators calculation for all companies in the platform. The goal is to provide 5 years of daily End-of-Day (EOD) price data along with essential technical indicators like RSI, MACD, Moving Averages, and more.

---

## 📊 **Data Requirements**

### **Historical Price Data (5 Years)**
- **Time Period**: 5 years of daily EOD data
- **Companies**: All 35 companies + 10 sector ETFs
- **Total Records**: ~45 entities × 1,250 trading days = ~56,250 price records
- **Data Points per Record**:
  - Date, Open, High, Low, Close, Volume
  - Adjusted Close, Dividend Amount, Split Coefficient

### **Technical Indicators**
- **RSI (Relative Strength Index)**: 14, 21, 50 periods
- **MACD (Moving Average Convergence Divergence)**: 12, 26, 9 periods
- **Moving Averages**: SMA 20, 50, 200; EMA 12, 26
- **Bollinger Bands**: 20-period, 2 standard deviations
- **Stochastic Oscillator**: 14, 3, 3 periods
- **Williams %R**: 14-period
- **ATR (Average True Range)**: 14-period
- **Volume Indicators**: OBV, Volume SMA

---

## 🗄️ **Database Schema Design**

### **1. Historical Price Data Table**
```sql
-- Historical price data table
CREATE TABLE historical_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10, 4) NOT NULL,
    high DECIMAL(10, 4) NOT NULL,
    low DECIMAL(10, 4) NOT NULL,
    close DECIMAL(10, 4) NOT NULL,
    volume BIGINT NOT NULL,
    adjusted_close DECIMAL(10, 4),
    dividend_amount DECIMAL(10, 4) DEFAULT 0,
    split_coefficient DECIMAL(10, 4) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE(company_id, date)
);

-- Indexes for performance
CREATE INDEX idx_historical_prices_company_date ON historical_prices(company_id, date);
CREATE INDEX idx_historical_prices_date ON historical_prices(date);
```

### **2. Technical Indicators Table**
```sql
-- Technical indicators table
CREATE TABLE technical_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    date DATE NOT NULL,
    indicator_type VARCHAR(50) NOT NULL,
    indicator_name VARCHAR(100) NOT NULL,
    value DECIMAL(15, 6),
    period INTEGER,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE(company_id, date, indicator_type, indicator_name, period)
);

-- Indexes for performance
CREATE INDEX idx_technical_indicators_company_date ON technical_indicators(company_id, date);
CREATE INDEX idx_technical_indicators_type ON technical_indicators(indicator_type);
```

### **3. Data Quality Metrics Table**
```sql
-- Data quality and validation metrics
CREATE TABLE data_quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- 'price' or 'indicator'
    date_range_start DATE NOT NULL,
    date_range_end DATE NOT NULL,
    total_records INTEGER NOT NULL,
    missing_records INTEGER DEFAULT 0,
    quality_score DECIMAL(3, 2), -- 0.00 to 1.00
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

---

## 🔧 **Technical Implementation**

### **Phase 1: Data Collection Infrastructure (Week 26)**

#### **1.1 API Integration Service**
```python
# api/src/services/historical_data_service.py
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from ..models.database import Company, HistoricalPrice, TechnicalIndicator
from ..core.config import settings

class HistoricalDataService:
    def __init__(self, db: Session):
        self.db = db
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.yahoo_finance_enabled = settings.YAHOO_FINANCE_ENABLED

    async def collect_historical_prices(
        self,
        company: Company,
        years: int = 5
    ) -> List[HistoricalPrice]:
        """Collect 5 years of historical price data for a company"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        # Try Alpha Vantage first, fallback to Yahoo Finance
        try:
            data = await self._fetch_alpha_vantage_data(
                company.symbol, start_date, end_date
            )
        except Exception as e:
            logger.warning(f"Alpha Vantage failed for {company.symbol}: {e}")
            data = await self._fetch_yahoo_finance_data(
                company.symbol, start_date, end_date
            )

        return self._process_price_data(company.id, data)

    async def _fetch_alpha_vantage_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Fetch data from Alpha Vantage API"""
        import aiohttp

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": self.alpha_vantage_key
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

        if "Error Message" in data:
            raise Exception(f"Alpha Vantage error: {data['Error Message']}")

        # Convert to DataFrame
        time_series = data.get("Time Series (Daily)", {})
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Filter by date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]

        return df

    async def _fetch_yahoo_finance_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """Fetch data from Yahoo Finance (backup)"""
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)

        return data

    def _process_price_data(
        self,
        company_id: int,
        data: pd.DataFrame
    ) -> List[HistoricalPrice]:
        """Process and validate price data"""
        prices = []

        for date, row in data.iterrows():
            price = HistoricalPrice(
                company_id=company_id,
                date=date.date(),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume']),
                adjusted_close=float(row.get('Adj Close', row['Close'])),
                dividend_amount=float(row.get('Dividend Amount', 0)),
                split_coefficient=float(row.get('Split Coefficient', 1.0))
            )
            prices.append(price)

        return prices
```

#### **1.2 Technical Indicators Calculator**
```python
# api/src/services/technical_indicators_service.py
import pandas as pd
import numpy as np
from typing import List, Dict
from ..models.database import TechnicalIndicator

class TechnicalIndicatorsService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_all_indicators(
        self,
        company_id: int,
        prices: List[HistoricalPrice]
    ) -> List[TechnicalIndicator]:
        """Calculate all technical indicators for a company"""
        df = self._prices_to_dataframe(prices)
        indicators = []

        # RSI calculations
        indicators.extend(self._calculate_rsi(company_id, df))

        # MACD calculations
        indicators.extend(self._calculate_macd(company_id, df))

        # Moving Averages
        indicators.extend(self._calculate_moving_averages(company_id, df))

        # Bollinger Bands
        indicators.extend(self._calculate_bollinger_bands(company_id, df))

        # Stochastic Oscillator
        indicators.extend(self._calculate_stochastic(company_id, df))

        # Williams %R
        indicators.extend(self._calculate_williams_r(company_id, df))

        # ATR
        indicators.extend(self._calculate_atr(company_id, df))

        # Volume Indicators
        indicators.extend(self._calculate_volume_indicators(company_id, df))

        return indicators

    def _calculate_rsi(self, company_id: int, df: pd.DataFrame) -> List[TechnicalIndicator]:
        """Calculate RSI for multiple periods"""
        indicators = []
        periods = [14, 21, 50]

        for period in periods:
            rsi_values = self._compute_rsi(df['close'], period)

            for date, value in rsi_values.items():
                indicator = TechnicalIndicator(
                    company_id=company_id,
                    date=date,
                    indicator_type='RSI',
                    indicator_name=f'RSI_{period}',
                    value=value,
                    period=period
                )
                indicators.append(indicator)

        return indicators

    def _compute_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI using pandas"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(
        self,
        company_id: int,
        df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate MACD and Signal line"""
        indicators = []

        # MACD Line
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        macd_line = ema_12 - ema_26

        # Signal Line
        signal_line = macd_line.ewm(span=9).mean()

        # MACD Histogram
        histogram = macd_line - signal_line

        for date in macd_line.index:
            if not pd.isna(macd_line[date]):
                # MACD Line
                indicators.append(TechnicalIndicator(
                    company_id=company_id,
                    date=date.date(),
                    indicator_type='MACD',
                    indicator_name='MACD_Line',
                    value=macd_line[date],
                    period=12
                ))

                # Signal Line
                indicators.append(TechnicalIndicator(
                    company_id=company_id,
                    date=date.date(),
                    indicator_type='MACD',
                    indicator_name='MACD_Signal',
                    value=signal_line[date],
                    period=9
                ))

                # Histogram
                indicators.append(TechnicalIndicator(
                    company_id=company_id,
                    date=date.date(),
                    indicator_type='MACD',
                    indicator_name='MACD_Histogram',
                    value=histogram[date],
                    period=9
                ))

        return indicators

    def _calculate_moving_averages(
        self,
        company_id: int,
        df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate Simple and Exponential Moving Averages"""
        indicators = []

        # SMA periods
        sma_periods = [20, 50, 200]
        for period in sma_periods:
            sma = df['close'].rolling(window=period).mean()
            for date, value in sma.items():
                if not pd.isna(value):
                    indicators.append(TechnicalIndicator(
                        company_id=company_id,
                        date=date.date(),
                        indicator_type='SMA',
                        indicator_name=f'SMA_{period}',
                        value=value,
                        period=period
                    ))

        # EMA periods
        ema_periods = [12, 26]
        for period in ema_periods:
            ema = df['close'].ewm(span=period).mean()
            for date, value in ema.items():
                if not pd.isna(value):
                    indicators.append(TechnicalIndicator(
                        company_id=company_id,
                        date=date.date(),
                        indicator_type='EMA',
                        indicator_name=f'EMA_{period}',
                        value=value,
                        period=period
                    ))

        return indicators

    def _calculate_bollinger_bands(
        self,
        company_id: int,
        df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate Bollinger Bands"""
        indicators = []
        period = 20
        std_dev = 2

        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        for date in sma.index:
            if not pd.isna(sma[date]):
                # Upper Band
                indicators.append(TechnicalIndicator(
                    company_id=company_id,
                    date=date.date(),
                    indicator_type='BOLLINGER',
                    indicator_name='BB_Upper',
                    value=upper_band[date],
                    period=period
                ))

                # Middle Band (SMA)
                indicators.append(TechnicalIndicator(
                    company_id=company_id,
                    date=date.date(),
                    indicator_type='BOLLINGER',
                    indicator_name='BB_Middle',
                    value=sma[date],
                    period=period
                ))

                # Lower Band
                indicators.append(TechnicalIndicator(
                    company_id=company_id,
                    date=date.date(),
                    indicator_type='BOLLINGER',
                    indicator_name='BB_Lower',
                    value=lower_band[date],
                    period=period
                ))

        return indicators
```

### **Phase 2: Data Processing & Storage (Week 27)**

#### **2.1 Batch Data Collection Script**
```python
# scripts/collect_historical_data.py
import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from api.src.services.historical_data_service import HistoricalDataService
from api.src.services.technical_indicators_service import TechnicalIndicatorsService
from api.src.core.database import get_database_session
from api.src.models.database import Company

async def collect_all_historical_data():
    """Collect historical data for all companies"""
    db = next(get_database_session())

    try:
        # Get all companies
        companies = db.query(Company).filter(Company.is_active == True).all()

        historical_service = HistoricalDataService(db)
        indicators_service = TechnicalIndicatorsService(db)

        for i, company in enumerate(companies, 1):
            logger.info(f"Processing {company.symbol} ({i}/{len(companies)})")

            try:
                # Collect historical prices
                prices = await historical_service.collect_historical_prices(company)

                # Save prices to database
                for price in prices:
                    db.add(price)
                db.commit()

                # Calculate technical indicators
                indicators = indicators_service.calculate_all_indicators(
                    company.id, prices
                )

                # Save indicators to database
                for indicator in indicators:
                    db.add(indicator)
                db.commit()

                logger.info(f"Completed {company.symbol}: {len(prices)} prices, {len(indicators)} indicators")

            except Exception as e:
                logger.error(f"Error processing {company.symbol}: {e}")
                db.rollback()
                continue

        logger.info("Historical data collection completed")

    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(collect_all_historical_data())
```

#### **2.2 Data Validation & Quality Control**
```python
# api/src/services/data_validation_service.py
class DataValidationService:
    def __init__(self, db: Session):
        self.db = db

    def validate_price_data(self, company_id: int) -> Dict[str, Any]:
        """Validate price data quality for a company"""
        prices = self.db.query(HistoricalPrice).filter(
            HistoricalPrice.company_id == company_id
        ).order_by(HistoricalPrice.date).all()

        if not prices:
            return {"error": "No price data found"}

        # Check for missing dates
        expected_dates = self._get_expected_trading_dates(
            prices[0].date, prices[-1].date
        )
        actual_dates = {price.date for price in prices}
        missing_dates = expected_dates - actual_dates

        # Check for data anomalies
        anomalies = self._detect_price_anomalies(prices)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            len(prices), len(missing_dates), len(anomalies)
        )

        return {
            "total_records": len(prices),
            "missing_dates": len(missing_dates),
            "anomalies": len(anomalies),
            "quality_score": quality_score,
            "date_range": {
                "start": prices[0].date.isoformat(),
                "end": prices[-1].date.isoformat()
            }
        }

    def _detect_price_anomalies(self, prices: List[HistoricalPrice]) -> List[Dict]:
        """Detect price anomalies (gaps, spikes, etc.)"""
        anomalies = []

        for i in range(1, len(prices)):
            prev_price = prices[i-1]
            curr_price = prices[i]

            # Check for large price gaps (>20% change)
            price_change = abs(curr_price.close - prev_price.close) / prev_price.close
            if price_change > 0.2:
                anomalies.append({
                    "date": curr_price.date,
                    "type": "large_price_gap",
                    "change_percent": price_change * 100
                })

            # Check for volume spikes (>5x average)
            if i >= 20:  # Need some history for average
                avg_volume = sum(p.volume for p in prices[i-20:i]) / 20
                if curr_price.volume > avg_volume * 5:
                    anomalies.append({
                        "date": curr_price.date,
                        "type": "volume_spike",
                        "volume_ratio": curr_price.volume / avg_volume
                    })

        return anomalies
```

### **Phase 3: API Endpoints & Frontend Integration (Week 28)**

#### **3.1 Historical Data API Endpoints**
```python
# api/src/api/v1/endpoints/historical_data.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/companies/{symbol}/historical-prices")
async def get_historical_prices(
    symbol: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(1000, le=5000),
    db: Session = Depends(get_database_session)
):
    """Get historical price data for a company"""
    company = db.query(Company).filter(Company.symbol == symbol).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    query = db.query(HistoricalPrice).filter(HistoricalPrice.company_id == company.id)

    if start_date:
        query = query.filter(HistoricalPrice.date >= start_date)
    if end_date:
        query = query.filter(HistoricalPrice.date <= end_date)

    prices = query.order_by(HistoricalPrice.date.desc()).limit(limit).all()

    return {
        "symbol": symbol,
        "company_name": company.name,
        "prices": [
            {
                "date": price.date.isoformat(),
                "open": price.open,
                "high": price.high,
                "low": price.low,
                "close": price.close,
                "volume": price.volume,
                "adjusted_close": price.adjusted_close
            }
            for price in prices
        ],
        "total_records": len(prices)
    }

@router.get("/companies/{symbol}/technical-indicators")
async def get_technical_indicators(
    symbol: str,
    indicator_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_database_session)
):
    """Get technical indicators for a company"""
    company = db.query(Company).filter(Company.symbol == symbol).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    query = db.query(TechnicalIndicator).filter(
        TechnicalIndicator.company_id == company.id
    )

    if indicator_type:
        query = query.filter(TechnicalIndicator.indicator_type == indicator_type)
    if start_date:
        query = query.filter(TechnicalIndicator.date >= start_date)
    if end_date:
        query = query.filter(TechnicalIndicator.date <= end_date)

    indicators = query.order_by(TechnicalIndicator.date.desc()).all()

    # Group by indicator type
    grouped_indicators = {}
    for indicator in indicators:
        key = f"{indicator.indicator_type}_{indicator.indicator_name}"
        if key not in grouped_indicators:
            grouped_indicators[key] = []

        grouped_indicators[key].append({
            "date": indicator.date.isoformat(),
            "value": indicator.value,
            "period": indicator.period
        })

    return {
        "symbol": symbol,
        "company_name": company.name,
        "indicators": grouped_indicators
    }
```

#### **3.2 Frontend Chart Integration**
```tsx
// frontend/src/components/charts/HistoricalPriceChart.tsx
'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface HistoricalPriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adjusted_close: number;
}

interface TechnicalIndicatorData {
  [key: string]: Array<{
    date: string;
    value: number;
    period: number;
  }>;
}

export function HistoricalPriceChart({ symbol }: { symbol: string }) {
  const [priceData, setPriceData] = useState<HistoricalPriceData[]>([]);
  const [indicators, setIndicators] = useState<TechnicalIndicatorData>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistoricalData();
  }, [symbol]);

  const fetchHistoricalData = async () => {
    try {
      setLoading(true);

      // Fetch price data
      const priceResponse = await fetch(
        `/api/v1/historical-data/companies/${symbol}/historical-prices?limit=1000`
      );
      const priceData = await priceResponse.json();
      setPriceData(priceData.prices);

      // Fetch technical indicators
      const indicatorsResponse = await fetch(
        `/api/v1/historical-data/companies/${symbol}/technical-indicators`
      );
      const indicatorsData = await indicatorsResponse.json();
      setIndicators(indicatorsData.indicators);

    } catch (error) {
      console.error('Error fetching historical data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="h-64 flex items-center justify-center">Loading chart...</div>;
  }

  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={priceData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => new Date(value).toLocaleDateString()}
          />
          <YAxis domain={['dataMin - 5', 'dataMax + 5']} />
          <Tooltip
            labelFormatter={(value) => new Date(value).toLocaleDateString()}
            formatter={(value, name) => [value, name]}
          />

          {/* Price lines */}
          <Line
            type="monotone"
            dataKey="close"
            stroke="#2563eb"
            strokeWidth={2}
            name="Close Price"
          />
          <Line
            type="monotone"
            dataKey="open"
            stroke="#10b981"
            strokeWidth={1}
            name="Open Price"
          />

          {/* Moving averages if available */}
          {indicators.SMA_SMA_20 && (
            <Line
              type="monotone"
              dataKey="sma_20"
              stroke="#f59e0b"
              strokeWidth={1}
              name="SMA 20"
            />
          )}

          {indicators.SMA_SMA_50 && (
            <Line
              type="monotone"
              dataKey="sma_50"
              stroke="#ef4444"
              strokeWidth={1}
              name="SMA 50"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## 📈 **Data Sources & APIs**

### **Primary: Alpha Vantage**
- **Free Tier**: 5 API calls per minute, 500 calls per day
- **Premium Tier**: Higher limits, real-time data
- **Coverage**: US stocks, some international
- **Data Quality**: High, professional-grade

### **Secondary: Yahoo Finance**
- **Free**: No rate limits
- **Coverage**: Global markets
- **Data Quality**: Good, community-maintained
- **Backup**: Use when Alpha Vantage fails

### **Alternative: Polygon.io**
- **Free Tier**: 5 calls per minute
- **Premium**: Real-time and historical data
- **Coverage**: US markets
- **Quality**: Professional-grade

---

## 🔄 **Data Update Strategy**

### **Initial Load**
- Collect 5 years of historical data for all companies
- Calculate all technical indicators
- Validate data quality and completeness

### **Daily Updates**
- Update with previous day's EOD data
- Recalculate technical indicators
- Update data quality metrics

### **Incremental Updates**
- Handle missing data points
- Backfill any gaps in historical data
- Update indicators for recent periods

---

## 📊 **Performance Considerations**

### **Database Optimization**
- Proper indexing on company_id and date
- Partitioning by date for large datasets
- Compression for historical data

### **API Rate Limiting**
- Implement exponential backoff
- Queue system for API calls
- Caching for frequently accessed data

### **Memory Management**
- Process data in batches
- Stream large datasets
- Clean up temporary data

---

## 🎯 **Success Criteria**

- [ ] 5 years of daily EOD data for all 45 entities
- [ ] All technical indicators calculated and stored
- [ ] Data quality score >95% for all companies
- [ ] API response time <2 seconds for historical data
- [ ] Frontend charts displaying historical data
- [ ] Daily update process automated
- [ ] Data validation and error handling

---

## 📋 **Dependencies**

- **Backend**: FastAPI + SQLAlchemy (already available)
- **Database**: SQLite (upgrade to PostgreSQL recommended)
- **APIs**: Alpha Vantage, Yahoo Finance
- **Libraries**: pandas, numpy, yfinance, aiohttp
- **Frontend**: Recharts for data visualization

---

**Document Version**: 1.0
**Last Updated**: January 21, 2025
**Next Review**: Before implementation start
**Maintained By**: Development Team
