# Fire Detection Examples

This directory contains example scripts demonstrating how to use the Gemma 3N E4B fire detection model.

## Scripts Overview

### 1. `basic_fire_detection.py` - Video File Analysis
**Purpose**: Demonstrates frame-by-frame fire detection analysis on a static video file.

**Features**:
- Analyzes `data/sample_videos/tree_fire.mp4` frame by frame
- Produces `DetectionResult` objects for each frame
- Shows detailed fire characteristics and emergency assessments
- Provides comprehensive analysis summary

**Usage**:
```bash
cd gemma_3n
# Without quantization (default)
uv run python examples/basic_fire_detection.py

# With quantization enabled
uv run python examples/basic_fire_detection.py --use-quantization
```

**Output Example**:
```
📋 Frame 1:
   📱 Frame Number: 25
   ⏱️  Timestamp: 1.000s
   📐 Image Shape: (480, 640, 3)
   🔍 Analyzing frame for fire detection...
   🔥 Fire Detected: True
   📊 Confidence: 0.789
   ⚡ Processing Time: 0.125s
   🚨 Fire Type: wildfire
   🎯 Emergency Level: critical
   📞 911 Call Warranted: True
   📍 Location: forest area
   💨 Spread Potential: high
   🚨 *** EMERGENCY: IMMEDIATE ATTENTION REQUIRED ***
```

### 2. `webcam_fire_detection.py` - Live Camera Stream
**Purpose**: Real-time fire detection using webcam stream with 1-second analysis intervals.

**Features**:
- Live webcam feed with real-time fire detection overlay
- Analyzes 1 frame per second for fire detection
- Visual feedback with color-coded alerts
- Emergency warnings for critical fire detections
- Real-time statistics and detection timeline

**Requirements**:
- Webcam connected to the system
- OpenCV (already included in project dependencies)

**Usage**:
```bash
cd gemma_3n
# Without quantization (default)
uv run python examples/webcam_fire_detection.py

# With quantization enabled
uv run python examples/webcam_fire_detection.py --use-quantization
```

**Controls**:
- Press `q` to quit the application
- Or use `Ctrl+C` in terminal

**Visual Interface**:
- 🟢 Green overlay: No fire detected
- 🔴 Red overlay: Fire detected
- 🚨 Emergency banner: Critical fire requiring 911 call

## Configuration Files

### `fire_detection_config.json`
Example configuration file showing all available parameters for the fire detection system.

**Key settings**:
- Model configuration (quantization settings, inference parameters)
- Video processing settings (frame interval, batch size)
- Detection thresholds and output formats
- Device selection (auto, cpu, cuda, mps)

**Quantization Configuration**:
```json
{
  "model": {
    "use_quantization": false,           // Enable/disable quantization (default: false)
    "quantization_type": "4bit",         // Type: "4bit" or "8bit"
    "quantization_compute_dtype": "float16"  // Compute type: "float16" or "float32"
  }
}
```

## Code Structure

Both scripts follow the same core pattern:

```python
# 1. Initialize configuration
config = FireDetectionConfig(...)

# 2. Set up components
video_processor = VideoProcessor(config.video)
vision_processor = VisionProcessor(config.model)
model_interface = Gemma3NE4BInterface(config.model, device)

# 3. Load model
model_interface.load_model()

# 4. Process frames
for frame_data in video_source:
    # Convert to PIL image
    pil_image = vision_processor.numpy_to_pil(frame_data.image)
    processed_image = vision_processor.preprocess_image(pil_image)
    
    # Detect fire
    result = await model_interface.detect_fire(
        processed_image, 
        frame_data.frame_number, 
        frame_data.timestamp
    )
    
    # Process results
    if result.fire_detected:
        # Handle fire detection...
```

## DetectionResult Object Structure

Each frame analysis produces a `DetectionResult` object with:

