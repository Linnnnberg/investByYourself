"""
Generate Sample Charts - investByYourself

This script generates sample financial charts from our calculations
and saves them to the charts folder for demonstration purposes.

Part of Story-002: Financial Calculation Testing Suite
"""

import os
from datetime import datetime, timedelta

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set style for better-looking charts
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")

# Create charts directory if it doesn't exist
os.makedirs("charts", exist_ok=True)


def create_portfolio_allocation_chart():
    """Create a sample portfolio allocation pie chart."""
    print("Creating portfolio allocation chart...")

    # Sample portfolio data
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    values = [25000, 40000, 18000, 22000, 15000]
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

    # Create pie chart
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(
        values,
        labels=symbols,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        explode=(0.05, 0.05, 0.05, 0.05, 0.05),
    )

    # Customize text
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax.set_title("Sample Portfolio Allocation", fontsize=16, fontweight="bold", pad=20)

    # Add total value annotation
    total_value = sum(values)
    ax.text(
        0,
        -1.2,
        f"Total Portfolio Value: ${total_value:,.0f}",
        ha="center",
        fontsize=12,
        fontweight="bold",
    )

    plt.tight_layout()
    plt.savefig("charts/portfolio_allocation_sample.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✅ Portfolio allocation chart saved!")


def create_portfolio_performance_chart():
    """Create a sample portfolio performance line chart."""
    print("Creating portfolio performance chart...")

    # Generate sample performance data over time
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="M")
    initial_value = 100000

    # Simulate realistic portfolio performance with some volatility
    np.random.seed(42)  # For reproducible results
    monthly_returns = np.random.normal(
        0.008, 0.04, len(dates)
    )  # 0.8% monthly return, 4% volatility

    portfolio_values = [initial_value]
    for return_rate in monthly_returns:
        new_value = portfolio_values[-1] * (1 + return_rate)
        portfolio_values.append(new_value)

    # Create line chart
    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(
        dates,
        portfolio_values[1:],
        linewidth=3,
        color="#2E86AB",
        marker="o",
        markersize=4,
    )
    ax.fill_between(dates, portfolio_values[1:], alpha=0.3, color="#2E86AB")

    # Customize chart
    ax.set_title(
        "Portfolio Performance Over Time", fontsize=16, fontweight="bold", pad=20
    )
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Portfolio Value ($)", fontsize=12)
    ax.grid(True, alpha=0.3)

    # Add performance metrics
    final_value = portfolio_values[-1]
    total_return = ((final_value - initial_value) / initial_value) * 100
    ax.text(
        0.02,
        0.98,
        f"Total Return: {total_return:+.1f}%",
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
    )

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("charts/portfolio_performance_sample.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✅ Portfolio performance chart saved!")


