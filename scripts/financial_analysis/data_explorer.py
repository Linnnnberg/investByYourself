#!/usr/bin/env python3
"""
Data Explorer - Financial Data Query and Visualization System
Tech-008: Database Infrastructure Setup

This module provides a comprehensive interface for exploring financial data
from the InvestByYourself database, including:
- SQL queries for top companies by market cap
- Interactive charts and visualizations
- Company profile generation
- Sector analysis and comparisons
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import streamlit as st
from plotly.subplots import make_subplots
from psycopg2.extras import RealDictCursor

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.database import DatabaseConfig, DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialDataExplorer:
    """Financial data exploration and visualization system."""

    def __init__(self):
        """Initialize the data explorer with database connection."""
        try:
            self.db_manager = DatabaseManager(DatabaseConfig.from_env())
            self.test_connection()
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    def test_connection(self):
        """Test database connection."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    results = cur.fetchall()
                    return pd.DataFrame(results)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    def get_top_companies_by_market_cap(
        self, limit: int = 10, sector: Optional[str] = None
    ) -> pd.DataFrame:
        """Get top companies by market capitalization."""
        query = """
        SELECT
            c.symbol,
            c.name,
            c.sector,
            c.industry,
            c.market_cap,
            c.enterprise_value,
            md.close_price as current_price,
            md.pe_ratio,
            md.pb_ratio,
            md.dividend_yield,
            md.beta,
            c.updated_at as last_updated
        FROM companies c
        LEFT JOIN market_data md ON c.id = md.company_id
        WHERE c.is_active = TRUE
        AND c.market_cap IS NOT NULL
        """

        if sector:
            query += f" AND c.sector = %s"
            params = (sector,)
        else:
            params = None

        query += """
        AND md.data_date = (
            SELECT MAX(data_date)
            FROM market_data md2
            WHERE md2.company_id = c.id
        )
        ORDER BY c.market_cap DESC
        LIMIT %s
        """

        if params:
            params = params + (limit,)
        else:
            params = (limit,)

        return self.execute_query(query, params)

    def get_sector_performance(self) -> pd.DataFrame:
        """Get sector performance metrics."""
        query = """
        SELECT
            c.sector,
            COUNT(*) as company_count,
            AVG(c.market_cap) as avg_market_cap,
            SUM(c.market_cap) as total_market_cap,
            AVG(md.pe_ratio) as avg_pe_ratio,
            AVG(md.pb_ratio) as avg_pb_ratio,
            AVG(md.dividend_yield) as avg_dividend_yield
        FROM companies c
        LEFT JOIN market_data md ON c.id = md.company_id
        WHERE c.is_active = TRUE
        AND c.sector IS NOT NULL
        AND md.data_date = (
            SELECT MAX(data_date)
            FROM market_data md2
            WHERE md2.company_id = c.id
        )
        GROUP BY c.sector
        HAVING COUNT(*) > 0
        ORDER BY total_market_cap DESC
        """

        return self.execute_query(query)

    def get_company_financial_history(
        self, symbol: str, days: int = 365
    ) -> pd.DataFrame:
        """Get financial history for a specific company."""
        query = """
        SELECT
            md.data_date,
            md.open_price,
            md.high_price,
            md.low_price,
            md.close_price,
            md.adjusted_close,
            md.volume,
            md.market_cap,
            md.pe_ratio,
            md.pb_ratio,
            md.ps_ratio,
            md.dividend_yield,
            md.beta
        FROM companies c
        JOIN market_data md ON c.id = md.company_id
        WHERE c.symbol = %s
        AND md.data_date >= %s
        ORDER BY md.data_date ASC
        """

        start_date = datetime.now() - timedelta(days=days)
        return self.execute_query(query, (symbol, start_date.date()))

    def get_financial_ratios_trend(
        self, symbol: str, ratio_type: str = "pe_ratio", days: int = 365
    ) -> pd.DataFrame:
        """Get trend of a specific financial ratio for a company."""
        query = """
        SELECT
            fr.ratio_date,
            fr.ratio_value,
            fr.confidence_score
        FROM companies c
        JOIN financial_ratios fr ON c.id = fr.company_id
        WHERE c.symbol = %s
        AND fr.ratio_type = %s
        AND fr.ratio_date >= %s
        ORDER BY fr.ratio_date ASC
        """

        start_date = datetime.now() - timedelta(days=days)
        return self.execute_query(query, (symbol, ratio_type, start_date.date()))

    def get_peer_comparison(self, symbol: str) -> pd.DataFrame:
        """Get peer comparison for a company within the same sector."""
        query = """
        SELECT
            c.symbol,
            c.name,
            c.market_cap,
            md.close_price as current_price,
            md.pe_ratio,
            md.pb_ratio,
            md.ps_ratio,
            md.dividend_yield,
            md.beta
        FROM companies c
        LEFT JOIN market_data md ON c.id = md.company_id
        WHERE c.sector = (
            SELECT sector FROM companies WHERE symbol = %s
        )
        AND c.symbol != %s
        AND c.is_active = TRUE
        AND md.data_date = (
            SELECT MAX(data_date)
            FROM market_data md2
            WHERE md2.company_id = c.id
        )
        ORDER BY c.market_cap DESC
        LIMIT 10
        """

        return self.execute_query(query, (symbol, symbol))

    def get_economic_indicators(
        self, indicator_type: str = "CPI", months: int = 24
    ) -> pd.DataFrame:
        """Get economic indicators data."""
        query = """
        SELECT
            indicator_date,
            indicator_value,
            indicator_unit,
            period_type
        FROM economic_indicators
        WHERE indicator_type = %s
        AND indicator_date >= %s
        ORDER BY indicator_date ASC
        """

        start_date = datetime.now() - timedelta(days=months * 30)
        return self.execute_query(query, (indicator_type, start_date.date()))