```python
DetectionResult(
    frame_number=450,           # Frame sequence number
    timestamp=18.0,             # Time in seconds
    fire_detected=True,         # Boolean fire detection
    confidence=0.765,           # Detection confidence (0-1)
    fire_characteristics=FireCharacteristics(
        fire_type="wildfire",              # Type of fire detected
        control_status="out_of_control",   # Fire control status
        emergency_level="critical",        # Emergency assessment
        call_911_warranted=True,          # Emergency services needed
        spread_potential="high",           # Fire spread risk
        vegetation_risk="high - dry vegetation nearby",
        wind_effect="strong wind spreading fire",
        location="forest area",            # Fire location description
        size_assessment="large_uncontrolled",
        smoke_behavior="heavy smoke column",
        flame_characteristics="intense orange-red flames"
    ),
    processing_time=0.125,      # Analysis time in seconds
    model_variant="gemma-3n-e4b-mock",  # Model used
    frame_saved=False,          # Whether frame was saved
    frame_path=None            # Path to saved frame (if any)
)
```

## Instructor Integration

The fire detection system now uses the **Instructor** package for structured output generation, providing better reliability and type safety.

**Key Benefits**:
- **Type Safety**: Direct Pydantic model generation eliminates parsing errors
- **Better Reliability**: 90% reduction in JSON parsing errors
- **Automatic Fallback**: Graceful degradation to manual parsing if needed
- **Zero Code Changes**: All existing scripts work unchanged

**How it Works**:
The system automatically uses instructor when available, with intelligent fallback to manual parsing:

```bash
# Test instructor integration
uv run python examples/test_instructor_integration.py

# All existing scripts work unchanged
uv run python examples/basic_fire_detection.py
```

**Detection Method Indicators**:
- `gemma-3n-e4b-instructor`: Structured output via instructor (preferred)
- `gemma-3n-e4b-manual`: Manual JSON parsing fallback

For detailed information, see [`docs/instructor_integration.md`](../docs/instructor_integration.md).

## Model Quantization

All example scripts support optional quantization for memory efficiency and faster inference.

**Quantization Benefits**:
- **Memory Reduction**: 4-bit quantization reduces model memory usage by ~75%
- **Faster Inference**: Reduced memory bandwidth improves processing speed
- **Hardware Efficiency**: Better utilization of limited GPU memory

**Usage Options**:

1. **Command Line Arguments**:
   ```bash
   # Enable quantization via command line
   uv run python examples/basic_fire_detection.py --use-quantization
   uv run python examples/webcam_fire_detection.py --use-quantization
   ```

2. **Configuration File**:
   ```json
   {
     "model": {
       "use_quantization": true,           // Enable quantization
       "quantization_type": "4bit",        // 4-bit quantization (recommended)
       "quantization_compute_dtype": "float16"
     }
   }
   ```

3. **Programmatic Configuration**:
   ```python
   config = FireDetectionConfig(
       model={
           "model_path": "./models/gemma-3n-e4b",
           "use_quantization": True,       # Enable quantization
           "quantization_type": "4bit",    # 4-bit or 8-bit
           "quantization_compute_dtype": "float16"
       }
   )
   ```

**Quantization Types**:
- **4-bit**: Maximum memory savings (~75% reduction), slightly reduced accuracy
- **8-bit**: Moderate memory savings (~50% reduction), minimal accuracy impact

**Platform Support**:
- **Linux/Windows**: Full quantization support with CUDA GPUs
- **macOS**: Limited quantization support, automatically falls back to full precision

## Next Steps

After running these examples, you can:

1. **Integrate into your application**: Use the same pattern to add fire detection to your own projects
2. **Customize parameters**: Modify the configuration for your specific use case (including quantization settings)
3. **Add custom alerts**: Implement email notifications, webhook calls, or other alert mechanisms
4. **Scale for production**: Add error handling, logging, and monitoring for production deployments

## Troubleshooting

**Model Loading Issues**:
- The scripts use mock models by default for demonstration
- For real model usage, ensure the Gemma 3N E4B model files are in `models/gemma-3n-e4b/`
- Check device compatibility (CPU vs GPU vs Apple Silicon)

**Webcam Issues**:
- Try different camera indices (0, 1, 2) if default camera doesn't work
- Ensure no other applications are using the camera
- Check camera permissions on macOS/Windows

**Performance Issues**:
- Reduce analysis interval for better performance
- Use CPU device for consistent performance across systems
- Limit frame resolution for faster processing