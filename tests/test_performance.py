#!/usr/bin/env python3
"""
Performance testing suite for the OWLban application
"""

import pytest
import requests
import time
import statistics
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import json
import os
from datetime import datetime


class TestPerformance:
    """Performance tests for the application"""

    def setup_method(self):
        """Set up test environment"""
        self.base_url = os.getenv('TEST_BASE_URL', 'http://localhost:5000')
        self.num_threads = int(os.getenv('PERF_THREADS', '10'))
        self.duration = int(os.getenv('PERF_DURATION', '30'))  # seconds
        self.requests_per_second = int(os.getenv('PERF_RPS', '50'))

    def make_request(self, endpoint, method='GET', data=None):
        """Make a single request and return timing"""
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            elif method == 'POST':
                response = requests.post(f"{self.base_url}{endpoint}",
                                       json=data,
                                       timeout=10)
            end_time = time.time()

            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200,
                'endpoint': endpoint
            }
        except Exception as e:
            end_time = time.time()
            return {
                'status_code': None,
                'response_time': end_time - start_time,
                'success': False,
                'error': str(e),
                'endpoint': endpoint
            }

    def test_health_endpoint_performance(self):
        """Test health endpoint performance under load"""
        print(f"\nTesting health endpoint with {self.num_threads} concurrent users...")

        results = []

        def worker():
            for _ in range(100):  # 100 requests per thread
                result = self.make_request('/health')
                results.append(result)
                time.sleep(0.01)  # Small delay between requests

        # Run concurrent requests
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        successful_requests = [r for r in results if r['success']]
        response_times = [r['response_time'] for r in results]

        print(f"Total requests: {len(results)}")
        print(f"Successful requests: {len(successful_requests)}")
        print(f"Failed requests: {len(results) - len(successful_requests)}")
        print(f"Average response time: {statistics.mean(response_times):.3f}s")
        print(f"Median response time: {statistics.median(response_times):.3f}s")
        print(f"95th percentile: {statistics.quantiles(response_times, n=20)[18]:.3f}s")
        print(f"Min response time: {min(response_times):.3f}s")
        print(f"Max response time: {max(response_times):.3f}s")

        # Assertions
        assert len(successful_requests) / len(results) > 0.95, "Success rate should be > 95%"
        assert statistics.mean(response_times) < 1.0, "Average response time should be < 1s"
        assert max(response_times) < 5.0, "Max response time should be < 5s"

    def test_api_endpoints_performance(self):
        """Test API endpoints performance"""
        print(f"\nTesting API endpoints with {self.num_threads} concurrent users...")

        endpoints = [
            ('/api/earnings', 'GET', None),
            ('/api/gpu/status', 'GET', None),
            ('/api/leadership/lead_team', 'POST', {
                'leader_name': 'PerfTest',
                'leadership_style': 'DEMOCRATIC',
                'team_members': ['Dev1:Developer', 'Dev2:Designer']
            })
        ]

        all_results = {}

        for endpoint, method, data in endpoints:
            print(f"\nTesting {endpoint}...")
            results = []

            def worker():
                for _ in range(50):  # 50 requests per thread per endpoint
                    result = self.make_request(endpoint, method, data)
                    results.append(result)
                    time.sleep(0.02)  # Small delay

            # Run concurrent requests
            threads = []
            for _ in range(min(self.num_threads, 5)):  # Limit threads per endpoint
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # Analyze results
            successful_requests = [r for r in results if r['success']]
            response_times = [r['response_time'] for r in results]

            stats = {
                'total_requests': len(results),
                'successful_requests': len(successful_requests),
                'success_rate': len(successful_requests) / len(results),
                'avg_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'p95_response_time': statistics.quantiles(response_times, n=20)[18],
                'min_response_time': min(response_times),
                'max_response_time': max(response_times)
            }

            all_results[endpoint] = stats

            print(f"  Total requests: {stats['total_requests']}")
            print(f"  Success rate: {stats['success_rate']:.1%}")
            print(f"  Avg response time: {stats['avg_response_time']:.3f}s")
            print(f"  95th percentile: {stats['p95_response_time']:.3f}s")

            # Assertions
            assert stats['success_rate'] > 0.90, f"Success rate for {endpoint} should be > 90%"
            assert stats['avg_response_time'] < 2.0, f"Average response time for {endpoint} should be < 2s"

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f'performance_results_{timestamp}.json', 'w') as f:
            json.dump(all_results, f, indent=2)

    def test_memory_usage_under_load(self):
        """Test memory usage under sustained load"""
        print(f"\nTesting memory usage under sustained load...")

        # This is a basic test - in production you'd use memory profiling tools
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Initial memory usage: {initial_memory:.2f} MB")

        # Generate sustained load
        results = []
        start_time = time.time()

        def load_worker():
            while time.time() - start_time < 10:  # 10 seconds of load
                result = self.make_request('/health')
                results.append(result)
                time.sleep(0.01)

        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=load_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"Final memory usage: {final_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        print(f"Total requests during test: {len(results)}")

        # Memory should not increase excessively
        assert memory_increase < 50, "Memory increase should be < 50MB during load test"

    def test_database_connection_pooling(self):
        """Test database connection handling under load"""
        # This would test database connection pooling if the app used a database
        # For now, just test that the app handles many concurrent requests without issues

        print(f"\nTesting concurrent request handling...")

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []

            # Submit many concurrent requests
            for _ in range(200):
                future = executor.submit(self.make_request, '/health')
                futures.append(future)

            # Collect results
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        successful_requests = [r for r in results if r['success']]
        response_times = [r['response_time'] for r in results]

        print(f"Concurrent requests: {len(results)}")
        print(f"Successful: {len(successful_requests)}")
        print(f"Success rate: {len(successful_requests)/len(results):.1%}")
        print(f"Average response time: {statistics.mean(response_times):.3f}s")

        assert len(successful_requests) / len(results) > 0.95, "High concurrency success rate should be > 95%"

    def test_error_rate_under_load(self):
        """Test error rate under various load conditions"""
        print(f"\nTesting error rates under load...")

        # Test with different concurrency levels
        concurrency_levels = [1, 5, 10, 20]

        for concurrency in concurrency_levels:
            print(f"\nTesting with {concurrency} concurrent users...")

            results = []

            def worker():
                for _ in range(50):
                    result = self.make_request('/health')
                    results.append(result)
                    time.sleep(0.01)

            threads = []
            for _ in range(concurrency):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            successful_requests = [r for r in results if r['success']]
            error_rate = 1 - (len(successful_requests) / len(results))

            print(f"  Error rate: {error_rate:.1%}")

            # Error rate should remain low
            assert error_rate < 0.05, f"Error rate should be < 5% at concurrency {concurrency}"

    def test_response_time_distribution(self):
        """Test response time distribution under load"""
        print(f"\nAnalyzing response time distribution...")

        results = []

        def worker():
            for _ in range(200):
                result = self.make_request('/health')
                results.append(result)
                time.sleep(0.005)

        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        response_times = [r['response_time'] for r in results if r['success']]

        # Calculate percentiles
        percentiles = statistics.quantiles(response_times, n=100)

        print("Response time percentiles:")
        print(f"  50th percentile (median): {percentiles[49]:.3f}s")
        print(f"  90th percentile: {percentiles[89]:.3f}s")
        print(f"  95th percentile: {percentiles[94]:.3f}s")
        print(f"  99th percentile: {percentiles[98]:.3f}s")

        # Most requests should be fast
        assert percentiles[94] < 1.0, "95th percentile should be < 1s"
        assert percentiles[98] < 2.0, "99th percentile should be < 2s"


