"""Vision processing utilities for Gemma 3N E4B."""

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from gemma_3n.fire_detection.config import Gemma3NE4BConfig


class VisionProcessor:
    """Vision processing for Gemma 3N E4B model input."""
    
    def __init__(self, config: Gemma3NE4BConfig):
        """Initialize vision processor.
        
        Args:
            config: Model configuration
        """
        self.config = config
        self.image_size = config.image_resolution
        
        # Standard preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize(
                (self.image_size, self.image_size),
                interpolation=transforms.InterpolationMode.BICUBIC
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.48145466, 0.4578275, 0.40821073],
                std=[0.26862954, 0.26130258, 0.27577711]
            )
        ])
    
    def numpy_to_pil(self, image: np.ndarray) -> Image.Image:
        """Convert numpy array to PIL Image.
        
        Args:
            image: Numpy array (BGR format from OpenCV)
            
        Returns:
            PIL Image in RGB format
        """
        # Convert BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        return Image.fromarray(image_rgb)
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for optimal fire detection.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size while maintaining aspect ratio
        image = image.resize(
            (self.image_size, self.image_size),
            Image.Resampling.BICUBIC
        )
        
        # Optional: enhance contrast for better fire detection
        # This can help with low-light scenarios
        if self._should_enhance_contrast(image):
            image = self._enhance_contrast(image)
        
        return image
    
    def _should_enhance_contrast(self, image: Image.Image) -> bool:
        """Determine if image needs contrast enhancement.
        
        Args:
            image: PIL Image
            
        Returns:
            True if enhancement is recommended
        """
        # Convert to grayscale for analysis
        gray = image.convert('L')
        
        # Calculate histogram
        histogram = gray.histogram()
        
        # Check if image is too dark (most pixels in lower range)
        total_pixels = sum(histogram)
        dark_pixels = sum(histogram[:85])  # First third of range
        
        return (dark_pixels / total_pixels) > 0.6
    
    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Enhance image contrast for better fire detection.
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced PIL Image
        """
        from PIL import ImageEnhance
        
        # Enhance contrast slightly
        enhancer = ImageEnhance.Contrast(image)
        enhanced = enhancer.enhance(1.2)
        
        # Enhance brightness slightly if image is dark
        brightness_enhancer = ImageEnhance.Brightness(enhanced)
        enhanced = brightness_enhancer.enhance(1.1)
        
        return enhanced
    
    def extract_image_features(self, image: Image.Image) -> torch.Tensor:
        """Extract features from image for model input.
        
        Args:
            image: PIL Image
            
        Returns:
            Feature tensor
        """
        # Apply preprocessing transforms
        tensor = self.transform(image)
        
        # Add batch dimension
        tensor = tensor.unsqueeze(0)
        
        return tensor
    
    def create_image_description(self, image: Image.Image) -> str:
        """Create textual description of image for model context.
        
        Args:
            image: PIL Image
            
        Returns:
            Image description string
        """
        # Basic image properties
        width, height = image.size
        
        # Analyze image characteristics
        description_parts = [
            f"Image dimensions: {width}x{height}",
            f"Aspect ratio: {width/height:.2f}",
        ]
        
        # Analyze color distribution
        color_info = self._analyze_colors(image)
        if color_info:
            description_parts.append(f"Color analysis: {color_info}")
        
        # Analyze brightness
        brightness = self._analyze_brightness(image) 
        description_parts.append(f"Brightness: {brightness}")
        
        return " | ".join(description_parts)
    
    def _analyze_colors(self, image: Image.Image) -> str:
        """Analyze dominant colors in image.
        
        Args:
            image: PIL Image
            
        Returns:
            Color analysis description
        """
        # Convert to numpy for analysis
        img_array = np.array(image)
        
        # Calculate average RGB values
        avg_r = np.mean(img_array[:, :, 0])
        avg_g = np.mean(img_array[:, :, 1])
        avg_b = np.mean(img_array[:, :, 2])
        
        # Determine dominant color tendency
        if avg_r > avg_g and avg_r > avg_b:
            if avg_r > 150:
                return "red-dominant (potential fire indicator)"
            else:
                return "reddish tones"
        elif avg_r > 100 and avg_g > 80 and avg_b < 80:
            return "orange/yellow tones (potential fire indicator)"
        elif avg_r > avg_g * 1.2 and avg_g > avg_b * 1.2:
            return "warm tones"
        else:
            return "cool/neutral tones"
    
    def _analyze_brightness(self, image: Image.Image) -> str:
        """Analyze image brightness level.
        
        Args:
            image: PIL Image
            
        Returns:
            Brightness description
        """
        # Convert to grayscale and calculate average
        gray = image.convert('L')
        avg_brightness = np.mean(np.array(gray))
        
        if avg_brightness < 50:
            return "very dark"
        elif avg_brightness < 100:
            return "dark"
        elif avg_brightness < 150:
            return "moderate"
        elif avg_brightness < 200:
            return "bright"
        else:
            return "very bright"