#!/usr/bin/env python3
"""
InvestByYourself Authentication Test Script
Tech-028: API Implementation

Simple test script to verify authentication endpoints work correctly.
"""

import asyncio
import json
import sys
from typing import Any, Dict

import httpx


class AuthTester:
    """Simple authentication tester."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.access_token: str = ""
        self.refresh_token: str = ""

    async def test_health(self) -> bool:
        """Test health endpoint."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            print(f"Health check: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
                return True
            return False
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    async def test_register(
        self, email: str, password: str, first_name: str, last_name: str
    ) -> bool:
        """Test user registration."""
        try:
            data = {
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/register", json=data
            )

            print(f"Registration: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["access_token"]
                self.refresh_token = result["refresh_token"]
                print(f"Registration successful: {result}")
                return True
            else:
                print(f"Registration failed: {response.text}")
                return False

        except Exception as e:
            print(f"Registration test failed: {e}")
            return False

    async def test_login(self, email: str, password: str) -> bool:
        """Test user login."""
        try:
            data = {"email": email, "password": password}

            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/login", json=data
            )

            print(f"Login: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["access_token"]
                self.refresh_token = result["refresh_token"]
                print(f"Login successful: {result}")
                return True
            else:
                print(f"Login failed: {response.text}")
                return False

        except Exception as e:
            print(f"Login test failed: {e}")
            return False

    async def test_profile(self) -> bool:
        """Test getting user profile."""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}

            response = await self.client.get(
                f"{self.base_url}/api/v1/auth/profile", headers=headers
            )

            print(f"Profile: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Profile data: {result}")
                return True
            else:
                print(f"Profile failed: {response.text}")
                return False

        except Exception as e:
            print(f"Profile test failed: {e}")
            return False

    async def test_refresh(self) -> bool:
        """Test token refresh."""
        try:
            headers = {"Authorization": f"Bearer {self.refresh_token}"}

            response = await self.client.post(
                f"{self.base_url}/api/v1/auth/refresh", headers=headers
            )

            print(f"Refresh: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["access_token"]
                self.refresh_token = result["refresh_token"]
                print(f"Refresh successful: {result}")
                return True
            else:
                print(f"Refresh failed: {response.text}")
                return False

        except Exception as e:
            print(f"Refresh test failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Run authentication tests."""
    print("Starting InvestByYourself Authentication Tests...")

    tester = AuthTester()

    try:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        if not await tester.test_health():
            print("Health check failed, server might not be running")
            return

        # Test registration
        print("\n2. Testing user registration...")
        test_email = "test@example.com"
        test_password = "${TEST_PASSWORD:-TestPass123!}"

        if not await tester.test_register(
            email=test_email,
            password=test_password,
            first_name="Test",
            last_name="User",
        ):
            print("Registration failed")
            return

        # Test profile access
        print("\n3. Testing profile access...")
        if not await tester.test_profile():
            print("Profile access failed")
            return

        # Test token refresh
        print("\n4. Testing token refresh...")
        if not await tester.test_refresh():
            print("Token refresh failed")
            return

        # Test login with existing user
        print("\n5. Testing login with existing user...")
        if not await tester.test_login(test_email, test_password):
            print("Login failed")
            return

        print("\n✅ All authentication tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
