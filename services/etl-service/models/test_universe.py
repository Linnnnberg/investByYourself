"""
Test Universe Configuration for ETL Service
Tech-021: ETL Service Extraction

Defines the "Magnificent 7 Stocks" as the essential test universe for company and stock data functionality testing.
"""

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class StockUniverse(BaseModel):
    """Represents a stock in the test universe."""

    symbol: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Full company name")
    sector: str = Field(..., description="Business sector")
    industry: str = Field(..., description="Industry classification")
    market_cap_category: str = Field(..., description="Market cap classification")
    description: str = Field(..., description="Brief company description")
    website: str = Field(..., description="Company website")
    exchange: str = Field(default="NASDAQ", description="Primary exchange")
    country: str = Field(default="US", description="Country of incorporation")

    # Data collection priorities
    priority: int = Field(..., description="Data collection priority (1=highest)")
    data_types: List[str] = Field(..., description="Types of data to collect")

    # Expected data availability
    expected_profile_completeness: float = Field(
        ..., description="Expected profile data completeness %"
    )
    expected_financials: bool = Field(
        ..., description="Whether financial data should be available"
    )
    expected_market_data: bool = Field(
        ..., description="Whether market data should be available"
    )


class TestUniverseConfig(BaseModel):
    """Configuration for the test universe."""

    name: str = Field(default="Magnificent 7 Stocks", description="Test universe name")
    description: str = Field(
        default="Essential test universe for ETL functionality testing"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")

    # Universe composition
    stocks: List[StockUniverse] = Field(..., description="Stocks in the test universe")

    # Data collection settings
    default_batch_size: int = Field(
        default=7, description="Default batch size for collection"
    )
    refresh_interval_hours: int = Field(
        default=24, description="Data refresh interval in hours"
    )

    # Quality thresholds
    min_profile_completeness: float = Field(
        default=0.8, description="Minimum profile completeness %"
    )
    min_financial_data_availability: float = Field(
        default=0.9, description="Minimum financial data availability %"
    )
    min_market_data_availability: float = Field(
        default=0.95, description="Minimum market data availability %"
    )


# Magnificent 7 Stocks Test Universe
MAGNIFICENT_7_UNIVERSE = TestUniverseConfig(
    name="Magnificent 7 Stocks",
    description="The seven largest technology companies by market cap, perfect for ETL testing",
    stocks=[
        StockUniverse(
            symbol="AAPL",
            company_name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            market_cap_category="Mega Cap",
            description="Designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            website="https://www.apple.com",
            exchange="NASDAQ",
            country="US",
            priority=1,
            data_types=["profile", "financials", "market_data", "earnings", "ratios"],
            expected_profile_completeness=0.95,
            expected_financials=True,
            expected_market_data=True,
        ),
        StockUniverse(
            symbol="MSFT",
            company_name="Microsoft Corporation",
            sector="Technology",
            industry="Software",
            market_cap_category="Mega Cap",
            description="Develops, licenses, and supports software, services, devices, and solutions worldwide.",
            website="https://www.microsoft.com",
            exchange="NASDAQ",
            country="US",
            priority=1,
            data_types=["profile", "financials", "market_data", "earnings", "ratios"],
            expected_profile_completeness=0.95,
            expected_financials=True,
            expected_market_data=True,
        ),
        StockUniverse(
            symbol="GOOGL",
            company_name="Alphabet Inc.",
            sector="Technology",
            industry="Internet Content & Information",
            market_cap_category="Mega Cap",
            description="Provides online advertising services in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America.",
            website="https://www.alphabet.com",
            exchange="NASDAQ",
            country="US",
            priority=1,
            data_types=["profile", "financials", "market_data", "earnings", "ratios"],
            expected_profile_completeness=0.95,
            expected_financials=True,
            expected_market_data=True,
        ),
        StockUniverse(
            symbol="AMZN",
            company_name="Amazon.com Inc.",
            sector="Consumer Cyclical",
            industry="Internet Retail",
            market_cap_category="Mega Cap",
            description="Engages in the retail sale of consumer products and subscriptions in North America and internationally.",
            website="https://www.amazon.com",
            exchange="NASDAQ",
            country="US",
            priority=1,
            data_types=["profile", "financials", "market_data", "earnings", "ratios"],
            expected_profile_completeness=0.95,
            expected_financials=True,
            expected_market_data=True,
        ),
        StockUniverse(
            symbol="NVDA",
            company_name="NVIDIA Corporation",
            sector="Technology",
            industry="Semiconductors",
            market_cap_category="Mega Cap",
            description="Designs, develops, and manufactures computer graphics processors, chipsets, and related multimedia software.",
            website="https://www.nvidia.com",
            exchange="NASDAQ",
            country="US",
            priority=1,
            data_types=["profile", "financials", "market_data", "earnings", "ratios"],
            expected_profile_completeness=0.95,
            expected_financials=True,
            expected_market_data=True,
        ),
        StockUniverse(
            symbol="META",
            company_name="Meta Platforms Inc.",
            sector="Technology",
            industry="Internet Content & Information",
            market_cap_category="Mega Cap",
            description="Develops products that enable people to connect and share with friends and family through mobile devices, personal computers, virtual reality headsets, and wearables worldwide.",
            website="https://www.meta.com",
            exchange="NASDAQ",
            country="US",
            priority=1,
            data_types=["profile", "financials", "market_data", "earnings", "ratios"],
            expected_profile_completeness=0.95,
            expected_financials=True,
            expected_market_data=True,
        ),
        StockUniverse(
            symbol="TSLA",
            company_name="Tesla Inc.",
            sector="Consumer Cyclical",
            industry="Auto Manufacturers",
            market_cap_category="Mega Cap",
            description="Designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally.",
            website="https://www.tesla.com",
            exchange="NASDAQ",
            country="US",
            priority=1,
            data_types=["profile", "financials", "market_data", "earnings", "ratios"],
            expected_profile_completeness=0.95,
            expected_financials=True,
            expected_market_data=True,
        ),
    ],
    default_batch_size=7,
    refresh_interval_hours=24,
    min_profile_completeness=0.8,
    min_financial_data_availability=0.9,
    min_market_data_availability=0.95,
)


class UniverseManager:
    """Manages the test universe and provides utility functions."""

    def __init__(self, universe: TestUniverseConfig = None):
        """Initialize the universe manager."""
        self.universe = universe or MAGNIFICENT_7_UNIVERSE
        self.symbols = [stock.symbol for stock in self.universe.stocks]
        self.symbol_to_stock = {stock.symbol: stock for stock in self.universe.stocks}

    def get_stock_by_symbol(self, symbol: str) -> StockUniverse:
        """Get stock information by symbol."""
        return self.symbol_to_stock.get(symbol.upper())

    def get_stocks_by_sector(self, sector: str) -> List[StockUniverse]:
        """Get all stocks in a specific sector."""
        return [
            stock
            for stock in self.universe.stocks
            if stock.sector.lower() == sector.lower()
        ]

    def get_stocks_by_priority(self, min_priority: int = 1) -> List[StockUniverse]:
        """Get stocks with priority >= min_priority."""
        return [
            stock for stock in self.universe.stocks if stock.priority >= min_priority
        ]

    def get_all_symbols(self) -> List[str]:
        """Get all stock symbols in the universe."""
        return self.symbols.copy()

    def get_universe_summary(self) -> Dict[str, Any]:
        """Get a summary of the test universe."""
        sectors = list(set(stock.sector for stock in self.universe.stocks))
        industries = list(set(stock.industry for stock in self.universe.stocks))

        return {
            "name": self.universe.name,
            "description": self.universe.description,
            "total_stocks": len(self.universe.stocks),
            "sectors": sectors,
            "industries": industries,
            "exchanges": list(set(stock.exchange for stock in self.universe.stocks)),
            "countries": list(set(stock.country for stock in self.universe.stocks)),
            "market_cap_categories": list(
                set(stock.market_cap_category for stock in self.universe.stocks)
            ),
            "data_types": list(
                set(
                    data_type
                    for stock in self.universe.stocks
                    for data_type in stock.data_types
                )
            ),
            "created_at": self.universe.created_at.isoformat(),
            "version": self.universe.version,
        }

    def validate_data_availability(self, actual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate actual data availability against expected values."""
        validation_results = {}

        for stock in self.universe.stocks:
            symbol = stock.symbol
            stock_data = actual_data.get(symbol, {})

            # Profile completeness validation
            profile_data = stock_data.get("profile", {})
            actual_completeness = (
                len([v for v in profile_data.values() if v is not None])
                / len(profile_data)
                if profile_data
                else 0
            )

            # Financial data validation
            financials_available = bool(stock_data.get("financials"))

            # Market data validation
            market_data_available = bool(stock_data.get("market_data"))

            validation_results[symbol] = {
                "expected_profile_completeness": stock.expected_profile_completeness,
                "actual_profile_completeness": actual_completeness,
                "profile_completeness_met": actual_completeness
                >= stock.expected_profile_completeness,
                "expected_financials": stock.expected_financials,
                "actual_financials_available": financials_available,
                "financials_met": financials_available == stock.expected_financials,
                "expected_market_data": stock.expected_market_data,
                "actual_market_data_available": market_data_available,
                "market_data_met": market_data_available == stock.expected_market_data,
                "overall_quality_score": (
                    (actual_completeness / stock.expected_profile_completeness * 0.4)
                    + (
                        1.0
                        if financials_available == stock.expected_financials
                        else 0.0
                    )
                    * 0.3
                    + (
                        1.0
                        if market_data_available == stock.expected_market_data
                        else 0.0
                    )
                    * 0.3
                ),
            }

        return validation_results


# Convenience functions
def get_magnificent_7_universe() -> TestUniverseConfig:
    """Get the Magnificent 7 stocks test universe."""
    return MAGNIFICENT_7_UNIVERSE


def get_universe_manager() -> UniverseManager:
    """Get a universe manager instance."""
    return UniverseManager(MAGNIFICENT_7_UNIVERSE)


def get_test_symbols() -> List[str]:
    """Get all test stock symbols."""
    return [stock.symbol for stock in MAGNIFICENT_7_UNIVERSE.stocks]


def get_stock_info(symbol: str) -> StockUniverse:
    """Get stock information by symbol."""
    return next(
        (
            stock
            for stock in MAGNIFICENT_7_UNIVERSE.stocks
            if stock.symbol.upper() == symbol.upper()
        ),
        None,
    )
