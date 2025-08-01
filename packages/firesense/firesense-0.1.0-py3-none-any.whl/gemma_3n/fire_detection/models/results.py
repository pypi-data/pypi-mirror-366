"""Data models for detection results."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box for detected objects."""
    
    x: float = Field(ge=0.0, le=1.0, description="X coordinate (normalized)")
    y: float = Field(ge=0.0, le=1.0, description="Y coordinate (normalized)")
    width: float = Field(ge=0.0, le=1.0, description="Width (normalized)")
    height: float = Field(ge=0.0, le=1.0, description="Height (normalized)")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence")


class FireCharacteristics(BaseModel):
    """Characteristics of detected fire with focus on wildfire and emergency assessment."""
    
    # Primary fire classification
    fire_type: str = Field(description="Type of fire: controlled, uncontrolled, wildfire, or no_fire")
    control_status: str = Field(description="Fire control status: contained, spreading, out_of_control")
    
    # Emergency assessment
    emergency_level: str = Field(description="Emergency level: none, monitor, alert, critical")
    call_911_warranted: bool = Field(default=False, description="Whether emergency services should be contacted")
    
    # Wildfire risk factors
    spread_potential: str = Field(description="Potential for fire spread: low, moderate, high, extreme")
    vegetation_risk: str = Field(description="Risk from surrounding vegetation/fuel")
    wind_effect: str = Field(description="Observed wind effect on fire behavior")
    
    # Fire characteristics
    location: str = Field(description="Fire location in frame")
    size_assessment: str = Field(description="Fire size: small_controlled, medium_spreading, large_uncontrolled")
    smoke_behavior: str = Field(description="Smoke pattern indicating fire behavior")
    flame_characteristics: str = Field(description="Flame color and behavior indicating fire type")


class DetectionResult(BaseModel):
    """Result of fire detection for a single frame."""
    
    frame_number: int = Field(description="Frame number in video")
    timestamp: float = Field(description="Timestamp in seconds")
    fire_detected: bool = Field(description="Whether fire was detected")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence")
    
    # Enhanced fire detection probabilities
    fire_presence_probability: float = Field(ge=0.0, le=1.0, default=0.0, description="Probability of any fire present")
    uncontrolled_fire_probability: float = Field(ge=0.0, le=1.0, default=0.0, description="Probability fire is uncontrolled")
    
    # Optional detailed information
    bounding_boxes: Optional[List[BoundingBox]] = Field(default=None)
    fire_characteristics: Optional[FireCharacteristics] = Field(default=None)
    detection_details: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing metadata
    processing_time: float = Field(description="Processing time in seconds")
    model_variant: str = Field(default="gemma-3n-e4b", description="Model used")
    
    # Frame storage
    frame_saved: bool = Field(default=False, description="Whether frame was saved")
    frame_path: Optional[Path] = Field(default=None, description="Path to saved frame")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class AnalysisSummary(BaseModel):
    """Summary of video analysis results."""
    
    # Processing statistics
    total_frames_processed: int = Field(description="Total frames processed")
    processing_duration: float = Field(description="Total processing time")
    average_processing_time: float = Field(description="Average time per frame")
    
    # Detection statistics
    fire_detections: int = Field(description="Number of fire detections")
    detection_rate: float = Field(ge=0.0, le=1.0, description="Percentage of frames with fire")
    average_confidence: float = Field(ge=0.0, le=1.0, description="Average confidence score")
    max_confidence: float = Field(ge=0.0, le=1.0, description="Maximum confidence score")
    
    # Temporal analysis
    first_detection_time: Optional[float] = Field(default=None, description="First detection timestamp")
    last_detection_time: Optional[float] = Field(default=None, description="Last detection timestamp")
    detection_duration: Optional[float] = Field(default=None, description="Duration of detections")
    
    # Quality metrics
    frames_saved: int = Field(default=0, description="Number of frames saved")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def from_results(cls, results: List[DetectionResult]) -> "AnalysisSummary":
        """Create summary from detection results.
        
        Args:
            results: List of detection results
            
        Returns:
            Analysis summary
        """
        if not results:
            return cls(
                total_frames_processed=0,
                processing_duration=0.0,
                average_processing_time=0.0,
                fire_detections=0,
                detection_rate=0.0,
                average_confidence=0.0,
                max_confidence=0.0
            )
        
        fire_results = [r for r in results if r.fire_detected]
        
        total_processing_time = sum(r.processing_time for r in results)
        avg_processing_time = total_processing_time / len(results)
        
        confidences = [r.confidence for r in fire_results] if fire_results else [0.0]
        avg_confidence = sum(confidences) / len(confidences)
        max_confidence = max(confidences)
        
        first_detection = min(r.timestamp for r in fire_results) if fire_results else None
        last_detection = max(r.timestamp for r in fire_results) if fire_results else None
        detection_duration = (
            last_detection - first_detection if first_detection and last_detection else None
        )
        
        return cls(
            total_frames_processed=len(results),
            processing_duration=total_processing_time,
            average_processing_time=avg_processing_time,
            fire_detections=len(fire_results),
            detection_rate=len(fire_results) / len(results),
            average_confidence=avg_confidence,
            max_confidence=max_confidence,
            first_detection_time=first_detection,
            last_detection_time=last_detection,
            detection_duration=detection_duration,
            frames_saved=sum(1 for r in results if r.frame_saved)
        )


