# Performance Testing Configuration
import pytest
import time
from unittest.mock import Mock
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor

class PerformanceTestConfig:
    """Configuration for performance tests"""
    MAX_RESPONSE_TIME = 5.0  # seconds
    MAX_MEMORY_USAGE = 2048  # MB
    MAX_CPU_USAGE = 80  # percent
    CONCURRENT_USERS = 10
    TEST_DURATION = 30  # seconds

@pytest.fixture
def performance_config():
    return PerformanceTestConfig()

@pytest.fixture
def system_monitor():
    """Monitor system resources during tests"""
    class SystemMonitor:
        def __init__(self):
            self.monitoring = False
            self.stats = []
        
        def start_monitoring(self):
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor)
            self.monitor_thread.start()
        
        def stop_monitoring(self):
            self.monitoring = False
            if hasattr(self, 'monitor_thread'):
                self.monitor_thread.join()
            return self.stats
        
        def _monitor(self):
            while self.monitoring:
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                
                self.stats.append({
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_info.percent,
                    'memory_used_mb': memory_info.used / 1024 / 1024
                })
                
                time.sleep(0.5)
    
    return SystemMonitor()

@pytest.mark.performance
class TestPerformance:
    """Performance tests for Phelomia"""
    
    def test_document_processing_speed(self, performance_config, system_monitor):
        """Test document processing speed"""
        from src.document_intelligence import analyze_document_type
        
        # Create a test image
        test_image_path = "test_image.png"
        
        system_monitor.start_monitoring()
        
        start_time = time.time()
        
        # Process document
        result = analyze_document_type(test_image_path)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        stats = system_monitor.stop_monitoring()
        
        # Assertions
        assert processing_time < performance_config.MAX_RESPONSE_TIME
        assert result is not None
        
        # Check resource usage
        if stats:
            max_memory = max(stat['memory_used_mb'] for stat in stats)
            max_cpu = max(stat['cpu_percent'] for stat in stats)
            
            assert max_memory < performance_config.MAX_MEMORY_USAGE
            assert max_cpu < performance_config.MAX_CPU_USAGE
    
    def test_concurrent_processing(self, performance_config, system_monitor):
        """Test concurrent document processing"""
        from src.document_intelligence import analyze_document_type
        
        def process_document():
            return analyze_document_type("test_image.png")
        
        system_monitor.start_monitoring()
        
        start_time = time.time()
        
        # Run concurrent processes
        with ThreadPoolExecutor(max_workers=performance_config.CONCURRENT_USERS) as executor:
            futures = [
                executor.submit(process_document) 
                for _ in range(performance_config.CONCURRENT_USERS)
            ]
            
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        stats = system_monitor.stop_monitoring()
        
        # Assertions
        assert len(results) == performance_config.CONCURRENT_USERS
        assert all(result is not None for result in results)
        assert total_time < performance_config.MAX_RESPONSE_TIME * 2  # Allow some overhead
        
        # Check resource usage during concurrent processing
        if stats:
            max_memory = max(stat['memory_used_mb'] for stat in stats)
            max_cpu = max(stat['cpu_percent'] for stat in stats)
            
            # Allow higher limits for concurrent processing
            assert max_memory < performance_config.MAX_MEMORY_USAGE * 1.5
            assert max_cpu < performance_config.MAX_CPU_USAGE * 1.2
    
    def test_memory_leak_detection(self, performance_config):
        """Test for memory leaks during extended processing"""
        from src.analytics import PerformanceTracker
        import gc
        
        tracker = PerformanceTracker()
        initial_memory = psutil.virtual_memory().used / 1024 / 1024
        
        # Run many operations to detect memory leaks
        for i in range(100):
            request_id = tracker.track_request_start("test_request")
            tracker.track_request_end(request_id, True, 1.0)
            
            # Force garbage collection periodically
            if i % 10 == 0:
                gc.collect()
        
        final_memory = psutil.virtual_memory().used / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 50MB)
        assert memory_increase < 50
    
    def test_batch_processing_scalability(self, performance_config):
        """Test batch processing scalability"""
        from src.batch_processing import BatchProcessor
        
        processor = BatchProcessor(max_concurrent_jobs=2, max_workers=4)
        
        # Test with increasing batch sizes
        batch_sizes = [1, 5, 10, 20]
        processing_times = []
        
        for batch_size in batch_sizes:
            file_paths = [f"test_{i}.png" for i in range(batch_size)]
            
            start_time = time.time()
            
            # Simulate batch processing
            job = processor.BatchJob(
                job_id=f"test_batch_{batch_size}",
                file_paths=file_paths,
                analysis_types=["document"]
            )
            
            # Simulate processing time
            time.sleep(batch_size * 0.1)  # Linear scaling simulation
            
            end_time = time.time()
            processing_time = end_time - start_time
            processing_times.append(processing_time)
        
        # Check that processing time scales reasonably
        # Should not be exponential growth
        for i in range(1, len(processing_times)):
            ratio = processing_times[i] / processing_times[i-1]
            batch_ratio = batch_sizes[i] / batch_sizes[i-1]
            
            # Processing time ratio should not be much higher than batch size ratio
            assert ratio <= batch_ratio * 1.5
    
    @pytest.mark.slow
    def test_long_running_stability(self, performance_config):
        """Test application stability during long-running operations"""
        from src.analytics import PerformanceTracker
        
        tracker = PerformanceTracker()
        start_time = time.time()
        
        # Run for extended period
        while time.time() - start_time < performance_config.TEST_DURATION:
            request_id = tracker.track_request_start("stability_test")
            
            # Simulate processing
            time.sleep(0.1)
            
            tracker.track_request_end(request_id, True, 0.1)
            
            # Check memory usage periodically
            current_memory = psutil.virtual_memory().used / 1024 / 1024
            assert current_memory < performance_config.MAX_MEMORY_USAGE
        
        # Verify tracker is still functional
        metrics = tracker.get_dashboard_metrics()
        assert metrics is not None
        assert metrics["system_metrics"]["total_requests"] > 0

