"""Unit tests for fire detection system."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import numpy as np
from PIL import Image

from gemma_3n.fire_detection.config import FireDetectionConfig, Gemma3NE4BConfig
from gemma_3n.fire_detection.models.results import DetectionResult, AnalysisSummary
from gemma_3n.fire_detection.processing.video import FrameData, VideoMetadata, VideoProcessor


class TestFireDetectionConfig:
    """Test configuration models."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = FireDetectionConfig()
        
        assert config.model.model_variant == "gemma-3n-e4b"
        assert config.video.frame_interval == 2.0
        assert config.detection.confidence_threshold == 0.7
        assert config.output.output_format == "json"
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid confidence threshold
        with pytest.raises(ValueError):
            FireDetectionConfig(
                detection=FireDetectionConfig.detection(confidence_threshold=1.5)
            )
        
        # Test invalid frame interval
        with pytest.raises(ValueError):
            FireDetectionConfig(
                video=FireDetectionConfig.video(frame_interval=0.0)
            )
    
    def test_device_auto_selection(self):
        """Test automatic device selection."""
        config = FireDetectionConfig(device="auto")
        device = config.get_device()
        assert device in ["cpu", "cuda", "mps"]


class TestDetectionResult:
    """Test detection result models."""
    
    def test_detection_result_creation(self):
        """Test detection result creation."""
        result = DetectionResult(
            frame_number=1,
            timestamp=2.0,
            fire_detected=True,
            confidence=0.85,
            processing_time=0.5
        )
        
        assert result.frame_number == 1
        assert result.timestamp == 2.0
        assert result.fire_detected is True
        assert result.confidence == 0.85
        assert result.processing_time == 0.5
        assert result.model_variant == "gemma-3n-e4b"
    
    def test_analysis_summary_from_results(self):
        """Test analysis summary creation from results."""
        results = [
            DetectionResult(
                frame_number=1, timestamp=1.0, fire_detected=True, 
                confidence=0.8, processing_time=0.1
            ),
            DetectionResult(
                frame_number=2, timestamp=2.0, fire_detected=False,
                confidence=0.3, processing_time=0.1
            ),
            DetectionResult(
                frame_number=3, timestamp=3.0, fire_detected=True,
                confidence=0.9, processing_time=0.1
            )
        ]
        
        summary = AnalysisSummary.from_results(results)
        
        assert summary.total_frames_processed == 3
        assert summary.fire_detections == 2
        assert summary.detection_rate == 2/3
        assert summary.average_confidence == 0.85  # (0.8 + 0.9) / 2
        assert summary.max_confidence == 0.9
        assert summary.first_detection_time == 1.0
        assert summary.last_detection_time == 3.0


class TestVideoProcessor:
    """Test video processing functionality."""
    
    def test_video_processor_initialization(self):
        """Test video processor initialization."""
        from gemma_3n.fire_detection.config import VideoProcessingConfig
        
        config = VideoProcessingConfig()
        processor = VideoProcessor(config)
        
        assert processor.config == config
    
    @patch('cv2.VideoCapture')
    def test_get_video_metadata(self, mock_video_capture):
        """Test video metadata extraction."""
        from gemma_3n.fire_detection.config import VideoProcessingConfig
        
        # Mock video capture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = [30.0, 900, 1920, 1080, 1665.0]  # fps, frames, width, height, fourcc
        mock_video_capture.return_value = mock_cap
        
        config = VideoProcessingConfig()
        processor = VideoProcessor(config)
        
        # Create a temporary file for testing
        test_video = Path("test_video.mp4")
        test_video.touch()
        
        try:
            metadata = processor.get_video_metadata(test_video)
            
            assert metadata.fps == 30.0
            assert metadata.total_frames == 900
            assert metadata.width == 1920
            assert metadata.height == 1080
            assert metadata.duration == 30.0  # 900 frames / 30 fps
            
        finally:
            test_video.unlink()
    
    def test_validate_video_format(self):
        """Test video format validation."""
        from gemma_3n.fire_detection.config import VideoProcessingConfig
        
        config = VideoProcessingConfig()
        processor = VideoProcessor(config)
        
        # Test supported format
        video_path = Path("test.mp4")
        assert not processor.validate_video(video_path)  # File doesn't exist
        
        # Test unsupported format
        unsupported_path = Path("test.txt")
        with pytest.raises(ValueError, match="Unsupported video format"):
            processor.get_video_metadata(unsupported_path)


class TestFrameData:
    """Test frame data model."""
    
    def test_frame_data_creation(self):
        """Test frame data creation."""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        frame_data = FrameData(
            frame_number=10,
            timestamp=5.0,
            image=image,
            metadata={"video_fps": 30.0}
        )
        
        assert frame_data.frame_number == 10
        assert frame_data.timestamp == 5.0
        assert frame_data.image.shape == (480, 640, 3)
        assert frame_data.metadata["video_fps"] == 30.0


class TestGemmaE4BInterface:
    """Test Gemma 3N E4B model interface."""
    
    def test_model_interface_initialization(self):
        """Test model interface initialization."""
        from gemma_3n.fire_detection.models.gemma_e4b import Gemma3NE4BInterface
        
        config = Gemma3NE4BConfig()
        interface = Gemma3NE4BInterface(config, device="cpu")
        
        assert interface.config == config
        assert interface.device == "cpu"
        assert not interface._model_loaded
    
    def test_device_selection(self):
        """Test device selection logic."""
        from gemma_3n.fire_detection.models.gemma_e4b import Gemma3NE4BInterface
        
        config = Gemma3NE4BConfig()
        interface = Gemma3NE4BInterface(config, device="auto")
        
        device = interface._get_device("auto")
        assert device in ["cpu", "cuda", "mps"]
    
    def test_parse_detection_response(self):
        """Test response parsing."""
        from gemma_3n.fire_detection.models.gemma_e4b import Gemma3NE4BInterface
        
        config = Gemma3NE4BConfig()
        interface = Gemma3NE4BInterface(config, device="cpu")
        
        # Test JSON response
        json_response = '{"fire_detected": true, "confidence": 85}'
        result = interface._parse_detection_response(json_response)
        
        assert result['fire_detected'] is True
        assert result['confidence'] == 0.85
        
        # Test fallback parsing
        text_response = "Fire detected: yes\nConfidence: 90%"
        result = interface._parse_detection_response(text_response)
        
        assert result['fire_detected'] is True
        assert result['confidence'] == 0.9


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functionality."""
    
    async def test_async_frame_processing(self):
        """Test async frame processing."""
        # Mock async processing
        async def mock_extract_frames():
            for i in range(3):
                yield FrameData(
                    frame_number=i,
                    timestamp=float(i),
                    image=np.zeros((100, 100, 3), dtype=np.uint8),
                    metadata={}
                )
        
        # Test async iteration
        frames = []
        async for frame in mock_extract_frames():
            frames.append(frame)
        
        assert len(frames) == 3
        assert frames[0].frame_number == 0
        assert frames[2].frame_number == 2


if __name__ == "__main__":
    pytest.main([__file__])