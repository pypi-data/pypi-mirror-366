"""Main fire detection pipeline implementation."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import cv2
from PIL import Image
from rich.console import Console
from rich.progress import Progress, TaskID

from gemma_3n.fire_detection.config import FireDetectionConfig
from gemma_3n.fire_detection.models.gemma_e4b import Gemma3NE4BInterface
from gemma_3n.fire_detection.models.results import (
    AnalysisSummary,
    DetectionResult,
    VideoAnalysisResult,
)
from gemma_3n.fire_detection.processing.frame_extractor import FrameExtractor
from gemma_3n.fire_detection.processing.video import FrameData, VideoProcessor
from gemma_3n.fire_detection.vision.processor import VisionProcessor

logger = logging.getLogger(__name__)


class FireDetector:
    """Main fire detection system using Gemma 3N E4B model."""
    
    def __init__(self, config: FireDetectionConfig, console: Optional[Console] = None):
        """Initialize fire detector.
        
        Args:
            config: Fire detection configuration
            console: Rich console for output (optional)
        """
        self.config = config
        self.console = console or Console()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.video_processor = VideoProcessor(config.video)
        self.frame_extractor = FrameExtractor(config.video)
        self.vision_processor = VisionProcessor(config.model)
        self.model_interface = Gemma3NE4BInterface(config.model, config.get_device(), detection_config=config.detection)
        
        # Results storage
        self.current_results: List[DetectionResult] = []
    
    async def process_video(self, video_path: Path) -> VideoAnalysisResult:
        """Process a video file for fire detection.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Complete video analysis results
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not self.video_processor.validate_video(video_path):
            raise ValueError(f"Invalid video file: {video_path}")
        
        self.logger.info(f"Starting fire detection analysis for {video_path.name}")
        analysis_start = datetime.now()
        
        # Get video metadata
        metadata = self.video_processor.get_video_metadata(video_path)
        
        # Calculate extraction statistics
        extraction_stats = self.frame_extractor.calculate_extraction_stats(video_path)
        
        self.console.print(f"[bold green]Processing video:[/bold green] {video_path.name}")
        self.console.print(f"Duration: {metadata.duration:.1f}s, FPS: {metadata.fps:.1f}")
        self.console.print(f"Frames to process: {extraction_stats['frames_to_extract']}")
        
        # Initialize results
        results: List[DetectionResult] = []
        
        # Process frames with progress tracking
        with Progress(console=self.console) as progress:
            task = progress.add_task(
                "[green]Detecting fire...", 
                total=extraction_stats['frames_to_extract']
            )
            
            if self.config.video.async_processing:
                results = await self._process_frames_async(video_path, progress, task)
            else:
                results = await self._process_frames_sync(video_path, progress, task)
        
        # Create analysis summary
        summary = AnalysisSummary.from_results(results)
        
        # Create final result
        analysis_result = VideoAnalysisResult(
            video_path=video_path,
            video_duration=metadata.duration,
            video_fps=metadata.fps,
            detections=results,
            summary=summary,
            config_snapshot=self.config.model_dump(),
            analysis_started=analysis_start,
            analysis_completed=datetime.now()
        )
        
        # Save results
        await self._save_results(analysis_result)
        
        # Print summary
        self._print_summary(analysis_result)
        
        return analysis_result
    
    async def _process_frames_async(
        self, 
        video_path: Path, 
        progress: Progress, 
        task: TaskID
    ) -> List[DetectionResult]:
        """Process frames asynchronously.
        
        Args:
            video_path: Path to video file
            progress: Progress tracker
            task: Progress task ID
            
        Returns:
            List of detection results
        """
        results: List[DetectionResult] = []
        
        # Process in batches if configured
        if self.config.video.batch_size > 1:
            async for batch in self.frame_extractor.extract_batched_frames(video_path):
                batch_results = await self._process_frame_batch(batch)
                results.extend(batch_results)
                progress.update(task, advance=len(batch))
        else:
            async for frame_data in self.video_processor.extract_frames(video_path):
                result = await self._process_single_frame(frame_data)
                results.append(result)
                progress.update(task, advance=1)
        
        return results
    
    async def _process_frames_sync(
        self, 
        video_path: Path, 
        progress: Progress, 
        task: TaskID
    ) -> List[DetectionResult]:
        """Process frames synchronously.
        
        Args:
            video_path: Path to video file
            progress: Progress tracker
            task: Progress task ID
            
        Returns:
            List of detection results
        """
        results: List[DetectionResult] = []
        
        async for frame_data in self.video_processor.extract_frames(video_path):
            result = await self._process_single_frame(frame_data)
            results.append(result)
            progress.update(task, advance=1)
        
        return results
    
    async def _process_frame_batch(self, batch: List[FrameData]) -> List[DetectionResult]:
        """Process a batch of frames.
        
        Args:
            batch: List of frame data
            
        Returns:
            List of detection results
        """
        tasks = [self._process_single_frame(frame_data) for frame_data in batch]
        return await asyncio.gather(*tasks)
    
    async def _process_single_frame(self, frame_data: FrameData) -> DetectionResult:
        """Process a single frame for fire detection.
        
        Args:
            frame_data: Frame data to process
            
        Returns:
            Detection result
        """
        try:
            # Convert frame to PIL Image
            image = self.vision_processor.numpy_to_pil(frame_data.image)
            
            # Preprocess image if needed
            processed_image = self.vision_processor.preprocess_image(image)
            
            # Run fire detection
            result = await self.model_interface.detect_fire(
                processed_image,
                frame_data.frame_number,
                frame_data.timestamp
            )
            
            # Save frame if fire detected and configured to do so
            if result.fire_detected and self.config.detection.save_positive_frames:
                frame_path = await self._save_frame(frame_data, result, "fire_detected")
                result.frame_saved = True
                result.frame_path = frame_path
            elif self.config.detection.save_all_frames:
                frame_path = await self._save_frame(frame_data, result, "all_frames")
                result.frame_saved = True
                result.frame_path = frame_path
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing frame {frame_data.frame_number}: {e}")
            
            return DetectionResult(
                frame_number=frame_data.frame_number,
                timestamp=frame_data.timestamp,
                fire_detected=False,
                confidence=0.0,
                detection_details={'error': str(e)},
                processing_time=0.0,
                model_variant="gemma-3n-e4b"
            )
    
    async def _save_frame(
        self, 
        frame_data: FrameData, 
        result: DetectionResult,
        category: str
    ) -> Path:
        """Save frame image to disk.
        
        Args:
            frame_data: Frame data
            result: Detection result
            category: Frame category for organization
            
        Returns:
            Path to saved frame
        """
        # Create category directory
        frames_dir = self.config.output.output_dir / "frames" / category
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        confidence_str = f"{result.confidence:.3f}" if result.fire_detected else "negative"
        filename = (
            f"frame_{result.frame_number:06d}_"
            f"t{result.timestamp:.3f}_"
            f"conf{confidence_str}.{self.config.detection.frame_format}"
        )
        
        frame_path = frames_dir / filename
        
        # Convert and save frame
        image = Image.fromarray(cv2.cvtColor(frame_data.image, cv2.COLOR_BGR2RGB))
        
        if self.config.detection.frame_format == "jpg":
            image.save(frame_path, format="JPEG", quality=85)
        else:
            image.save(frame_path, format="PNG")
        
        return frame_path
    
    async def _save_results(self, analysis_result: VideoAnalysisResult) -> None:
        """Save analysis results to disk.
        
        Args:
            analysis_result: Analysis results to save
        """
        output_dir = self.config.output.output_dir
        base_filename = self.config.output.results_filename
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"{base_filename}_{timestamp}"
        
        # Save based on configured format
        if self.config.output.output_format in ["json", "both"]:
            json_path = output_dir / f"{filename_base}.json"
            analysis_result.save_json(json_path)
            self.logger.info(f"Results saved to: {json_path}")
        
        if self.config.output.output_format in ["csv", "both"]:
            csv_path = output_dir / f"{filename_base}.csv"
            analysis_result.save_csv(csv_path)
            self.logger.info(f"Results saved to: {csv_path}")
    
    def _print_summary(self, analysis_result: VideoAnalysisResult) -> None:
        """Print analysis summary to console.
        
        Args:
            analysis_result: Analysis results
        """
        summary = analysis_result.summary
        
        self.console.print("\n[bold blue]Fire Detection Analysis Complete[/bold blue]")
        self.console.print(f"Video: {analysis_result.video_path.name}")
        self.console.print(f"Duration: {analysis_result.video_duration:.1f} seconds")
        
        self.console.print(f"\n[bold]Processing Statistics:[/bold]")
        self.console.print(f"  Frames processed: {summary.total_frames_processed}")
        self.console.print(f"  Processing time: {summary.processing_duration:.1f}s")
        self.console.print(f"  Average per frame: {summary.average_processing_time:.3f}s")
        
        self.console.print(f"\n[bold]Detection Results:[/bold]")
        self.console.print(f"  Fire detections: {summary.fire_detections}")
        self.console.print(f"  Detection rate: {summary.detection_rate:.1%}")
        self.console.print(f"  Average confidence: {summary.average_confidence:.1%}")
        self.console.print(f"  Max confidence: {summary.max_confidence:.1%}")
        
        if summary.first_detection_time is not None:
            self.console.print(f"  First detection: {summary.first_detection_time:.1f}s")
            self.console.print(f"  Last detection: {summary.last_detection_time:.1f}s")
            
            if summary.detection_duration:
                self.console.print(f"  Detection span: {summary.detection_duration:.1f}s")
        
        if summary.frames_saved > 0:
            self.console.print(f"  Frames saved: {summary.frames_saved}")
        
        # Show fire timeline if available
        timeline = analysis_result.get_fire_timeline()
        if timeline:
            self.console.print(f"\n[bold]Fire Timeline:[/bold]")
            for i, (start, end) in enumerate(timeline, 1):
                duration = end - start
                self.console.print(f"  Period {i}: {start:.1f}s - {end:.1f}s ({duration:.1f}s)")
    
    def process_video_sync(self, video_path: Path) -> VideoAnalysisResult:
        """Synchronous wrapper for video processing.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Video analysis results
        """
        return asyncio.run(self.process_video(video_path))
    
    def process_video_stream(self, video_path: Path) -> VideoAnalysisResult:
        """Process video in streaming mode with real-time analysis.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Video analysis results
        """
        return asyncio.run(self._process_video_stream_async(video_path))
    
    async def _process_video_stream_async(self, video_path: Path) -> VideoAnalysisResult:
        """Async implementation of streaming video processing.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Video analysis results
        """
        self.logger.info(f"Starting streaming analysis of {video_path}")
        
        # Initialize video capture
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            self.console.print(f"[blue]📹 Video: {video_path.name}[/blue]")
            self.console.print(f"[blue]⏱️  Duration: {duration:.1f}s, FPS: {fps:.1f}, Total frames: {total_frames}[/blue]")
            self.console.print(f"[blue]🔥 Starting real-time fire detection...[/blue]\n")
            
            # Calculate frame interval in frame numbers
            frame_interval = int(fps * self.config.video.frame_interval)
            if frame_interval == 0:
                frame_interval = 1
            
            results: List[DetectionResult] = []
            frame_count = 0
            processed_count = 0
            
            # Progress tracking
            with self.console.status("[bold green]Processing frames in real-time...") as status:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Process frame if it's at the interval
                    if frame_count % frame_interval == 0:
                        timestamp = frame_count / fps if fps > 0 else processed_count * self.config.video.frame_interval
                        
                        # Convert BGR to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Create frame data
                        frame_data = FrameData(
                            image=frame_rgb,
                            frame_number=frame_count,
                            timestamp=timestamp,
                            metadata={
                                "original_frame": frame_count,
                                "fps": fps,
                                "streaming": True,
                                "video_duration": duration
                            }
                        )
                        
                        # Process frame in real-time
                        status.update(f"[bold green]Processing frame {processed_count + 1} at {timestamp:.1f}s...")
                        result = await self._process_single_frame(frame_data)
                        results.append(result)
                        processed_count += 1
                        
                        # Show immediate results for fire detections
                        if result.fire_detected:
                            fire_chars = result.fire_characteristics
                            emergency_indicator = "🚨 EMERGENCY" if fire_chars and fire_chars.call_911_warranted else "🔥 FIRE"
                            self.console.print(
                                f"[bold red]{emergency_indicator}[/bold red] "
                                f"Frame {frame_count} ({timestamp:.1f}s): "
                                f"Confidence {result.confidence:.1%}"
                            )
                            if fire_chars and fire_chars.call_911_warranted:
                                self.console.print(
                                    f"[bold red]⚠️  911 CALL WARRANTED - {fire_chars.emergency_level.upper()} LEVEL[/bold red]"
                                )
                        elif self.config.verbose:
                            self.console.print(
                                f"[dim]Frame {frame_count} ({timestamp:.1f}s): No fire detected[/dim]"
                            )
                        
                        # Apply max frames limit
                        if self.config.video.max_frames and processed_count >= self.config.video.max_frames:
                            self.console.print(f"[yellow]Reached maximum frame limit ({self.config.video.max_frames})[/yellow]")
                            break
                    
                    frame_count += 1
            
            # Create summary
            fire_detections = sum(1 for r in results if r.fire_detected)
            emergency_calls = sum(1 for r in results if r.fire_characteristics and r.fire_characteristics.call_911_warranted)
            
            # Calculate timing and confidence metrics
            total_processing_time = sum(r.processing_time for r in results)
            avg_processing_time = total_processing_time / len(results) if results else 0.0
            avg_confidence = sum(r.confidence for r in results) / len(results) if results else 0.0
            max_confidence = max((r.confidence for r in results), default=0.0)
            detection_rate = fire_detections / len(results) if results else 0.0
            
            # Find first and last detection times
            fire_results = [r for r in results if r.fire_detected]
            first_detection = min((r.timestamp for r in fire_results), default=None)
            last_detection = max((r.timestamp for r in fire_results), default=None)
            detection_duration = (last_detection - first_detection) if first_detection and last_detection else None
            
            summary = AnalysisSummary(
                total_frames_processed=processed_count,
                processing_duration=total_processing_time,
                average_processing_time=avg_processing_time,
                fire_detections=fire_detections,
                detection_rate=detection_rate,
                average_confidence=avg_confidence,
                max_confidence=max_confidence,
                first_detection_time=first_detection,
                last_detection_time=last_detection,
                detection_duration=detection_duration,
                frames_saved=sum(1 for r in results if r.frame_saved)
            )
            
            self.console.print(f"\n[bold green]✅ Streaming analysis complete![/bold green]")
            self.console.print(f"[green]Processed {processed_count} frames in real-time[/green]")
            if fire_detections > 0:
                self.console.print(f"[bold red]🔥 {fire_detections} fire detections found![/bold red]")
                if emergency_calls > 0:
                    self.console.print(f"[bold red]🚨 {emergency_calls} frames warrant 911 calls![/bold red]")
            
            # Create and save results
            analysis_result = VideoAnalysisResult(
                video_path=video_path,
                video_duration=duration,
                video_fps=fps,
                detections=results,
                summary=summary,
                config_snapshot=self.config.model_dump(),
                analysis_completed=datetime.now()
            )
            
            # Save results
            await self._save_results(analysis_result)
            
            return analysis_result
            
        finally:
            cap.release()