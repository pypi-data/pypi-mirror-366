"""Gemma 3N E4B model interface for fire detection."""

import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from transformers import BitsAndBytesConfig
    BITSANDBYTES_AVAILABLE = True
except ImportError:
    BITSANDBYTES_AVAILABLE = False
    BitsAndBytesConfig = None

try:
    import instructor
    from pydantic import BaseModel, Field
    INSTRUCTOR_AVAILABLE = True
except ImportError:
    INSTRUCTOR_AVAILABLE = False
    instructor = None
    BaseModel = None
    Field = None

from gemma_3n.fire_detection.config import Gemma3NE4BConfig
from gemma_3n.fire_detection.models.results import DetectionResult, FireCharacteristics

logger = logging.getLogger(__name__)


class FireDetectionResponse(BaseModel):
    """Structured response for fire detection."""
    fire_detected: bool = Field(description="Whether fire or flames are detected in the image")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    location: str = Field(default="unknown", description="Location of fire if detected")
    intensity: str = Field(default="unknown", description="Intensity of fire (low/medium/high)")
    color: str = Field(default="unknown", description="Color of flames if detected")
    spread_risk: str = Field(default="unknown", description="Risk of fire spreading (low/medium/high)")


class SimpleFireDetectionResponse(BaseModel):
    """Simple structured response for basic fire detection."""
    fire_detected: bool = Field(description="Whether fire is detected")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence between 0.0 and 1.0")


