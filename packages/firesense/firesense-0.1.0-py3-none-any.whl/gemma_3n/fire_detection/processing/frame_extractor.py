"""Frame extraction utilities with batch processing support."""

import asyncio
import logging
from pathlib import Path
from typing import AsyncIterator, List

from gemma_3n.fire_detection.config import VideoProcessingConfig
from gemma_3n.fire_detection.processing.video import FrameData, VideoProcessor

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Advanced frame extraction with batch processing and optimization."""
    
    def __init__(self, config: VideoProcessingConfig):
        """Initialize frame extractor.
        
        Args:
            config: Video processing configuration
        """
        self.config = config
        self.video_processor = VideoProcessor(config)
        self.logger = logging.getLogger(__name__)
    
    async def extract_batched_frames(
        self, 
        video_path: Path
    ) -> AsyncIterator[List[FrameData]]:
        """Extract frames in batches for efficient processing.
        
        Args:
            video_path: Path to video file
            
        Yields:
            Batches of frame data
        """
        batch = []
        
        async for frame_data in self.video_processor.extract_frames(video_path):
            batch.append(frame_data)
            
            if len(batch) >= self.config.batch_size:
                yield batch
                batch = []
        
        # Yield remaining frames
        if batch:
            yield batch
    
    async def extract_frames_concurrent(
        self, 
        video_paths: List[Path]
    ) -> AsyncIterator[tuple[Path, FrameData]]:
        """Extract frames from multiple videos concurrently.
        
        Args:
            video_paths: List of video file paths
            
        Yields:
            Tuples of video path and frame data
        """
        async def _process_video(video_path: Path):
            async for frame_data in self.video_processor.extract_frames(video_path):
                yield (video_path, frame_data)
        
        # Create tasks for concurrent processing
        tasks = [_process_video(path) for path in video_paths[:self.config.max_workers]]
        
        # Process results as they come
        for task in asyncio.as_completed(tasks):
            async for result in await task:
                yield result
    
    def calculate_extraction_stats(self, video_path: Path) -> dict:
        """Calculate statistics for frame extraction.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with extraction statistics
        """
        metadata = self.video_processor.get_video_metadata(video_path)
        
        # Calculate extraction parameters
        frame_skip = int(self.config.frame_interval * metadata.fps)
        start_frame = int(self.config.start_time * metadata.fps)
        end_frame = (
            int(self.config.end_time * metadata.fps)
            if self.config.end_time
            else metadata.total_frames
        )
        
        total_extractable = (end_frame - start_frame) // frame_skip
        
        if self.config.max_frames:
            total_extractable = min(total_extractable, self.config.max_frames)
        
        estimated_time = total_extractable * 0.01  # Rough estimate
        
        return {
            "video_duration": metadata.duration,
            "total_frames": metadata.total_frames,
            "frames_to_extract": total_extractable,
            "extraction_interval": self.config.frame_interval,
            "estimated_processing_time": estimated_time,
            "video_fps": metadata.fps,
            "frame_skip": frame_skip,
            "start_frame": start_frame,
            "end_frame": end_frame
        }
    
    async def preview_extraction(self, video_path: Path, max_preview: int = 5) -> List[FrameData]:
        """Preview frame extraction for testing.
        
        Args:
            video_path: Path to video file
            max_preview: Maximum number of frames to preview
            
        Returns:
            List of preview frame data
        """
        preview_frames = []
        
        async for frame_data in self.video_processor.extract_frames(video_path):
            preview_frames.append(frame_data)
            
            if len(preview_frames) >= max_preview:
                break
        
        self.logger.info(f"Preview extracted {len(preview_frames)} frames")
        return preview_frames