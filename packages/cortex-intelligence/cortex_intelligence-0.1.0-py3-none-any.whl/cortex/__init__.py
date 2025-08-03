"""
Cortex: A three-layer intelligence engine for Open Agent Spec

Layer 1: Raw data senses (eyes/ears) with basic rote functions
Layer 2: Onboard ONNX/LLM for base-level data interpretation  
Layer 3: External LLM vendor calls for complex reasoning
"""

from .core import Cortex, create_simple_cortex, create_cortex_function
from .layers.layer1 import SenseLayer
from .layers.layer2 import InterpretationLayer
from .layers.layer3 import ReasoningLayer
from .oas_integration import (
    CortexOASIntelligence, 
    CortexOASConfig, 
    create_cortex_oas_intelligence,
    create_cortex_oas_function,
    EXAMPLE_OAS_CONFIG
)
from .layers.onnx_models import (
    ONNXModelManager,
    ONNXInference,
    create_default_model_manager,
    DEFAULT_MODEL_CONFIGS,
    ModelConfig,
    ModelType
)

__version__ = "0.1.0"
__all__ = [
    "Cortex", 
    "SenseLayer", 
    "InterpretationLayer", 
    "ReasoningLayer", 
    "create_simple_cortex", 
    "create_cortex_function",
    "CortexOASIntelligence",
    "CortexOASConfig", 
    "create_cortex_oas_intelligence",
    "create_cortex_oas_function",
    "EXAMPLE_OAS_CONFIG",
    "ONNXModelManager",
    "ONNXInference",
    "create_default_model_manager",
    "DEFAULT_MODEL_CONFIGS",
    "ModelConfig",
    "ModelType"
]