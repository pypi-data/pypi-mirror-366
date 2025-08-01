"""Video processing utilities for fire detection."""

import asyncio
import logging
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional

import cv2
import numpy as np
from pydantic import BaseModel

from gemma_3n.fire_detection.config import VideoProcessingConfig

logger = logging.getLogger(__name__)


class FrameData(BaseModel):
    """Data structure for video frame information."""
    
    frame_number: int
    timestamp: float  # seconds from start
    image: np.ndarray
    metadata: Dict[str, Any]
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class VideoMetadata(BaseModel):
    """Video file metadata."""
    
    path: Path
    duration: float  # seconds
    fps: float
    width: int
    height: int
    total_frames: int
    codec: str
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class VideoProcessor:
    """Process video files for frame extraction."""
    
    def __init__(self, config: VideoProcessingConfig):
        """Initialize video processor.
        
        Args:
            config: Video processing configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_video_metadata(self, video_path: Path) -> VideoMetadata:
        """Extract metadata from video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Video metadata
            
        Raises:
            ValueError: If video cannot be opened
        """
        if not video_path.exists():
            raise ValueError(f"Video file not found: {video_path}")
        
        if video_path.suffix.lower() not in self.config.supported_formats:
            raise ValueError(f"Unsupported video format: {video_path.suffix}")
        
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Get codec information
            fourcc = cap.get(cv2.CAP_PROP_FOURCC)
            codec = "".join([chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
            
            return VideoMetadata(
                path=video_path,
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                total_frames=total_frames,
                codec=codec
            )
        finally:
            cap.release()
    
    async def extract_frames(self, video_path: Path) -> AsyncIterator[FrameData]:
        """Extract frames from video at specified intervals.
        
        Args:
            video_path: Path to video file
            
        Yields:
            FrameData: Frame data with metadata
            
        Raises:
            ValueError: If video cannot be processed
        """
        metadata = self.get_video_metadata(video_path)
        
        # Calculate frame extraction parameters
        frame_skip = int(self.config.frame_interval * metadata.fps)
        start_frame = int(self.config.start_time * metadata.fps)
        end_frame = (
            int(self.config.end_time * metadata.fps)
            if self.config.end_time
            else metadata.total_frames
        )
        
        if self.config.max_frames:
            max_possible_frames = (end_frame - start_frame) // frame_skip
            if max_possible_frames > self.config.max_frames:
                end_frame = start_frame + (self.config.max_frames * frame_skip)
        
        self.logger.info(
            f"Extracting frames from {video_path.name}: "
            f"start={start_frame}, end={end_frame}, skip={frame_skip}"
        )
        
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        try:
            current_frame = start_frame
            frame_count = 0
            
            # Set starting position
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            while current_frame < end_frame:
                ret, frame = cap.read()
                
                if not ret:
                    self.logger.warning(f"Failed to read frame {current_frame}")
                    break
                
                timestamp = current_frame / metadata.fps
                
                frame_data = FrameData(
                    frame_number=current_frame,
                    timestamp=timestamp,
                    image=frame.copy(),
                    metadata={
                        "video_path": str(video_path),
                        "frame_shape": frame.shape,
                        "extraction_interval": self.config.frame_interval,
                        "video_fps": metadata.fps,
                        "video_duration": metadata.duration
                    }
                )
                
                yield frame_data
                
                frame_count += 1
                current_frame += frame_skip
                
                # Skip to next target frame
                if current_frame < end_frame:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                
                # Allow other tasks to run
                if self.config.async_processing:
                    await asyncio.sleep(0)
            
            self.logger.info(f"Extracted {frame_count} frames from {video_path.name}")
            
        finally:
            cap.release()
    
    def extract_frames_sync(self, video_path: Path) -> list[FrameData]:
        """Synchronous version of frame extraction.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of frame data
        """
        async def _extract():
            frames = []
            async for frame_data in self.extract_frames(video_path):
                frames.append(frame_data)
            return frames
        
        return asyncio.run(_extract())
    
    def validate_video(self, video_path: Path) -> bool:
        """Validate if video file can be processed.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if video is valid
        """
        try:
            self.get_video_metadata(video_path)
            return True
        except Exception as e:
            self.logger.error(f"Video validation failed: {e}")
            return False