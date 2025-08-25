#!/usr/bin/env python3
"""
Financial Dashboard - Interactive Streamlit Interface
Tech-008: Database Infrastructure Setup

This module provides a Streamlit-based dashboard for exploring financial data
from the InvestByYourself database, including:
- Market cap rankings and sector analysis
- Interactive company profiles and charts
- Real-time data exploration
- Financial ratio comparisons
"""

import os
import sys
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scripts.financial_analysis.data_explorer import (
    CompanyProfile,
    FinancialCharts,
    FinancialDataExplorer,
)

# Page configuration
st.set_page_config(
    page_title="InvestByYourself - Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .company-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "data_explorer" not in st.session_state:
    st.session_state.data_explorer = None
if "charts" not in st.session_state:
    st.session_state.charts = None
if "profile_generator" not in st.session_state:
    st.session_state.profile_generator = None


def initialize_components():
    """Initialize data exploration components."""
    try:
        if st.session_state.data_explorer is None:
            with st.spinner("Connecting to database..."):
                st.session_state.data_explorer = FinancialDataExplorer()
                st.session_state.charts = FinancialCharts()
                st.session_state.profile_generator = CompanyProfile(
                    st.session_state.data_explorer
                )
            st.success("Database connection established!")
        return True
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return False


def main():
    """Main dashboard function."""

    # Header
    st.markdown(
        '<h1 class="main-header">📊 InvestByYourself Financial Dashboard</h1>',
        unsafe_allow_html=True,
    )

    # Initialize components
    if not initialize_components():
        st.stop()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        [
            "🏠 Dashboard Overview",
            "📈 Market Analysis",
            "🏢 Company Profiles",
            "📊 Sector Analysis",
            "🔍 Data Explorer",
        ],
    )

    if page == "🏠 Dashboard Overview":
        show_dashboard_overview()
    elif page == "📈 Market Analysis":
        show_market_analysis()
    elif page == "🏢 Company Profiles":
        show_company_profiles()
    elif page == "📊 Sector Analysis":
        show_sector_analysis()
    elif page == "🔍 Data Explorer":
        show_data_explorer()


def show_dashboard_overview():
    """Show dashboard overview with key metrics."""
    st.header("🏠 Dashboard Overview")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    try:
        # Get top companies for metrics
        top_companies = st.session_state.data_explorer.get_top_companies_by_market_cap(
            limit=10
        )
        sector_perf = st.session_state.data_explorer.get_sector_performance()

        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Total Companies", len(top_companies) if not top_companies.empty else 0
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            total_market_cap = (
                top_companies["market_cap"].sum() if not top_companies.empty else 0
            )
            st.metric(
                "Total Market Cap",
                f"${total_market_cap/1e12:.2f}T" if total_market_cap > 0 else "N/A",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Sectors Covered", len(sector_perf) if not sector_perf.empty else 0
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Data Freshness", "Real-time")
            st.markdown("</div>", unsafe_allow_html=True)

        # Top companies chart
        if not top_companies.empty:
            st.subheader("Top 10 Companies by Market Cap")
            fig = st.session_state.charts.create_market_cap_chart(top_companies)
            st.plotly_chart(fig, use_container_width=True)

        # Sector overview
        if not sector_perf.empty:
            st.subheader("Sector Market Capitalization")
            fig = st.session_state.charts.create_sector_performance_chart(sector_perf)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")


def show_market_analysis():
    """Show market analysis with interactive charts."""
    st.header("📈 Market Analysis")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        limit = st.selectbox("Number of companies:", [5, 10, 20, 50], index=1)

    with col2:
        sector_filter = st.selectbox(
            "Filter by sector:",
            ["All Sectors"]
            + list(
                st.session_state.data_explorer.get_sector_performance()[
                    "sector"
                ].unique()
            )
            if "sector_perf" in locals()
            else [],
        )

    with col3:
        chart_type = st.selectbox(
            "Chart type:", ["Market Cap", "P/E Ratio", "P/B Ratio", "Dividend Yield"]
        )

    try:
        # Get filtered data
        if sector_filter == "All Sectors":
            companies_data = (
                st.session_state.data_explorer.get_top_companies_by_market_cap(
                    limit=limit
                )
            )
        else:
            companies_data = (
                st.session_state.data_explorer.get_top_companies_by_market_cap(
                    limit=limit, sector=sector_filter
                )
            )

        if not companies_data.empty:
            # Display data table
            st.subheader(f"Top {limit} Companies by Market Cap")
            if sector_filter != "All Sectors":
                st.subheader(f"Sector: {sector_filter}")

            # Format the display data
            display_data = companies_data.copy()
            display_data["market_cap_formatted"] = display_data["market_cap"].apply(
                lambda x: f"${x/1e9:.1f}B" if pd.notna(x) else "N/A"
            )
            display_data["current_price_formatted"] = display_data[
                "current_price"
            ].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")

            st.dataframe(
                display_data[
                    [
                        "symbol",
                        "name",
                        "sector",
                        "market_cap_formatted",
                        "current_price_formatted",
                        "pe_ratio",
                        "pb_ratio",
                        "dividend_yield",
                    ]
                ],
                use_container_width=True,
            )

            # Create appropriate chart based on selection
            if chart_type == "Market Cap":
                fig = st.session_state.charts.create_market_cap_chart(
                    companies_data, f"Top {limit} Companies by Market Cap"
                )
            elif chart_type == "P/E Ratio":
                fig = st.session_state.charts.create_ratio_comparison_chart(
                    companies_data, f"P/E Ratio Comparison - Top {limit} Companies"
                )
            elif chart_type == "P/B Ratio":
                fig = st.session_state.charts.create_ratio_comparison_chart(
                    companies_data, f"P/B Ratio Comparison - Top {limit} Companies"
                )
            elif chart_type == "Dividend Yield":
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=companies_data["symbol"],
                            y=companies_data["dividend_yield"],
                            text=[
                                f"{dy:.2%}" if pd.notna(dy) else "N/A"
                                for dy in companies_data["dividend_yield"]
                            ],
                            textposition="auto",
                            marker_color="lightcoral",
                        )
                    ]
                )
                fig.update_layout(
                    title=f"Dividend Yield - Top {limit} Companies",
                    xaxis_title="Company Symbol",
                    yaxis_title="Dividend Yield (%)",
                    height=500,
                )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading market analysis: {e}")