@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests using pytest-benchmark"""
    
    def test_document_analysis_benchmark(self, benchmark):
        """Benchmark document analysis performance"""
        from src.document_intelligence import analyze_document_type
        
        result = benchmark(analyze_document_type, "test_image.png")
        
        # Verify result
        assert result is not None
        assert 'confidence_scores' in result
    
    def test_analytics_tracking_benchmark(self, benchmark):
        """Benchmark analytics tracking performance"""
        from src.analytics import PerformanceTracker
        
        tracker = PerformanceTracker()
        
        def track_operation():
            request_id = tracker.track_request_start("benchmark_test")
            tracker.track_request_end(request_id, True, 1.0)
            return tracker.get_dashboard_metrics()
        
        result = benchmark(track_operation)
        
        # Verify result
        assert result is not None
        assert 'system_metrics' in result

# Load testing utilities
class LoadTestRunner:
    """Utility class for running load tests"""
    
    def __init__(self, target_function, concurrent_users=10, duration=30):
        self.target_function = target_function
        self.concurrent_users = concurrent_users
        self.duration = duration
        self.results = []
    
    def run_load_test(self):
        """Run load test with specified parameters"""
        start_time = time.time()
        
        def worker():
            while time.time() - start_time < self.duration:
                try:
                    result_start = time.time()
                    result = self.target_function()
                    result_end = time.time()
                    
                    self.results.append({
                        'success': True,
                        'response_time': result_end - result_start,
                        'timestamp': result_end
                    })
                    
                except Exception as e:
                    self.results.append({
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    })
                
                time.sleep(0.1)  # Small delay between requests
        
        # Start worker threads
        threads = []
        for _ in range(self.concurrent_users):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        return self.analyze_results()
    
    def analyze_results(self):
        """Analyze load test results"""
        if not self.results:
            return {}
        
        successful_results = [r for r in self.results if r['success']]
        failed_results = [r for r in self.results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_results]
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful_results),
            'failed_requests': len(failed_results),
            'success_rate': len(successful_results) / len(self.results) * 100,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'requests_per_second': len(successful_results) / self.duration
        }