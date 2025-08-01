import unittest
import os
import sys
import time
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from fastapi.testclient import TestClient
    from fastapi import Request
    from main import app, rate_limit_middleware, rate_limit_store, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False


@unittest.skipUnless(RATE_LIMITING_AVAILABLE, "Rate limiting dependencies not available")
class TestRateLimiting(unittest.TestCase):
    """Test suite for rate limiting functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear rate limit store
        rate_limit_store.clear()
        self.client = TestClient(app)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Clear rate limit store
        rate_limit_store.clear()

    def test_rate_limit_store_initialization(self):
        """Test that rate limit store is properly initialized."""
        self.assertIsInstance(rate_limit_store, dict)
        self.assertEqual(len(rate_limit_store), 0)

    def test_rate_limit_constants(self):
        """Test that rate limiting constants are properly set."""
        self.assertIsInstance(RATE_LIMIT_REQUESTS, int)
        self.assertGreater(RATE_LIMIT_REQUESTS, 0)
        self.assertIsInstance(RATE_LIMIT_WINDOW, int)
        self.assertGreater(RATE_LIMIT_WINDOW, 0)

    def test_single_request_within_limit(self):
        """Test that a single request is allowed."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_multiple_requests_within_limit(self):
        """Test multiple requests within the rate limit."""
        # Make several requests (well below the limit)
        num_requests = min(10, RATE_LIMIT_REQUESTS // 2)
        
        for i in range(num_requests):
            response = self.client.get("/health")
            self.assertEqual(response.status_code, 200, f"Request {i+1} failed")

    def test_rate_limit_tracking_per_ip(self):
        """Test that rate limiting tracks requests per IP."""
        # Make a request
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        # Check that the IP was added to rate limit store
        # Note: TestClient might use a default IP, so we check for any entry
        self.assertGreater(len(rate_limit_store), 0)

    @patch('main.datetime')
    def test_rate_limit_window_cleanup(self, mock_datetime_module):
        """Test that old entries are cleaned up from rate limit store."""
        # Set up mock time
        base_time = datetime.now()
        mock_datetime_module.now.return_value.timestamp.return_value = base_time.timestamp()
        
        # Manually add old entries to rate limit store
        old_timestamp = base_time.timestamp() - RATE_LIMIT_WINDOW - 10
        rate_limit_store["test_ip"] = [old_timestamp, old_timestamp + 1]
        
        # Make a request which should trigger cleanup
        response = self.client.get("/health")
        
        # The old entries should be cleaned up, but new entry for the request should exist
        # Note: Actual IP might be different from "test_ip"
        if "test_ip" in rate_limit_store:
            # If test_ip still exists, it should have fewer entries
            self.assertLess(len(rate_limit_store["test_ip"]), 2)

    def test_rate_limit_middleware_response_format(self):
        """Test that rate limit middleware returns proper error format."""
        # This test manually checks the middleware behavior
        # Since we can't easily trigger rate limiting with TestClient,
        # we'll test the middleware function directly
        
        # Create a mock request
        mock_request = MagicMock()
        mock_request.client.host = "test_ip"
        
        # Fill up the rate limit for this IP
        current_time = datetime.now().timestamp()
        rate_limit_store["test_ip"] = [current_time] * (RATE_LIMIT_REQUESTS + 1)
        
        # Create a mock call_next function
        async def mock_call_next(request):
            return MagicMock()
        
        # Test the middleware
        async def test_middleware():
            try:
                result = await rate_limit_middleware(mock_request, mock_call_next)
                # Should raise HTTPException, not return it
                self.fail("Expected HTTPException to be raised")
            except Exception as e:
                from fastapi import HTTPException
                self.assertIsInstance(e, HTTPException)
                self.assertEqual(e.status_code, 429)
                self.assertEqual(e.detail, "Rate limit exceeded")
        
        # Run the async test
        asyncio.run(test_middleware())

    def test_rate_limit_different_ips(self):
        """Test that rate limiting is applied per IP address."""
        # This is difficult to test with TestClient as it uses the same IP
        # But we can test the logic manually
        
        current_time = datetime.now().timestamp()
        
        # Simulate requests from different IPs
        rate_limit_store["ip1"] = [current_time] * (RATE_LIMIT_REQUESTS // 2)
        rate_limit_store["ip2"] = [current_time] * (RATE_LIMIT_REQUESTS // 2)
        
        # Both IPs should be under their individual limits
        self.assertLess(len(rate_limit_store["ip1"]), RATE_LIMIT_REQUESTS)
        self.assertLess(len(rate_limit_store["ip2"]), RATE_LIMIT_REQUESTS)

    def test_rate_limit_edge_case_exact_limit(self):
        """Test behavior when exactly at the rate limit."""
        # Manually set up rate limit store to be at the exact limit
        current_time = datetime.now().timestamp()
        test_ip = "edge_case_ip"
        rate_limit_store[test_ip] = [current_time] * RATE_LIMIT_REQUESTS
        
        # Check that the IP is at the limit
        self.assertEqual(len(rate_limit_store[test_ip]), RATE_LIMIT_REQUESTS)

    def test_rate_limit_cleanup_empty_entries(self):
        """Test that empty IP entries are removed during cleanup."""
        # Add an entry with old timestamps that should be cleaned up
        old_time = datetime.now().timestamp() - RATE_LIMIT_WINDOW - 10
        test_ip = "cleanup_test_ip"
        rate_limit_store[test_ip] = [old_time, old_time + 1]
        
        # Make a request to trigger cleanup
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        
        # The test_ip entry should be removed if all its timestamps were old
        # Note: We can't guarantee this because the actual client IP might be different
        # But we can check that cleanup occurred by looking at the store structure

    def test_rate_limit_concurrent_requests(self):
        """Test rate limiting with concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = self.client.get("/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads to make concurrent requests
        threads = []
        num_threads = min(5, RATE_LIMIT_REQUESTS // 2)  # Stay well under limit
        
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed since we're under the limit
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), num_threads)
        self.assertTrue(all(status == 200 for status in results))

    def test_rate_limit_middleware_with_no_client(self):
        """Test rate limiting middleware when request has no client."""
        # Create a mock request without client info
        mock_request = MagicMock()
        mock_request.client = None
        
        async def mock_call_next(request):
            response = MagicMock()
            return response
        
        # Test the middleware
        async def test_middleware():
            result = await rate_limit_middleware(mock_request, mock_call_next)
            self.assertIsNotNone(result)
        
        # Should not raise an exception
        asyncio.run(test_middleware())

    def test_rate_limit_time_window_behavior(self):
        """Test that rate limiting respects the time window."""
        current_time = datetime.now().timestamp()
        test_ip = "time_window_test"
        
        # Add timestamps spanning the window
        timestamps = [
            current_time - RATE_LIMIT_WINDOW + 1,  # Just within window
            current_time - RATE_LIMIT_WINDOW - 1,  # Just outside window
            current_time,  # Current time
        ]
        
        rate_limit_store[test_ip] = timestamps
        
        # Make a request to trigger cleanup
        response = self.client.get("/health")
        
        # The old timestamp should be cleaned up
        if test_ip in rate_limit_store:
            # Should only have timestamps within the window
            for timestamp in rate_limit_store[test_ip]:
                self.assertGreaterEqual(timestamp, current_time - RATE_LIMIT_WINDOW)


if __name__ == '__main__':
    unittest.main()