def show_company_profiles():
    """Show company profile exploration."""
    st.header("🏢 Company Profiles")

    # Company search
    col1, col2 = st.columns([2, 1])

    with col1:
        company_symbol = st.text_input(
            "Enter company symbol (e.g., AAPL, MSFT):", value="AAPL"
        ).upper()

    with col2:
        if st.button("Load Profile"):
            st.session_state.selected_company = company_symbol

    # Load company profile
    if (
        hasattr(st.session_state, "selected_company")
        and st.session_state.selected_company
    ):
        try:
            profile = st.session_state.profile_generator.generate_company_profile(
                st.session_state.selected_company
            )

            if "error" in profile:
                st.error(profile["error"])
            else:
                # Company overview card
                st.markdown('<div class="company-card">', unsafe_allow_html=True)
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader(
                        f"{profile['overview']['symbol']} - {profile['overview']['name']}"
                    )
                    st.write(f"**Sector:** {profile['overview']['sector']}")
                    st.write(f"**Industry:** {profile['overview']['industry']}")
                    st.write(f"**Exchange:** {profile['overview']['exchange']}")
                    st.write(f"**Country:** {profile['overview']['country']}")
                    if profile["overview"]["website"]:
                        st.write(f"**Website:** {profile['overview']['website']}")

                with col2:
                    if profile["overview"]["market_cap"]:
                        st.metric(
                            "Market Cap",
                            f"${profile['overview']['market_cap']/1e9:.1f}B",
                        )
                    if profile["market_data"]["current_price"]:
                        st.metric(
                            "Current Price",
                            f"${profile['market_data']['current_price']:.2f}",
                        )
                    if profile["market_data"]["pe_ratio"]:
                        st.metric(
                            "P/E Ratio", f"{profile['market_data']['pe_ratio']:.2f}"
                        )

                st.markdown("</div>", unsafe_allow_html=True)

                # Company description
                if profile["overview"]["description"]:
                    st.subheader("Company Description")
                    st.write(profile["overview"]["description"])

                # Financial metrics
                if profile["market_data"]["current_price"]:
                    st.subheader("Financial Metrics")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "P/E Ratio",
                            f"{profile['market_data']['pe_ratio']:.2f}"
                            if profile["market_data"]["pe_ratio"]
                            else "N/A",
                        )
                    with col2:
                        st.metric(
                            "P/B Ratio",
                            f"{profile['market_data']['pb_ratio']:.2f}"
                            if profile["market_data"]["pb_ratio"]
                            else "N/A",
                        )
                    with col3:
                        st.metric(
                            "P/S Ratio",
                            f"{profile['market_data']['ps_ratio']:.2f}"
                            if profile["market_data"]["ps_ratio"]
                            else "N/A",
                        )
                    with col4:
                        st.metric(
                            "Dividend Yield",
                            f"{profile['market_data']['dividend_yield']:.2%}"
                            if profile["market_data"]["dividend_yield"]
                            else "N/A",
                        )

                # Price history chart
                try:
                    price_history = (
                        st.session_state.data_explorer.get_company_financial_history(
                            company_symbol, days=365
                        )
                    )
                    if not price_history.empty:
                        st.subheader("Price History (1 Year)")
                        fig = st.session_state.charts.create_price_history_chart(
                            price_history, company_symbol
                        )
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not load price history: {e}")

                # Peer comparison
                if profile["peers"]:
                    st.subheader("Peer Comparison")
                    peers_df = pd.DataFrame(profile["peers"])
                    st.dataframe(peers_df, use_container_width=True)

                    # Peer comparison chart
                    fig = st.session_state.charts.create_ratio_comparison_chart(
                        peers_df, f"{company_symbol} vs Peers - Financial Ratios"
                    )
                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading company profile: {e}")


