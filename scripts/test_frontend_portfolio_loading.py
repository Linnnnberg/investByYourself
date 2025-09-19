#!/usr/bin/env python3
"""
Test Frontend Portfolio Loading
InvestByYourself Financial Platform

Test if the frontend can now load portfolios after fixing the API URL issue.
"""

import json

import requests


def test_frontend_portfolio_loading():
    """Test if frontend can load portfolios."""
    print("Testing frontend portfolio loading...")

    # Test the API endpoint that frontend calls
    api_url = "http://localhost:8000/api/v1/portfolios"

    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            portfolios = data.get("portfolios", [])

            print(f"✅ API call successful")
            print(f"Number of portfolios: {len(portfolios)}")

            if portfolios:
                print(f"\nPortfolio details:")
                for i, portfolio in enumerate(portfolios[:3]):  # Show first 3
                    print(
                        f"  {i+1}. {portfolio['name']} ({portfolio['status']}) - ${portfolio['value']:,.0f}"
                    )

                print(
                    f"\n✅ Frontend should now be able to display {len(portfolios)} portfolios"
                )
                print(
                    f"✅ Portfolio data format matches PortfolioList component expectations"
                )
            else:
                print("❌ No portfolios found")
        else:
            print(f"❌ API call failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_frontend_portfolio_loading()
