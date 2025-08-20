"""
Portfolio Dashboard - investByYourself

A Streamlit-based dashboard that demonstrates our existing financial calculations
with a real user interface. This shows what we can build with our current foundation.

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


class PortfolioCalculator:
    """Portfolio calculation engine using our existing financial logic."""

    def __init__(self):
        self.holdings = []
        self.current_prices = {}

    def add_holding(self, symbol: str, shares: float, cost_basis: float):
        """Add a new holding to the portfolio."""
        holding = {
            "symbol": symbol.upper(),
            "shares": shares,
            "cost_basis": cost_basis,
            "current_price": self.current_prices.get(symbol.upper(), cost_basis),
        }
        self.holdings.append(holding)

    def update_prices(self, prices: Dict[str, float]):
        """Update current market prices."""
        self.current_prices.update(prices)
        for holding in self.holdings:
            if holding["symbol"] in self.current_prices:
                holding["current_price"] = self.current_prices[holding["symbol"]]

    def calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value using our existing logic."""
        return sum(
            holding["shares"] * holding["current_price"] for holding in self.holdings
        )

    def calculate_total_cost(self) -> float:
        """Calculate total cost basis."""
        return sum(
            holding["shares"] * holding["cost_basis"] for holding in self.holdings
        )

    def calculate_total_pnl(self) -> float:
        """Calculate total profit/loss."""
        return self.calculate_portfolio_value() - self.calculate_total_cost()

    def calculate_percentage_return(self) -> float:
        """Calculate percentage return using our existing logic."""
        total_cost = self.calculate_total_cost()
        if total_cost == 0:
            return 0.0
        return (self.calculate_total_pnl() / total_cost) * 100

    def get_holdings_dataframe(self) -> pd.DataFrame:
        """Convert holdings to pandas DataFrame for display."""
        data = []
        for holding in self.holdings:
            current_value = holding["shares"] * holding["current_price"]
            cost_value = holding["shares"] * holding["cost_basis"]
            pnl = current_value - cost_value
            pnl_percent = (pnl / cost_value * 100) if cost_value > 0 else 0

            data.append(
                {
                    "Symbol": holding["symbol"],
                    "Shares": holding["shares"],
                    "Cost Basis": f"${holding['cost_basis']:.2f}",
                    "Current Price": f"${holding['current_price']:.2f}",
                    "Current Value": f"${current_value:.2f}",
                    "P&L": f"${pnl:.2f}",
                    "P&L %": f"{pnl_percent:.2f}%",
                }
            )

        return pd.DataFrame(data)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="InvestByYourself - Portfolio Dashboard",
        page_icon="📈",
        layout="wide",
    )

    st.title("📈 InvestByYourself Portfolio Dashboard")
    st.markdown("**Your personal investment platform with real-time calculations**")

    # Initialize session state
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = PortfolioCalculator()

    # Sidebar for portfolio management
    with st.sidebar:
        st.header("📊 Portfolio Management")

        # Add new holding
        st.subheader("Add New Holding")
        symbol = st.text_input("Stock Symbol", placeholder="AAPL").upper()
        shares = st.number_input(
            "Number of Shares", min_value=0.01, value=1.0, step=0.01
        )
        cost_basis = st.number_input(
            "Cost Basis per Share", min_value=0.01, value=100.0, step=0.01
        )

        if st.button("Add Holding") and symbol:
            st.session_state.portfolio.add_holding(symbol, shares, cost_basis)
            st.success(f"Added {shares} shares of {symbol} at ${cost_basis:.2f}")
            st.rerun()

        # Update prices
        st.subheader("Update Market Prices")
        price_symbol = st.text_input(
            "Symbol for Price Update", placeholder="AAPL"
        ).upper()
        new_price = st.number_input(
            "Current Market Price", min_value=0.01, value=100.0, step=0.01
        )

        if st.button("Update Price") and price_symbol:
            st.session_state.portfolio.update_prices({price_symbol: new_price})
            st.success(f"Updated {price_symbol} price to ${new_price:.2f}")
            st.rerun()

        # Portfolio summary
        st.subheader("Portfolio Summary")
        if st.session_state.portfolio.holdings:
            total_value = st.session_state.portfolio.calculate_portfolio_value()
            total_cost = st.session_state.portfolio.calculate_total_cost()
            total_pnl = st.session_state.portfolio.calculate_total_pnl()
            pnl_percent = st.session_state.portfolio.calculate_percentage_return()

            st.metric("Total Value", f"${total_value:,.2f}")
            st.metric("Total Cost", f"${total_cost:,.2f}")
            st.metric("Total P&L", f"${total_pnl:,.2f}", f"{pnl_percent:+.2f}%")

    # Main content area
    if not st.session_state.portfolio.holdings:
        st.info("👈 Add your first holding using the sidebar to get started!")

        # Demo data
        if st.button("Load Demo Portfolio"):
            demo_portfolio = PortfolioCalculator()
            demo_portfolio.add_holding("AAPL", 10, 140.0)
            demo_portfolio.add_holding("GOOGL", 5, 2700.0)
            demo_portfolio.add_holding("MSFT", 8, 320.0)
            demo_portfolio.update_prices(
                {"AAPL": 150.0, "GOOGL": 2800.0, "MSFT": 350.0}
            )
            st.session_state.portfolio = demo_portfolio
            st.rerun()
    else:
        # Portfolio overview
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_value = st.session_state.portfolio.calculate_portfolio_value()
            st.metric("Portfolio Value", f"${total_value:,.2f}")

        with col2:
            total_cost = st.session_state.portfolio.calculate_total_cost()
            st.metric("Total Cost", f"${total_cost:,.2f}")

        with col3:
            total_pnl = st.session_state.portfolio.calculate_total_pnl()
            st.metric("Total P&L", f"${total_pnl:,.2f}")

        with col4:
            pnl_percent = st.session_state.portfolio.calculate_percentage_return()
            st.metric("Return %", f"{pnl_percent:+.2f}%")

        # Holdings table
        st.subheader("📋 Current Holdings")
        holdings_df = st.session_state.portfolio.get_holdings_dataframe()
        st.dataframe(holdings_df, use_container_width=True)

        # Portfolio allocation chart
        st.subheader("📊 Portfolio Allocation")
        if len(st.session_state.portfolio.holdings) > 1:
            # Calculate allocation percentages
            total_value = st.session_state.portfolio.calculate_portfolio_value()
            allocations = []
            labels = []

            for holding in st.session_state.portfolio.holdings:
                value = holding["shares"] * holding["current_price"]
                percentage = (value / total_value) * 100
                allocations.append(percentage)
                labels.append(f"{holding['symbol']} ({percentage:.1f}%)")

            # Create pie chart
            fig = go.Figure(data=[go.Pie(labels=labels, values=allocations)])
            fig.update_layout(title="Portfolio Allocation by Value")
            st.plotly_chart(fig, use_container_width=True)

        # Performance metrics
        st.subheader("📈 Performance Metrics")
        col1, col2 = st.columns(2)

        with col1:
            # Individual stock performance
            st.write("**Individual Stock Performance**")
            for holding in st.session_state.portfolio.holdings:
                current_value = holding["shares"] * holding["current_price"]
                cost_value = holding["shares"] * holding["cost_basis"]
                pnl = current_value - cost_value
                pnl_percent = (pnl / cost_value * 100) if cost_value > 0 else 0

                color = "green" if pnl >= 0 else "red"
                st.markdown(
                    f"**{holding['symbol']}**: {pnl_percent:+.2f}% ({pnl:+.2f})"
                )

        with col2:
            # Portfolio statistics
            st.write("**Portfolio Statistics**")
            if len(st.session_state.portfolio.holdings) > 1:
                # Calculate portfolio beta (simplified)
                st.write("**Diversification**: Multi-stock portfolio")
                st.write("**Risk Level**: Moderate (diversified)")
            else:
                st.write("**Diversification**: Single stock (high risk)")
                st.write("**Risk Level**: High (concentrated)")

    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit • Powered by investByYourself*")


if __name__ == "__main__":
    main()
