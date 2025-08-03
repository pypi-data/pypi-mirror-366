"""
ONNX Models for Layer 2 Intelligence

This module provides ONNX model integration for Cortex Layer 2,
enabling intelligent classification and decision-making without external API calls.
"""

import os
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.warning("ONNX Runtime not available. Install with: pip install onnxruntime")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available. Install with: pip install pillow")


class ModelType(Enum):
    """Types of ONNX models supported"""
    TEXT_CLASSIFICATION = "text_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    INTENT_CLASSIFICATION = "intent_classification"
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    AUDIO_CLASSIFICATION = "audio_classification"
    SPEECH_DETECTION = "speech_detection"


@dataclass
class ModelConfig:
    """Configuration for ONNX models"""
    model_type: ModelType
    model_path: str
    input_shape: Tuple[int, ...]
    output_classes: List[str]
    preprocessing_config: Dict[str, Any]
    confidence_threshold: float = 0.5
    max_input_length: Optional[int] = None


class ONNXModelManager:
    """Manages ONNX models for different data types"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models: Dict[str, ort.InferenceSession] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        self.logger = logging.getLogger(__name__)
        
        # Create models directory if it doesn't exist
        os.makedirs(models_dir, exist_ok=True)
    
    def load_model(self, model_name: str, config: ModelConfig) -> bool:
        """Load an ONNX model"""
        if not ONNX_AVAILABLE:
            self.logger.error("ONNX Runtime not available")
            return False
        
        try:
            model_path = os.path.join(self.models_dir, config.model_path)
            if not os.path.exists(model_path):
                self.logger.warning(f"Model file not found: {model_path}")
                return False
            
            # Load ONNX model
            session = ort.InferenceSession(model_path)
            self.models[model_name] = session
            self.model_configs[model_name] = config
            
            self.logger.info(f"Loaded ONNX model: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    def get_model(self, model_name: str) -> Optional[ort.InferenceSession]:
        """Get a loaded model"""
        return self.models.get(model_name)
    
    def get_config(self, model_name: str) -> Optional[ModelConfig]:
        """Get model configuration"""
        return self.model_configs.get(model_name)
    
    def list_loaded_models(self) -> List[str]:
        """List all loaded models"""
        return list(self.models.keys())


class TextPreprocessor:
    """Preprocesses text for ONNX models"""
    
    def __init__(self, max_length: int = 512):
        self.max_length = max_length
        self.vocab_size = 1000
    
    def preprocess(self, text: str) -> np.ndarray:
        """
        Enhanced text preprocessing with better tokenization
        """
        # Convert to lowercase and basic cleaning
        text = text.lower().strip()
        
        # Simple word-based tokenization (better than character-level)
        words = text.split()[:self.max_length]
        
        # Create a simple vocabulary mapping
        # In a real implementation, you'd use a proper tokenizer
        encoded = []
        for word in words:
            # Simple hash-based tokenization
            token_id = hash(word) % self.vocab_size
            encoded.append(token_id)
        
        # Pad or truncate
        if len(encoded) < self.max_length:
            encoded.extend([0] * (self.max_length - len(encoded)))
        else:
            encoded = encoded[:self.max_length]
        
        return np.array(encoded, dtype=np.float32).reshape(1, -1)


class ImagePreprocessor:
    """Preprocesses images for ONNX models"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
    
    def preprocess(self, image: Union[str, np.ndarray, 'Image.Image']) -> np.ndarray:
        """Preprocess image for ONNX model"""
        if not PIL_AVAILABLE:
            raise ImportError("PIL required for image preprocessing")
        
        # Load image if it's a path
        if isinstance(image, str):
            img = Image.open(image)
        elif isinstance(image, np.ndarray):
            img = Image.fromarray(image)
        else:
            img = image
        
        # Resize
        img = img.resize(self.target_size)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to numpy array and normalize
        img_array = np.array(img, dtype=np.float32)
        img_array = img_array / 255.0  # Normalize to [0, 1]
        
        # Add batch dimension
        img_array = img_array.reshape(1, *img_array.shape)
        
        return img_array


class AudioPreprocessor:
    """Preprocesses audio for ONNX models"""
    
    def __init__(self, sample_rate: int = 16000, max_duration: float = 10.0):
        self.sample_rate = sample_rate
        self.max_samples = int(sample_rate * max_duration)
    
    def preprocess(self, audio_data: np.ndarray) -> np.ndarray:
        """Preprocess audio for ONNX model"""
        # Ensure mono
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        # Pad or truncate to max_samples
        if len(audio_data) < self.max_samples:
            audio_data = np.pad(audio_data, (0, self.max_samples - len(audio_data)))
        else:
            audio_data = audio_data[:self.max_samples]
        
        # Normalize
        audio_data = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) > 0 else audio_data
        
        # Add batch dimension
        audio_data = audio_data.reshape(1, -1)
        
        return audio_data.astype(np.float32)


