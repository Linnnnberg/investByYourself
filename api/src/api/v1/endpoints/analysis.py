#!/usr/bin/env python3
"""
InvestByYourself API Financial Analysis Endpoints
Tech-028: API Implementation

Financial analysis endpoints for technical and fundamental analysis.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ....models.company_analysis import (
    AnalysisRequest,
    AnalysisResponse,
    CompanyProfile,
    DataUpdateRequest,
    DataUpdateResponse,
    SectorBenchmark,
    SectorComparison,
    SectorListResponse,
)
from ....services.company_analysis import company_analysis_service

router = APIRouter()


@router.get("/health", summary="Analysis Service Health Check")
async def analysis_health():
    """Health check endpoint for analysis service."""
    return {
        "status": "healthy",
        "service": "Financial Analysis API",
        "version": "1.0.0",
        "endpoints": [
            "GET /companies/{symbol} - Get company profile",
            "POST /companies/analyze - Analyze company",
            "GET /sectors - List available sectors",
            "GET /sectors/{sector} - Get sector benchmark",
            "GET /companies/{symbol}/sector-comparison - Compare company to sector",
            "POST /companies/{symbol}/update - Trigger data update",
        ],
    }


@router.get(
    "/companies/{symbol}", response_model=CompanyProfile, summary="Get Company Profile"
)
async def get_company_profile(symbol: str):
    """
    Get comprehensive company profile with financial metrics.

    Args:
        symbol: Company ticker symbol (e.g., AAPL, MSFT)

    Returns:
        CompanyProfile with basic information and financial metrics
    """
    try:
        profile = await company_analysis_service.get_company_profile(symbol)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Company {symbol} not found")

        return profile

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get company profile: {str(e)}"
        )


@router.post(
    "/companies/analyze", response_model=AnalysisResponse, summary="Analyze Company"
)
async def analyze_company(request: AnalysisRequest):
    """
    Perform comprehensive company analysis.

    Args:
        request: Analysis request with company symbol and analysis type

    Returns:
        AnalysisResponse with analysis results
    """
    try:
        response = await company_analysis_service.analyze_company(request)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get(
    "/sectors", response_model=SectorListResponse, summary="List Available Sectors"
)
async def list_sectors():
    """
    Get list of available sectors and their ETF symbols.

    Returns:
        SectorListResponse with sector information
    """
    try:
        sectors = [
            {"sector": sector, "etf_symbol": etf_symbol}
            for etf_symbol, sector in company_analysis_service.sector_etfs.items()
        ]

        return SectorListResponse(
            sectors=sectors,
            total_count=len(sectors),
            last_updated=company_analysis_service.get_current_timestamp(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sectors: {str(e)}")


@router.get(
    "/sectors/{sector}", response_model=SectorBenchmark, summary="Get Sector Benchmark"
)
async def get_sector_benchmark(sector: str):
    """
    Get sector benchmark data.

    Args:
        sector: Sector name (e.g., Technology, Financials)

    Returns:
        SectorBenchmark with sector ETF data
    """
    try:
        benchmark = await company_analysis_service.get_sector_benchmark(sector)
        if not benchmark:
            raise HTTPException(status_code=404, detail=f"Sector {sector} not found")

        return benchmark

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get sector benchmark: {str(e)}"
        )


@router.get(
    "/companies/{symbol}/sector-comparison",
    response_model=SectorComparison,
    summary="Compare Company to Sector",
)
async def compare_company_to_sector(symbol: str):
    """
    Compare a company to its sector benchmark.

    Args:
        symbol: Company ticker symbol

    Returns:
        SectorComparison with relative metrics
    """
    try:
        comparison = await company_analysis_service.compare_company_to_sector(symbol)
        if not comparison:
            raise HTTPException(
                status_code=404, detail=f"Company {symbol} or sector not found"
            )

        return comparison

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to compare company to sector: {str(e)}"
        )


@router.get(
    "/sectors/benchmarks/all",
    response_model=List[SectorBenchmark],
    summary="Get All Sector Benchmarks",
)
async def get_all_sector_benchmarks():
    """
    Get benchmark data for all 10 sectors.

    Returns:
        List of SectorBenchmark objects
    """
    try:
        benchmarks = await company_analysis_service.get_all_sector_benchmarks()
        return benchmarks

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get sector benchmarks: {str(e)}"
        )


@router.post(
    "/companies/{symbol}/update",
    response_model=DataUpdateResponse,
    summary="Trigger Data Update",
)
async def trigger_data_update(symbol: str, request: DataUpdateRequest = None):
    """
    Trigger data update for a specific company.

    Args:
        symbol: Company ticker symbol
        request: Data update request (optional)

    Returns:
        DataUpdateResponse with update status
    """
    try:
        if request and request.symbol != symbol:
            raise HTTPException(status_code=400, detail="Symbol mismatch in request")

        result = await company_analysis_service.trigger_data_update(symbol)

        return DataUpdateResponse(
            success=result["success"],
            symbol=result["symbol"],
            message=result["message"],
            timestamp=result["timestamp"],
            status=result["status"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger data update: {str(e)}"
        )


@router.get("/companies/{symbol}/metrics", summary="Get Company Financial Metrics")
async def get_company_metrics(symbol: str):
    """
    Get detailed financial metrics for a company.

    Args:
        symbol: Company ticker symbol

    Returns:
        Financial metrics and ratios
    """
    try:
        profile = await company_analysis_service.get_company_profile(symbol)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Company {symbol} not found")

        if not profile.financial_metrics:
            raise HTTPException(
                status_code=404, detail=f"No financial metrics available for {symbol}"
            )

        return {
            "symbol": symbol,
            "metrics": profile.financial_metrics,
            "last_updated": profile.last_updated,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get company metrics: {str(e)}"
        )


# - GET /analysis/technical/{symbol} - Technical analysis
# - GET /analysis/fundamental/{symbol} - Fundamental analysis
# - GET /analysis/indicators/{symbol} - Technical indicators
# - GET /analysis/valuation/{symbol} - Valuation analysis
# - GET /analysis/risk/{symbol} - Risk analysis
# - POST /analysis/correlation - Correlation analysis
# - GET /analysis/strategies - Available strategies
