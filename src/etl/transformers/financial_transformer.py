"""
Financial Data Transformer - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 2

This module provides financial data transformation capabilities including:
- Financial statement data transformation
- Financial ratio calculations
- Financial metrics computation
- Data validation and quality assessment
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Union

import structlog

from .base_transformer import (BaseDataTransformer, DataQualityMetrics,
                               TransformationResult, TransformationRule)

logger = structlog.get_logger(__name__)


@dataclass
class FinancialMetrics:
    """Standardized financial metrics."""

    # Valuation metrics
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    ev_to_ebitda: Optional[float] = None

    # Profitability metrics
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    roic: Optional[float] = None  # Return on Invested Capital

    # Growth metrics
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    book_value_growth: Optional[float] = None

    # Financial strength metrics
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    interest_coverage: Optional[float] = None

    # Efficiency metrics
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None


@dataclass
class FinancialStatement:
    """Standardized financial statement data."""

    statement_type: str  # 'income_statement', 'balance_sheet', 'cash_flow'
    period: str  # 'annual', 'quarterly'
    date: datetime
    currency: str = "USD"

    # Income statement fields
    revenue: Optional[float] = None
    cost_of_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_expenses: Optional[float] = None
    operating_income: Optional[float] = None
    interest_expense: Optional[float] = None
    income_before_taxes: Optional[float] = None
    income_tax_expense: Optional[float] = None
    net_income: Optional[float] = None
    ebitda: Optional[float] = None

    # Balance sheet fields
    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    accounts_receivable: Optional[float] = None
    inventory: Optional[float] = None
    total_liabilities: Optional[float] = None
    current_liabilities: Optional[float] = None
    long_term_debt: Optional[float] = None
    total_equity: Optional[float] = None
    retained_earnings: Optional[float] = None

    # Cash flow fields
    operating_cash_flow: Optional[float] = None
    investing_cash_flow: Optional[float] = None
    financing_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None


class FinancialRatioCalculator:
    """Calculates financial ratios from financial statement data."""

    @staticmethod
    def calculate_pe_ratio(price: float, earnings_per_share: float) -> Optional[float]:
        """Calculate Price-to-Earnings ratio."""
        if earnings_per_share and earnings_per_share != 0:
            return price / earnings_per_share
        return None

    @staticmethod
    def calculate_forward_pe(price: float, forward_eps: float) -> Optional[float]:
        """Calculate Forward Price-to-Earnings ratio."""
        if forward_eps and forward_eps != 0:
            return price / forward_eps
        return None

    @staticmethod
    def calculate_price_to_book(
        price: float, book_value_per_share: float
    ) -> Optional[float]:
        """Calculate Price-to-Book ratio."""
        if book_value_per_share and book_value_per_share != 0:
            return price / book_value_per_share
        return None

    @staticmethod
    def calculate_price_to_sales(
        price: float, sales_per_share: float
    ) -> Optional[float]:
        """Calculate Price-to-Sales ratio."""
        if sales_per_share and sales_per_share != 0:
            return price / sales_per_share
        return None

    @staticmethod
    def calculate_ev_to_ebitda(
        enterprise_value: float, ebitda: float
    ) -> Optional[float]:
        """Calculate Enterprise Value to EBITDA ratio."""
        if ebitda and ebitda != 0:
            return enterprise_value / ebitda
        return None

    @staticmethod
    def calculate_gross_margin(
        revenue: float, cost_of_revenue: float
    ) -> Optional[float]:
        """Calculate Gross Margin percentage."""
        if revenue and revenue != 0:
            return ((revenue - cost_of_revenue) / revenue) * 100
        return None

    @staticmethod
    def calculate_operating_margin(
        revenue: float, operating_income: float
    ) -> Optional[float]:
        """Calculate Operating Margin percentage."""
        if revenue and revenue != 0:
            return (operating_income / revenue) * 100
        return None

    @staticmethod
    def calculate_net_margin(revenue: float, net_income: float) -> Optional[float]:
        """Calculate Net Margin percentage."""
        if revenue and revenue != 0:
            return (net_income / revenue) * 100
        return None

    @staticmethod
    def calculate_roe(net_income: float, total_equity: float) -> Optional[float]:
        """Calculate Return on Equity percentage."""
        if total_equity and total_equity != 0:
            return (net_income / total_equity) * 100
        return None

    @staticmethod
    def calculate_roa(net_income: float, total_assets: float) -> Optional[float]:
        """Calculate Return on Assets percentage."""
        if total_assets and total_assets != 0:
            return (net_income / total_assets) * 100
        return None

    @staticmethod
    def calculate_debt_to_equity(
        total_debt: float, total_equity: float
    ) -> Optional[float]:
        """Calculate Debt-to-Equity ratio."""
        if total_equity and total_equity != 0:
            return total_debt / total_equity
        return None

    @staticmethod
    def calculate_current_ratio(
        current_assets: float, current_liabilities: float
    ) -> Optional[float]:
        """Calculate Current Ratio."""
        if current_liabilities and current_liabilities != 0:
            return current_assets / current_liabilities
        return None

    @staticmethod
    def calculate_quick_ratio(
        current_assets: float, inventory: float, current_liabilities: float
    ) -> Optional[float]:
        """Calculate Quick Ratio (Acid-Test Ratio)."""
        if current_liabilities and current_liabilities != 0:
            return (current_assets - inventory) / current_liabilities
        return None


class FinancialMetricsCalculator:
    """Calculates comprehensive financial metrics from raw data."""

    def __init__(self):
        """Initialize the financial metrics calculator."""
        self.ratio_calculator = FinancialRatioCalculator()

    def calculate_all_metrics(
        self,
        financial_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None,
    ) -> FinancialMetrics:
        """Calculate all available financial metrics."""
        metrics = FinancialMetrics()

        # Extract financial statement data
        income_stmt = financial_data.get("income_statement", {})
        balance_sheet = financial_data.get("balance_sheet", {})
        cash_flow = financial_data.get("cash_flow", {})

        # Calculate profitability metrics
        if income_stmt.get("revenue") and income_stmt.get("cost_of_revenue"):
            metrics.gross_margin = self.ratio_calculator.calculate_gross_margin(
                income_stmt["revenue"], income_stmt["cost_of_revenue"]
            )

        if income_stmt.get("revenue") and income_stmt.get("operating_income"):
            metrics.operating_margin = self.ratio_calculator.calculate_operating_margin(
                income_stmt["revenue"], income_stmt["operating_income"]
            )

        if income_stmt.get("revenue") and income_stmt.get("net_income"):
            metrics.net_margin = self.ratio_calculator.calculate_net_margin(
                income_stmt["revenue"], income_stmt["net_income"]
            )

        # Calculate return metrics
        if income_stmt.get("net_income") and balance_sheet.get("total_equity"):
            metrics.roe = self.ratio_calculator.calculate_roe(
                income_stmt["net_income"], balance_sheet["total_equity"]
            )

        if income_stmt.get("net_income") and balance_sheet.get("total_assets"):
            metrics.roa = self.ratio_calculator.calculate_roa(
                income_stmt["net_income"], balance_sheet["total_assets"]
            )

        # Calculate financial strength metrics
        if balance_sheet.get("total_debt") and balance_sheet.get("total_equity"):
            metrics.debt_to_equity = self.ratio_calculator.calculate_debt_to_equity(
                balance_sheet["total_debt"], balance_sheet["total_equity"]
            )

        if balance_sheet.get("current_assets") and balance_sheet.get(
            "current_liabilities"
        ):
            metrics.current_ratio = self.ratio_calculator.calculate_current_ratio(
                balance_sheet["current_assets"], balance_sheet["current_liabilities"]
            )

        # Calculate additional financial strength metrics
        if (
            balance_sheet.get("current_assets")
            and balance_sheet.get("current_liabilities")
            and balance_sheet.get("total_assets")
        ):
            # Quick ratio (assuming inventory is part of current assets)
            metrics.quick_ratio = self.ratio_calculator.calculate_quick_ratio(
                balance_sheet["current_assets"],
                0,  # Assume no separate inventory field for now
                balance_sheet["current_liabilities"],
            )

        # Calculate debt ratios
        if balance_sheet.get("total_debt") and balance_sheet.get("total_assets"):
            # Debt to assets ratio
            debt_to_assets = balance_sheet["total_debt"] / balance_sheet["total_assets"]
            # Store this in a custom field if needed

        # Calculate valuation metrics if market data is available
        if market_data:
            price = market_data.get("price")
            if price:
                if income_stmt.get("earnings_per_share"):
                    metrics.pe_ratio = self.ratio_calculator.calculate_pe_ratio(
                        price, income_stmt["earnings_per_share"]
                    )

                if balance_sheet.get("book_value_per_share"):
                    metrics.price_to_book = (
                        self.ratio_calculator.calculate_price_to_book(
                            price, balance_sheet["book_value_per_share"]
                        )
                    )

        return metrics


class FinancialDataTransformer(BaseDataTransformer):
    """
    Transforms financial data from various sources into standardized formats.

    This transformer handles:
    - Financial statement data normalization
    - Financial ratio calculations
    - Data validation and quality assessment
    - Metric standardization across different data sources
    """

    def __init__(
        self,
        name: str = "FinancialDataTransformer",
        description: str = "Transforms and standardizes financial data",
        max_concurrent_transformations: int = 20,
        enable_validation: bool = True,
        enable_quality_monitoring: bool = True,
    ):
        """Initialize the financial data transformer."""
        super().__init__(
            name=name,
            description=description,
            max_concurrent_transformations=max_concurrent_transformations,
            enable_validation=enable_validation,
            enable_quality_monitoring=enable_quality_monitoring,
        )

        # Initialize calculators
        self.metrics_calculator = FinancialMetricsCalculator()
        self.ratio_calculator = FinancialRatioCalculator()

        # Add default transformation rules
        self._add_default_rules()

        logger.info(f"Financial Data Transformer initialized: {name}")

    def _add_default_rules(self):
        """Add default transformation rules."""
        # Rule for Yahoo Finance data
        yahoo_rule = TransformationRule(
            name="Yahoo Finance Standardization",
            description="Standardize Yahoo Finance financial data",
            field_mapping={
                "totalRevenue": "revenue",
                "costOfRevenue": "cost_of_revenue",
                "grossProfit": "gross_profit",
                "operatingIncome": "operating_income",
                "netIncome": "net_income",
                "totalAssets": "total_assets",
                "totalLiabilities": "total_liabilities",
                "totalEquity": "total_equity",
            },
            priority=1,
        )
        self.add_transformation_rule(yahoo_rule)

        # Rule for Alpha Vantage data
        alpha_vantage_rule = TransformationRule(
            name="Alpha Vantage Standardization",
            description="Standardize Alpha Vantage financial data",
            field_mapping={
                "Revenue": "revenue",
                "Cost of Revenue": "cost_of_revenue",
                "Gross Profit": "gross_profit",
                "Operating Income": "operating_income",
                "Net Income": "net_income",
            },
            priority=2,
        )
        self.add_transformation_rule(alpha_vantage_rule)

    async def transform_data(
        self,
        data: Dict[str, Any],
        transformation_rules: Optional[List[TransformationRule]] = None,
    ) -> TransformationResult:
        """
        Transform financial data according to specified rules.

        Args:
            data: Input financial data
            transformation_rules: Optional list of rules to apply

        Returns:
            Transformation result with standardized financial data
        """
        start_time = datetime.now()

        try:
            # Use default rules if none specified
            if transformation_rules is None:
                transformation_rules = self.transformation_rules

            # Create result object
            result = TransformationResult(
                source_data=data.copy(),
                transformed_data={},
                transformation_rules_applied=[],
            )

            # Apply transformation rules
            transformed_data = data.copy()
            for rule in transformation_rules:
                if rule.enabled:
                    transformed_data = self._apply_transformation_rule(
                        transformed_data, rule
                    )
                    result.transformation_rules_applied.append(rule.name)

            # Calculate financial metrics
            financial_metrics = self.metrics_calculator.calculate_all_metrics(
                transformed_data
            )

            # Create standardized output
            standardized_data = {
                "company_info": self._extract_company_info(transformed_data),
                "financial_statements": self._extract_financial_statements(
                    transformed_data
                ),
                "financial_metrics": self._metrics_to_dict(financial_metrics),
                "market_data": self._extract_market_data(transformed_data),
                "metadata": {
                    "transformation_timestamp": datetime.now().isoformat(),
                    "rules_applied": result.transformation_rules_applied,
                    "data_source": data.get("source", "unknown"),
                },
            }

            # Recalculate financial metrics with the properly structured data
            final_financial_metrics = self.metrics_calculator.calculate_all_metrics(
                standardized_data["financial_statements"],
                standardized_data["market_data"],
            )
            standardized_data["financial_metrics"] = self._metrics_to_dict(
                final_financial_metrics
            )

            result.transformed_data = standardized_data

            # Calculate quality metrics
            if self.enable_quality_monitoring:
                result.quality_metrics = self._calculate_quality_metrics(
                    data, standardized_data
                )

            # Calculate processing time
            end_time = datetime.now()
            result.processing_time = (end_time - start_time).total_seconds()

            logger.info(
                f"Financial data transformation completed",
                source_records=len(data),
                transformed_records=len(standardized_data),
                processing_time=result.processing_time,
            )

            return result

        except Exception as e:
            logger.error(f"Error transforming financial data: {str(e)}")
            result.errors.append(str(e))
            result.processing_time = (datetime.now() - start_time).total_seconds()
            return result

    async def validate_data(
        self, data: Dict[str, Any], validation_rules: Optional[List[str]] = None
    ) -> bool:
        """
        Validate financial data against business rules.

        Args:
            data: Financial data to validate
            validation_rules: Optional list of validation rules

        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Basic validation rules
            required_fields = ["revenue", "net_income", "total_assets"]

            for field in required_fields:
                if field not in data or data[field] is None:
                    logger.warning(f"Missing required field: {field}")
                    return False

            # Validate numeric values
            for field, value in data.items():
                if isinstance(value, (int, float)) and value < 0:
                    if field in ["revenue", "net_income", "total_assets"]:
                        logger.warning(f"Negative value for {field}: {value}")
                        return False

            # Validate financial ratios
            if "revenue" in data and "net_income" in data:
                if data["revenue"] > 0:
                    net_margin = data["net_income"] / data["revenue"]
                    if net_margin > 1.0:  # Net margin > 100%
                        logger.warning(f"Unrealistic net margin: {net_margin:.2%}")
                        return False

            return True

        except Exception as e:
            logger.error(f"Error validating financial data: {str(e)}")
            return False

    def _apply_transformation_rule(
        self, data: Dict[str, Any], rule: TransformationRule
    ) -> Dict[str, Any]:
        """Apply a transformation rule to the data."""
        transformed_data = data.copy()

        # Apply field mappings
        for source_field, target_field in rule.field_mapping.items():
            if source_field in transformed_data:
                transformed_data[target_field] = transformed_data.pop(source_field)

        # Apply transformation functions
        for func_name in rule.transformation_functions:
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                transformed_data = func(transformed_data)

        return transformed_data

    def _extract_company_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract company information from transformed data."""
        company_info = {}

        # Map common company fields
        company_fields = {
            "company_name": ["company_name", "name", "longName"],
            "symbol": ["symbol", "ticker"],
            "sector": ["sector", "industry"],
            "industry": ["industry", "sector"],
            "country": ["country", "countryCode"],
            "website": ["website", "webSite"],
        }

        for target_field, source_fields in company_fields.items():
            for source_field in source_fields:
                if source_field in data:
                    company_info[target_field] = data[source_field]
                    break

        return company_info

    def _extract_financial_statements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial statement data."""
        statements = {}

        # Income statement - check both original and transformed field names
        revenue_fields = ["revenue", "totalRevenue", "Revenue"]
        cost_fields = ["cost_of_revenue", "costOfRevenue", "Cost of Revenue"]
        gross_profit_fields = ["gross_profit", "grossProfit", "Gross Profit"]
        operating_income_fields = [
            "operating_income",
            "operatingIncome",
            "Operating Income",
        ]
        net_income_fields = ["net_income", "netIncome", "Net Income"]

        if any(field in data for field in revenue_fields):
            statements["income_statement"] = {
                "revenue": data.get("revenue")
                or data.get("totalRevenue")
                or data.get("Revenue"),
                "cost_of_revenue": data.get("cost_of_revenue")
                or data.get("costOfRevenue")
                or data.get("Cost of Revenue"),
                "gross_profit": data.get("gross_profit")
                or data.get("grossProfit")
                or data.get("Gross Profit"),
                "operating_income": data.get("operating_income")
                or data.get("operatingIncome")
                or data.get("Operating Income"),
                "net_income": data.get("net_income")
                or data.get("netIncome")
                or data.get("Net Income"),
            }

        # Balance sheet - check both original and transformed field names
        assets_fields = ["total_assets", "totalAssets", "Total Assets"]
        current_assets_fields = ["current_assets", "currentAssets", "Current Assets"]
        liabilities_fields = [
            "total_liabilities",
            "totalLiabilities",
            "Total Liabilities",
        ]
        current_liabilities_fields = [
            "current_liabilities",
            "currentLiabilities",
            "Current Liabilities",
        ]
        equity_fields = ["total_equity", "totalEquity", "Total Equity"]
        debt_fields = [
            "total_debt",
            "totalDebt",
            "Total Debt",
            "longTermDebt",
            "long_term_debt",
        ]

        if any(field in data for field in assets_fields):
            statements["balance_sheet"] = {
                "total_assets": data.get("total_assets")
                or data.get("totalAssets")
                or data.get("Total Assets"),
                "current_assets": data.get("current_assets")
                or data.get("currentAssets")
                or data.get("Current Assets"),
                "total_liabilities": data.get("total_liabilities")
                or data.get("totalLiabilities")
                or data.get("Total Liabilities"),
                "current_liabilities": data.get("current_liabilities")
                or data.get("currentLiabilities")
                or data.get("Current Liabilities"),
                "total_equity": data.get("total_equity")
                or data.get("totalEquity")
                or data.get("Total Equity"),
                "total_debt": data.get("total_debt")
                or data.get("totalDebt")
                or data.get("Total Debt")
                or data.get("longTermDebt")
                or data.get("long_term_debt"),
            }

        return statements

    def _extract_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market-related data."""
        market_data = {}

        # Price fields - check multiple variations
        price_value = (
            data.get("price")
            or data.get("currentPrice")
            or data.get("regularMarketPrice")
            or data.get("Price")
        )
        if price_value:
            market_data["price"] = price_value

        # Market cap fields
        market_cap_value = (
            data.get("market_cap")
            or data.get("marketCap")
            or data.get("Market Cap")
            or data.get("market_capitalization")
        )
        if market_cap_value:
            market_data["market_cap"] = market_cap_value

        # Volume fields
        volume_value = (
            data.get("volume")
            or data.get("regularMarketVolume")
            or data.get("Volume")
            or data.get("market_volume")
        )
        if volume_value:
            market_data["volume"] = volume_value

        # PE ratio fields
        pe_ratio_value = (
            data.get("pe_ratio")
            or data.get("trailingPE")
            or data.get("PE Ratio")
            or data.get("price_earnings_ratio")
        )
        if pe_ratio_value:
            market_data["pe_ratio"] = pe_ratio_value

        # Additional market metrics
        if data.get("earningsPerShare"):
            market_data["earnings_per_share"] = data["earningsPerShare"]
        if data.get("bookValuePerShare"):
            market_data["book_value_per_share"] = data["bookValuePerShare"]
        if data.get("salesPerShare"):
            market_data["sales_per_share"] = data["salesPerShare"]

        return market_data

    def _metrics_to_dict(self, metrics: FinancialMetrics) -> Dict[str, Any]:
        """Convert FinancialMetrics object to dictionary."""
        return {
            "valuation": {
                "pe_ratio": metrics.pe_ratio,
                "forward_pe": metrics.forward_pe,
                "price_to_book": metrics.price_to_book,
                "price_to_sales": metrics.price_to_sales,
                "ev_to_ebitda": metrics.ev_to_ebitda,
            },
            "profitability": {
                "gross_margin": metrics.gross_margin,
                "operating_margin": metrics.operating_margin,
                "net_margin": metrics.net_margin,
                "roe": metrics.roe,
                "roa": metrics.roa,
                "roic": metrics.roic,
            },
            "financial_strength": {
                "debt_to_equity": metrics.debt_to_equity,
                "current_ratio": metrics.current_ratio,
                "quick_ratio": metrics.quick_ratio,
                "interest_coverage": metrics.interest_coverage,
            },
        }

    def _calculate_quality_metrics(
        self, source_data: Dict[str, Any], transformed_data: Dict[str, Any]
    ) -> DataQualityMetrics:
        """Calculate data quality metrics."""
        metrics = DataQualityMetrics()

        # Completeness: Check required fields
        required_fields = ["company_info", "financial_statements", "financial_metrics"]
        present_fields = sum(
            1 for field in required_fields if field in transformed_data
        )
        metrics.completeness = present_fields / len(required_fields)

        # Accuracy: Check if numeric values are reasonable
        accuracy_score = 0.0
        accuracy_checks = 0

        if "financial_statements" in transformed_data:
            income_stmt = transformed_data["financial_statements"].get(
                "income_statement", {}
            )
            if income_stmt.get("revenue") and income_stmt.get("net_income"):
                if (
                    income_stmt["revenue"] > 0
                    and income_stmt["net_income"] <= income_stmt["revenue"]
                ):
                    accuracy_score += 1.0
                accuracy_checks += 1

        if accuracy_checks > 0:
            metrics.accuracy = accuracy_score / accuracy_checks

        # Consistency: Check if ratios are within reasonable ranges
        consistency_score = 0.0
        consistency_checks = 0

        if "financial_metrics" in transformed_data:
            profitability = transformed_data["financial_metrics"].get(
                "profitability", {}
            )
            if profitability.get("gross_margin"):
                margin = profitability["gross_margin"]
                if 0 <= margin <= 100:
                    consistency_score += 1.0
                consistency_checks += 1

        if consistency_checks > 0:
            metrics.consistency = consistency_score / consistency_checks

        # Timeliness: Assume data is current if no timestamp issues
        metrics.timeliness = 1.0

        # Calculate overall score
        metrics.calculate_overall_score()

        return metrics