class Gemma3NE4BInterface:
    """Interface for Gemma 3N E4B model with fire detection capabilities."""
    
    def __init__(self, config: Gemma3NE4BConfig, device: str = "auto", detection_config=None):
        """Initialize Gemma 3N E4B interface.
        
        Args:
            config: Model configuration
            device: Device to use (auto, cpu, cuda, mps)
        """
        self.config = config
        self.detection_config = detection_config
        self.device = self._get_device(device)
        self.model = None
        self.tokenizer = None
        self.logger = logging.getLogger(__name__)
        
        # Model state
        self._model_loaded = False
        self._temp_dir = Path(tempfile.mkdtemp(prefix="gemma_e4b_"))
        
        # Instructor integration
        self._instructor_client = None
        self._use_instructor = INSTRUCTOR_AVAILABLE
        
    def _get_device(self, device: str) -> str:
        """Determine the actual device to use.
        
        Args:
            device: Requested device
            
        Returns:
            Actual device string
        """
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def _check_hf_authentication(self) -> bool:
        """Check if authenticated with Hugging Face."""
        try:
            from huggingface_hub import whoami
            whoami()
            return True
        except Exception as e:
            self.logger.warning(f"HuggingFace authentication check failed: {e}")
            return False
    
    def load_model(self) -> None:
        """Load Gemma 3N E4B model with 4-bit quantization."""
        if self._model_loaded:
            return
        
        # Check authentication for gated models
        if "google/gemma" in str(self.config.model_path).lower():
            if not self._check_hf_authentication():
                self.logger.error("Authentication required for Gemma models. Please set HUGGINGFACE_HUB_TOKEN environment variable or run 'hf auth login'")
                raise RuntimeError("HuggingFace authentication required for Gemma models")
        
        self.logger.info(f"Loading {self.config.model_variant} model from {self.config.model_path}")
        
        try:
            # Optional quantization configuration
            quantization_config = None
            if self.config.use_quantization:
                # Check if we're on macOS and warn about BitsAndBytes incompatibility
                import platform
                if platform.system() == "Darwin":
                    self.logger.warning("BitsAndBytes quantization not available on macOS. Disabling quantization.")
                    self.config.use_quantization = False
                elif BITSANDBYTES_AVAILABLE and BitsAndBytesConfig is not None:
                    # Configure quantization based on config settings
                    compute_dtype = getattr(torch, self.config.quantization_compute_dtype, torch.float16)
                    
                    if self.config.quantization_type == "4bit":
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=compute_dtype,
                            bnb_4bit_quant_type="nf4",  # Normal Float 4
                            bnb_4bit_use_double_quant=True,
                        )
                        self.logger.info("Using 4-bit quantization")
                    elif self.config.quantization_type == "8bit":
                        quantization_config = BitsAndBytesConfig(
                            load_in_8bit=True,
                            llm_int8_enable_fp32_cpu_offload=True,
                        )
                        self.logger.info("Using 8-bit quantization")
                    else:
                        self.logger.warning(f"Unknown quantization type: {self.config.quantization_type}")
                else:
                    self.logger.warning("BitsAndBytes not available - quantization disabled, using full precision model")
                    self.config.use_quantization = False
            
            if not self.config.use_quantization:
                self.logger.info("Quantization disabled - using full precision model")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            # Ensure pad token is set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with or without quantization
            model_kwargs = {
                "device_map": "auto" if self.device == "cuda" else None,
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
                "low_cpu_mem_usage": True
            }
            
            # Only add quantization config if available
            if quantization_config is not None:
                model_kwargs["quantization_config"] = quantization_config
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                **model_kwargs
            )
            
            # Move to device if not using device_map
            if self.device != "cuda":
                self.model = self.model.to(self.device)
            
            self.model.eval()  # Set to evaluation mode
            
            # For now, disable instructor as it requires proper OpenAI API compatibility
            # Modern instructor doesn't have from_transformers - it's designed for OpenAI-compatible APIs
            self._use_instructor = False
            self.logger.info(f"Model loaded successfully on {self.device} (using structured parsing with Pydantic validation)")
            
            self._model_loaded = True
            
        except Exception as e:
            # Handle specific common issues with clear error messages
            error_str = str(e).lower()
            
            if "bitsandbytes" in error_str and "darwin" in os.uname().sysname.lower():
                self.logger.error("BitsAndBytes quantization not available on macOS. Please disable quantization or use a compatible platform.")
            elif "no such file or directory" in error_str or "not found" in error_str:
                self.logger.error(f"Gemma model files not found at {self.config.model_path}. Please ensure model files are properly installed.")
            else:
                self.logger.error(f"Model loading failed: {e}")
            
            raise RuntimeError(f"Model loading failed: {e}")
    
    def _create_fire_detection_prompt(self, image_description: str = "") -> str:
        """Create fire detection prompt for Gemma 3N E4B.
        
        Args:
            image_description: Optional image description
            
        Returns:
            Formatted prompt
        """
        if self.detection_config is None:
            # Enhanced Gemma-optimized prompt for better fire detection
            system_prompt = "You are an expert fire detection AI trained to identify fire, flames, smoke, and burning in images."
            detection_prompt = """Carefully analyze this image for ANY signs of:
1. Fire, flames, or burning (any size, even small)
2. Smoke or heat distortion
3. Orange/red/yellow glowing that could be fire
4. Any combustion or burning materials

BE SENSITIVE to fire - it's better to flag potential fire than miss it.

Provide your analysis as JSON with these exact fields:
{
  "fire_detected": true/false,
  "fire_presence_probability": 0.0-1.0,
  "uncontrolled_fire_probability": 0.0-1.0,
  "confidence": 0.0-1.0,
  "fire_type": "none/controlled/uncontrolled/wildfire",
  "location": "description of where in image",
  "intensity": "none/low/medium/high/extreme",
  "visual_evidence": "what you see that indicates fire"
}

Analysis:"""
        else:
            system_prompt = self.detection_config.system_prompt
            detection_prompt = self.detection_config.detection_prompt
            
        # Gemma-style prompt format
        return f"""<bos><start_of_turn>user
{system_prompt}

{image_description}

{detection_prompt}<end_of_turn>
<start_of_turn>model
"""

    def _create_structured_fire_detection_prompt(self) -> tuple[str, str]:
        """Create system and user prompts for structured fire detection.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        system_prompt = """You are an expert fire safety analyst with 20+ years of experience in wildfire detection and emergency response.

