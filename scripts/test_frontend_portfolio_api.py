#!/usr/bin/env python3
"""
Test Frontend Portfolio API
InvestByYourself Financial Platform

Test the portfolio API call that the frontend would make.
"""

import json

import requests


def test_frontend_portfolio_api():
    """Test the portfolio API call that frontend makes."""
    base_url = "http://localhost:8000/api/v1"

    print("Testing frontend portfolio API call...")

    try:
        # Simulate the exact call the frontend makes
        response = requests.get(
            f"{base_url}/portfolios",
            {
                "method": "GET",
                "headers": {
                    "Content-Type": "application/json",
                },
            },
            timeout=5,
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API call successful")
            print(f"Response structure: {list(data.keys())}")

            portfolios = data.get("portfolios", [])
            print(f"Number of portfolios: {len(portfolios)}")

            if portfolios:
                print(f"\nFirst portfolio:")
                first_portfolio = portfolios[0]
                print(f"  ID: {first_portfolio.get('id')}")
                print(f"  Name: {first_portfolio.get('name')}")
                print(f"  Status: {first_portfolio.get('status')}")
                print(f"  Value: {first_portfolio.get('value')}")
                print(f"  Risk Level: {first_portfolio.get('riskLevel')}")

                # Check if data matches PortfolioList expectations
                required_fields = [
                    "id",
                    "name",
                    "description",
                    "value",
                    "change",
                    "changePercent",
                    "allocation",
                    "riskLevel",
                    "lastUpdated",
                    "status",
                ]
                missing_fields = [
                    field for field in required_fields if field not in first_portfolio
                ]

                if missing_fields:
                    print(f"❌ Missing fields for PortfolioList: {missing_fields}")
                else:
                    print(f"✅ All fields present for PortfolioList")
            else:
                print("❌ No portfolios in response")
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_frontend_portfolio_api()
