#!/usr/bin/env python3
"""
Rate Limiting Test for InvestByYourself API
Tech-028: API Implementation

Tests the API gateway's ability to handle high-frequency requests
and protect against over-calling.
"""

import asyncio
import statistics
import time
from typing import Any, Dict, List

import httpx


class RateLimitTester:
    """Test rate limiting functionality of the API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []

    async def make_request(
        self, endpoint: str, client: httpx.AsyncClient
    ) -> Dict[str, Any]:
        """Make a single HTTP request and record the result."""
        start_time = time.time()
        try:
            response = await client.get(f"{self.base_url}{endpoint}")
            end_time = time.time()

            return {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "timestamp": start_time,
                "success": response.status_code < 400,
                "rate_limited": response.status_code == 429,
                "response_size": len(response.content) if response.content else 0,
            }
        except Exception as e:
            end_time = time.time()
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "response_time": end_time - start_time,
                "timestamp": start_time,
                "success": False,
                "rate_limited": False,
                "error": str(e),
                "response_size": 0,
            }

    async def burst_test(
        self, endpoint: str, num_requests: int, delay: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Test burst of requests to a single endpoint."""
        print(f"\n🚀 Burst Test: {num_requests} requests to {endpoint}")
        print(f"   Delay between requests: {delay}s")

        results = []
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = []
            for i in range(num_requests):
                if delay > 0:
                    await asyncio.sleep(delay)
                task = self.make_request(endpoint, client)
                tasks.append(task)

            # Execute all requests
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and convert to proper format
            valid_results = []
            for result in results:
                if isinstance(result, dict):
                    valid_results.append(result)
                else:
                    valid_results.append(
                        {
                            "endpoint": endpoint,
                            "status_code": 0,
                            "response_time": 0,
                            "timestamp": time.time(),
                            "success": False,
                            "rate_limited": False,
                            "error": str(result),
                            "response_size": 0,
                        }
                    )

        return valid_results

    async def sustained_test(
        self, endpoint: str, duration: int, requests_per_second: int
    ) -> List[Dict[str, Any]]:
        """Test sustained load over a period of time."""
        print(
            f"\n⏱️  Sustained Test: {requests_per_second} req/s for {duration}s to {endpoint}"
        )

        results = []
        delay = 1.0 / requests_per_second
        end_time = time.time() + duration

        async with httpx.AsyncClient(timeout=10.0) as client:
            while time.time() < end_time:
                result = await self.make_request(endpoint, client)
                results.append(result)
                await asyncio.sleep(delay)

        return results

    def analyze_results(self, results: List[Dict[str, Any]], test_name: str) -> None:
        """Analyze and display test results."""
        if not results:
            print(f"❌ No results for {test_name}")
            return

        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        rate_limited_requests = sum(1 for r in results if r["rate_limited"])
        failed_requests = total_requests - successful_requests

        response_times = [r["response_time"] for r in results if r["success"]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0

        print(f"\n📊 {test_name} Results:")
        print(f"   Total Requests: {total_requests}")
        print(
            f"   Successful: {successful_requests} ({successful_requests/total_requests*100:.1f}%)"
        )
        print(
            f"   Rate Limited: {rate_limited_requests} ({rate_limited_requests/total_requests*100:.1f}%)"
        )
        print(
            f"   Failed: {failed_requests} ({failed_requests/total_requests*100:.1f}%)"
        )
        print(f"   Response Times:")
        print(f"     Average: {avg_response_time:.3f}s")
        print(f"     Min: {min_response_time:.3f}s")
        print(f"     Max: {max_response_time:.3f}s")

        # Show status code distribution
        status_codes = {}
        for result in results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1

        print(f"   Status Codes: {dict(status_codes)}")

        # Show rate limiting effectiveness
        if rate_limited_requests > 0:
            print(
                f"   ✅ Rate limiting is working! {rate_limited_requests} requests were blocked"
            )
        else:
            print(f"   ⚠️  No rate limiting detected - all requests went through")

    async def run_comprehensive_test(self) -> None:
        """Run comprehensive rate limiting tests."""
        print("🧪 InvestByYourself API Rate Limiting Test")
        print("=" * 50)

        # Test endpoints
        endpoints = ["/", "/health", "/api/v1/portfolio/test"]

        for endpoint in endpoints:
            print(f"\n🎯 Testing endpoint: {endpoint}")

            # Test 1: Small burst (should pass)
            print("\n1️⃣ Small Burst Test (10 requests)")
            results = await self.burst_test(endpoint, 10, 0.1)
            self.analyze_results(results, f"Small Burst - {endpoint}")

            # Test 2: Medium burst (might trigger rate limiting)
            print("\n2️⃣ Medium Burst Test (50 requests)")
            results = await self.burst_test(endpoint, 50, 0.01)
            self.analyze_results(results, f"Medium Burst - {endpoint}")

            # Test 3: Large burst (should definitely trigger rate limiting)
            print("\n3️⃣ Large Burst Test (200 requests)")
            results = await self.burst_test(endpoint, 200, 0.001)
            self.analyze_results(results, f"Large Burst - {endpoint}")

            # Test 4: Sustained load
            print("\n4️⃣ Sustained Load Test (5 seconds at 20 req/s)")
            results = await self.sustained_test(endpoint, 5, 20)
            self.analyze_results(results, f"Sustained Load - {endpoint}")

        print("\n" + "=" * 50)
        print("🏁 Rate Limiting Test Complete!")
        print("\n💡 Expected Results:")
        print("   - Small bursts should succeed")
        print("   - Large bursts should trigger rate limiting (429 status)")
        print("   - Rate limiting should protect the server from overload")


async def main():
    """Main test function."""
    tester = RateLimitTester()

    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Server is running and responding")
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Server is not running or not accessible: {e}")
        print("Please start the server with: python simple_main.py")
        return

    # Run comprehensive tests
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())
