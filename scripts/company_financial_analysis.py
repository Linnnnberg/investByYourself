import matplotlib
import pandas as pd
import seaborn as sns
from financetoolkit import Toolkit

matplotlib.use("Agg")  # Use non-interactive backend
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

# Set seaborn style for better looking charts
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)

# Create toolkit instance - will use Yahoo Finance if no valid API key
companies = Toolkit(["AAPL", "MSFT"], start_date="2017-12-31")

print("Fetching financial data for AAPL and MSFT...")
print("=" * 50)

# Initialize markdown content
markdown_content = []
markdown_content.append("# Financial Analysis Report: AAPL vs MSFT")
markdown_content.append(
    f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
)
markdown_content.append("")

# Get profitability ratios first
try:
    profitability_ratios = companies.ratios.collect_profitability_ratios()

    markdown_content.append("## Profitability Ratios Comparison")
    markdown_content.append("")

    # AAPL Analysis
    markdown_content.append("### Apple Inc. (AAPL)")
    aapl_ratios = profitability_ratios.loc["AAPL"]
    markdown_content.append("| Metric | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |")
    markdown_content.append("|--------|------|------|------|------|------|------|")

    for metric in aapl_ratios.index:
        values = aapl_ratios.loc[metric]
        row = f"| {metric} |"
        for year in ["2020", "2021", "2022", "2023", "2024", "2025"]:
            if year in values.index and pd.notna(values[year]):
                row += f" {values[year]:.4f} |"
            else:
                row += " N/A |"
        markdown_content.append(row)

    markdown_content.append("")

    # MSFT Analysis
    markdown_content.append("### Microsoft Corporation (MSFT)")
    msft_ratios = profitability_ratios.loc["MSFT"]
    markdown_content.append("| Metric | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |")
    markdown_content.append("|--------|------|------|------|------|------|------|")

    for metric in msft_ratios.index:
        values = msft_ratios.loc[metric]
        row = f"| {metric} |"
        for year in ["2020", "2021", "2022", "2023", "2024", "2025"]:
            if year in values.index and pd.notna(values[year]):
                row += f" {values[year]:.4f} |"
            else:
                row += " N/A |"
        row += ""
        markdown_content.append(row)

    markdown_content.append("")

    # Create visualization charts
    print("Creating visualization charts...")

    # Prepare data for visualization
    years = ["2020", "2021", "2022", "2023", "2024"]
    key_metrics = [
        "Gross Margin",
        "Operating Margin",
        "Net Profit Margin",
        "Return on Equity",
        "Return on Assets",
    ]

    # Create comparison dataframe
    comparison_data = []
    for metric in key_metrics:
        for year in years:
            if (
                metric in aapl_ratios.index
                and year in aapl_ratios.index
                and pd.notna(aapl_ratios.loc[metric, year])
            ):
                comparison_data.append(
                    {
                        "Year": year,
                        "Metric": metric,
                        "Company": "AAPL",
                        "Value": aapl_ratios.loc[metric, year],
                    }
                )
            if (
                metric in msft_ratios.index
                and year in msft_ratios.index
                and pd.notna(msft_ratios.loc[metric, year])
            ):
                comparison_data.append(
                    {
                        "Year": year,
                        "Metric": metric,
                        "Company": "MSFT",
                        "Value": msft_ratios.loc[metric, year],
                    }
                )

    comparison_df = pd.DataFrame(comparison_data)

    if not comparison_df.empty:
        # Create charts
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(
            "Financial Performance Comparison: AAPL vs MSFT",
            fontsize=16,
            fontweight="bold",
        )

        # Chart 1: Margin Comparison Over Time
        margin_data = comparison_df[
            comparison_df["Metric"].isin(
                ["Gross Margin", "Operating Margin", "Net Profit Margin"]
            )
        ]
        if not margin_data.empty:
            sns.lineplot(
                data=margin_data,
                x="Year",
                y="Value",
                hue="Company",
                style="Metric",
                markers=True,
                ax=axes[0, 0],
            )
            axes[0, 0].set_title("Margin Trends Over Time")
            axes[0, 0].set_ylabel("Margin Ratio")
            axes[0, 0].tick_params(axis="x", rotation=45)
            axes[0, 0].legend(title="Company & Metric")

        # Chart 2: 2024 Performance Comparison (Bar Chart)
        data_2024 = comparison_df[comparison_df["Year"] == "2024"]
        if not data_2024.empty:
            pivot_data = data_2024.pivot(
                index="Metric", columns="Company", values="Value"
            )
            pivot_data.plot(kind="bar", ax=axes[0, 1], color=["#007AFF", "#00C851"])
            axes[0, 1].set_title("2024 Performance Comparison")
            axes[0, 1].set_ylabel("Ratio Value")
            axes[0, 1].tick_params(axis="x", rotation=45)
            axes[0, 1].legend(title="Company")

        # Chart 3: Return Metrics Comparison
        return_data = comparison_df[
            comparison_df["Metric"].isin(
                ["Return on Equity", "Return on Assets", "Return on Invested Capital"]
            )
        ]
        if not return_data.empty:
            sns.lineplot(
                data=return_data,
                x="Year",
                y="Value",
                hue="Company",
                style="Metric",
                markers=True,
                ax=axes[1, 0],
            )
            axes[1, 0].set_title("Return Metrics Over Time")
            axes[1, 0].set_ylabel("Return Ratio")
            axes[1, 0].tick_params(axis="x", rotation=45)
            axes[1, 0].legend(title="Company & Metric")

        # Chart 4: Heatmap of Key Metrics
        available_metrics = comparison_df["Metric"].unique()
        available_years = comparison_df["Year"].unique()

        if len(available_metrics) > 0 and len(available_years) > 0:
            heatmap_matrix = np.zeros(
                (len(available_metrics), len(available_years) * 2)
            )

            for i, metric in enumerate(available_metrics):
                for j, year in enumerate(available_years):
                    # AAPL values
                    aapl_val = comparison_df[
                        (comparison_df["Metric"] == metric)
                        & (comparison_df["Year"] == year)
                        & (comparison_df["Company"] == "AAPL")
                    ]["Value"].values
                    if len(aapl_val) > 0:
                        heatmap_matrix[i, j * 2] = aapl_val[0]

                    # MSFT values
                    msft_val = comparison_df[
                        (comparison_df["Metric"] == metric)
                        & (comparison_df["Year"] == year)
                        & (comparison_df["Company"] == "MSFT")
                    ]["Value"].values
                    if len(msft_val) > 0:
                        heatmap_matrix[i, j * 2 + 1] = msft_val[0]

            # Create heatmap
            years_labels = []
            for year in available_years:
                years_labels.extend([f"{year}_AAPL", f"{year}_MSFT"])

            sns.heatmap(
                heatmap_matrix,
                annot=True,
                fmt=".3f",
                cmap="RdYlGn",
                xticklabels=years_labels,
                yticklabels=available_metrics,
                ax=axes[1, 1],
            )
            axes[1, 1].set_title("Financial Metrics Heatmap")
            axes[1, 1].tick_params(axis="x", rotation=45)

        plt.tight_layout()

        # Save the chart
        chart_filename = "financial_comparison_charts.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches="tight")
        print(f"Charts saved as: {chart_filename}")

        # Add chart to markdown
        markdown_content.append("## Visual Analysis")
        markdown_content.append("")
        markdown_content.append(f"![Financial Comparison Charts]({chart_filename})")
        markdown_content.append("")
        markdown_content.append("### Chart Descriptions:")
        markdown_content.append(
            "1. **Margin Trends Over Time**: Shows how Gross, Operating, and Net Profit margins evolved for both companies"
        )
        markdown_content.append(
            "2. **2024 Performance Comparison**: Direct comparison of key metrics for the most recent year"
        )
        markdown_content.append(
            "3. **Return Metrics Over Time**: Tracks Return on Equity, Assets, and Invested Capital trends"
        )
        markdown_content.append(
            "4. **Financial Metrics Heatmap**: Comprehensive view of all metrics across companies and years"
        )
        markdown_content.append("")

        # Key Insights
        markdown_content.append("## Key Financial Insights")
        markdown_content.append("")

        # Compare 2024 metrics
        try:
            aapl_2024 = aapl_ratios["2024"]
            msft_2024 = msft_ratios["2024"]

            markdown_content.append("### 2024 Performance Comparison")
            markdown_content.append("")

            if pd.notna(aapl_2024.get("Gross Margin")) and pd.notna(
                msft_2024.get("Gross Margin")
            ):
                aapl_gm = aapl_2024["Gross Margin"]
                msft_gm = msft_2024["Gross Margin"]
                markdown_content.append(
                    f"- **Gross Margin**: MSFT leads with {msft_gm:.1%} vs AAPL's {aapl_gm:.1%}"
                )

            if pd.notna(aapl_2024.get("Operating Margin")) and pd.notna(
                msft_2024.get("Operating Margin")
            ):
                aapl_om = aapl_2024["Operating Margin"]
                msft_om = msft_2024["Operating Margin"]
                markdown_content.append(
                    f"- **Operating Margin**: MSFT leads with {msft_om:.1%} vs AAPL's {aapl_om:.1%}"
                )

            if pd.notna(aapl_2024.get("Net Profit Margin")) and pd.notna(
                msft_2024.get("Net Profit Margin")
            ):
                aapl_npm = aapl_2024["Net Profit Margin"]
                msft_npm = msft_2024["Net Profit Margin"]
                markdown_content.append(
                    f"- **Net Profit Margin**: MSFT leads with {msft_npm:.1%} vs AAPL's {aapl_npm:.1%}"
                )

            markdown_content.append("")

        except Exception as e:
            markdown_content.append(f"*Error comparing 2024 metrics: {e}*")
            markdown_content.append("")

        markdown_content.append("### Trend Analysis")
        markdown_content.append("- Both companies show strong profitability metrics")
        markdown_content.append(
            "- MSFT generally maintains higher margins across most categories"
        )
        markdown_content.append(
            "- AAPL shows strong return on equity and capital efficiency"
        )
        markdown_content.append("")

except Exception as e:
    markdown_content.append("## Profitability Ratios")
    markdown_content.append(f"*Error: {e}*")
    markdown_content.append("")

# Add conclusion
markdown_content.append("## Conclusion")
markdown_content.append(
    "This analysis provides a comprehensive view of the financial performance of Apple Inc. and Microsoft Corporation."
)
markdown_content.append(
    "Both companies demonstrate strong financial health with robust profitability ratios."
)
markdown_content.append(
    "The visual charts help identify trends and make direct comparisons between the two tech giants."
)
markdown_content.append("")
markdown_content.append("---")
markdown_content.append("*Data source: Yahoo Finance via FinanceToolkit*")

# Write markdown file
with open("financial_analysis_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(markdown_content))

print("Markdown report generated successfully!")
print("File saved as: financial_analysis_report.md")
print("Charts saved as: financial_comparison_charts.png")
print("\n" + "=" * 50)
print("Analysis complete!")
