"""
TGA Liquidity Tracking - Simple Interactive Demo
InvestByYourself Platform

A minimal prototype demonstrating TGA liquidity tracking with interactive charts.
No dependencies on the main codebase - runs standalone.

Usage:
    python demos/tga_liquidity_demo.py
"""

import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
import sys


def fetch_tga_data(lookback_months=24):
    """
    Fetch TGA data from US Treasury API.

    Args:
        lookback_months: Number of months to look back (default: 24)

    Returns:
        pandas DataFrame with TGA data
    """
    print("=" * 70)
    print("📊 TGA LIQUIDITY TRACKING DEMO")
    print("=" * 70)
    print(f"\n🔄 Fetching TGA data from US Treasury (last {lookback_months} months)...")

    # Calculate date range
    end = date.today()
    start = end - timedelta(days=lookback_months * 30)

    # Treasury API endpoint
    base = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
    endpoint = "/v1/accounting/dts/operating_cash_balance"

    params = {
        "fields": "record_date,close_today_bal,open_today_bal",
        "filter": f"record_date:gte:{start},record_date:lte:{end}",
        "sort": "record_date",
        "page[size]": 10000,
        "format": "json"
    }

    try:
        # Add User-Agent header to avoid 403 errors
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(base + endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "data" not in data or len(data["data"]) == 0:
            print("❌ No data received from Treasury API")
            sys.exit(1)

        # Convert to DataFrame
        df = pd.DataFrame(data["data"])

        # Parse dates and values
        df["record_date"] = pd.to_datetime(df["record_date"])
        df["close_today_bal"] = pd.to_numeric(df["close_today_bal"], errors="coerce")
        df["open_today_bal"] = pd.to_numeric(df["open_today_bal"], errors="coerce")

        # Remove invalid rows
        df = df.dropna(subset=["close_today_bal"]).sort_values("record_date")

        print(f"✅ Successfully fetched {len(df)} records")
        print(f"📅 Date range: {df['record_date'].min().strftime('%Y-%m-%d')} to {df['record_date'].max().strftime('%Y-%m-%d')}")

        return df

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        sys.exit(1)


def calculate_liquidity_metrics(df):
    """
    Calculate liquidity metrics from TGA data.

    Args:
        df: DataFrame with TGA data

    Returns:
        DataFrame with calculated metrics
    """
    print("\n🔢 Calculating liquidity metrics...")

    # Convert to billions for readability
    df["balance_billions"] = df["close_today_bal"] / 1000

    # 1. Daily change (positive = drain, negative = add)
    df["daily_change"] = df["close_today_bal"].diff() / 1000  # billions

    # 2. Liquidity Index (original method: cumulative -dTGA)
    df["liquidity_index"] = (-df["daily_change"]).cumsum()

    # 3. Moving averages (smooth the noise)
    df["ma_7day"] = df["balance_billions"].rolling(7, min_periods=1).mean()
    df["ma_30day"] = df["balance_billions"].rolling(30, min_periods=1).mean()

    # 4. Volatility (30-day rolling standard deviation)
    df["volatility_30d"] = df["balance_billions"].rolling(30, min_periods=1).std()

    # 5. Z-score (statistical measure vs 90-day average)
    rolling_mean = df["balance_billions"].rolling(90, min_periods=30).mean()
    rolling_std = df["balance_billions"].rolling(90, min_periods=30).std()
    df["zscore"] = ((df["balance_billions"] - rolling_mean) / rolling_std).fillna(0)

    # 6. Liquidity stress indicator
    volatility_threshold = df["volatility_30d"].quantile(0.9)
    df["is_stress"] = (df["zscore"].abs() > 2) | (df["volatility_30d"] > volatility_threshold)

    print(f"✅ Metrics calculated")

    # Print summary
    latest = df.iloc[-1]
    print(f"\n📈 LATEST TGA METRICS ({latest['record_date'].strftime('%Y-%m-%d')}):")
    print(f"   Balance: ${latest['balance_billions']:.1f}B")
    print(f"   Daily Change: ${latest['daily_change']:.2f}B")
    print(f"   7-day MA: ${latest['ma_7day']:.1f}B")
    print(f"   30-day MA: ${latest['ma_30day']:.1f}B")
    print(f"   Volatility: ${latest['volatility_30d']:.2f}B")
    print(f"   Z-score: {latest['zscore']:.2f}")
    print(f"   Liquidity Index: ${latest['liquidity_index']:.1f}B")
    print(f"   Stress: {'⚠️  YES' if latest['is_stress'] else '✅ NO'}")

    return df


def create_interactive_dashboard(df):
    """
    Create interactive Plotly dashboard.

    Args:
        df: DataFrame with TGA data and metrics
    """
    print("\n🎨 Creating interactive dashboard...")

    # Create subplots: 3 rows
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            "TGA Balance & Moving Averages",
            "Liquidity Index (Cumulative -ΔTGA)",
            "Daily Changes & Volatility"
        ),
        vertical_spacing=0.1,
        row_heights=[0.35, 0.35, 0.30]
    )

    # ============================================================
    # CHART 1: TGA Balance with Moving Averages
    # ============================================================

    # TGA Balance
    fig.add_trace(
        go.Scatter(
            x=df["record_date"],
            y=df["balance_billions"],
            name="TGA Balance",
            line=dict(color="#2E86DE", width=2),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Balance: $%{y:.1f}B<extra></extra>"
        ),
        row=1, col=1
    )

    # 7-day MA
    fig.add_trace(
        go.Scatter(
            x=df["record_date"],
            y=df["ma_7day"],
            name="7-day MA",
            line=dict(color="#FFA502", width=1.5, dash="dash"),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>7d MA: $%{y:.1f}B<extra></extra>"
        ),
        row=1, col=1
    )

    # 30-day MA
    fig.add_trace(
        go.Scatter(
            x=df["record_date"],
            y=df["ma_30day"],
            name="30-day MA",
            line=dict(color="#FF6348", width=1.5, dash="dot"),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>30d MA: $%{y:.1f}B<extra></extra>"
        ),
        row=1, col=1
    )

    # Highlight stress periods
    stress_periods = df[df["is_stress"]]
    if not stress_periods.empty:
        fig.add_trace(
            go.Scatter(
                x=stress_periods["record_date"],
                y=stress_periods["balance_billions"],
                mode="markers",
                name="Stress Periods",
                marker=dict(
                    color="red",
                    size=8,
                    symbol="x",
                    line=dict(width=2)
                ),
                hovertemplate="<b>%{x|%Y-%m-%d}</b><br>⚠️ STRESS<br>Balance: $%{y:.1f}B<extra></extra>"
            ),
            row=1, col=1
        )

    # ============================================================
    # CHART 2: Liquidity Index
    # ============================================================

    # Color-code based on value (green = positive liquidity, red = negative)
    colors = ['green' if x >= 0 else 'red' for x in df["liquidity_index"]]

    fig.add_trace(
        go.Scatter(
            x=df["record_date"],
            y=df["liquidity_index"],
            name="Liquidity Index",
            line=dict(color="#10AC84", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(16, 172, 132, 0.2)",
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Liquidity: $%{y:.1f}B<extra></extra>"
        ),
        row=2, col=1
    )

    # Add zero line
    fig.add_hline(
        y=0, line_dash="dash", line_color="gray", opacity=0.5,
        row=2, col=1
    )

    # ============================================================
    # CHART 3: Daily Changes & Volatility
    # ============================================================

    # Daily changes as bars (green = liquidity add, red = drain)
    colors = ['green' if x < 0 else 'red' for x in df["daily_change"]]

    fig.add_trace(
        go.Bar(
            x=df["record_date"],
            y=df["daily_change"],
            name="Daily Change",
            marker_color=colors,
            opacity=0.6,
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Change: $%{y:.2f}B<extra></extra>"
        ),
        row=3, col=1
    )

    # Volatility line
    fig.add_trace(
        go.Scatter(
            x=df["record_date"],
            y=df["volatility_30d"],
            name="Volatility (30d)",
            line=dict(color="#EE5A6F", width=2),
            yaxis="y4",
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Volatility: $%{y:.2f}B<extra></extra>"
        ),
        row=3, col=1
    )

    # ============================================================
    # LAYOUT
    # ============================================================

    fig.update_xaxes(title_text="Date", row=3, col=1)

    fig.update_yaxes(title_text="TGA Balance (Billions USD)", row=1, col=1)
    fig.update_yaxes(title_text="Liquidity Index (Billions USD)", row=2, col=1)
    fig.update_yaxes(title_text="Daily Change (Billions USD)", row=3, col=1)

    # Add secondary y-axis for volatility
    fig.update_layout(
        yaxis4=dict(
            title="Volatility ($B)",
            overlaying="y3",
            side="right"
        )
    )

    fig.update_layout(
        title={
            "text": "🏦 TGA Liquidity Tracking Dashboard<br><sub>Treasury General Account & Market Liquidity Analysis</sub>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 24}
        },
        height=1200,
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template="plotly_white"
    )

    return fig


def print_analysis(df):
    """Print key analysis insights."""
    print("\n" + "=" * 70)
    print("📊 LIQUIDITY ANALYSIS")
    print("=" * 70)

    # Recent trends (last 30 days)
    recent = df.tail(30)

    print(f"\n📈 30-Day Trends:")
    print(f"   TGA Change: ${(recent.iloc[-1]['balance_billions'] - recent.iloc[0]['balance_billions']):.1f}B")
    print(f"   Average Daily Change: ${recent['daily_change'].mean():.2f}B")
    print(f"   Max Daily Drain: ${recent['daily_change'].max():.2f}B")
    print(f"   Max Daily Add: ${recent['daily_change'].min():.2f}B")
    print(f"   Stress Days: {recent['is_stress'].sum()} / {len(recent)}")

    # Historical context
    print(f"\n📊 Historical Context:")
    current_balance = df.iloc[-1]["balance_billions"]
    percentile = (df["balance_billions"] < current_balance).mean() * 100
    print(f"   Current TGA at {percentile:.1f}th percentile (historical)")

    current_volatility = df.iloc[-1]["volatility_30d"]
    vol_percentile = (df["volatility_30d"] < current_volatility).mean() * 100
    print(f"   Current volatility at {vol_percentile:.1f}th percentile")

    # Liquidity phases (last 90 days)
    last_90 = df.tail(90)
    draining_days = (last_90["daily_change"] > 0).sum()
    adding_days = (last_90["daily_change"] < 0).sum()

    print(f"\n💧 Liquidity Phases (last 90 days):")
    print(f"   Draining: {draining_days} days ({draining_days/len(last_90)*100:.1f}%) 📉")
    print(f"   Adding: {adding_days} days ({adding_days/len(last_90)*100:.1f}%) 📈")

    # Interpretation
    latest = df.iloc[-1]
    print(f"\n🎯 Current Market Liquidity:")
    if latest["liquidity_index"] > 0:
        print(f"   ✅ Net liquidity ADDED: ${latest['liquidity_index']:.1f}B since start")
        print(f"   💡 Interpretation: Treasury operations have added liquidity to markets")
    else:
        print(f"   ⚠️  Net liquidity DRAINED: ${abs(latest['liquidity_index']):.1f}B since start")
        print(f"   💡 Interpretation: Treasury operations have drained liquidity from markets")

    if latest["is_stress"]:
        print(f"   🚨 STRESS CONDITION DETECTED")
        print(f"      - Z-score: {latest['zscore']:.2f} (>2 indicates stress)")
        print(f"      - Volatility: ${latest['volatility_30d']:.2f}B")
    else:
        print(f"   ✅ Normal liquidity conditions")


def main():
    """Main execution function."""
    try:
        # Step 1: Fetch data
        df = fetch_tga_data(lookback_months=24)

        # Step 2: Calculate metrics
        df = calculate_liquidity_metrics(df)

        # Step 3: Print analysis
        print_analysis(df)

        # Step 4: Create interactive dashboard
        fig = create_interactive_dashboard(df)

        print("\n" + "=" * 70)
        print("🌐 Opening interactive dashboard in browser...")
        print("=" * 70)
        print("\n💡 Dashboard Features:")
        print("   • Hover over charts for detailed data")
        print("   • Zoom: Click and drag on chart")
        print("   • Pan: Shift + drag")
        print("   • Reset: Double-click on chart")
        print("   • Toggle series: Click legend items")
        print("\n📌 Understanding the Charts:")
        print("   • Chart 1: TGA balance trend with moving averages")
        print("   • Chart 2: Liquidity Index (↑ = liquidity added, ↓ = drained)")
        print("   • Chart 3: Daily changes (green = add, red = drain) + volatility")
        print("\n🔴 Red X markers = Liquidity stress periods")
        print("=" * 70)

        # Show the dashboard
        fig.show()

        print("\n✅ Demo complete! Close the browser tab when done.\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
