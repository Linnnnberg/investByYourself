"""
Financial Calculator Dashboard - investByYourself

A Streamlit-based calculator that demonstrates our existing financial calculations
including PE ratios, CAGR, percentage changes, and portfolio metrics.

Part of Story-002: Financial Calculation Testing Suite
"""

from decimal import Decimal, getcontext
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Set precision for financial calculations
getcontext().prec = 28


class FinancialCalculator:
    """Financial calculation engine using our existing logic."""

    @staticmethod
    def calculate_pe_ratio(price: float, earnings: float) -> float:
        """Calculate PE ratio using our existing logic."""
        if earnings <= 0:
            raise ValueError("Earnings must be positive for PE ratio calculation")
        return price / earnings

    @staticmethod
    def calculate_cagr(initial_value: float, final_value: float, years: float) -> float:
        """Calculate CAGR using our existing logic."""
        if years <= 0:
            raise ValueError("Years must be positive for CAGR calculation")
        if initial_value <= 0:
            raise ValueError("Initial value must be positive for CAGR calculation")
        return (final_value / initial_value) ** (1 / years) - 1

    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """Calculate percentage change using our existing logic."""
        if old_value == 0:
            raise ValueError(
                "Old value cannot be zero for percentage change calculation"
            )
        return ((new_value - old_value) / old_value) * 100

    @staticmethod
    def calculate_portfolio_value(holdings: List[Dict[str, float]]) -> float:
        """Calculate portfolio value using our existing logic."""
        return sum(holding["shares"] * holding["price"] for holding in holdings)

    @staticmethod
    def calculate_risk_free_adjustment(
        market_return: float, risk_free_rate: float
    ) -> float:
        """Calculate risk-free rate adjustment using our existing logic."""
        return market_return - risk_free_rate

    @staticmethod
    def calculate_weighted_average(values: List[float], weights: List[float]) -> float:
        """Calculate weighted average for portfolio metrics."""
        if len(values) != len(weights):
            raise ValueError("Values and weights must have the same length")
        if sum(weights) == 0:
            raise ValueError("Sum of weights cannot be zero")

        return sum(v * w for v, w in zip(values, weights)) / sum(weights)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="InvestByYourself - Financial Calculator",
        page_icon="🧮",
        layout="wide",
    )

    st.title("🧮 InvestByYourself Financial Calculator")
    st.markdown("**Professional financial calculations powered by our tested engine**")

    # Create tabs for different calculators
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 PE Ratio Calculator",
            "📈 CAGR Calculator",
            "💰 Portfolio Calculator",
            "📉 Percentage Change",
            "🎯 Risk Metrics",
        ]
    )

    # Tab 1: PE Ratio Calculator
    with tab1:
        st.header("📊 PE Ratio Calculator")
        st.markdown("Calculate Price-to-Earnings ratio for stock valuation")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Input Values")
            price = st.number_input(
                "Stock Price ($)", min_value=0.01, value=150.0, step=0.01
            )
            earnings = st.number_input(
                "Earnings Per Share ($)", min_value=0.01, value=5.0, step=0.01
            )

            if st.button("Calculate PE Ratio"):
                try:
                    pe_ratio = FinancialCalculator.calculate_pe_ratio(price, earnings)
                    st.success(f"**PE Ratio: {pe_ratio:.2f}**")

                    # Interpretation
                    if pe_ratio < 15:
                        st.info("📉 **Low PE**: Potentially undervalued stock")
                    elif pe_ratio < 25:
                        st.info("📊 **Moderate PE**: Fairly valued stock")
                    else:
                        st.info("📈 **High PE**: Potentially overvalued stock")

                except ValueError as e:
                    st.error(f"❌ **Error**: {e}")

        with col2:
            st.subheader("PE Ratio Analysis")
            st.markdown(
                """
            **What PE Ratio Means:**

            - **< 15**: Potentially undervalued
            - **15-25**: Fairly valued
            - **> 25**: Potentially overvalued

            **Note**: PE ratios vary by industry and market conditions.
            """
            )

            # Example calculations
            st.subheader("Example Calculations")
            examples = [
                {"Stock": "AAPL", "Price": 150, "Earnings": 5, "PE": 30},
                {"Stock": "GOOGL", "Price": 2800, "Earnings": 100, "PE": 28},
                {"Stock": "MSFT", "Price": 350, "Earnings": 10, "PE": 35},
            ]

            for example in examples:
                st.write(
                    f"**{example['Stock']}**: ${example['Price']} / ${example['Earnings']} = PE {example['PE']}"
                )

    # Tab 2: CAGR Calculator
    with tab2:
        st.header("📈 CAGR Calculator")
        st.markdown("Calculate Compound Annual Growth Rate for investment returns")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Input Values")
            initial_value = st.number_input(
                "Initial Investment ($)", min_value=0.01, value=10000.0, step=100.0
            )
            final_value = st.number_input(
                "Final Value ($)", min_value=0.01, value=20000.0, step=100.0
            )
            years = st.number_input(
                "Investment Period (Years)", min_value=0.1, value=5.0, step=0.1
            )

            if st.button("Calculate CAGR"):
                try:
                    cagr = FinancialCalculator.calculate_cagr(
                        initial_value, final_value, years
                    )
                    cagr_percent = cagr * 100
                    st.success(f"**CAGR: {cagr_percent:.2f}%**")

                    # Interpretation
                    if cagr_percent < 5:
                        st.info("📉 **Low Growth**: Conservative investment")
                    elif cagr_percent < 15:
                        st.info("📊 **Moderate Growth**: Balanced investment")
                    else:
                        st.info("📈 **High Growth**: Aggressive investment")

                except ValueError as e:
                    st.error(f"❌ **Error**: {e}")

        with col2:
            st.subheader("CAGR Analysis")
            st.markdown(
                """
            **What CAGR Means:**

            - **< 5%**: Conservative (bonds, savings)
            - **5-15%**: Balanced (diversified portfolio)
            - **> 15%**: Aggressive (growth stocks)

            **Note**: Past performance doesn't guarantee future results.
            """
            )

            # CAGR visualization
            if st.button("Show CAGR Visualization"):
                years_range = np.arange(0, years + 0.1, 0.1)
                values = [initial_value * (1 + cagr) ** year for year in years_range]

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=years_range,
                        y=values,
                        mode="lines+markers",
                        name="Investment Growth",
                        line=dict(color="green", width=3),
                    )
                )

                fig.update_layout(
                    title=f"Investment Growth: ${initial_value:,.0f} → ${final_value:,.0f}",
                    xaxis_title="Years",
                    yaxis_title="Value ($)",
                    showlegend=True,
                )

                st.plotly_chart(fig, use_container_width=True)

    # Tab 3: Portfolio Calculator
    with tab3:
        st.header("💰 Portfolio Calculator")
        st.markdown("Calculate portfolio metrics using our existing logic")

        st.subheader("Portfolio Holdings")

        # Dynamic portfolio input
        num_holdings = st.number_input(
            "Number of Holdings", min_value=1, max_value=20, value=3
        )

        holdings = []
        for i in range(num_holdings):
            col1, col2, col3 = st.columns(3)
            with col1:
                symbol = st.text_input(
                    f"Symbol {i+1}", value=f"STOCK{i+1}", key=f"sym_{i}"
                )
            with col2:
                shares = st.number_input(
                    f"Shares {i+1}", min_value=0.01, value=100.0, key=f"shares_{i}"
                )
            with col3:
                price = st.number_input(
                    f"Price {i+1}", min_value=0.01, value=50.0, key=f"price_{i}"
                )

            holdings.append({"symbol": symbol, "shares": shares, "price": price})

        if st.button("Calculate Portfolio"):
            try:
                total_value = FinancialCalculator.calculate_portfolio_value(holdings)

                # Calculate allocation percentages
                allocations = []
                for holding in holdings:
                    value = holding["shares"] * holding["price"]
                    percentage = (value / total_value) * 100
                    allocations.append(percentage)

                # Display results
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Total Portfolio Value", f"${total_value:,.2f}")

                    # Holdings breakdown
                    st.subheader("Holdings Breakdown")
                    for i, holding in enumerate(holdings):
                        value = holding["shares"] * holding["price"]
                        percentage = allocations[i]
                        st.write(
                            f"**{holding['symbol']}**: {holding['shares']} shares × ${holding['price']:.2f} = ${value:,.2f} ({percentage:.1f}%)"
                        )

                with col2:
                    # Allocation chart
                    st.subheader("Portfolio Allocation")
                    labels = [h["symbol"] for h in holdings]
                    fig = go.Figure(data=[go.Pie(labels=labels, values=allocations)])
                    fig.update_layout(title="Portfolio Allocation by Value")
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"❌ **Error**: {e}")

    # Tab 4: Percentage Change Calculator
    with tab4:
        st.header("📉 Percentage Change Calculator")
        st.markdown("Calculate percentage changes for price movements and returns")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Input Values")
            old_value = st.number_input(
                "Old Value", min_value=0.01, value=100.0, step=0.01
            )
            new_value = st.number_input(
                "New Value", min_value=0.01, value=120.0, step=0.01
            )

            if st.button("Calculate Change"):
                try:
                    change = FinancialCalculator.calculate_percentage_change(
                        old_value, new_value
                    )
                    absolute_change = new_value - old_value

                    st.success(f"**Percentage Change: {change:+.2f}%**")
                    st.info(f"**Absolute Change: {absolute_change:+.2f}**")

                    # Interpretation
                    if change > 0:
                        st.success("📈 **Positive Change**: Value increased")
                    else:
                        st.error("📉 **Negative Change**: Value decreased")

                except ValueError as e:
                    st.error(f"❌ **Error**: {e}")

        with col2:
            st.subheader("Change Analysis")
            st.markdown(
                """
            **What This Means:**

            - **Positive %**: Value increased
            - **Negative %**: Value decreased
            - **Large %**: Significant change
            - **Small %**: Minimal change

            **Common Use Cases:**
            - Stock price changes
            - Portfolio returns
            - Economic indicators
            """
            )

    # Tab 5: Risk Metrics
    with tab5:
        st.header("🎯 Risk Metrics Calculator")
        st.markdown("Calculate risk-adjusted returns and portfolio metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Risk-Adjusted Returns")
            market_return = st.number_input(
                "Market Return (%)",
                min_value=-100.0,
                max_value=100.0,
                value=12.0,
                step=0.1,
            )
            risk_free_rate = st.number_input(
                "Risk-Free Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.1
            )

            if st.button("Calculate Risk Premium"):
                try:
                    risk_premium = FinancialCalculator.calculate_risk_free_adjustment(
                        market_return, risk_free_rate
                    )
                    st.success(f"**Risk Premium: {risk_premium:.2f}%**")

                    # Interpretation
                    if risk_premium > 8:
                        st.info("📈 **High Risk Premium**: Aggressive market conditions")
                    elif risk_premium > 4:
                        st.info("📊 **Moderate Risk Premium**: Normal market conditions")
                    else:
                        st.info(
                            "📉 **Low Risk Premium**: Conservative market conditions"
                        )

                except Exception as e:
                    st.error(f"❌ **Error**: {e}")

        with col2:
            st.subheader("Risk Analysis")
            st.markdown(
                """
            **Risk Premium Interpretation:**

            - **< 4%**: Low risk, low return expectations
            - **4-8%**: Normal risk-return balance
            - **> 8%**: High risk, high return potential

            **Risk-Free Rate**: Usually 10-year Treasury yield
            """
            )

    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit • Powered by investByYourself*")


if __name__ == "__main__":
    main()
