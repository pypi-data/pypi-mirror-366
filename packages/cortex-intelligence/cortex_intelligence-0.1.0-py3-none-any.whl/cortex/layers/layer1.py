"""
Layer 1: Raw Data Senses (Eyes and Ears)
Basic rote functions for capturing and preprocessing raw sensory data
"""

import io
import base64
from typing import Dict, Any, Optional, List
from PIL import Image
import numpy as np


class BaseSense:
    """Base class for all senses"""
    
    def __init__(self, name: str):
        self.name = name
        self.active = False
    
    def activate(self):
        """Activate this sense"""
        self.active = True
    
    def deactivate(self):
        """Deactivate this sense"""
        self.active = False
    
    def process(self, data: Any) -> Dict[str, Any]:
        """Process raw sensory data"""
        raise NotImplementedError


class VisionSense(BaseSense):
    """Vision sense for processing image data"""
    
    def __init__(self):
        super().__init__("vision")
        self.supported_formats = ["PNG", "JPEG", "JPG", "BMP", "TIFF"]
    
    def process(self, data: Any) -> Dict[str, Any]:
        """
        Process image data
        
        Args:
            data: Can be PIL Image, numpy array, file path, or base64 string
            
        Returns:
            Dict containing processed image metadata and features
        """
        if not self.active:
            return {"error": "Vision sense not active"}
        
        try:
            image = self._normalize_image(data)
            
            # Extract basic image features
            width, height = image.size
            mode = image.mode
            format_type = image.format or "Unknown"
            
            # Convert to numpy for basic analysis
            img_array = np.array(image)
            
            # Basic statistical features
            if len(img_array.shape) == 3:  # Color image
                mean_rgb = np.mean(img_array, axis=(0, 1))
                std_rgb = np.std(img_array, axis=(0, 1))
                brightness = np.mean(img_array)
            else:  # Grayscale
                mean_rgb = [np.mean(img_array)]
                std_rgb = [np.std(img_array)]
                brightness = np.mean(img_array)
            
            return {
                "type": "image",
                "width": width,
                "height": height,
                "mode": mode,
                "format": format_type,
                "mean_rgb": mean_rgb.tolist(),
                "std_rgb": std_rgb.tolist(),
                "brightness": float(brightness),
                "size_bytes": len(img_array.tobytes()),
                "processed": True
            }
            
        except Exception as e:
            return {"error": f"Vision processing failed: {str(e)}"}
    
    def _normalize_image(self, data: Any) -> Image.Image:
        """Convert various image input formats to PIL Image"""
        if isinstance(data, Image.Image):
            return data
        elif isinstance(data, np.ndarray):
            return Image.fromarray(data)
        elif isinstance(data, str):
            if data.startswith('data:image'):
                # Handle base64 data URLs
                header, encoded = data.split(',', 1)
                image_data = base64.b64decode(encoded)
                return Image.open(io.BytesIO(image_data))
            else:
                # Assume file path
                return Image.open(data)
        elif isinstance(data, bytes):
            return Image.open(io.BytesIO(data))
        else:
            raise ValueError(f"Unsupported image data type: {type(data)}")


class AudioSense(BaseSense):
    """Audio sense for processing sound data"""
    
    def __init__(self):
        super().__init__("audio")
        self.sample_rate = 16000  # Default sample rate
    
    def process(self, data: Any) -> Dict[str, Any]:
        """
        Process audio data
        
        Args:
            data: Audio data (numpy array, file path, or raw bytes)
            
        Returns:
            Dict containing processed audio metadata and features
        """
        if not self.active:
            return {"error": "Audio sense not active"}
        
        try:
            audio_data = self._normalize_audio(data)
            
            # Basic audio features
            duration = len(audio_data) / self.sample_rate
            amplitude_mean = np.mean(np.abs(audio_data))
            amplitude_max = np.max(np.abs(audio_data))
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Zero crossing rate (basic pitch indicator)
            zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
            zcr = zero_crossings / len(audio_data)
            
            return {
                "type": "audio",
                "duration": float(duration),
                "sample_rate": self.sample_rate,
                "amplitude_mean": float(amplitude_mean),
                "amplitude_max": float(amplitude_max),
                "rms": float(rms),
                "zero_crossing_rate": float(zcr),
                "length": len(audio_data),
                "processed": True
            }
            
        except Exception as e:
            return {"error": f"Audio processing failed: {str(e)}"}
    
    def _normalize_audio(self, data: Any) -> np.ndarray:
        """Convert various audio input formats to numpy array"""
        if isinstance(data, np.ndarray):
            return data
        elif isinstance(data, str):
            # For now, assume it's a simple numpy array save file
            # In a real implementation, you'd use librosa or similar
            return np.load(data)
        elif isinstance(data, bytes):
            # Convert bytes to numpy array (basic implementation)
            return np.frombuffer(data, dtype=np.float32)
        else:
            raise ValueError(f"Unsupported audio data type: {type(data)}")


