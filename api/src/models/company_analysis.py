#!/usr/bin/env python3
"""
Company Analysis Data Models
Story-005: Enhanced Company Profile & Fundamentals Analysis (MVP)

Data models for company analysis, sector benchmarking, and financial metrics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FinancialMetrics(BaseModel):
    """Financial metrics for a company."""

    # Valuation metrics
    pe_ratio: Optional[float] = Field(None, description="Price-to-Earnings ratio")
    forward_pe: Optional[float] = Field(None, description="Forward P/E ratio")
    price_to_book: Optional[float] = Field(None, description="Price-to-Book ratio")
    price_to_sales: Optional[float] = Field(None, description="Price-to-Sales ratio")
    ev_to_ebitda: Optional[float] = Field(None, description="EV/EBITDA ratio")

    # Profitability metrics
    gross_margin: Optional[float] = Field(None, description="Gross margin percentage")
    operating_margin: Optional[float] = Field(
        None, description="Operating margin percentage"
    )
    net_margin: Optional[float] = Field(None, description="Net margin percentage")
    roe: Optional[float] = Field(None, description="Return on Equity")
    roa: Optional[float] = Field(None, description="Return on Assets")
    roic: Optional[float] = Field(None, description="Return on Invested Capital")

    # Growth metrics
    revenue_growth: Optional[float] = Field(None, description="Revenue growth rate")
    earnings_growth: Optional[float] = Field(None, description="Earnings growth rate")
    book_value_growth: Optional[float] = Field(
        None, description="Book value growth rate"
    )

    # Financial strength metrics
    debt_to_equity: Optional[float] = Field(None, description="Debt-to-Equity ratio")
    current_ratio: Optional[float] = Field(None, description="Current ratio")
    quick_ratio: Optional[float] = Field(None, description="Quick ratio")
    interest_coverage: Optional[float] = Field(
        None, description="Interest coverage ratio"
    )

    # Efficiency metrics
    asset_turnover: Optional[float] = Field(None, description="Asset turnover ratio")
    receivables_turnover: Optional[float] = Field(
        None, description="Receivables turnover ratio"
    )


class CompanyProfile(BaseModel):
    """Company profile with basic information and financial metrics."""

    symbol: str = Field(..., description="Company ticker symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Business sector")
    industry: Optional[str] = Field(None, description="Industry classification")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    country: Optional[str] = Field(None, description="Country of incorporation")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    enterprise_value: Optional[float] = Field(None, description="Enterprise value")
    website: Optional[str] = Field(None, description="Company website")
    description: Optional[str] = Field(None, description="Business description")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    ceo: Optional[str] = Field(None, description="Chief Executive Officer")
    headquarters: Optional[str] = Field(None, description="Headquarters location")
    founded_year: Optional[int] = Field(None, description="Year founded")
    financial_metrics: Optional[FinancialMetrics] = Field(
        None, description="Financial metrics"
    )
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class SectorBenchmark(BaseModel):
    """Sector benchmark data from sector ETF."""

    sector: str = Field(..., description="Sector name")
    etf_symbol: str = Field(..., description="Sector ETF symbol")
    etf_name: str = Field(..., description="Sector ETF name")
    current_price: Optional[float] = Field(None, description="Current ETF price")
    market_cap: Optional[float] = Field(None, description="ETF market cap")
    pe_ratio: Optional[float] = Field(None, description="ETF P/E ratio")
    pb_ratio: Optional[float] = Field(None, description="ETF P/B ratio")
    dividend_yield: Optional[float] = Field(None, description="ETF dividend yield")
    beta: Optional[float] = Field(None, description="ETF beta")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class SectorComparison(BaseModel):
    """Comparison between company and sector benchmark."""

    company_symbol: str = Field(..., description="Company symbol")
    sector: str = Field(..., description="Sector name")
    etf_symbol: str = Field(..., description="Sector ETF symbol")
    comparison_date: datetime = Field(..., description="Comparison date")

    # Relative metrics (company vs sector)
    pe_ratio_vs_sector: Optional[float] = Field(
        None, description="Company P/E vs Sector P/E"
    )
    pb_ratio_vs_sector: Optional[float] = Field(
        None, description="Company P/B vs Sector P/B"
    )
    market_cap_rank: Optional[str] = Field(
        None, description="Market cap ranking vs sector"
    )

    # Performance indicators
    outperforming_sector: Optional[bool] = Field(
        None, description="Whether company outperforms sector"
    )
    relative_valuation: Optional[str] = Field(
        None, description="Relative valuation assessment"
    )


class CompanyAnalysis(BaseModel):
    """Comprehensive company analysis result."""

    company_profile: CompanyProfile = Field(..., description="Company profile")
    sector_comparison: Optional[SectorComparison] = Field(
        None, description="Sector comparison"
    )
    analysis_date: datetime = Field(..., description="Analysis date")
    analysis_type: str = Field(..., description="Type of analysis performed")

    # Analysis summary
    overall_score: Optional[float] = Field(
        None, description="Overall analysis score (0-100)"
    )
    strengths: Optional[List[str]] = Field(None, description="Company strengths")
    weaknesses: Optional[List[str]] = Field(None, description="Company weaknesses")
    recommendations: Optional[List[str]] = Field(
        None, description="Investment recommendations"
    )


class AnalysisRequest(BaseModel):
    """Request for company analysis."""

    symbol: str = Field(..., description="Company ticker symbol")
    analysis_type: str = Field("basic", description="Type of analysis to perform")
    include_sector_comparison: bool = Field(
        True, description="Include sector comparison"
    )
    include_financial_metrics: bool = Field(
        True, description="Include financial metrics"
    )


class AnalysisResponse(BaseModel):
    """Response from company analysis."""

    success: bool = Field(..., description="Whether analysis was successful")
    analysis: Optional[CompanyAnalysis] = Field(None, description="Analysis results")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds"
    )


class DataUpdateRequest(BaseModel):
    """Request for data update."""

    symbol: str = Field(..., description="Company ticker symbol")
    update_type: str = Field("full", description="Type of update (full, incremental)")
    force_update: bool = Field(
        False, description="Force update even if recent data exists"
    )


class DataUpdateResponse(BaseModel):
    """Response from data update request."""

    success: bool = Field(..., description="Whether update was successful")
    symbol: str = Field(..., description="Company ticker symbol")
    message: str = Field(..., description="Update status message")
    timestamp: datetime = Field(..., description="Update timestamp")
    status: str = Field(
        ..., description="Update status (queued, processing, completed, failed)"
    )


class SectorListResponse(BaseModel):
    """Response with list of available sectors."""

    sectors: List[Dict[str, str]] = Field(
        ..., description="List of sectors and their ETF symbols"
    )
    total_count: int = Field(..., description="Total number of sectors")
    last_updated: datetime = Field(..., description="Last update timestamp")