class TestLoadPatterns:
    """Test different load patterns"""

    def test_burst_load(self):
        """Test handling of burst traffic"""
        print(f"\nTesting burst load handling...")

        # Simulate burst traffic
        burst_sizes = [10, 50, 100]

        for burst_size in burst_sizes:
            print(f"\nTesting burst of {burst_size} concurrent requests...")

            results = []

            def burst_worker():
                result = self.make_request('/health')
                results.append(result)

            threads = []
            for _ in range(burst_size):
                thread = threading.Thread(target=burst_worker)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            successful_requests = [r for r in results if r['success']]
            response_times = [r['response_time'] for r in results if r['success']]

            print(f"  Success rate: {len(successful_requests)/len(results):.1%}")
            if response_times:
                print(f"  Avg response time: {statistics.mean(response_times):.3f}s")
                print(f"  Max response time: {max(response_times):.3f}s")

            assert len(successful_requests) / len(results) > 0.90, f"Burst success rate should be > 90%"

    def test_sustained_load(self):
        """Test handling of sustained load over time"""
        print(f"\nTesting sustained load for {self.duration} seconds...")

        results = []
        start_time = time.time()
        request_count = 0

        def sustained_worker():
            nonlocal request_count
            while time.time() - start_time < self.duration:
                result = self.make_request('/health')
                results.append(result)
                request_count += 1
                time.sleep(0.1)  # 10 requests per second per thread

        threads = []
        for _ in range(min(self.num_threads, 5)):  # Limit threads for sustained test
            thread = threading.Thread(target=sustained_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        successful_requests = [r for r in results if r['success']]
        response_times = [r['response_time'] for r in results if r['success']]

        duration_actual = time.time() - start_time
        rps = len(results) / duration_actual

        print(f"  Duration: {duration_actual:.1f}s")
        print(f"  Total requests: {len(results)}")
        print(f"  Requests per second: {rps:.1f}")
        print(f"  Success rate: {len(successful_requests)/len(results):.1%}")
        if response_times:
            print(f"  Avg response time: {statistics.mean(response_times):.3f}s")

        assert len(successful_requests) / len(results) > 0.95, "Sustained load success rate should be > 95%"
        assert rps > 10, "Should handle at least 10 RPS"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
