#!/usr/bin/env python3
"""
Test Portfolio API Response
InvestByYourself Financial Platform

Test the portfolio API response to see the exact data structure.
"""

import json

import requests


def test_portfolio_api_response():
    """Test portfolio API response structure."""
    base_url = "http://localhost:8000/api/v1"

    print("Testing portfolio API response...")

    try:
        response = requests.get(f"{base_url}/portfolios/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response successful")
            print(f"Response structure: {list(data.keys())}")

            portfolios = data.get("portfolios", [])
            print(f"Number of portfolios: {len(portfolios)}")

            if portfolios:
                print(f"\nFirst portfolio structure:")
                first_portfolio = portfolios[0]
                print(json.dumps(first_portfolio, indent=2))

                print(f"\nPortfolio keys: {list(first_portfolio.keys())}")

                # Check if all required fields are present
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
                    print(f"❌ Missing required fields: {missing_fields}")
                else:
                    print(f"✅ All required fields present")
            else:
                print("❌ No portfolios returned")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_portfolio_api_response()