class FinancialCharts:
    """Financial chart generation and visualization."""

    @staticmethod
    def create_market_cap_chart(
        df: pd.DataFrame, title: str = "Top Companies by Market Cap"
    ) -> go.Figure:
        """Create a bar chart of companies by market cap."""
        fig = go.Figure(
            data=[
                go.Bar(
                    x=df["symbol"],
                    y=df["market_cap"] / 1e9,  # Convert to billions
                    text=[f"${mc/1e9:.1f}B" for mc in df["market_cap"]],
                    textposition="auto",
                    marker_color="lightblue",
                )
            ]
        )

        fig.update_layout(
            title=title,
            xaxis_title="Company Symbol",
            yaxis_title="Market Cap (Billions USD)",
            showlegend=False,
            height=500,
        )

        return fig

    @staticmethod
    def create_sector_performance_chart(df: pd.DataFrame) -> go.Figure:
        """Create a sector performance chart."""
        fig = go.Figure(
            data=[
                go.Bar(
                    x=df["sector"],
                    y=df["total_market_cap"] / 1e12,  # Convert to trillions
                    text=[f"${mc/1e12:.2f}T" for mc in df["total_market_cap"]],
                    textposition="auto",
                    marker_color="lightgreen",
                )
            ]
        )

        fig.update_layout(
            title="Sector Market Capitalization",
            xaxis_title="Sector",
            yaxis_title="Total Market Cap (Trillions USD)",
            showlegend=False,
            height=500,
            xaxis_tickangle=-45,
        )

        return fig

    @staticmethod
    def create_price_history_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
        """Create a price history chart for a company."""
        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=df["data_date"],
                open=df["open_price"],
                high=df["high_price"],
                low=df["low_price"],
                close=df["close_price"],
                name="OHLC",
            )
        )

        fig.update_layout(
            title=f"{symbol} - Price History",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            xaxis_rangeslider_visible=False,
        )

        return fig

    @staticmethod
    def create_ratio_comparison_chart(df: pd.DataFrame, title: str) -> go.Figure:
        """Create a comparison chart for financial ratios."""
        fig = go.Figure(
            data=[
                go.Bar(
                    x=df["symbol"],
                    y=df["pe_ratio"],
                    name="P/E Ratio",
                    marker_color="lightblue",
                ),
                go.Bar(
                    x=df["symbol"],
                    y=df["pb_ratio"],
                    name="P/B Ratio",
                    marker_color="lightgreen",
                ),
            ]
        )

        fig.update_layout(
            title=title,
            xaxis_title="Company",
            yaxis_title="Ratio Value",
            barmode="group",
            height=500,
        )

        return fig

    @staticmethod
    def create_economic_indicator_chart(
        df: pd.DataFrame, indicator_type: str
    ) -> go.Figure:
        """Create a line chart for economic indicators."""
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["indicator_date"],
                y=df["indicator_value"],
                mode="lines+markers",
                name=indicator_type,
                line=dict(color="red", width=2),
            )
        )

        fig.update_layout(
            title=f"{indicator_type} - Economic Indicator",
            xaxis_title="Date",
            yaxis_title="Value",
            height=500,
        )

        return fig