class ONNXInference:
    """Handles ONNX model inference"""
    
    def __init__(self, model_manager: ONNXModelManager):
        self.model_manager = model_manager
        self.text_preprocessor = TextPreprocessor()
        self.image_preprocessor = ImagePreprocessor()
        self.audio_preprocessor = AudioPreprocessor()
        self.logger = logging.getLogger(__name__)
    
    def classify_text(self, text: str, model_name: str = "text_classifier") -> Dict[str, Any]:
        """Classify text using ONNX model"""
        model = self.model_manager.get_model(model_name)
        config = self.model_manager.get_config(model_name)
        
        if not model or not config:
            return {"error": f"Model {model_name} not loaded"}
        
        try:
            # Preprocess text
            input_data = self.text_preprocessor.preprocess(text)
            
            # Run inference
            input_name = model.get_inputs()[0].name
            output_name = model.get_outputs()[0].name
            
            outputs = model.run([output_name], {input_name: input_data})
            predictions = outputs[0][0]
            
            # Apply softmax to get probabilities
            exp_preds = np.exp(predictions - np.max(predictions))
            probabilities = exp_preds / np.sum(exp_preds)
            
            # Get top predictions
            top_indices = np.argsort(probabilities)[::-1][:3]
            results = []
            
            for idx in top_indices:
                if idx < len(config.output_classes):
                    class_name = config.output_classes[idx]
                    confidence = float(probabilities[idx])
                    results.append({
                        "class": class_name,
                        "confidence": confidence
                    })
            
            return {
                "success": True,
                "predictions": results,
                "top_class": results[0]["class"] if results else None,
                "top_confidence": results[0]["confidence"] if results else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Text classification failed: {e}")
            return {"error": str(e)}
    
    def classify_image(self, image: Union[str, np.ndarray, 'Image.Image'], 
                      model_name: str = "image_classifier") -> Dict[str, Any]:
        """Classify image using ONNX model"""
        model = self.model_manager.get_model(model_name)
        config = self.model_manager.get_config(model_name)
        
        if not model or not config:
            return {"error": f"Model {model_name} not loaded"}
        
        try:
            # Preprocess image
            input_data = self.image_preprocessor.preprocess(image)
            
            # Run inference
            input_name = model.get_inputs()[0].name
            output_name = model.get_outputs()[0].name
            
            outputs = model.run([output_name], {input_name: input_data})
            predictions = outputs[0][0]
            
            # Get top predictions
            top_indices = np.argsort(predictions)[::-1][:3]
            results = []
            
            for idx in top_indices:
                if idx < len(config.output_classes):
                    class_name = config.output_classes[idx]
                    confidence = float(predictions[idx])
                    results.append({
                        "class": class_name,
                        "confidence": confidence
                    })
            
            return {
                "success": True,
                "predictions": results,
                "top_class": results[0]["class"] if results else None,
                "top_confidence": results[0]["confidence"] if results else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Image classification failed: {e}")
            return {"error": str(e)}
    
    def classify_audio(self, audio_data: np.ndarray, 
                      model_name: str = "audio_classifier") -> Dict[str, Any]:
        """Classify audio using ONNX model"""
        model = self.model_manager.get_model(model_name)
        config = self.model_manager.get_config(model_name)
        
        if not model or not config:
            return {"error": f"Model {model_name} not loaded"}
        
        try:
            # Preprocess audio
            input_data = self.audio_preprocessor.preprocess(audio_data)
            
            # Run inference
            input_name = model.get_inputs()[0].name
            output_name = model.get_outputs()[0].name
            
            outputs = model.run([output_name], {input_name: input_data})
            predictions = outputs[0][0]
            
            # Get top predictions
            top_indices = np.argsort(predictions)[::-1][:3]
            results = []
            
            for idx in top_indices:
                if idx < len(config.output_classes):
                    class_name = config.output_classes[idx]
                    confidence = float(predictions[idx])
                    results.append({
                        "class": class_name,
                        "confidence": confidence
                    })
            
            return {
                "success": True,
                "predictions": results,
                "top_class": results[0]["class"] if results else None,
                "top_confidence": results[0]["confidence"] if results else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Audio classification failed: {e}")
            return {"error": str(e)}


# Default model configurations
DEFAULT_MODEL_CONFIGS = {
    "text_classifier": ModelConfig(
        model_type=ModelType.TEXT_CLASSIFICATION,
        model_path="text_classifier.onnx",
        input_shape=(1, 512),
        output_classes=["simple", "complex", "urgent", "question", "statement"],
        preprocessing_config={"max_length": 512},
        confidence_threshold=0.6
    ),
    
    "sentiment_analyzer": ModelConfig(
        model_type=ModelType.SENTIMENT_ANALYSIS,
        model_path="sentiment_analyzer.onnx",
        input_shape=(1, 512),
        output_classes=["positive", "negative", "neutral", "urgent"],
        preprocessing_config={"max_length": 512},
        confidence_threshold=0.5
    ),
    
    "image_classifier": ModelConfig(
        model_type=ModelType.IMAGE_CLASSIFICATION,
        model_path="image_classifier.onnx",
        input_shape=(1, 3, 224, 224),
        output_classes=["normal", "important", "urgent", "error", "alert"],
        preprocessing_config={"target_size": (224, 224)},
        confidence_threshold=0.6
    ),
    
    "audio_classifier": ModelConfig(
        model_type=ModelType.AUDIO_CLASSIFICATION,
        model_path="audio_classifier.onnx",
        input_shape=(1, 160000),  # 10 seconds at 16kHz
        output_classes=["silence", "speech", "music", "noise", "alert"],
        preprocessing_config={"sample_rate": 16000, "max_duration": 10.0},
        confidence_threshold=0.5
    )
}


def create_default_model_manager(models_dir: str = "models") -> ONNXModelManager:
    """Create a model manager with default configurations"""
    manager = ONNXModelManager(models_dir)
    
    # Load default models if they exist
    for model_name, config in DEFAULT_MODEL_CONFIGS.items():
        manager.load_model(model_name, config)
    
    return manager 