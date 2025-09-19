#!/usr/bin/env python3
"""
Test Fixed API Calls
InvestByYourself Financial Platform

Test the API calls after fixing the endpoint URLs.
"""

import json

import requests


def test_fixed_api_calls():
    """Test the fixed API calls."""
    base_url = "http://localhost:8000/api/v1"

    print("Testing fixed API calls...")

    # Test portfolios endpoint
    try:
        response = requests.get(f"{base_url}/portfolios/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            portfolios = data.get("portfolios", [])
            print(f"✅ Portfolios endpoint working - {len(portfolios)} portfolios")
        else:
            print(f"❌ Portfolios endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Portfolios endpoint error: {e}")

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint working - {data.get('status')}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

    # Test workflows endpoint
    try:
        response = requests.get(f"{base_url}/workflows/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            workflows = data.get("workflows", [])
            print(f"✅ Workflows endpoint working - {len(workflows)} workflows")
        else:
            print(f"❌ Workflows endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Workflows endpoint error: {e}")


if __name__ == "__main__":
    test_fixed_api_calls()