class TextSense(BaseSense):
    """Text sense for processing textual data"""
    
    def __init__(self):
        super().__init__("text")
    
    def process(self, data: Any) -> Dict[str, Any]:
        """
        Process text data
        
        Args:
            data: Text string or file path
            
        Returns:
            Dict containing processed text metadata and features
        """
        if not self.active:
            return {"error": "Text sense not active"}
        
        try:
            text = self._normalize_text(data)
            
            # Basic text features
            char_count = len(text)
            word_count = len(text.split())
            line_count = text.count('\n') + 1
            
            # Character frequency analysis
            char_freq = {}
            for char in text.lower():
                char_freq[char] = char_freq.get(char, 0) + 1
            
            # Most common characters (excluding spaces)
            common_chars = sorted(
                [(char, freq) for char, freq in char_freq.items() if char != ' '], 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return {
                "type": "text",
                "char_count": char_count,
                "word_count": word_count,
                "line_count": line_count,
                "common_chars": common_chars,
                "has_punctuation": any(c in text for c in ".,!?;:"),
                "has_numbers": any(c.isdigit() for c in text),
                "processed": True
            }
            
        except Exception as e:
            return {"error": f"Text processing failed: {str(e)}"}
    
    def _normalize_text(self, data: Any) -> str:
        """Convert various text input formats to string"""
        if isinstance(data, str):
            if data.startswith('/') or data.startswith('./'):
                # Assume file path
                with open(data, 'r', encoding='utf-8') as f:
                    return f.read()
            return data
        elif isinstance(data, bytes):
            return data.decode('utf-8')
        else:
            return str(data)


class SenseLayer:
    """
    Layer 1: Combines all senses and provides unified interface
    """
    
    def __init__(self):
        self.senses = {
            "vision": VisionSense(),
            "audio": AudioSense(),
            "text": TextSense()
        }
        self.active_senses = set()
    
    def activate_sense(self, sense_name: str):
        """Activate a specific sense"""
        if sense_name in self.senses:
            self.senses[sense_name].activate()
            self.active_senses.add(sense_name)
        else:
            raise ValueError(f"Unknown sense: {sense_name}")
    
    def deactivate_sense(self, sense_name: str):
        """Deactivate a specific sense"""
        if sense_name in self.senses:
            self.senses[sense_name].deactivate()
            self.active_senses.discard(sense_name)
    
    def activate_all(self):
        """Activate all senses"""
        for sense_name in self.senses:
            self.activate_sense(sense_name)
    
    def process_input(self, data: Any, sense_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Process input data through appropriate sense
        
        Args:
            data: Input data to process
            sense_type: Specific sense to use, or None for auto-detection
            
        Returns:
            Dict containing processed data and metadata
        """
        if sense_type:
            if sense_type in self.senses:
                return self.senses[sense_type].process(data)
            else:
                return {"error": f"Unknown sense type: {sense_type}"}
        
        # Auto-detect sense type
        detected_sense = self._detect_sense_type(data)
        if detected_sense:
            return self.senses[detected_sense].process(data)
        else:
            return {"error": "Could not detect appropriate sense for input data"}
    
    def _detect_sense_type(self, data: Any) -> Optional[str]:
        """Auto-detect which sense should process the data"""
        if isinstance(data, Image.Image) or isinstance(data, np.ndarray):
            return "vision"
        elif isinstance(data, str):
            if any(data.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']):
                return "vision"
            elif any(data.lower().endswith(ext) for ext in ['.wav', '.mp3', '.flac']):
                return "audio"
            else:
                return "text"
        elif hasattr(data, 'read'):  # File-like object
            return "text"
        else:
            return "text"  # Default fallback
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all senses"""
        return {
            "active_senses": list(self.active_senses),
            "available_senses": list(self.senses.keys()),
            "sense_status": {
                name: sense.active for name, sense in self.senses.items()
            }
        }