def show_sector_analysis():
    """Show sector analysis and comparisons."""
    st.header("📊 Sector Analysis")

    try:
        sector_data = st.session_state.data_explorer.get_sector_performance()

        if not sector_data.empty:
            # Sector overview
            st.subheader("Sector Overview")
            st.dataframe(sector_data, use_container_width=True)

            # Sector chart
            fig = st.session_state.charts.create_sector_performance_chart(sector_data)
            st.plotly_chart(fig, use_container_width=True)

            # Sector metrics comparison
            st.subheader("Sector Metrics Comparison")

            col1, col2 = st.columns(2)

            with col1:
                # Average P/E by sector
                fig = px.bar(
                    sector_data,
                    x="sector",
                    y="avg_pe_ratio",
                    title="Average P/E Ratio by Sector",
                    labels={"avg_pe_ratio": "Average P/E Ratio", "sector": "Sector"},
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Average P/B by sector
                fig = px.bar(
                    sector_data,
                    x="sector",
                    y="avg_pb_ratio",
                    title="Average P/B Ratio by Sector",
                    labels={"avg_pb_ratio": "Average P/B Ratio", "sector": "Sector"},
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

            # Sector details
            st.subheader("Sector Details")
            selected_sector = st.selectbox(
                "Select a sector for detailed analysis:", sector_data["sector"].unique()
            )

            if selected_sector:
                sector_companies = (
                    st.session_state.data_explorer.get_top_companies_by_market_cap(
                        limit=50, sector=selected_sector
                    )
                )

                if not sector_companies.empty:
                    st.write(f"**Companies in {selected_sector} sector:**")
                    st.dataframe(
                        sector_companies[
                            ["symbol", "name", "market_cap", "pe_ratio", "pb_ratio"]
                        ],
                        use_container_width=True,
                    )

                    # Sector company chart
                    fig = st.session_state.charts.create_market_cap_chart(
                        sector_companies, f"Top Companies in {selected_sector} Sector"
                    )
                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading sector analysis: {e}")


def show_data_explorer():
    """Show advanced data exploration tools."""
    st.header("🔍 Data Explorer")

    st.subheader("Custom SQL Queries")
    st.write("Explore the database with custom SQL queries:")

    # Predefined queries
    query_options = {
        "Top 10 Companies by Market Cap": """
        SELECT c.symbol, c.name, c.sector, c.market_cap, md.close_price
        FROM companies c
        LEFT JOIN market_data md ON c.id = md.company_id
        WHERE c.is_active = TRUE AND c.market_cap IS NOT NULL
        ORDER BY c.market_cap DESC LIMIT 10
        """,
        "Sector Performance": """
        SELECT sector, COUNT(*) as company_count, AVG(market_cap) as avg_market_cap
        FROM companies
        WHERE is_active = TRUE AND sector IS NOT NULL
        GROUP BY sector
        ORDER BY avg_market_cap DESC
        """,
        "High P/E Companies": """
        SELECT c.symbol, c.name, c.sector, md.pe_ratio, md.close_price
        FROM companies c
        LEFT JOIN market_data md ON c.id = md.company_id
        WHERE c.is_active = TRUE AND md.pe_ratio > 20
        ORDER BY md.pe_ratio DESC
        """,
        "High Dividend Yield": """
        SELECT c.symbol, c.name, c.sector, md.dividend_yield, md.close_price
        FROM companies c
        LEFT JOIN market_data md ON c.id = md.company_id
        WHERE c.is_active = TRUE AND md.dividend_yield > 0.05
        ORDER BY md.dividend_yield DESC
        """,
    }

    selected_query = st.selectbox(
        "Choose a predefined query:", list(query_options.keys())
    )

    if st.button("Execute Query"):
        try:
            query = query_options[selected_query]
            results = st.session_state.data_explorer.execute_query(query)

            if not results.empty:
                st.subheader("Query Results")
                st.dataframe(results, use_container_width=True)

                # Basic visualization
                if "market_cap" in results.columns and "symbol" in results.columns:
                    fig = px.bar(
                        results,
                        x="symbol",
                        y="market_cap",
                        title="Query Results Visualization",
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No results found for this query.")

        except Exception as e:
            st.error(f"Query execution failed: {e}")

    # Custom query input
    st.subheader("Custom SQL Query")
    custom_query = st.text_area("Enter your SQL query:", height=100)

    if st.button("Execute Custom Query"):
        if custom_query.strip():
            try:
                results = st.session_state.data_explorer.execute_query(custom_query)

                if not results.empty:
                    st.subheader("Custom Query Results")
                    st.dataframe(results, use_container_width=True)
                else:
                    st.info("No results found for this query.")

            except Exception as e:
                st.error(f"Custom query execution failed: {e}")
        else:
            st.warning("Please enter a SQL query.")


if __name__ == "__main__":
    main()
