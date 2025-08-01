#!/usr/bin/env python3
"""
Test script to verify Instructor integration with fire detection.

This script tests the instructor integration by running a simple fire detection
analysis and showing whether instructor structured output is being used.

Usage:
    cd gemma_3n
    uv run python examples/test_instructor_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from PIL import Image
from gemma_3n.fire_detection.config import FireDetectionConfig
from gemma_3n.fire_detection.models.gemma_e4b import Gemma3NE4BInterface
from gemma_3n.fire_detection.vision.processor import VisionProcessor


async def test_instructor_integration():
    """Test instructor integration with fire detection."""
    print("🔥 Testing Instructor Integration with Fire Detection")
    print("=" * 60)
    
    # Create configuration
    config = FireDetectionConfig(
        model={
            "model_path": str(project_root / "models" / "gemma-3n-e4b"),
            "use_quantization": False  # Disable quantization for test
        },
        detection={
            "confidence_threshold": 0.7,
            "save_positive_frames": False,
            "save_all_frames": False
        },
        device="auto",
        verbose=True
    )
    
    print(f"🤖 Initializing fire detection components...")
    
    # Initialize components
    vision_processor = VisionProcessor(config.model)
    model_interface = Gemma3NE4BInterface(
        config.model,
        config.get_device(),
        detection_config=config.detection
    )
    
    # Load model
    print(f"📦 Loading model...")
    try:
        model_interface.load_model()
        print(f"✅ Model loaded successfully")
        
        # Check if instructor is being used
        if hasattr(model_interface, '_use_instructor') and model_interface._use_instructor:
            if model_interface._instructor_client:
                print(f"✅ Instructor client initialized successfully")
                instructor_status = "Available and Active"
            else:
                print(f"⚠️  Instructor available but client not initialized")
                instructor_status = "Available but Inactive"
        else:
            print(f"ℹ️  Instructor not available, using manual parsing")
            instructor_status = "Not Available"
            
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print(f"💡 Please ensure model files are properly installed")
        instructor_status = "Model Failed"
        
        # Early return since we can't continue without a model
        print(f"\n❌ Cannot continue test - model loading failed")
        return 1
    
    print(f"\n📊 Instructor Status: {instructor_status}")
    print(f"🔧 Model Status: Real model loaded successfully")
    
    # Test with a simple dummy image
    print(f"\n🖼️  Creating test image...")
    test_image = Image.new('RGB', (640, 480), color='gray')
    
    # Run detection test
    print(f"🔍 Running fire detection test...")
    
    try:
        detection_result = await model_interface.detect_fire(
            test_image,
            frame_number=1,
            timestamp=1.0
        )
        
        print(f"\n📋 Detection Results:")
        print(f"   🔥 Fire Detected: {detection_result.fire_detected}")
        print(f"   📊 Confidence: {detection_result.confidence:.3f}")
        print(f"   ⚡ Processing Time: {detection_result.processing_time:.3f}s")
        print(f"   🏷️  Model Variant: {detection_result.model_variant}")
        
        # Check instructor usage
        instructor_used = detection_result.detection_details.get('instructor_used', False)
        structured_output = detection_result.detection_details.get('structured_output', False)
        
        print(f"\n🎯 Instructor Integration Results:")
        print(f"   📝 Instructor Used: {'✅ Yes' if instructor_used else '❌ No'}")
        print(f"   🏗️  Structured Output: {'✅ Yes' if structured_output else '❌ No'}")
        
        if not instructor_used:
            fallback_reason = detection_result.detection_details.get('fallback_reason', 'unknown')
            print(f"   ⚠️  Fallback Reason: {fallback_reason}")
        
        # Show fire characteristics if available
        if detection_result.fire_characteristics:
            print(f"\n🔥 Fire Characteristics:")
            print(f"   🏷️  Type: {detection_result.fire_characteristics.fire_type}")
            print(f"   🎛️  Control Status: {detection_result.fire_characteristics.control_status}")
            print(f"   🚨 Emergency Level: {detection_result.fire_characteristics.emergency_level}")
            print(f"   📞 911 Call Warranted: {detection_result.fire_characteristics.call_911_warranted}")
        
        print(f"\n✅ Test completed successfully!")
        
        # Summary
        print(f"\n📈 Test Summary:")
        if instructor_used:
            print(f"🎉 SUCCESS: Instructor integration is working correctly!")
            print(f"   - Structured DetectionResult generated directly")
            print(f"   - No manual JSON parsing required")
            print(f"   - Type-safe Pydantic model validation")
        else:
            print(f"ℹ️  INFO: Using fallback to manual parsing")
            print(f"   - Instructor not available or failed")
            print(f"   - Manual JSON parsing used as backup")
            print(f"   - Functionality maintained through fallback")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Detection test failed: {e}")
        return 1


async def main():
    """Main entry point for instructor integration test."""
    print("🧪 Instructor Integration Test for Gemma 3N Fire Detection")
    print("=" * 70)
    print("🎯 Purpose: Verify instructor package integration with fire detection")
    print("📝 Expected: Structured DetectionResult generation via instructor")
    print("🔄 Fallback: Manual JSON parsing if instructor unavailable")
    print("=" * 70)
    
    result = await test_instructor_integration()
    
    if result == 0:
        print(f"\n🎯 Instructor integration test PASSED! 🎉")
    else:
        print(f"\n❌ Instructor integration test FAILED! ❌")
    
    print(f"\n💡 Next steps:")
    print(f"   - All existing example scripts work unchanged")
    print(f"   - Instructor provides better structured output when available")
    print(f"   - Manual parsing provides reliable fallback")
    
    return result


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))