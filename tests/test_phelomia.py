"""
Test Suite for Phelomia Application
Comprehensive testing for document analysis features
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from PIL import Image
import numpy as np

# Test configuration
@pytest.fixture
def sample_image():
    """Create a sample test image"""
    img = Image.new('RGB', (800, 600), color='white')
    return img

@pytest.fixture
def temp_image_file(sample_image):
    """Create a temporary image file"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        sample_image.save(tmp.name)
        yield tmp.name
    os.unlink(tmp.name)

class TestDocumentIntelligence:
    """Test document type detection system"""
    
    def test_analyze_document_basic(self, temp_image_file):
        """Test basic document analysis"""
        from src.document_intelligence import analyze_document_type
        
        result = analyze_document_type(temp_image_file)
        
        assert 'suggested_analysis' in result
        assert 'confidence_scores' in result
        assert 'recommendations' in result
        assert isinstance(result['suggested_analysis'], list)
        assert isinstance(result['confidence_scores'], dict)
    
    def test_document_detector_initialization(self):
        """Test DocumentTypeDetector initialization"""
        from src.document_intelligence import DocumentTypeDetector
        
        detector = DocumentTypeDetector()
        assert detector.detection_patterns is not None
        assert 'table' in detector.detection_patterns
        assert 'formula' in detector.detection_patterns
    
    def test_confidence_scores_range(self, temp_image_file):
        """Test that confidence scores are in valid range"""
        from src.document_intelligence import analyze_document_type
        
        result = analyze_document_type(temp_image_file)
        
        for doc_type, score in result['confidence_scores'].items():
            assert 0 <= score <= 1, f"Score for {doc_type} is out of range: {score}"

class TestAnalytics:
    """Test analytics and performance tracking"""
    
    def test_performance_tracker_initialization(self):
        """Test PerformanceTracker initialization"""
        from src.analytics import PerformanceTracker
        
        tracker = PerformanceTracker(log_file="test_performance.json")
        assert tracker.stats is not None
        assert tracker.processing_times is not None
    
    def test_track_request_lifecycle(self):
        """Test complete request tracking lifecycle"""
        from src.analytics import PerformanceTracker
        
        tracker = PerformanceTracker(log_file="test_performance.json")
        
        # Start request
        request_id = tracker.track_request_start("test_request")
        assert request_id is not None
        assert tracker.total_requests == 1
        
        # End request successfully
        tracker.track_request_end(request_id, success=True, execution_time=1.5)
        assert tracker.successful_requests == 1
        assert len(tracker.processing_times) == 1
    
    def test_feature_usage_tracking(self):
        """Test feature usage tracking"""
        from src.analytics import PerformanceTracker
        
        tracker = PerformanceTracker(log_file="test_performance.json")
        
        tracker.track_feature_usage("table_recognition")
        tracker.track_feature_usage("table_recognition")
        tracker.track_feature_usage("formula_conversion")
        
        assert tracker.stats["feature_table_recognition"] == 2
        assert tracker.stats["feature_formula_conversion"] == 1

class TestBatchProcessing:
    """Test batch processing system"""
    
    @pytest.mark.asyncio
    async def test_batch_job_creation(self):
        """Test batch job creation"""
        from src.batch_processing import BatchProcessor
        
        processor = BatchProcessor(max_concurrent_jobs=1, max_workers=1)
        
        job_id = await processor.submit_batch_job(
            file_paths=["test1.png", "test2.png"],
            analysis_types=["table", "formula"]
        )
        
        assert job_id is not None
        assert job_id in processor.active_jobs
        
        job = processor.active_jobs[job_id]
        assert job.file_paths == ["test1.png", "test2.png"]
        assert job.analysis_types == ["table", "formula"]
    
    def test_job_status_tracking(self):
        """Test job status tracking"""
        from src.batch_processing import BatchProcessor, BatchJob, ProcessingStatus
        
        processor = BatchProcessor()
        
        job = BatchJob(
            job_id="test_job_1",
            file_paths=["test.png"],
            analysis_types=["table"]
        )
        
        processor.active_jobs["test_job_1"] = job
        
        status = processor.get_job_status("test_job_1")
        assert status is not None
        assert status["job_id"] == "test_job_1"
        assert status["status"] == ProcessingStatus.PENDING.value

