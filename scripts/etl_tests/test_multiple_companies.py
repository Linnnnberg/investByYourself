#!/usr/bin/env python3
"""
Multiple Companies Financial Analysis - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 2

This script demonstrates the data processing engine capabilities
by analyzing multiple companies and generating comparison charts.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.transformers import FinancialDataTransformer, TransformationRule


class CompanyFinancialAnalyzer:
    """Analyzes financial data for multiple companies and generates visualizations."""

    def __init__(self):
        """Initialize the analyzer."""
        self.transformer = FinancialDataTransformer(
            name="Multi-Company Financial Analyzer",
            description="Analyzes and compares financial metrics across companies",
            max_concurrent_transformations=10,
        )
        self.companies_data = {}
        self.analysis_results = {}

    def get_sample_company_data(self) -> Dict[str, Dict[str, Any]]:
        """Get sample financial data for multiple companies."""
        return {
            "AAPL": {
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "country": "US",
                "website": "https://www.apple.com",
                # Income Statement (in millions USD)
                "totalRevenue": 394328.0,  # $394.3B
                "costOfRevenue": 223546.0,  # $223.5B
                "grossProfit": 170782.0,  # $170.8B
                "operatingIncome": 114301.0,  # $114.3B
                "netIncome": 96995.0,  # $97.0B
                "ebitda": 120000.0,  # Estimated EBITDA
                # Balance Sheet (in millions USD)
                "totalAssets": 352755.0,  # $352.8B
                "currentAssets": 143713.0,  # $143.7B
                "totalLiabilities": 287912.0,  # $287.9B
                "totalEquity": 64843.0,  # $64.8B
                "totalDebt": 95977.0,  # $96.0B
                "currentLiabilities": 137632.0,  # $137.6B
                # Market Data
                "marketCap": 3000000000000,  # $3T market cap
                "currentPrice": 175.0,  # $175 per share
                "trailingPE": 18.0,  # P/E ratio
                "earningsPerShare": 6.16,  # EPS
                "bookValuePerShare": 4.25,  # Book value per share
                "salesPerShare": 25.0,  # Sales per share
                "source": "yahoo_finance",
                "timestamp": datetime.now().isoformat(),
            },
            "MSFT": {
                "symbol": "MSFT",
                "company_name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
                "country": "US",
                "website": "https://www.microsoft.com",
                # Income Statement (in millions USD)
                "totalRevenue": 211915.0,  # $211.9B
                "costOfRevenue": 65863.0,  # $65.9B
                "grossProfit": 146052.0,  # $146.1B
                "operatingIncome": 88482.0,  # $88.5B
                "netIncome": 72415.0,  # $72.4B
                "ebitda": 95000.0,  # Estimated EBITDA
                # Balance Sheet (in millions USD)
                "totalAssets": 411976.0,  # $412.0B
                "currentAssets": 184257.0,  # $184.3B
                "totalLiabilities": 198298.0,  # $198.3B
                "totalEquity": 213678.0,  # $213.7B
                "totalDebt": 59578.0,  # $59.6B
                "currentLiabilities": 110471.0,  # $110.5B
                # Market Data
                "marketCap": 2800000000000,  # $2.8T market cap
                "currentPrice": 375.0,  # $375 per share
                "trailingPE": 28.0,  # P/E ratio
                "earningsPerShare": 13.39,  # EPS
                "bookValuePerShare": 28.50,  # Book value per share
                "salesPerShare": 28.0,  # Sales per share
                "source": "yahoo_finance",
                "timestamp": datetime.now().isoformat(),
            },
            "GOOGL": {
                "symbol": "GOOGL",
                "company_name": "Alphabet Inc.",
                "sector": "Technology",
                "industry": "Internet Services",
                "country": "US",
                "website": "https://www.google.com",
                # Income Statement (in millions USD)
                "totalRevenue": 307394.0,  # $307.4B
                "costOfRevenue": 126203.0,  # $126.2B
                "grossProfit": 181191.0,  # $181.2B
                "operatingIncome": 84289.0,  # $84.3B
                "netIncome": 76033.0,  # $76.0B
                "ebitda": 95000.0,  # Estimated EBITDA
                # Balance Sheet (in millions USD)
                "totalAssets": 402392.0,  # $402.4B
                "currentAssets": 184633.0,  # $184.6B
                "totalLiabilities": 109120.0,  # $109.1B
                "totalEquity": 293272.0,  # $293.3B
                "totalDebt": 13959.0,  # $14.0B
                "currentLiabilities": 74889.0,  # $74.9B
                # Market Data
                "marketCap": 1900000000000,  # $1.9T market cap
                "currentPrice": 150.0,  # $150 per share
                "trailingPE": 25.0,  # P/E ratio
                "earningsPerShare": 6.00,  # EPS
                "bookValuePerShare": 23.50,  # Book value per share
                "salesPerShare": 24.5,  # Sales per share
                "source": "yahoo_finance",
                "timestamp": datetime.now().isoformat(),
            },
            "TSLA": {
                "symbol": "TSLA",
                "company_name": "Tesla, Inc.",
                "sector": "Consumer Discretionary",
                "industry": "Automobiles",
                "country": "US",
                "website": "https://www.tesla.com",
                # Income Statement (in millions USD)
                "totalRevenue": 96773.0,  # $96.8B
                "costOfRevenue": 79113.0,  # $79.1B
                "grossProfit": 17660.0,  # $17.7B
                "operatingIncome": 8891.0,  # $8.9B
                "netIncome": 14999.0,  # $15.0B
                "ebitda": 18000.0,  # Estimated EBITDA
                # Balance Sheet (in millions USD)
                "totalAssets": 106618.0,  # $106.6B
                "currentAssets": 45666.0,  # $45.7B
                "totalLiabilities": 64216.0,  # $64.2B
                "totalEquity": 42402.0,  # $42.4B
                "totalDebt": 2197.0,  # $2.2B
                "currentLiabilities": 29047.0,  # $29.0B
                # Market Data
                "marketCap": 800000000000,  # $800B market cap
                "currentPrice": 250.0,  # $250 per share
                "trailingPE": 53.0,  # P/E ratio
                "earningsPerShare": 4.72,  # EPS
                "bookValuePerShare": 13.30,  # Book value per share
                "salesPerShare": 30.5,  # Sales per share
                "source": "yahoo_finance",
                "timestamp": datetime.now().isoformat(),
            },
            "AMZN": {
                "symbol": "AMZN",
                "company_name": "Amazon.com, Inc.",
                "sector": "Consumer Discretionary",
                "industry": "Internet Retail",
                "country": "US",
                "website": "https://www.amazon.com",
                # Income Statement (in millions USD)
                "totalRevenue": 574785.0,  # $574.8B
                "costOfRevenue": 316824.0,  # $316.8B
                "grossProfit": 257961.0,  # $258.0B
                "operatingIncome": 24512.0,  # $24.5B
                "netIncome": 30425.0,  # $30.4B
                "ebitda": 35000.0,  # Estimated EBITDA
                # Balance Sheet (in millions USD)
                "totalAssets": 527854.0,  # $527.9B
                "currentAssets": 143286.0,  # $143.3B
                "totalLiabilities": 430109.0,  # $430.1B
                "totalEquity": 97745.0,  # $97.7B
                "totalDebt": 138791.0,  # $138.8B
                "currentLiabilities": 155393.0,  # $155.4B
                # Market Data
                "marketCap": 1800000000000,  # $1.8T market cap
                "currentPrice": 175.0,  # $175 per share
                "trailingPE": 59.0,  # P/E ratio
                "earningsPerShare": 2.97,  # EPS
                "bookValuePerShare": 19.50,  # Book value per share
                "salesPerShare": 56.0,  # Sales per share
                "source": "yahoo_finance",
                "timestamp": datetime.now().isoformat(),
            },
        }

    async def analyze_companies(self) -> Dict[str, Any]:
        """Analyze financial data for all companies."""
        print("🔍 Starting Multi-Company Financial Analysis")
        print("=" * 60)

        companies_data = self.get_sample_company_data()
        results = {}

        for symbol, data in companies_data.items():
            print(f"\n📊 Analyzing {symbol} ({data['company_name']})...")

            try:
                # Transform the data
                result = await self.transformer.transform_data(data)

                if result.success:
                    results[symbol] = {
                        "company_info": result.transformed_data["company_info"],
                        "financial_statements": result.transformed_data[
                            "financial_statements"
                        ],
                        "financial_metrics": result.transformed_data[
                            "financial_metrics"
                        ],
                        "market_data": result.transformed_data["market_data"],
                        "quality_score": result.quality_metrics.overall_score,
                        "quality_level": result.quality_level.value,
                    }

                    print(f"   ✅ Transformation successful")
                    print(
                        f"   📈 Quality Score: {result.quality_metrics.overall_score:.1%}"
                    )
                    print(f"   🎯 Quality Level: {result.quality_level.value.upper()}")

                    # Show key metrics
                    metrics = result.transformed_data["financial_metrics"]
                    if metrics.get("profitability", {}).get("gross_margin"):
                        print(
                            f"   💰 Gross Margin: {metrics['profitability']['gross_margin']:.1f}%"
                        )
                    if metrics.get("profitability", {}).get("roe"):
                        print(f"   📊 ROE: {metrics['profitability']['roe']:.1f}%")

                    # Show financial strength metrics
                    if metrics.get("financial_strength", {}).get("debt_to_equity"):
                        print(
                            f"   💪 Debt/Equity: {metrics['financial_strength']['debt_to_equity']:.2f}"
                        )
                    if metrics.get("financial_strength", {}).get("current_ratio"):
                        print(
                            f"   📈 Current Ratio: {metrics['financial_strength']['current_ratio']:.2f}"
                        )

                    # Debug: Show extracted financial statements
                    financial_statements = result.transformed_data[
                        "financial_statements"
                    ]
                    if "balance_sheet" in financial_statements:
                        balance_sheet = financial_statements["balance_sheet"]
                        print(
                            f"   🔍 Balance Sheet Fields: {list(balance_sheet.keys())}"
                        )
                        if balance_sheet.get("total_debt"):
                            print(
                                f"      Total Debt: ${balance_sheet['total_debt']/1000:.1f}B"
                            )
                        if balance_sheet.get("total_equity"):
                            print(
                                f"      Total Equity: ${balance_sheet['total_equity']/1000:.1f}B"
                            )
                else:
                    print(f"   ❌ Transformation failed: {result.errors}")

            except Exception as e:
                print(f"   ❌ Error analyzing {symbol}: {str(e)}")

        self.analysis_results = results
        return results

    def create_comparison_charts(self):
        """Create comprehensive comparison charts for all companies."""
        if not self.analysis_results:
            print("❌ No analysis results available. Run analyze_companies() first.")
            return

        print(f"\n📊 Creating Comparison Charts")
        print("=" * 60)

        # Set up the plotting style
        plt.style.use("default")
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(
            "Multi-Company Financial Analysis Comparison",
            fontsize=16,
            fontweight="bold",
        )

        companies = list(self.analysis_results.keys())

        # Chart 1: Profitability Metrics (Gross Margin, Operating Margin, Net Margin)
        self._create_profitability_chart(axes[0, 0], companies)

        # Chart 2: Return Metrics (ROE, ROA)
        self._create_return_metrics_chart(axes[0, 1], companies)

        # Chart 3: Valuation Metrics (P/E Ratio, Price/Book)
        self._create_valuation_chart(axes[0, 2], companies)

        # Chart 4: Financial Strength (Debt/Equity, Current Ratio)
        self._create_financial_strength_chart(axes[1, 0], companies)

        # Chart 5: Market Capitalization Comparison
        self._create_market_cap_chart(axes[1, 1], companies)

        # Chart 6: Data Quality Scores
        self._create_quality_scores_chart(axes[1, 2], companies)

        plt.tight_layout()
        plt.subplots_adjust(top=0.93)

        # Save the chart
        chart_filename = f"company_financial_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches="tight")
        print(f"   📈 Chart saved as: {chart_filename}")

        # Display the chart
        plt.show()

        return chart_filename

    def _create_profitability_chart(self, ax, companies):
        """Create profitability metrics comparison chart."""
        ax.set_title("Profitability Metrics Comparison", fontweight="bold")

        metrics = ["gross_margin", "operating_margin", "net_margin"]
        x = np.arange(len(companies))
        width = 0.25

        for i, metric in enumerate(metrics):
            values = []
            for company in companies:
                value = (
                    self.analysis_results[company]["financial_metrics"]
                    .get("profitability", {})
                    .get(metric, 0)
                )
                values.append(value if value is not None else 0)

            ax.bar(
                x + i * width,
                values,
                width,
                label=metric.replace("_", " ").title(),
                alpha=0.8,
            )

        ax.set_xlabel("Companies")
        ax.set_ylabel("Percentage (%)")
        ax.set_xticks(x + width)
        ax.set_xticklabels(companies)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _create_return_metrics_chart(self, ax, companies):
        """Create return metrics comparison chart."""
        ax.set_title("Return Metrics Comparison", fontweight="bold")

        metrics = ["roe", "roa"]
        x = np.arange(len(companies))
        width = 0.35

        for i, metric in enumerate(metrics):
            values = []
            for company in companies:
                value = (
                    self.analysis_results[company]["financial_metrics"]
                    .get("profitability", {})
                    .get(metric, 0)
                )
                values.append(value if value is not None else 0)

            ax.bar(x + i * width, values, width, label=metric.upper(), alpha=0.8)

        ax.set_xlabel("Companies")
        ax.set_ylabel("Percentage (%)")
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(companies)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _create_valuation_chart(self, ax, companies):
        """Create valuation metrics comparison chart."""
        ax.set_title("Valuation Metrics Comparison", fontweight="bold")

        # Get P/E ratios from market data
        pe_ratios = []
        for company in companies:
            pe = self.analysis_results[company]["market_data"].get("pe_ratio", 0)
            pe_ratios.append(pe if pe is not None else 0)

        bars = ax.bar(companies, pe_ratios, alpha=0.8, color="skyblue")
        ax.set_xlabel("Companies")
        ax.set_ylabel("P/E Ratio")
        ax.set_title("Price-to-Earnings (P/E) Ratio Comparison")
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, value in zip(bars, pe_ratios):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.5,
                f"{value:.1f}",
                ha="center",
                va="bottom",
            )

    def _create_financial_strength_chart(self, ax, companies):
        """Create financial strength metrics comparison chart."""
        ax.set_title("Financial Strength Metrics", fontweight="bold")

        # Get debt/equity ratios
        debt_equity = []
        for company in companies:
            de = (
                self.analysis_results[company]["financial_metrics"]
                .get("financial_strength", {})
                .get("debt_to_equity", 0)
            )
            debt_equity.append(de if de is not None else 0)

        bars = ax.bar(companies, debt_equity, alpha=0.8, color="lightcoral")
        ax.set_xlabel("Companies")
        ax.set_ylabel("Debt/Equity Ratio")
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, value in zip(bars, debt_equity):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.01,
                f"{value:.2f}",
                ha="center",
                va="bottom",
            )

    def _create_market_cap_chart(self, ax, companies):
        """Create market capitalization comparison chart."""
        ax.set_title("Market Capitalization Comparison", fontweight="bold")

        market_caps = []
        for company in companies:
            mc = self.analysis_results[company]["market_data"].get("market_cap", 0)
            market_caps.append(mc / 1e12)  # Convert to trillions

        bars = ax.bar(companies, market_caps, alpha=0.8, color="lightgreen")
        ax.set_xlabel("Companies")
        ax.set_ylabel("Market Cap (Trillions USD)")
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, value in zip(bars, market_caps):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.05,
                f"${value:.1f}T",
                ha="center",
                va="bottom",
            )

    def _create_quality_scores_chart(self, ax, companies):
        """Create data quality scores comparison chart."""
        ax.set_title("Data Quality Scores", fontweight="bold")

        quality_scores = []
        for company in companies:
            score = self.analysis_results[company]["quality_score"]
            quality_scores.append(score * 100)  # Convert to percentage

        bars = ax.bar(companies, quality_scores, alpha=0.8, color="gold")
        ax.set_xlabel("Companies")
        ax.set_ylabel("Quality Score (%)")
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, value in zip(bars, quality_scores):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{value:.0f}%",
                ha="center",
                va="bottom",
            )

    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        if not self.analysis_results:
            print("❌ No analysis results available. Run analyze_companies() first.")
            return

        print(f"\n📋 Financial Analysis Summary Report")
        print("=" * 60)

        # Create summary table
        summary_data = []
        for symbol, data in self.analysis_results.items():
            company_info = data["company_info"]
            financial_metrics = data["financial_metrics"]
            market_data = data["market_data"]

            summary_data.append(
                {
                    "Symbol": symbol,
                    "Company": company_info.get("company_name", "N/A"),
                    "Sector": company_info.get("sector", "N/A"),
                    "Market Cap": f"${market_data.get('market_cap', 0) / 1e12:.1f}T",
                    "P/E Ratio": f"{market_data.get('pe_ratio', 0):.1f}",
                    "Gross Margin": f"{financial_metrics.get('profitability', {}).get('gross_margin', 0):.1f}%",
                    "ROE": f"{financial_metrics.get('profitability', {}).get('roe', 0):.1f}%",
                    "Quality Score": f"{data['quality_score']:.1%}",
                }
            )

        # Display summary table
        df = pd.DataFrame(summary_data)
        print(df.to_string(index=False))

        # Key insights
        print(f"\n🔍 Key Insights:")

        # Best performers
        best_gross_margin = max(
            summary_data, key=lambda x: float(x["Gross Margin"].rstrip("%"))
        )
        best_roe = max(summary_data, key=lambda x: float(x["ROE"].rstrip("%")))
        lowest_pe = min(summary_data, key=lambda x: float(x["P/E Ratio"]))

        print(
            f"   🏆 Best Gross Margin: {best_gross_margin['Symbol']} ({best_gross_margin['Gross Margin']})"
        )
        print(f"   🏆 Best ROE: {best_roe['Symbol']} ({best_roe['ROE']})")
        print(f"   🏆 Lowest P/E: {lowest_pe['Symbol']} ({lowest_pe['P/E Ratio']})")

        return df


async def main():
    """Main analysis function."""
    try:
        # Initialize analyzer
        analyzer = CompanyFinancialAnalyzer()

        # Analyze all companies
        results = await analyzer.analyze_companies()

        if results:
            # Generate summary report
            summary_df = analyzer.generate_summary_report()

            # Create comparison charts
            chart_filename = analyzer.create_comparison_charts()

            print(f"\n🎉 Multi-Company Analysis Completed Successfully!")
            print(f"   📊 Companies analyzed: {len(results)}")
            print(f"   📈 Charts generated: {chart_filename}")
            print(f"   📋 Summary report: Generated")

        else:
            print("❌ No companies were successfully analyzed.")

    except Exception as e:
        print(f"❌ Analysis failed with error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