def create_pe_ratio_comparison_chart():
    """Create a sample PE ratio comparison bar chart."""
    print("Creating PE ratio comparison chart...")

    # Sample stock data
    stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    pe_ratios = [28.5, 25.2, 32.1, 45.8, 65.3, 42.7, 18.9, 38.4]
    sectors = [
        "Technology",
        "Technology",
        "Technology",
        "Consumer",
        "Automotive",
        "Technology",
        "Technology",
        "Consumer",
    ]

    # Create color map based on PE ratio ranges
    colors = []
    for pe in pe_ratios:
        if pe < 20:
            colors.append("#2ECC71")  # Green for low PE
        elif pe < 30:
            colors.append("#F39C12")  # Orange for moderate PE
        else:
            colors.append("#E74C3C")  # Red for high PE

    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 8))

    bars = ax.bar(
        stocks, pe_ratios, color=colors, alpha=0.8, edgecolor="black", linewidth=1
    )

    # Customize chart
    ax.set_title(
        "P/E Ratio Comparison - Major Tech Stocks",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Stock Symbol", fontsize=12)
    ax.set_ylabel("P/E Ratio", fontsize=12)
    ax.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar, pe in zip(bars, pe_ratios):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 1,
            f"{pe:.1f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # Add legend for PE ratio ranges
    legend_elements = [
        mpatches.Patch(color="#2ECC71", label="Low PE (< 20)"),
        mpatches.Patch(color="#F39C12", label="Moderate PE (20-30)"),
        mpatches.Patch(color="#E74C3C", label="High PE (> 30)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    # Add average PE line
    avg_pe = np.mean(pe_ratios)
    ax.axhline(y=avg_pe, color="red", linestyle="--", alpha=0.7, linewidth=2)
    ax.text(
        len(stocks) - 1,
        avg_pe + 2,
        f"Average PE: {avg_pe:.1f}",
        ha="right",
        fontweight="bold",
        color="red",
    )

    plt.tight_layout()
    plt.savefig("charts/pe_ratio_comparison_sample.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✅ PE ratio comparison chart saved!")


def create_cagr_analysis_chart():
    """Create a sample CAGR analysis chart."""
    print("Creating CAGR analysis chart...")

    # Sample investment scenarios
    scenarios = [
        "Conservative\n(Bonds)",
        "Balanced\n(Portfolio)",
        "Growth\n(Stocks)",
        "Aggressive\n(Tech)",
    ]
    cagr_rates = [4.5, 8.2, 12.8, 18.5]
    initial_investment = 10000
    years = 10

    # Calculate final values
    final_values = [
        initial_investment * (1 + cagr / 100) ** years for cagr in cagr_rates
    ]

    # Create subplot with two charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Chart 1: CAGR comparison
    colors = ["#3498DB", "#2ECC71", "#F39C12", "#E74C3C"]
    bars1 = ax1.bar(
        scenarios, cagr_rates, color=colors, alpha=0.8, edgecolor="black", linewidth=1
    )

    ax1.set_title(
        "CAGR Comparison by Investment Strategy", fontsize=14, fontweight="bold"
    )
    ax1.set_ylabel("CAGR (%)", fontsize=12)
    ax1.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar, cagr in zip(bars1, cagr_rates):
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.5,
            f"{cagr:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # Chart 2: Growth projection
    time_periods = np.arange(0, years + 1)

    for i, cagr in enumerate(cagr_rates):
        growth_curve = [
            initial_investment * (1 + cagr / 100) ** year for year in time_periods
        ]
        ax2.plot(
            time_periods,
            growth_curve,
            linewidth=3,
            color=colors[i],
            label=f'{scenarios[i].replace(chr(10), " ")} ({cagr:.1f}%)',
            marker="o",
        )

    ax2.set_title(
        "Investment Growth Projection (10 Years)", fontsize=14, fontweight="bold"
    )
    ax2.set_xlabel("Years", fontsize=12)
    ax2.set_ylabel("Portfolio Value ($)", fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    # Add final value annotations
    for i, final_value in enumerate(final_values):
        ax2.annotate(
            f"${final_value:,.0f}",
            xy=(years, final_value),
            xytext=(years + 0.5, final_value),
            arrowprops=dict(arrowstyle="->", color=colors[i]),
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig("charts/cagr_analysis_sample.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✅ CAGR analysis chart saved!")


def create_risk_return_scatter():
    """Create a sample risk-return scatter plot."""
    print("Creating risk-return scatter plot...")

    # Sample asset data (risk vs return)
    assets = [
        "Treasury\nBonds",
        "Corporate\nBonds",
        "Large Cap\nStocks",
        "Small Cap\nStocks",
        "International\nStocks",
        "Emerging\nMarkets",
        "Real Estate",
        "Commodities",
    ]

    annual_returns = [3.2, 5.8, 10.5, 12.8, 9.2, 15.6, 8.9, 7.4]
    volatility = [2.1, 8.5, 15.2, 22.4, 18.7, 28.9, 16.3, 25.1]

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Color code by asset class
    colors = [
        "#3498DB",
        "#2980B9",
        "#E74C3C",
        "#C0392B",
        "#F39C12",
        "#E67E22",
        "#27AE60",
        "#229954",
    ]

    for i, (asset, ret, vol) in enumerate(zip(assets, annual_returns, volatility)):
        ax.scatter(
            vol, ret, s=200, c=colors[i], alpha=0.8, edgecolor="black", linewidth=1
        )
        ax.annotate(
            asset,
            (vol, ret),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=10,
            fontweight="bold",
            ha="left",
        )

    # Add efficient frontier line (simplified)
    frontier_vol = np.linspace(2, 30, 100)
    frontier_ret = 2 + 0.4 * frontier_vol  # Simplified efficient frontier
    ax.plot(
        frontier_vol,
        frontier_ret,
        "--",
        color="gray",
        alpha=0.7,
        linewidth=2,
        label="Efficient Frontier",
    )

    # Customize chart
    ax.set_title(
        "Risk vs Return Analysis - Asset Classes",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("Volatility (Risk) %", fontsize=12)
    ax.set_ylabel("Expected Annual Return %", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Add risk-free rate line
    risk_free_rate = 3.2
    ax.axhline(
        y=risk_free_rate,
        color="green",
        linestyle=":",
        alpha=0.7,
        linewidth=2,
        label=f"Risk-Free Rate ({risk_free_rate}%)",
    )

    # Add Sharpe ratio zones
    ax.fill_between(
        [0, 30],
        [risk_free_rate, risk_free_rate + 0.5 * 30],
        alpha=0.1,
        color="green",
        label="High Sharpe Ratio Zone",
    )

    plt.tight_layout()
    plt.savefig("charts/risk_return_analysis_sample.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("✅ Risk-return scatter plot saved!")


def create_portfolio_heatmap():
    """Create a sample portfolio correlation heatmap."""
    print("Creating portfolio correlation heatmap...")

    # Sample correlation matrix
    assets = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX"]

    # Generate realistic correlation matrix
    np.random.seed(42)
    base_corr = 0.3  # Base correlation between tech stocks

    corr_matrix = np.eye(len(assets))  # Start with identity matrix
    for i in range(len(assets)):
        for j in range(i + 1, len(assets)):
            # Tech stocks have higher correlation
            if i < 6 and j < 6:  # First 6 are tech stocks
                correlation = base_corr + np.random.normal(0, 0.1)
            else:
                correlation = np.random.normal(0, 0.2)

            correlation = np.clip(correlation, -0.8, 0.8)  # Limit correlation range
            corr_matrix[i, j] = correlation
            corr_matrix[j, i] = correlation

    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(corr_matrix, cmap="RdYlBu_r", vmin=-1, vmax=1, aspect="auto")

    # Add correlation values as text
    for i in range(len(assets)):
        for j in range(len(assets)):
            text = ax.text(
                j,
                i,
                f"{corr_matrix[i, j]:.2f}",
                ha="center",
                va="center",
                color="black",
                fontweight="bold",
            )

    # Customize chart
    ax.set_title("Portfolio Correlation Matrix", fontsize=16, fontweight="bold", pad=20)
    ax.set_xticks(range(len(assets)))
    ax.set_yticks(range(len(assets)))
    ax.set_xticklabels(assets, rotation=45)
    ax.set_yticklabels(assets)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Correlation Coefficient", fontsize=12)

    plt.tight_layout()
    plt.savefig(
        "charts/portfolio_correlation_heatmap_sample.png", dpi=300, bbox_inches="tight"
    )
    plt.close()
    print("✅ Portfolio correlation heatmap saved!")


def create_summary_report():
    """Create a summary report of all generated charts."""
    print("\n📊 Chart Generation Summary")
    print("=" * 50)

    charts_created = [
        "portfolio_allocation_sample.png",
        "portfolio_performance_sample.png",
        "pe_ratio_comparison_sample.png",
        "cagr_analysis_sample.png",
        "risk_return_analysis_sample.png",
        "portfolio_correlation_heatmap_sample.png",
    ]

    print(f"✅ Generated {len(charts_created)} sample charts:")
    for chart in charts_created:
        print(f"   📈 {chart}")

    print(f"\n📁 Charts saved to: {os.path.abspath('charts')}")
    print("\n🎯 These charts demonstrate:")
    print("   • Portfolio allocation and performance")
    print("   • Financial ratio comparisons")
    print("   • Investment growth projections")
    print("   • Risk-return analysis")
    print("   • Portfolio correlation analysis")

    print("\n🚀 Ready for UI integration!")


def main():
    """Main function to generate all sample charts."""
    print("🚀 Generating Sample Financial Charts for investByYourself")
    print("=" * 60)

    try:
        # Generate all charts
        create_portfolio_allocation_chart()
        create_portfolio_performance_chart()
        create_pe_ratio_comparison_chart()
        create_cagr_analysis_chart()
        create_risk_return_scatter()
        create_portfolio_heatmap()

        # Create summary report
        create_summary_report()

    except Exception as e:
        print(f"❌ Error generating charts: {e}")
        raise


if __name__ == "__main__":
    main()