Your role is to analyze images for fire hazards with EXTREME PRECISION while avoiding false alarms.

DETECTION STANDARDS:
- Be CONSERVATIVE: False alarms cause unnecessary emergency responses
- Distinguish fire from: orange lights, reflections, sunset, electronic displays, clothing
- Consider environmental context: indoor vs outdoor, weather conditions, time of day
- Assess spread risk based on surrounding materials and conditions

FIRE CLASSIFICATION:
- controlled: Small fires that are contained (candles, fireplaces, controlled burns)
- uncontrolled: Fires spreading beyond their intended boundaries
- wildfire: Large uncontrolled fires in natural settings
- no_fire: No fire detected

EMERGENCY LEVELS:
- none: No fire or very minor controlled fire
- monitor: Small fire that should be watched
- alert: Uncontrolled fire requiring attention
- critical: Dangerous fire requiring immediate emergency response"""

        user_prompt = """Analyze this image for fire hazards using a systematic approach:

ANALYSIS STEPS:

1. INITIAL FIRE SCAN:
   - Look for ANY orange/red/yellow glowing areas
   - Check for smoke, haze, or heat distortion
   - Identify bright spots that could be flames
   - Note any areas with fire-like colors or patterns

2. FIRE PRESENCE ASSESSMENT:
   Rate the probability (0.0-1.0) that fire is present based on:
   - Visual evidence of flames or burning
   - Smoke or combustion products
   - Heat signatures or distortion
   - Fire-like colors and patterns

3. CONTROLLED VS UNCONTROLLED:
   If fire is detected, assess control status:
   - Controlled: campfire, fireplace, candle, contained burn
   - Uncontrolled: spreading fire, wildfire, structure fire
   - Rate probability (0.0-1.0) that any detected fire is uncontrolled

4. DETAILED CHARACTERISTICS:
   For any detected fire, describe:
   - Location in the image
   - Size and intensity
   - Spread potential
   - Visual evidence supporting detection

