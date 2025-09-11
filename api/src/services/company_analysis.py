#!/usr/bin/env python3
"""
Company Analysis Service
Story-005: Enhanced Company Profile & Fundamentals Analysis (MVP)

This service provides company analysis capabilities including:
- Basic company profile collection and analysis
- Sector benchmarking with 10 sector ETFs
- Financial ratio analysis and comparison
- Event-triggered data updates
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import structlog
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db_session
from ..models.company_analysis import (
    AnalysisRequest,
    AnalysisResponse,
    CompanyAnalysis,
    CompanyProfile,
    FinancialMetrics,
    SectorBenchmark,
    SectorComparison,
)
from ..models.database import Company, FinancialRatio, MarketData

logger = structlog.get_logger(__name__)


class CompanyAnalysisService:
    """Service for company analysis and sector benchmarking."""

    def __init__(self):
        """Initialize the company analysis service."""
        self.logger = structlog.get_logger(__name__)

        # 10 sector ETFs for benchmarking
        self.sector_etfs = {
            "XLK": "Technology",
            "XLF": "Financials",
            "XLE": "Energy",
            "XLV": "Healthcare",
            "XLI": "Industrials",
            "XLB": "Materials",
            "XLU": "Utilities",
            "XLP": "Consumer Staples",
            "XLY": "Consumer Discretionary",
            "XLC": "Communication Services",
        }

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """
        Get comprehensive company profile with basic analysis.

        Args:
            symbol: Company ticker symbol

        Returns:
            CompanyProfile object or None if not found
        """
        try:
            session_factory = await get_db_session()
            async with session_factory() as session:
                # Get company basic info
                company_query = select(Company).where(Company.symbol == symbol.upper())
                result = await session.execute(company_query)
                company = result.scalar_one_or_none()

                if not company:
                    self.logger.warning("Company not found", symbol=symbol)
                    return None

                # Get latest market data
                market_query = (
                    select(MarketData)
                    .where(MarketData.company_id == company.id)
                    .order_by(desc(MarketData.data_date))
                    .limit(1)
                )
                market_result = await session.execute(market_query)
                market_data = market_result.scalar_one_or_none()

                # Get latest financial ratios
                ratios_query = (
                    select(FinancialRatio)
                    .where(FinancialRatio.company_id == company.id)
                    .order_by(desc(FinancialRatio.ratio_date))
                    .limit(10)  # Get last 10 ratio entries
                )
                ratios_result = await session.execute(ratios_query)
                ratios = ratios_result.scalars().all()

                # Build financial metrics
                financial_metrics = self._build_financial_metrics(ratios, market_data)

                # Create company profile
                profile = CompanyProfile(
                    symbol=company.symbol,
                    name=company.name,
                    sector=company.sector,
                    industry=company.industry,
                    exchange=company.exchange,
                    country=company.country,
                    market_cap=company.market_cap,
                    enterprise_value=company.enterprise_value,
                    website=company.website,
                    description=company.description,
                    employee_count=company.employee_count,
                    ceo=company.ceo,
                    headquarters=company.headquarters,
                    founded_year=company.founded_year,
                    financial_metrics=financial_metrics,
                    last_updated=company.updated_at,
                )

                self.logger.info("Company profile retrieved", symbol=symbol)
                return profile

        except Exception as e:
            self.logger.error(
                "Failed to get company profile", symbol=symbol, error=str(e)
            )
            return None

    async def get_sector_benchmark(self, sector: str) -> Optional[SectorBenchmark]:
        """
        Get sector benchmark data for the given sector.

        Args:
            sector: Sector name (e.g., "Technology", "Financials")

        Returns:
            SectorBenchmark object or None if not found
        """
        try:
            # Find the ETF symbol for this sector
            etf_symbol = None
            for symbol, sector_name in self.sector_etfs.items():
                if sector_name.lower() == sector.lower():
                    etf_symbol = symbol
                    break

            if not etf_symbol:
                self.logger.warning("Sector ETF not found", sector=sector)
                return None

            # Get ETF data (treating it as a company in our database)
            session_factory = await get_db_session()
            async with session_factory() as session:
                company_query = select(Company).where(Company.symbol == etf_symbol)
                result = await session.execute(company_query)
                company = result.scalar_one_or_none()

                if not company:
                    self.logger.warning(
                        "Sector ETF not found in database", etf_symbol=etf_symbol
                    )
                    return None

                # Get latest market data for the ETF
                market_query = (
                    select(MarketData)
                    .where(MarketData.company_id == company.id)
                    .order_by(desc(MarketData.data_date))
                    .limit(1)
                )
                market_result = await session.execute(market_query)
                market_data = market_result.scalar_one_or_none()

                if not market_data:
                    self.logger.warning(
                        "No market data for sector ETF", etf_symbol=etf_symbol
                    )
                    return None

                # Create sector benchmark
                benchmark = SectorBenchmark(
                    sector=sector,
                    etf_symbol=etf_symbol,
                    etf_name=company.name,
                    current_price=market_data.close_price,
                    market_cap=market_data.market_cap,
                    pe_ratio=market_data.pe_ratio,
                    pb_ratio=market_data.pb_ratio,
                    dividend_yield=market_data.dividend_yield,
                    beta=market_data.beta,
                    last_updated=market_data.created_at,
                )

                self.logger.info(
                    "Sector benchmark retrieved", sector=sector, etf_symbol=etf_symbol
                )
                return benchmark

        except Exception as e:
            self.logger.error(
                "Failed to get sector benchmark", sector=sector, error=str(e)
            )
            return None

    async def compare_company_to_sector(
        self, symbol: str
    ) -> Optional[SectorComparison]:
        """
        Compare a company to its sector benchmark.

        Args:
            symbol: Company ticker symbol

        Returns:
            SectorComparison object or None if not found
        """
        try:
            # Get company profile
            company_profile = await self.get_company_profile(symbol)
            if not company_profile:
                return None

            # Get sector benchmark
            sector_benchmark = await self.get_sector_benchmark(company_profile.sector)
            if not sector_benchmark:
                return None

            # Calculate comparison metrics
            comparison = self._calculate_sector_comparison(
                company_profile, sector_benchmark
            )

            self.logger.info(
                "Sector comparison completed",
                symbol=symbol,
                sector=company_profile.sector,
            )
            return comparison

        except Exception as e:
            self.logger.error(
                "Failed to compare company to sector", symbol=symbol, error=str(e)
            )
            return None

    async def get_all_sector_benchmarks(self) -> List[SectorBenchmark]:
        """
        Get benchmark data for all 10 sectors.

        Returns:
            List of SectorBenchmark objects
        """
        benchmarks = []

        for sector in self.sector_etfs.values():
            benchmark = await self.get_sector_benchmark(sector)
            if benchmark:
                benchmarks.append(benchmark)

        self.logger.info("All sector benchmarks retrieved", count=len(benchmarks))
        return benchmarks

    async def analyze_company(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Perform comprehensive company analysis.

        Args:
            request: Analysis request with company symbol and analysis type

        Returns:
            AnalysisResponse with analysis results
        """
        try:
            symbol = request.symbol.upper()

            # Get company profile
            company_profile = await self.get_company_profile(symbol)
            if not company_profile:
                return AnalysisResponse(
                    success=False, error=f"Company {symbol} not found", analysis=None
                )

            # Get sector comparison
            sector_comparison = await self.compare_company_to_sector(symbol)

            # Create analysis result
            analysis = CompanyAnalysis(
                company_profile=company_profile,
                sector_comparison=sector_comparison,
                analysis_date=datetime.now(),
                analysis_type=request.analysis_type,
            )

            return AnalysisResponse(success=True, analysis=analysis, error=None)

        except Exception as e:
            self.logger.error(
                "Failed to analyze company", symbol=request.symbol, error=str(e)
            )
            return AnalysisResponse(
                success=False, error=f"Analysis failed: {str(e)}", analysis=None
            )

    async def trigger_data_update(self, symbol: str) -> Dict[str, Any]:
        """
        Trigger data update for a specific company.

        Args:
            symbol: Company ticker symbol

        Returns:
            Update status and results
        """
        try:
            # This would integrate with the ETL pipeline to trigger data collection
            # For now, we'll return a placeholder response

            self.logger.info("Data update triggered", symbol=symbol)

            return {
                "success": True,
                "symbol": symbol,
                "message": f"Data update triggered for {symbol}",
                "timestamp": datetime.now().isoformat(),
                "status": "queued",
            }

        except Exception as e:
            self.logger.error(
                "Failed to trigger data update", symbol=symbol, error=str(e)
            )
            return {
                "success": False,
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _build_financial_metrics(
        self, ratios: List[FinancialRatio], market_data: Optional[MarketData]
    ) -> FinancialMetrics:
        """Build financial metrics from ratios and market data."""
        metrics = FinancialMetrics()

        # Extract ratios by type
        ratio_dict = {ratio.ratio_type: ratio.ratio_value for ratio in ratios}

        # Valuation metrics
        metrics.pe_ratio = ratio_dict.get("pe_ratio") or (
            market_data.pe_ratio if market_data else None
        )
        metrics.price_to_book = ratio_dict.get("price_to_book") or (
            market_data.pb_ratio if market_data else None
        )
        metrics.price_to_sales = ratio_dict.get("price_to_sales")
        metrics.ev_to_ebitda = ratio_dict.get("ev_to_ebitda")

        # Profitability metrics
        metrics.gross_margin = ratio_dict.get("gross_margin")
        metrics.operating_margin = ratio_dict.get("operating_margin")
        metrics.net_margin = ratio_dict.get("net_margin")
        metrics.roe = ratio_dict.get("roe")
        metrics.roa = ratio_dict.get("roa")
        metrics.roic = ratio_dict.get("roic")

        # Growth metrics
        metrics.revenue_growth = ratio_dict.get("revenue_growth")
        metrics.earnings_growth = ratio_dict.get("earnings_growth")

        # Financial strength metrics
        metrics.debt_to_equity = ratio_dict.get("debt_to_equity")
        metrics.current_ratio = ratio_dict.get("current_ratio")
        metrics.quick_ratio = ratio_dict.get("quick_ratio")

        # Efficiency metrics
        metrics.asset_turnover = ratio_dict.get("asset_turnover")
        metrics.receivables_turnover = ratio_dict.get("receivables_turnover")

        return metrics

    def _calculate_sector_comparison(
        self, company: CompanyProfile, sector: SectorBenchmark
    ) -> SectorComparison:
        """Calculate comparison metrics between company and sector."""
        comparison = SectorComparison(
            company_symbol=company.symbol,
            sector=sector.sector,
            etf_symbol=sector.etf_symbol,
            comparison_date=datetime.now(),
        )

        # Compare key metrics
        if company.financial_metrics.pe_ratio and sector.pe_ratio:
            comparison.pe_ratio_vs_sector = (
                company.financial_metrics.pe_ratio / sector.pe_ratio
            )

        if company.financial_metrics.price_to_book and sector.pb_ratio:
            comparison.pb_ratio_vs_sector = (
                company.financial_metrics.price_to_book / sector.pb_ratio
            )

        # Calculate relative performance (simplified)
        if company.market_cap and sector.market_cap:
            comparison.market_cap_rank = (
                "Large" if company.market_cap > sector.market_cap else "Small"
            )

        return comparison

    def get_current_timestamp(self) -> datetime:
        """Get current timestamp."""
        return datetime.now()


# Create service instance
company_analysis_service = CompanyAnalysisService()
