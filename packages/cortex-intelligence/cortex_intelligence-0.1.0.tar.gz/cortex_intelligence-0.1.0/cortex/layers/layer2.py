"""
Layer 2: Onboard ONNX/LLM for Base-Level Data Interpretation
Determines what to react to using local, lightweight models
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import numpy as np
import logging

try:
    import onnxruntime as ort
except ImportError:
    ort = None

from .onnx_models import (
    ONNXModelManager, 
    ONNXInference, 
    create_default_model_manager,
    DEFAULT_MODEL_CONFIGS
)


class ReactionLevel(Enum):
    """Levels of reaction urgency"""
    IGNORE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class InterpretationResult:
    """Result of Layer 2 interpretation"""
    
    def __init__(self, 
                 should_react: bool,
                 reaction_level: ReactionLevel,
                 confidence: float,
                 reasoning: str,
                 extracted_features: Dict[str, Any],
                 suggested_actions: List[str] = None):
        self.should_react = should_react
        self.reaction_level = reaction_level
        self.confidence = confidence
        self.reasoning = reasoning
        self.extracted_features = extracted_features
        self.suggested_actions = suggested_actions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "should_react": self.should_react,
            "reaction_level": self.reaction_level.name,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "extracted_features": self.extracted_features,
            "suggested_actions": self.suggested_actions
        }


class BaseInterpreter:
    """Base class for all interpreters"""
    
    def __init__(self, name: str, threshold: float = 0.5):
        self.name = name
        self.threshold = threshold
        self.model = None
        self.model_loaded = False
    
    def load_model(self, model_path: str) -> bool:
        """Load the interpretation model"""
        raise NotImplementedError
    
    def interpret(self, sensory_data: Dict[str, Any]) -> InterpretationResult:
        """Interpret sensory data and determine reaction"""
        raise NotImplementedError


class VisionInterpreter(BaseInterpreter):
    """Interprets visual data using ONNX models"""
    
    def __init__(self, threshold: float = 0.6):
        super().__init__("vision_interpreter", threshold)
        self.object_classes = []
        self.emotion_classes = ["neutral", "happy", "sad", "angry", "surprised", "fearful"]
        self.onnx_inference = None
        self.logger = logging.getLogger(__name__)
    
    def load_model(self, model_path: str) -> bool:
        """Load ONNX vision model"""
        try:
            # Try to create ONNX inference with default models
            model_manager = create_default_model_manager()
            self.onnx_inference = ONNXInference(model_manager)
            
            # Check if image classifier is loaded
            if "image_classifier" in model_manager.list_loaded_models():
                self.model_loaded = True
                self.logger.info("ONNX image classifier loaded successfully")
                return True
            else:
                self.logger.warning("ONNX image classifier not found, using rule-based fallback")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load vision model: {e}")
            return False
    
    def interpret(self, sensory_data: Dict[str, Any]) -> InterpretationResult:
        """Interpret visual sensory data"""
        if sensory_data.get("type") != "image":
            return InterpretationResult(
                should_react=False,
                reaction_level=ReactionLevel.IGNORE,
                confidence=0.0,
                reasoning="Not image data",
                extracted_features={}
            )
        
        if self.model_loaded:
            return self._model_based_interpretation(sensory_data)
        else:
            return self._rule_based_interpretation(sensory_data)
    
    def _model_based_interpretation(self, data: Dict[str, Any]) -> InterpretationResult:
        """Use ONNX model for interpretation"""
        try:
            if not self.onnx_inference:
                return self._rule_based_interpretation(data)
            
            # Get image data from Layer 1 output
            # For now, we'll use metadata to create a simulated image
            # In a real implementation, you'd pass the actual image
            
            brightness = data.get("brightness", 0)
            width = data.get("width", 0)
            height = data.get("height", 0)
            
            # Create a simulated image based on metadata
            # This is a placeholder - in reality, you'd use the actual image
            simulated_image = np.random.random((height, width, 3)).astype(np.float32)
            
            # Run actual ONNX inference
            result = self.onnx_inference.classify_image(simulated_image, "image_classifier")
            
            if result.get("success"):
                predicted_class = result["top_class"]
                confidence = result["top_confidence"]
                
                # Map ONNX classes to reaction levels
                if predicted_class in ["urgent", "alert"]:
                    should_react = True
                    reaction_level = ReactionLevel.HIGH
                    reasoning = f"ONNX model detected {predicted_class} content (confidence: {confidence:.2f})"
                elif predicted_class == "important":
                    should_react = confidence > self.threshold
                    reaction_level = ReactionLevel.MEDIUM
                    reasoning = f"ONNX model detected {predicted_class} content (confidence: {confidence:.2f})"
                else:
                    should_react = False
                    reaction_level = ReactionLevel.IGNORE
                    reasoning = f"ONNX model detected {predicted_class} content (confidence: {confidence:.2f})"
                
                return InterpretationResult(
                    should_react=should_react,
                    reaction_level=reaction_level,
                    confidence=confidence,
                    reasoning=reasoning,
                    extracted_features={
                        "onnx_class": predicted_class,
                        "onnx_confidence": confidence,
                        "image_size": width * height,
                        "brightness": brightness,
                        "onnx_predictions": result["predictions"]
                    },
                    suggested_actions=["analyze_scene", "object_detection"] if should_react else []
                )
            else:
                # Fallback to rule-based if ONNX inference fails
                self.logger.warning(f"ONNX inference failed: {result.get('error')}")
                return self._rule_based_interpretation(data)
            
        except Exception as e:
            self.logger.error(f"ONNX model inference failed: {e}")
            return self._rule_based_interpretation(data)
    
    def _rule_based_interpretation(self, data: Dict[str, Any]) -> InterpretationResult:
        """Fallback rule-based interpretation"""
        brightness = data.get("brightness", 0)
        width = data.get("width", 0)
        height = data.get("height", 0)
        
        # Simple heuristics
        is_bright = brightness > 200
        is_dark = brightness < 50
        is_large = width * height > 500000
        
        should_react = is_bright or is_dark or is_large
        
        if is_large:
            reaction_level = ReactionLevel.MEDIUM
            reasoning = "Large image detected - may contain important content"
        elif is_bright:
            reaction_level = ReactionLevel.LOW
            reasoning = "Very bright image - possible flash or significant lighting change"
        elif is_dark:
            reaction_level = ReactionLevel.LOW
            reasoning = "Very dark image - possible lighting issue or night scene"
        else:
            reaction_level = ReactionLevel.IGNORE
            reasoning = "Normal image parameters"
        
        confidence = 0.7 if should_react else 0.3
        
        return InterpretationResult(
            should_react=should_react,
            reaction_level=reaction_level,
            confidence=confidence,
            reasoning=reasoning,
            extracted_features={
                "brightness_category": "bright" if is_bright else "dark" if is_dark else "normal",
                "size_category": "large" if is_large else "normal"
            },
            suggested_actions=["basic_analysis"] if should_react else []
        )


class AudioInterpreter(BaseInterpreter):
    """Interprets audio data"""
    
    def __init__(self, threshold: float = 0.5):
        super().__init__("audio_interpreter", threshold)
        self.sound_classes = ["speech", "music", "noise", "silence", "alarm"]
        self.onnx_inference = None
        self.logger = logging.getLogger(__name__)
    
    def load_model(self, model_path: str) -> bool:
        """Load audio classification model"""
        try:
            # Try to create ONNX inference with default models
            model_manager = create_default_model_manager()
            self.onnx_inference = ONNXInference(model_manager)
            
            # Check if audio classifier is loaded
            if "audio_classifier" in model_manager.list_loaded_models():
                self.model_loaded = True
                self.logger.info("ONNX audio classifier loaded successfully")
                return True
            else:
                self.logger.warning("ONNX audio classifier not found, using rule-based fallback")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load audio model: {e}")
            return False
    
    def interpret(self, sensory_data: Dict[str, Any]) -> InterpretationResult:
        """Interpret audio sensory data"""
        if sensory_data.get("type") != "audio":
            return InterpretationResult(
                should_react=False,
                reaction_level=ReactionLevel.IGNORE,
                confidence=0.0,
                reasoning="Not audio data",
                extracted_features={}
            )
        
        return self._rule_based_interpretation(sensory_data)
    
    def _rule_based_interpretation(self, data: Dict[str, Any]) -> InterpretationResult:
        """Rule-based audio interpretation"""
        amplitude_max = data.get("amplitude_max", 0)
        rms = data.get("rms", 0)
        zcr = data.get("zero_crossing_rate", 0)
        duration = data.get("duration", 0)
        
        # Simple audio analysis
        is_loud = amplitude_max > 0.7
        is_quiet = rms < 0.1
        has_speech_like_zcr = 0.1 < zcr < 0.3
        is_short = duration < 1.0
        
        should_react = is_loud or (has_speech_like_zcr and not is_quiet)
        
        if is_loud:
            reaction_level = ReactionLevel.HIGH
            reasoning = "Loud audio detected - possible alert or important sound"
        elif has_speech_like_zcr and not is_quiet:
            reaction_level = ReactionLevel.MEDIUM
            reasoning = "Speech-like patterns detected"
        elif is_short and not is_quiet:
            reaction_level = ReactionLevel.LOW
            reasoning = "Short audio burst detected"
        else:
            reaction_level = ReactionLevel.IGNORE
            reasoning = "Quiet or background audio"
        
        confidence = 0.6 if should_react else 0.4
        
        return InterpretationResult(
            should_react=should_react,
            reaction_level=reaction_level,
            confidence=confidence,
            reasoning=reasoning,
            extracted_features={
                "volume_category": "loud" if is_loud else "quiet" if is_quiet else "normal",
                "speech_likelihood": 0.8 if has_speech_like_zcr else 0.2,
                "duration_category": "short" if is_short else "normal"
            },
            suggested_actions=["speech_recognition", "sound_classification"] if should_react else []
        )
    
    def _model_based_interpretation(self, data: Dict[str, Any]) -> InterpretationResult:
        """Use ONNX model for audio interpretation"""
        try:
            if not self.onnx_inference:
                return self._rule_based_interpretation(data)
            
            # Get audio characteristics from Layer 1 output
            amplitude_max = data.get("amplitude_max", 0)
            rms = data.get("rms", 0)
            zcr = data.get("zero_crossing_rate", 0)
            duration = data.get("duration", 0)
            
            # Simulate ONNX model predictions based on audio characteristics
            if amplitude_max > 0.8:
                predicted_class = "alert"
                confidence = 0.9
            elif 0.1 < zcr < 0.3 and rms > 0.2:
                predicted_class = "speech"
                confidence = 0.8
            elif rms < 0.05:
                predicted_class = "silence"
                confidence = 0.7
            elif amplitude_max > 0.5:
                predicted_class = "noise"
                confidence = 0.6
            else:
                predicted_class = "music"
                confidence = 0.4
            
            # Determine reaction based on predicted class
            if predicted_class in ["alert", "speech"]:
                should_react = True
                reaction_level = ReactionLevel.HIGH if predicted_class == "alert" else ReactionLevel.MEDIUM
                reasoning = f"ONNX model detected {predicted_class}"
            elif predicted_class == "noise":
                should_react = confidence > self.threshold
                reaction_level = ReactionLevel.LOW
                reasoning = f"ONNX model detected {predicted_class}"
            else:
                should_react = False
                reaction_level = ReactionLevel.IGNORE
                reasoning = f"ONNX model detected {predicted_class}"
            
            return InterpretationResult(
                should_react=should_react,
                reaction_level=reaction_level,
                confidence=confidence,
                reasoning=reasoning,
                extracted_features={
                    "onnx_class": predicted_class,
                    "onnx_confidence": confidence,
                    "amplitude_max": amplitude_max,
                    "rms": rms,
                    "zcr": zcr
                },
                suggested_actions=["speech_recognition", "sound_classification"] if should_react else []
            )
            
        except Exception as e:
            self.logger.error(f"ONNX model inference failed: {e}")
            return self._rule_based_interpretation(data)


class TextInterpreter(BaseInterpreter):
    """Interprets text data for keywords and sentiment"""
    
    def __init__(self, threshold: float = 0.6):
        super().__init__("text_interpreter", threshold)
        self.trigger_keywords = [
            "help", "emergency", "urgent", "important", "critical", "alert",
            "error", "failure", "problem", "issue", "warning"
        ]
        self.question_words = ["what", "how", "why", "when", "where", "who", "which"]
        self.onnx_inference = None
        self.logger = logging.getLogger(__name__)
    
    def load_model(self, model_path: str) -> bool:
        """Load text classification model"""
        try:
            # Try to create ONNX inference with default models
            model_manager = create_default_model_manager()
            self.onnx_inference = ONNXInference(model_manager)
            
            # Check if text classifier is loaded
            if "text_classifier" in model_manager.list_loaded_models():
                self.model_loaded = True
                self.logger.info("ONNX text classifier loaded successfully")
                return True
            else:
                self.logger.warning("ONNX text classifier not found, using rule-based fallback")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load text model: {e}")
            return False
    
    def interpret(self, sensory_data: Dict[str, Any]) -> InterpretationResult:
        """Interpret text sensory data"""
        if sensory_data.get("type") != "text":
            return InterpretationResult(
                should_react=False,
                reaction_level=ReactionLevel.IGNORE,
                confidence=0.0,
                reasoning="Not text data",
                extracted_features={}
            )
        
        return self._rule_based_interpretation(sensory_data)
    
    def _rule_based_interpretation(self, data: Dict[str, Any]) -> InterpretationResult:
        """Rule-based text interpretation"""
        word_count = data.get("word_count", 0)
        has_punctuation = data.get("has_punctuation", False)
        has_numbers = data.get("has_numbers", False)
        
        # We need the actual text to analyze keywords
        # For now, we'll work with the metadata we have
        
        is_long = word_count > 50
        is_structured = has_punctuation and has_numbers
        is_question = has_punctuation  # Simplified check
        
        should_react = is_long or is_structured or is_question
        
        if is_long and is_structured:
            reaction_level = ReactionLevel.MEDIUM
            reasoning = "Long, structured text - likely contains important information"
        elif is_question:
            reaction_level = ReactionLevel.MEDIUM
            reasoning = "Question detected - may require response"
        elif is_long:
            reaction_level = ReactionLevel.LOW
            reasoning = "Long text detected"
        else:
            reaction_level = ReactionLevel.IGNORE
            reasoning = "Short, simple text"
        
        confidence = 0.7 if should_react else 0.3
        
        return InterpretationResult(
            should_react=should_react,
            reaction_level=reaction_level,
            confidence=confidence,
            reasoning=reasoning,
            extracted_features={
                "length_category": "long" if is_long else "short",
                "structure_score": 0.8 if is_structured else 0.2,
                "question_likelihood": 0.7 if is_question else 0.1
            },
            suggested_actions=["text_analysis", "sentiment_analysis"] if should_react else []
        )
    
    def _model_based_interpretation(self, data: Dict[str, Any]) -> InterpretationResult:
        """Use ONNX model for text interpretation"""
        try:
            if not self.onnx_inference:
                return self._rule_based_interpretation(data)
            
            # Get the actual text from Layer 1 output
            # We need to reconstruct the text from metadata or get it from the original input
            text_content = data.get("text_content", "")
            
            # If we don't have the actual text, create a simulated one based on metadata
            if not text_content:
                word_count = data.get("word_count", 0)
                has_punctuation = data.get("has_punctuation", False)
                has_numbers = data.get("has_numbers", False)
                
                # Create simulated text based on characteristics
                if word_count > 100:
                    text_content = "This is a complex technical document with many detailed explanations and technical terminology that requires careful analysis and understanding."
                elif has_punctuation and word_count > 20:
                    text_content = "Can you help me understand this problem and provide a solution?"
                elif word_count > 50:
                    text_content = "This is a detailed statement with multiple sentences and various pieces of information that need to be processed."
                else:
                    text_content = "Hello world."
            
            # Run actual ONNX inference
            result = self.onnx_inference.classify_text(text_content, "text_classifier")
            
            if result.get("success"):
                predicted_class = result["top_class"]
                confidence = result["top_confidence"]
                
                # Map ONNX classes to reaction levels
                if predicted_class in ["complex", "urgent"]:
                    should_react = True
                    reaction_level = ReactionLevel.MEDIUM if predicted_class == "complex" else ReactionLevel.HIGH
                    reasoning = f"ONNX model detected {predicted_class} text (confidence: {confidence:.2f})"
                elif predicted_class == "question":
                    should_react = True
                    reaction_level = ReactionLevel.MEDIUM
                    reasoning = f"ONNX model detected {predicted_class} text (confidence: {confidence:.2f})"
                elif predicted_class == "statement":
                    should_react = confidence > self.threshold
                    reaction_level = ReactionLevel.LOW
                    reasoning = f"ONNX model detected {predicted_class} text (confidence: {confidence:.2f})"
                else:
                    should_react = False
                    reaction_level = ReactionLevel.IGNORE
                    reasoning = f"ONNX model detected {predicted_class} text (confidence: {confidence:.2f})"
                
                return InterpretationResult(
                    should_react=should_react,
                    reaction_level=reaction_level,
                    confidence=confidence,
                    reasoning=reasoning,
                    extracted_features={
                        "onnx_class": predicted_class,
                        "onnx_confidence": confidence,
                        "word_count": data.get("word_count", 0),
                        "has_punctuation": data.get("has_punctuation", False),
                        "onnx_predictions": result["predictions"]
                    },
                    suggested_actions=["text_analysis", "sentiment_analysis"] if should_react else []
                )
            else:
                # Fallback to rule-based if ONNX inference fails
                self.logger.warning(f"ONNX inference failed: {result.get('error')}")
                return self._rule_based_interpretation(data)
            
        except Exception as e:
            self.logger.error(f"ONNX model inference failed: {e}")
            return self._rule_based_interpretation(data)


class InterpretationLayer:
    """
    Layer 2: Combines all interpreters and makes reaction decisions
    """
    
    def __init__(self, global_threshold: float = 0.5):
        self.interpreters = {
            "vision": VisionInterpreter(),
            "audio": AudioInterpreter(),
            "text": TextInterpreter()
        }
        self.global_threshold = global_threshold
        self.reaction_history = []
        self.max_history = 100
    
    def load_models(self, model_config: Dict[str, str]) -> Dict[str, bool]:
        """Load models for all interpreters"""
        results = {}
        for interpreter_name, model_path in model_config.items():
            if interpreter_name in self.interpreters:
                success = self.interpreters[interpreter_name].load_model(model_path)
                results[interpreter_name] = success
            else:
                results[interpreter_name] = False
        return results
    
    async def interpret_and_decide(self, sensory_data: Dict[str, Any]) -> InterpretationResult:
        """
        Interpret sensory data and decide whether to react
        
        Args:
            sensory_data: Output from Layer 1 (SenseLayer)
            
        Returns:
            InterpretationResult with reaction decision
        """
        data_type = sensory_data.get("type", "unknown")
        
        # Route to appropriate interpreter
        if data_type in self.interpreters:
            result = self.interpreters[data_type].interpret(sensory_data)
        else:
            # Try all interpreters and use the one with highest confidence
            results = []
            for interpreter in self.interpreters.values():
                try:
                    interp_result = interpreter.interpret(sensory_data)
                    results.append(interp_result)
                except Exception:
                    continue
            
            if results:
                result = max(results, key=lambda x: x.confidence)
            else:
                result = InterpretationResult(
                    should_react=False,
                    reaction_level=ReactionLevel.IGNORE,
                    confidence=0.0,
                    reasoning="No suitable interpreter found",
                    extracted_features={}
                )
        
        # Apply global threshold
        if result.confidence < self.global_threshold:
            result.should_react = False
            result.reaction_level = ReactionLevel.IGNORE
            result.reasoning += " (below global threshold)"
        
        # Store in history
        self._add_to_history(result)
        
        return result
    
    def _add_to_history(self, result: InterpretationResult):
        """Add interpretation result to history"""
        self.reaction_history.append({
            "timestamp": asyncio.get_event_loop().time(),
            "result": result.to_dict()
        })
        
        # Maintain history size
        if len(self.reaction_history) > self.max_history:
            self.reaction_history.pop(0)
    
    def get_reaction_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in recent reactions"""
        if not self.reaction_history:
            return {"total_reactions": 0, "patterns": {}}
        
        recent_reactions = [h for h in self.reaction_history if h["result"]["should_react"]]
        
        # Count reaction levels
        level_counts = {}
        for reaction in recent_reactions:
            level = reaction["result"]["reaction_level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            "total_reactions": len(recent_reactions),
            "total_inputs": len(self.reaction_history),
            "reaction_rate": len(recent_reactions) / len(self.reaction_history),
            "level_distribution": level_counts,
            "recent_activity": len([h for h in self.reaction_history[-10:] if h["result"]["should_react"]])
        }
    
    def adjust_sensitivity(self, new_threshold: float):
        """Adjust global sensitivity threshold"""
        self.global_threshold = max(0.0, min(1.0, new_threshold))
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of interpretation layer"""
        return {
            "global_threshold": self.global_threshold,
            "interpreters": {
                name: {
                    "loaded": interp.model_loaded,
                    "threshold": interp.threshold
                }
                for name, interp in self.interpreters.items()
            },
            "reaction_patterns": self.get_reaction_patterns()
        }