Provide a comprehensive fire detection analysis with separate probabilities for:
- Fire presence (any fire at all)
- Uncontrolled fire (if fire is present)
Include detailed visual evidence for your assessment."""

        return system_prompt, user_prompt

    async def _detect_fire_with_instructor(
        self,
        image: Image.Image,
        frame_number: int,
        timestamp: float
    ) -> DetectionResult:
        """Detect fire using instructor structured output.
        
        Args:
            image: PIL Image to analyze
            frame_number: Frame number in video
            timestamp: Timestamp in seconds
            
        Returns:
            Structured DetectionResult
        """
        start_time = time.time()
        
        try:
            # Create structured prompts
            system_prompt, user_prompt = self._create_structured_fire_detection_prompt()
            
            # Use instructor to generate structured DetectionResult
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Generate structured response using instructor
            detection_result = await self._instructor_client.chat.completions.create(
                model="local",  # Using local model
                messages=messages,
                response_model=DetectionResult,
                max_retries=2,
                temperature=self.config.temperature,
                max_tokens=self.config.max_new_tokens
            )
            
            # Set frame-specific metadata that instructor doesn't handle
            detection_result.frame_number = frame_number
            detection_result.timestamp = timestamp
            detection_result.processing_time = time.time() - start_time
            detection_result.model_variant = f"{self.config.model_variant}-instructor"
            detection_result.frame_saved = False
            detection_result.frame_path = None
            
            # Add instructor-specific detection details
            if not detection_result.detection_details:
                detection_result.detection_details = {}
            detection_result.detection_details.update({
                "instructor_used": True,
                "structured_output": True
            })
            
            self.logger.debug(
                f"Instructor Frame {frame_number}: fire={detection_result.fire_detected}, "
                f"confidence={detection_result.confidence:.3f}, "
                f"time={detection_result.processing_time:.3f}s"
            )
            
            return detection_result
            
        except Exception as e:
            self.logger.error(f"Instructor fire detection failed for frame {frame_number}: {e}")
            raise e  # Re-raise to fall back to manual parsing
    
    def _save_temp_image(self, image: Image.Image) -> Path:
        """Save image temporarily for processing.
        
        Args:
            image: PIL Image
            
        Returns:
            Path to temporary image file
        """
        temp_path = self._temp_dir / f"frame_{int(time.time() * 1000)}.jpg"
        image.save(temp_path, format="JPEG", quality=85)
        return temp_path
    
    def _parse_detection_response(self, response: str) -> Dict[str, Any]:
        """Parse model response for fire detection results.
        
        Args:
            response: Raw model response
            
        Returns:
            Parsed detection results
        """
        try:
            # Try to extract JSON from response with improved parsing
            json_str = None
            
            # Method 1: Look for the first complete JSON object
            json_start = response.find('{')
            if json_start != -1:
                # Find the matching closing brace
                brace_count = 0
                json_end = json_start
                for i, char in enumerate(response[json_start:], json_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                if brace_count == 0:  # Found complete JSON
                    json_str = response[json_start:json_end]
            
            # Method 2: Try to extract from code blocks
            if json_str is None:
                import re
                # Look for JSON in markdown code blocks
                code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
                match = re.search(code_block_pattern, response, re.DOTALL)
                if match:
                    json_str = match.group(1)
            
            # Method 3: Clean up common issues and try again
            if json_str is None and '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                # Clean up common issues
                json_str = json_str.replace('\\n', '\n').replace('\\"', '"')
            
            if json_str:
                # Clean and parse JSON
                json_str = json_str.strip()
                data = json.loads(json_str)
                
                # Normalize the response
                fire_detected = False
                confidence = 0.0
                fire_presence_prob = 0.0
                uncontrolled_prob = 0.0
                details = {}
                
                # Check various possible keys for fire detection
                for key in ['fire_detected', 'fire', 'has_fire', 'detected']:
                    if key in data:
                        value = data[key]
                        if isinstance(value, bool):
                            fire_detected = value
                        elif isinstance(value, str):
                            fire_detected = value.lower() in ['yes', 'true', '1']
                        break
                
                # Extract confidence
                for key in ['confidence', 'confidence_score', 'probability']:
                    if key in data:
                        conf_value = data[key]
                        if isinstance(conf_value, (int, float)):
                            confidence = float(conf_value)
                            if confidence > 1.0:  # Convert percentage to decimal
                                confidence = confidence / 100.0
                        elif isinstance(conf_value, str):
                            try:
                                confidence = float(conf_value.rstrip('%')) / 100.0
                            except ValueError:
                                pass
                        break
                
                # Extract fire presence probability
                if 'fire_presence_probability' in data:
                    fire_presence_prob = float(data['fire_presence_probability'])
                    if fire_presence_prob > 1.0:
                        fire_presence_prob = fire_presence_prob / 100.0
                
                # Extract uncontrolled fire probability
                if 'uncontrolled_fire_probability' in data:
                    uncontrolled_prob = float(data['uncontrolled_fire_probability'])
                    if uncontrolled_prob > 1.0:
                        uncontrolled_prob = uncontrolled_prob / 100.0
                
                # Extract additional details
                if fire_detected:
                    characteristics = {}
                    for key in ['location', 'intensity', 'color', 'spread_risk', 'size']:
                        if key in data:
                            characteristics[key] = str(data[key])
                    
                    if characteristics:
                        details['fire_characteristics'] = FireCharacteristics(
                            location=characteristics.get('location', 'Unknown'),
                            intensity=characteristics.get('intensity', 'Unknown'),
                            color=characteristics.get('color', 'Unknown'),
                            spread_risk=characteristics.get('spread_risk', 'Unknown'),
                            size_estimate=characteristics.get('size')
                        )
                
                return {
                    'fire_detected': fire_detected,
                    'confidence': confidence,
                    'fire_presence_probability': fire_presence_prob,
                    'uncontrolled_fire_probability': uncontrolled_prob,
                    'details': details,
                    'raw_response': response
                }
                
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Raw response was: {repr(response[:200])}")
            if json_str:
                self.logger.debug(f"Extracted JSON string was: {repr(json_str[:200])}")
        
        # Fallback parsing using text analysis
        response_lower = response.lower()
        
        # For GPT2, we might get simple responses, so let's be more flexible
        fire_detected = any(phrase in response_lower for phrase in [
            'fire_detected": true',
            'fire detected: yes',
            'fire: yes',
            '"fire": true',
            'fire present',
            'flame detected',
            'flames visible',
            'has fire: true',
            'fire is present',
            'flames detected'
        ])
        
        # Extract confidence from text
        confidence = 0.5  # Default moderate confidence
        for line in response.split('\n'):
            if 'confidence' in line.lower():
                # Try to extract number
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', line)
                if numbers:
                    conf = float(numbers[0])
                    confidence = conf / 100.0 if conf > 1.0 else conf
                    break
        
        return {
            'fire_detected': fire_detected,
            'confidence': confidence,
            'fire_presence_probability': confidence if fire_detected else 0.0,
            'uncontrolled_fire_probability': 0.5 if fire_detected else 0.0,
            'details': {'parsing_method': 'fallback'},
            'raw_response': response
        }
    
    def _parse_detection_response_structured(self, response: str) -> Dict[str, Any]:
        """Parse model response using structured Pydantic validation.
        
        Args:
            response: Raw model response
            
        Returns:
            Parsed detection results with validation
        """
        # First try to extract and validate JSON with full model
        try:
            json_str = self._extract_json_from_response(response)
            if json_str:
                # Try to validate with full FireDetectionResponse model first
                try:
                    detection_obj = FireDetectionResponse.model_validate_json(json_str)
                    return {
                        'fire_detected': detection_obj.fire_detected,
                        'confidence': detection_obj.confidence,
                        'fire_presence_probability': detection_obj.confidence,
                        'uncontrolled_fire_probability': 0.7 if detection_obj.intensity in ['medium', 'high'] else 0.3,
                        'details': {
                            'location': detection_obj.location,
                            'intensity': detection_obj.intensity,
                            'color': detection_obj.color,
                            'spread_risk': detection_obj.spread_risk,
                            'parsing_method': 'structured_full'
                        },
                        'raw_response': response
                    }
                except Exception:
                    # Fall back to simple model
                    detection_obj = SimpleFireDetectionResponse.model_validate_json(json_str)
                    return {
                        'fire_detected': detection_obj.fire_detected,
                        'confidence': detection_obj.confidence,
                        'fire_presence_probability': detection_obj.confidence,
                        'uncontrolled_fire_probability': 0.5 if detection_obj.fire_detected else 0.0,
                        'details': {'parsing_method': 'structured_simple'},
                        'raw_response': response
                    }
        except Exception as e:
            self.logger.warning(f"Structured parsing failed: {e}")
        
        # Fall back to the original parsing method
        return self._parse_detection_response(response)
    
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """Extract JSON string from model response."""
        import re
        
        # Method 1: Look for the first complete JSON object
        json_start = response.find('{')
        if json_start != -1:
            brace_count = 0
            json_end = json_start
            for i, char in enumerate(response[json_start:], json_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
            
            if brace_count == 0:  # Found complete JSON
                return response[json_start:json_end].strip()
        
        # Method 2: Look for JSON in code blocks
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(code_block_pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    
    async def detect_fire(
        self, 
        image: Image.Image, 
        frame_number: int, 
        timestamp: float
    ) -> DetectionResult:
        """Detect fire in image using Gemma 3N E4B.
        
        Args:
            image: PIL Image to analyze
            frame_number: Frame number in video
            timestamp: Timestamp in seconds
            
        Returns:
            Detection result
        """
        if not self._model_loaded:
            self.load_model()
        
        start_time = time.time()
        
        # Try instructor-based structured detection first (if available)
        if self._use_instructor and self._instructor_client:
            try:
                return await self._detect_fire_with_instructor(image, frame_number, timestamp)
            except Exception as e:
                self.logger.warning(f"Instructor detection failed, falling back to manual parsing: {e}")
                # Continue to manual detection below
        
        try:
            # Save image temporarily
            temp_image_path = self._save_temp_image(image)
            
            # Create prompt
            image_desc = f"Analyze this image saved at: {temp_image_path}"
            prompt = self._create_fire_detection_prompt(image_desc)
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Generate response with E4B optimizations
            with torch.no_grad():
                if self.device == "cuda":
                    with torch.amp.autocast('cuda', enabled=True):
                        outputs = self.model.generate(
                            **inputs,
                            max_new_tokens=self.config.max_new_tokens,
                            temperature=self.config.temperature,
                            top_p=self.config.top_p,
                            repetition_penalty=self.config.repetition_penalty,
                            do_sample=True,
                            use_cache=True,
                            pad_token_id=self.tokenizer.pad_token_id
                        )
                else:
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=self.config.max_new_tokens,
                        temperature=self.config.temperature,
                        top_p=self.config.top_p,
                        repetition_penalty=self.config.repetition_penalty,
                        do_sample=True,
                        use_cache=True,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][len(inputs["input_ids"][0]):],
                skip_special_tokens=True
            )
            
            # Parse response with Pydantic validation
            result_data = self._parse_detection_response_structured(response)
            
            # Clean up temporary file
            try:
                temp_image_path.unlink()
            except Exception:
                pass
            
            processing_time = time.time() - start_time
            
            # Create detection result
            # Update detection details to indicate instructor fallback
            detection_details = result_data['details'].copy()
            detection_details.update({
                "instructor_used": False,
                "manual_parsing": True,
                "fallback_reason": "instructor_unavailable" if not self._use_instructor else "instructor_failed"
            })
            
            detection_result = DetectionResult(
                frame_number=frame_number,
                timestamp=timestamp,
                fire_detected=result_data['fire_detected'],
                confidence=result_data['confidence'],
                fire_presence_probability=result_data.get('fire_presence_probability', result_data['confidence']),
                uncontrolled_fire_probability=result_data.get('uncontrolled_fire_probability', 0.5 if result_data['fire_detected'] else 0.0),
                fire_characteristics=result_data['details'].get('fire_characteristics'),
                detection_details=detection_details,
                processing_time=processing_time,
                model_variant=f"{self.config.model_variant}-manual"
            )
            
            self.logger.debug(
                f"Frame {frame_number}: fire={result_data['fire_detected']}, "
                f"confidence={result_data['confidence']:.3f}, "
                f"time={processing_time:.3f}s"
            )
            
            return detection_result
            
        except Exception as e:
            self.logger.error(f"Fire detection failed for frame {frame_number}: {e}")
            
            return DetectionResult(
                frame_number=frame_number,
                timestamp=timestamp,
                fire_detected=False,
                confidence=0.0,
                fire_presence_probability=0.0,
                uncontrolled_fire_probability=0.0,
                detection_details={
                    'error': str(e),
                    'instructor_used': False,
                    'manual_parsing': True,
                    'error_fallback': True
                },
                processing_time=time.time() - start_time,
                model_variant=f"{self.config.model_variant}-error"
            )
    
    def __del__(self):
        """Cleanup temporary directory."""
        try:
            import shutil
            if hasattr(self, '_temp_dir') and self._temp_dir.exists():
                shutil.rmtree(self._temp_dir)
        except Exception:
            pass