class TestConfiguration:
    """Test configuration management"""
    
    def test_settings_initialization(self):
        """Test settings initialization"""
        from src.config import PhelomiaSettings
        
        settings = PhelomiaSettings()
        assert settings.model_name is not None
        assert settings.device in ["auto", "cuda", "cpu", "mps"]
        assert settings.max_length > 0
    
    def test_get_device_function(self):
        """Test device detection function"""
        from src.config import get_device
        
        device = get_device()
        assert device in ["cuda", "cpu", "mps"]

class TestModernUI:
    """Test modern UI components"""
    
    def test_modern_ui_initialization(self):
        """Test ModernUI initialization"""
        from src.modern_ui import ModernUI
        
        ui = ModernUI()
        assert ui.current_step == 1
        assert ui.max_steps == 4

class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_sample_data_integrity(self):
        """Test that all sample data files exist and are valid"""
        from src.app_enhanced import sample_data
        
        for sample in sample_data:
            assert 'name' in sample
            assert 'category' in sample
            assert 'difficulty' in sample
            assert 'image' in sample
            assert 'prompts' in sample
            assert isinstance(sample['prompts'], list)
            assert len(sample['prompts']) > 0
    
    @patch('src.config.torch')
    def test_device_detection_mock(self, mock_torch):
        """Test device detection with mocked torch"""
        mock_torch.cuda.is_available.return_value = True
        mock_torch.backends.mps.is_available.return_value = False
        
        from src.config import get_device
        
        device = get_device()
        assert device == "cuda"

# Performance tests
class TestPerformance:
    """Performance and load testing"""
    
    def test_large_batch_handling(self):
        """Test handling of large batch sizes"""
        from src.batch_processing import BatchProcessor
        
        processor = BatchProcessor()
        
        # Test with large file list
        large_file_list = [f"test_{i}.png" for i in range(100)]
        
        # Should not raise exception
        job = processor.BatchJob(
            job_id="large_test",
            file_paths=large_file_list,
            analysis_types=["document"]
        )
        
        assert len(job.file_paths) == 100
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking in analytics"""
        from src.analytics import PerformanceTracker
        
        tracker = PerformanceTracker()
        
        # Add many processing times to test memory management
        for i in range(2000):  # More than maxlen of deque
            tracker.processing_times.append(float(i))
        
        # Should only keep last 1000
        assert len(tracker.processing_times) == 1000
        assert tracker.processing_times[0] == 1000.0  # First kept item

# Error handling tests
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_image_path(self):
        """Test handling of invalid image paths"""
        from src.document_intelligence import analyze_document_type
        
        result = analyze_document_type("nonexistent_file.png")
        
        # Should return fallback analysis
        assert result is not None
        assert 'suggested_analysis' in result
        assert result['suggested_analysis'] == ['document']
    
    def test_analytics_error_tracking(self):
        """Test error tracking in analytics"""
        from src.analytics import PerformanceTracker
        
        tracker = PerformanceTracker()
        
        # Track some errors
        tracker.track_request_end("test_1", success=False, error="Test error 1")
        tracker.track_request_end("test_2", success=False, error="Test error 1")
        tracker.track_request_end("test_3", success=False, error="Test error 2")
        
        assert tracker.failed_requests == 3
        assert tracker.error_counts["Test error 1"] == 2
        assert tracker.error_counts["Test error 2"] == 1

# Fixtures for testing
@pytest.fixture
def mock_model():
    """Mock AI model for testing"""
    mock = Mock()
    mock.generate.return_value = "Test generated content"
    return mock

@pytest.fixture
def mock_processor():
    """Mock processor for testing"""
    mock = Mock()
    mock.tokenizer = Mock()
    return mock

# Parameterized tests
@pytest.mark.parametrize("doc_type,expected_features", [
    ("table", ["grid_structure", "horizontal_lines", "vertical_lines"]),
    ("formula", ["mathematical_symbols", "white_space_ratio"]),
    ("code", ["text_density", "monospace_patterns"]),
    ("chart", ["chart_elements", "circular_features"])
])
def test_document_type_features(doc_type, expected_features):
    """Test document type specific feature detection"""
    from src.document_intelligence import DocumentTypeDetector
    
    detector = DocumentTypeDetector()
    patterns = detector.detection_patterns.get(doc_type, {})
    
    assert 'visual_features' in patterns
    # Could add more specific feature testing here

if __name__ == "__main__":
    pytest.main([__file__, "-v"])