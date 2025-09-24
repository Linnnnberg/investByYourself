#!/usr/bin/env python3
"""
Technical Indicators Service
Story-038: Portfolio Time Series & Data Structure Implementation

Service for calculating technical indicators from historical price data.
"""

import logging
import uuid
from datetime import date
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.database import HistoricalPrice, TechnicalIndicator

logger = logging.getLogger(__name__)


class TechnicalIndicatorsService:
    """Service for calculating technical indicators."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_all_indicators(
        self, company_id: str, prices: List[HistoricalPrice]
    ) -> List[TechnicalIndicator]:
        """Calculate all technical indicators for a company."""
        if len(prices) < 50:  # Need minimum data for indicators
            logger.warning(f"Insufficient data for indicators: {len(prices)} records")
            return []

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

        logger.info(
            f"Calculated {len(indicators)} technical indicators for company {company_id}"
        )
        return indicators

    def _prices_to_dataframe(self, prices: List[HistoricalPrice]) -> pd.DataFrame:
        """Convert price list to DataFrame."""
        data = []
        for price in prices:
            data.append(
                {
                    "date": price.date,
                    "open": float(price.open),
                    "high": float(price.high),
                    "low": float(price.low),
                    "close": float(price.close),
                    "volume": int(price.volume),
                }
            )

        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        return df

    def _calculate_rsi(
        self, company_id: str, df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate RSI for multiple periods."""
        indicators = []
        periods = [14, 21, 50]

        for period in periods:
            if len(df) < period + 1:
                continue

            rsi_values = self._compute_rsi(df["close"], period)

            for date, value in rsi_values.items():
                if not pd.isna(value):
                    indicator = TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="RSI",
                        indicator_name=f"RSI_{period}",
                        value=value,
                        period=period,
                    )
                    indicators.append(indicator)

        return indicators

    def _compute_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI using pandas."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Avoid division by zero
        rs = gain / loss.replace(0, np.inf)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(
        self, company_id: str, df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate MACD and Signal line."""
        indicators = []

        if len(df) < 26:  # Need at least 26 periods for MACD
            return indicators

        # MACD Line
        ema_12 = df["close"].ewm(span=12).mean()
        ema_26 = df["close"].ewm(span=26).mean()
        macd_line = ema_12 - ema_26

        # Signal Line
        signal_line = macd_line.ewm(span=9).mean()

        # MACD Histogram
        histogram = macd_line - signal_line

        for date in macd_line.index:
            if not pd.isna(macd_line[date]):
                # MACD Line
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="MACD",
                        indicator_name="MACD_Line",
                        value=macd_line[date],
                        period=12,
                    )
                )

                # Signal Line
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="MACD",
                        indicator_name="MACD_Signal",
                        value=signal_line[date],
                        period=9,
                    )
                )

                # Histogram
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="MACD",
                        indicator_name="MACD_Histogram",
                        value=histogram[date],
                        period=9,
                    )
                )

        return indicators

    def _calculate_moving_averages(
        self, company_id: str, df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate Simple and Exponential Moving Averages."""
        indicators = []

        # SMA periods
        sma_periods = [20, 50, 200]
        for period in sma_periods:
            if len(df) < period:
                continue

            sma = df["close"].rolling(window=period).mean()
            for date, value in sma.items():
                if not pd.isna(value):
                    indicators.append(
                        TechnicalIndicator(
                            id=str(uuid.uuid4()),
                            company_id=company_id,
                            date=date,
                            indicator_type="SMA",
                            indicator_name=f"SMA_{period}",
                            value=value,
                            period=period,
                        )
                    )

        # EMA periods
        ema_periods = [12, 26]
        for period in ema_periods:
            if len(df) < period:
                continue

            ema = df["close"].ewm(span=period).mean()
            for date, value in ema.items():
                if not pd.isna(value):
                    indicators.append(
                        TechnicalIndicator(
                            id=str(uuid.uuid4()),
                            company_id=company_id,
                            date=date,
                            indicator_type="EMA",
                            indicator_name=f"EMA_{period}",
                            value=value,
                            period=period,
                        )
                    )

        return indicators

    def _calculate_bollinger_bands(
        self, company_id: str, df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate Bollinger Bands."""
        indicators = []
        period = 20
        std_dev = 2

        if len(df) < period:
            return indicators

        sma = df["close"].rolling(window=period).mean()
        std = df["close"].rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        for date in sma.index:
            if not pd.isna(sma[date]):
                # Upper Band
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="BOLLINGER",
                        indicator_name="BB_Upper",
                        value=upper_band[date],
                        period=period,
                    )
                )

                # Middle Band (SMA)
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="BOLLINGER",
                        indicator_name="BB_Middle",
                        value=sma[date],
                        period=period,
                    )
                )

                # Lower Band
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="BOLLINGER",
                        indicator_name="BB_Lower",
                        value=lower_band[date],
                        period=period,
                    )
                )

        return indicators

    def _calculate_stochastic(
        self, company_id: str, df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate Stochastic Oscillator."""
        indicators = []
        k_period = 14
        d_period = 3

        if len(df) < k_period:
            return indicators

        # Calculate %K
        lowest_low = df["low"].rolling(window=k_period).min()
        highest_high = df["high"].rolling(window=k_period).max()

        k_percent = 100 * ((df["close"] - lowest_low) / (highest_high - lowest_low))

        # Calculate %D (SMA of %K)
        d_percent = k_percent.rolling(window=d_period).mean()

        for date in k_percent.index:
            if not pd.isna(k_percent[date]):
                # %K
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="STOCHASTIC",
                        indicator_name="Stoch_K",
                        value=k_percent[date],
                        period=k_period,
                    )
                )

                # %D
                if not pd.isna(d_percent[date]):
                    indicators.append(
                        TechnicalIndicator(
                            id=str(uuid.uuid4()),
                            company_id=company_id,
                            date=date,
                            indicator_type="STOCHASTIC",
                            indicator_name="Stoch_D",
                            value=d_percent[date],
                            period=d_period,
                        )
                    )

        return indicators

    def _calculate_williams_r(
        self, company_id: str, df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate Williams %R."""
        indicators = []
        period = 14

        if len(df) < period:
            return indicators

        highest_high = df["high"].rolling(window=period).max()
        lowest_low = df["low"].rolling(window=period).min()

        williams_r = -100 * ((highest_high - df["close"]) / (highest_high - lowest_low))

        for date in williams_r.index:
            if not pd.isna(williams_r[date]):
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="WILLIAMS_R",
                        indicator_name="Williams_R",
                        value=williams_r[date],
                        period=period,
                    )
                )

        return indicators

    def _calculate_atr(
        self, company_id: str, df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate Average True Range."""
        indicators = []
        period = 14

        if len(df) < period + 1:
            return indicators

        # Calculate True Range
        high_low = df["high"] - df["low"]
        high_close_prev = np.abs(df["high"] - df["close"].shift(1))
        low_close_prev = np.abs(df["low"] - df["close"].shift(1))

        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))

        # Calculate ATR
        atr = true_range.rolling(window=period).mean()

        for date in atr.index:
            if not pd.isna(atr[date]):
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="ATR",
                        indicator_name="ATR",
                        value=atr[date],
                        period=period,
                    )
                )

        return indicators

    def _calculate_volume_indicators(
        self, company_id: str, df: pd.DataFrame
    ) -> List[TechnicalIndicator]:
        """Calculate volume indicators."""
        indicators = []

        # On-Balance Volume (OBV)
        obv = self._calculate_obv(df)
        for date, value in obv.items():
            if not pd.isna(value):
                indicators.append(
                    TechnicalIndicator(
                        id=str(uuid.uuid4()),
                        company_id=company_id,
                        date=date,
                        indicator_type="VOLUME",
                        indicator_name="OBV",
                        value=value,
                        period=1,
                    )
                )

        # Volume SMA
        volume_sma_periods = [10, 20, 50]
        for period in volume_sma_periods:
            if len(df) < period:
                continue

            volume_sma = df["volume"].rolling(window=period).mean()
            for date, value in volume_sma.items():
                if not pd.isna(value):
                    indicators.append(
                        TechnicalIndicator(
                            id=str(uuid.uuid4()),
                            company_id=company_id,
                            date=date,
                            indicator_type="VOLUME",
                            indicator_name=f"Volume_SMA_{period}",
                            value=value,
                            period=period,
                        )
                    )

        return indicators

    def _calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume."""
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = df["volume"].iloc[0]

        for i in range(1, len(df)):
            if df["close"].iloc[i] > df["close"].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + df["volume"].iloc[i]
            elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - df["volume"].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]

        return obv

    def save_technical_indicators(self, indicators: List[TechnicalIndicator]) -> None:
        """Save technical indicators to database."""
        try:
            for indicator in indicators:
                self.db.add(indicator)
            self.db.commit()
            logger.info(f"Saved {len(indicators)} technical indicator records")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving technical indicators: {e}")
            raise

    async def get_technical_indicators(
        self,
        company_id: str,
        indicator_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[TechnicalIndicator]:
        """Get technical indicators for a company."""
        query = select(TechnicalIndicator).where(
            TechnicalIndicator.company_id == company_id
        )

        if indicator_type:
            query = query.where(TechnicalIndicator.indicator_type == indicator_type)
        if start_date:
            query = query.where(TechnicalIndicator.date >= start_date)
        if end_date:
            query = query.where(TechnicalIndicator.date <= end_date)

        query = query.order_by(TechnicalIndicator.date.desc())

        result = await self.db.execute(query)
        return result.scalars().all()