class VideoAnalysisResult(BaseModel):
    """Complete analysis result for a video."""
    
    # Video information
    video_path: Path = Field(description="Path to analyzed video")
    video_duration: float = Field(description="Video duration in seconds")
    video_fps: float = Field(description="Video frames per second")
    
    # Detection results
    detections: List[DetectionResult] = Field(description="Individual detection results")
    summary: AnalysisSummary = Field(description="Analysis summary")
    
    # Configuration used
    config_snapshot: Dict[str, Any] = Field(description="Configuration used for analysis")
    
    # Timestamps
    analysis_started: datetime = Field(default_factory=datetime.now)
    analysis_completed: Optional[datetime] = Field(default=None)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    def save_json(self, output_path: Path) -> None:
        """Save results to JSON file.
        
        Args:
            output_path: Path to save JSON file
        """
        data = self.model_dump()
        
        # Convert Path objects to strings for JSON serialization
        def convert_paths(obj):
            if isinstance(obj, Path):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(item) for item in obj]
            return obj
        
        data = convert_paths(data)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_csv(self, output_path: Path) -> None:
        """Save detection results to CSV file with comprehensive FireCharacteristics.
        
        Args:
            output_path: Path to save CSV file
        """
        import csv
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Enhanced header with wildfire-focused FireCharacteristics fields
            writer.writerow([
                'frame_number', 'timestamp', 'fire_detected', 'confidence',
                'fire_type', 'control_status', 'emergency_level', 'call_911_warranted',
                'spread_potential', 'vegetation_risk', 'wind_effect',
                'location', 'size_assessment', 'smoke_behavior', 'flame_characteristics',
                'processing_time', 'model_variant', 'frame_saved', 'frame_path'
            ])
            
            # Data rows with wildfire-focused fire characteristics
            for detection in self.detections:
                # Extract fire characteristics (handle None case)
                if detection.fire_characteristics:
                    fire_type = detection.fire_characteristics.fire_type
                    control_status = detection.fire_characteristics.control_status
                    emergency_level = detection.fire_characteristics.emergency_level
                    call_911_warranted = detection.fire_characteristics.call_911_warranted
                    spread_potential = detection.fire_characteristics.spread_potential
                    vegetation_risk = detection.fire_characteristics.vegetation_risk
                    wind_effect = detection.fire_characteristics.wind_effect
                    location = detection.fire_characteristics.location
                    size_assessment = detection.fire_characteristics.size_assessment
                    smoke_behavior = detection.fire_characteristics.smoke_behavior
                    flame_characteristics = detection.fire_characteristics.flame_characteristics
                else:
                    fire_type = "N/A"
                    control_status = "N/A"
                    emergency_level = "N/A"
                    call_911_warranted = False
                    spread_potential = "N/A"
                    vegetation_risk = "N/A"
                    wind_effect = "N/A"
                    location = "N/A"
                    size_assessment = "N/A"
                    smoke_behavior = "N/A"
                    flame_characteristics = "N/A"
                
                writer.writerow([
                    detection.frame_number,
                    round(detection.timestamp, 3),
                    detection.fire_detected,
                    round(detection.confidence, 4),
                    fire_type,
                    control_status,
                    emergency_level,
                    call_911_warranted,
                    spread_potential,
                    vegetation_risk,
                    wind_effect,
                    location,
                    size_assessment,
                    smoke_behavior,
                    flame_characteristics,
                    round(detection.processing_time, 4),
                    detection.model_variant,
                    detection.frame_saved,
                    str(detection.frame_path) if detection.frame_path else "N/A"
                ])
    
    def get_fire_timeline(self) -> List[tuple[float, float]]:
        """Get timeline of fire detections.
        
        Returns:
            List of (start_time, end_time) tuples for fire periods
        """
        fire_frames = [d for d in self.detections if d.fire_detected]
        if not fire_frames:
            return []
        
        # Group consecutive detections
        timeline = []
        current_start = fire_frames[0].timestamp
        current_end = fire_frames[0].timestamp
        
        for i in range(1, len(fire_frames)):
            frame = fire_frames[i]
            
            # Check if this frame is consecutive (within reasonable gap)
            if frame.timestamp - current_end <= (2 * self.config_snapshot.get('frame_interval', 2.0)):
                current_end = frame.timestamp
            else:
                # Gap found, close current period and start new one
                timeline.append((current_start, current_end))
                current_start = frame.timestamp
                current_end = frame.timestamp
        
        # Add the last period
        timeline.append((current_start, current_end))
        
        return timeline