class CompanyProfile:
    """Company profile generation and analysis."""

    def __init__(self, data_explorer: FinancialDataExplorer):
        """Initialize with data explorer."""
        self.explorer = data_explorer

    def generate_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Generate a comprehensive company profile."""
        try:
            # Get company overview
            overview_query = """
            SELECT
                c.symbol, c.name, c.sector, c.industry, c.exchange, c.country,
                c.website, c.description, c.employee_count, c.market_cap,
                c.enterprise_value, c.ceo, c.headquarters, c.founded_year
            FROM companies c
            WHERE c.symbol = %s
            """

            overview_df = self.explorer.execute_query(overview_query, (symbol,))

            if overview_df.empty:
                return {"error": f"Company {symbol} not found"}

            company = overview_df.iloc[0]

            # Get latest market data
            market_data = self.explorer.get_company_financial_history(symbol, days=1)
            latest_market = market_data.iloc[0] if not market_data.empty else None

            # Get peer comparison
            peers = self.explorer.get_peer_comparison(symbol)

            # Get financial ratios trend
            pe_trend = self.explorer.get_financial_ratios_trend(
                symbol, "pe_ratio", days=365
            )

            profile = {
                "overview": {
                    "symbol": company["symbol"],
                    "name": company["name"],
                    "sector": company["sector"],
                    "industry": company["industry"],
                    "exchange": company["exchange"],
                    "country": company["country"],
                    "website": company["website"],
                    "description": company["description"],
                    "employee_count": company["employee_count"],
                    "market_cap": company["market_cap"],
                    "enterprise_value": company["enterprise_value"],
                    "ceo": company["ceo"],
                    "headquarters": company["headquarters"],
                    "founded_year": company["founded_year"],
                },
                "market_data": {
                    "current_price": (
                        latest_market["close_price"]
                        if latest_market is not None
                        else None
                    ),
                    "pe_ratio": (
                        latest_market["pe_ratio"] if latest_market is not None else None
                    ),
                    "pb_ratio": (
                        latest_market["pb_ratio"] if latest_market is not None else None
                    ),
                    "ps_ratio": (
                        latest_market["ps_ratio"] if latest_market is not None else None
                    ),
                    "dividend_yield": (
                        latest_market["dividend_yield"]
                        if latest_market is not None
                        else None
                    ),
                    "beta": (
                        latest_market["beta"] if latest_market is not None else None
                    ),
                },
                "peers": peers.to_dict("records") if not peers.empty else [],
                "pe_trend": pe_trend.to_dict("records") if not pe_trend.empty else [],
            }

            return profile

        except Exception as e:
            logger.error(f"Failed to generate company profile for {symbol}: {e}")
            return {"error": str(e)}


def main():
    """Main function to run the data explorer."""
    try:
        # Initialize components
        explorer = FinancialDataExplorer()
        charts = FinancialCharts()
        profile_generator = CompanyProfile(explorer)

        print("=== Financial Data Explorer ===")
        print("Database connection successful!")

        # Example queries
        print("\n1. Top 5 US Companies by Market Cap:")
        top_companies = explorer.get_top_companies_by_market_cap(limit=5)
        if not top_companies.empty:
            print(
                top_companies[["symbol", "name", "sector", "market_cap"]].to_string(
                    index=False
                )
            )

        print("\n2. Sector Performance:")
        sector_perf = explorer.get_sector_performance()
        if not sector_perf.empty:
            print(
                sector_perf[["sector", "company_count", "total_market_cap"]].to_string(
                    index=False
                )
            )

        print("\n3. Company Profile Example (AAPL):")
        aapl_profile = profile_generator.generate_company_profile("AAPL")
        if "error" not in aapl_profile:
            print(f"Symbol: {aapl_profile['overview']['symbol']}")
            print(f"Name: {aapl_profile['overview']['name']}")
            print(f"Sector: {aapl_profile['overview']['sector']}")
            print(f"Market Cap: ${aapl_profile['overview']['market_cap']:,.0f}")

        print("\nData exploration system ready!")

    except Exception as e:
        logger.error(f"Failed to initialize data explorer: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
