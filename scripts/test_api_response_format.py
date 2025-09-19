#!/usr/bin/env python3
"""
Test API Response Format
InvestByYourself Financial Platform

Test the API response format to update the frontend interfaces.
"""

import json

import requests


def test_api_response_format():
    """Test API response format."""
    base_url = "http://localhost:8000/api/v1"

    print("Testing API response format...")

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

                # Check data types
                print(f"\nData types:")
                for key, value in first_portfolio.items():
                    print(f"  {key}: {type(value).__name__} = {value}")
            else:
                print("❌ No portfolios found")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_api_response_format()
