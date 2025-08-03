"""
Open Agent Spec Integration for Cortex Intelligence Engine

This module provides the interface for using Cortex as an intelligence engine
in Open Agent Spec, with configuration similar to standard OAS intelligence engines.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

from .core import Cortex, create_simple_cortex, create_cortex_function
from .core import CortexConfig, ProcessingMode
from .layers.layer3 import LLMConfig, LLMProvider


class CortexIntelligenceType(Enum):
    """Cortex intelligence engine types"""
    CORTEX = "cortex"
    CORTEX_ONNX = "cortex-onnx"  # With ONNX models
    CORTEX_HYBRID = "cortex-hybrid"  # Mixed local/external


@dataclass
class CortexOASConfig:
    """Configuration for Cortex as an OAS intelligence engine"""
    # Core Cortex settings
    processing_mode: str = "reactive"  # reactive, proactive, selective
    layer2_threshold: float = 0.6
    enable_layer3: bool = True
    max_processing_time: float = 30.0
    
    # Layer 2 (Internal) settings
    layer2_engine: str = "rule-based"  # rule-based, onnx, local-llm
    layer2_model_path: Optional[str] = None
    layer2_local_llm_url: Optional[str] = None
    
    # Layer 3 (External) settings
    external_engine: str = "openai"  # openai, claude, azure, local
    external_model: str = "gpt-4"
    external_endpoint: str = "https://api.openai.com/v1"
    external_api_key: Optional[str] = None
    
    # LLM Configuration
    temperature: float = 0.7
    max_tokens: int = 150
    timeout: int = 30
    
    # Behavior configuration
    trigger_keywords: Optional[list] = None
    priority_patterns: Optional[list] = None
    custom_actions: Optional[list] = None
    
    def __post_init__(self):
        if self.trigger_keywords is None:
            self.trigger_keywords = [
                "help", "emergency", "urgent", "important", "critical", "alert",
                "error", "failure", "problem", "issue", "warning", "assist"
            ]
        
        if self.priority_patterns is None:
            self.priority_patterns = [
                {"pattern": r"URGENT|CRITICAL|EMERGENCY", "priority": "high"},
                {"pattern": r"ERROR|FAILURE|PROBLEM", "priority": "medium"},
                {"pattern": r"HELP|ASSIST|SUPPORT", "priority": "medium"}
            ]
        
        if self.custom_actions is None:
            self.custom_actions = [
                "analyze_input", "extract_keywords", "classify_intent",
                "suggest_response", "escalate_if_needed"
            ]


class CortexOASIntelligence:
    """
    Cortex Intelligence Engine for Open Agent Spec
    
    This class provides the interface for using Cortex as an intelligence engine
    in Open Agent Spec, with intelligent filtering and routing capabilities.
    """
    
    def __init__(self, config: Union[Dict[str, Any], CortexOASConfig]):
        """
        Initialize Cortex OAS Intelligence Engine
        
        Args:
            config: Configuration dictionary or CortexOASConfig object
        """
        self.logger = logging.getLogger(__name__)
        
        if isinstance(config, dict):
            # Extract the actual config from OAS format
            if "config" in config:
                config_data = config["config"]
            else:
                config_data = config
            
            # Remove any OAS-specific fields that aren't part of CortexOASConfig
            config_data = {k: v for k, v in config_data.items() 
                          if k in CortexOASConfig.__annotations__}
            
            self.config = CortexOASConfig(**config_data)
        else:
            self.config = config
        
        # Initialize Cortex with OAS configuration
        self.cortex = self._create_cortex_instance()
        
        # Set up callbacks for OAS integration
        self._setup_callbacks()
        
        # Processing statistics
        self.stats = {
            "total_requests": 0,
            "layer2_only": 0,
            "layer3_triggered": 0,
            "average_response_time": 0.0
        }
    
    def _create_cortex_instance(self) -> Cortex:
        """Create Cortex instance with OAS configuration"""
        # Convert OAS config to Cortex config
        processing_mode = ProcessingMode(self.config.processing_mode)
        
        cortex_config = CortexConfig(
            processing_mode=processing_mode,
            layer2_threshold=self.config.layer2_threshold,
            enable_layer3=self.config.enable_layer3,
            max_processing_time=self.config.max_processing_time
        )
        
        cortex = Cortex(cortex_config)
        cortex.activate_senses()  # Activate all senses
        
        # Configure Layer 2 (Internal Intelligence)
        self._configure_layer2(cortex)
        
        # Configure Layer 3 (External LLM)
        if self.config.enable_layer3:
            self._configure_layer3(cortex)
        
        return cortex
    
    def _configure_layer2(self, cortex: Cortex):
        """Configure Layer 2 with internal intelligence"""
        if self.config.layer2_engine == "onnx":
            # Try to load ONNX models for Layer 2
            try:
                from .layers.onnx_models import create_default_model_manager
                
                # Create model manager with default models
                model_manager = create_default_model_manager()
                loaded_models = model_manager.list_loaded_models()
                
                if loaded_models:
                    # Configure each interpreter to use ONNX models
                    for interpreter_name in ["vision", "audio", "text"]:
                        if interpreter_name in cortex.layer2.interpreters:
                            interpreter = cortex.layer2.interpreters[interpreter_name]
                            # The load_model method will automatically try to load ONNX models
                            interpreter.load_model("")  # Empty path triggers default model loading
                    
                    self.logger.info(f"Loaded ONNX models: {loaded_models}")
                else:
                    self.logger.warning("No ONNX models found, using rule-based fallback")
                    
            except Exception as e:
                self.logger.error(f"Failed to configure ONNX models: {e}")
        
        elif self.config.layer2_engine == "local-llm" and self.config.layer2_local_llm_url:
            # Configure local LLM for Layer 2
            local_config = LLMConfig(
                provider=LLMProvider.LOCAL,
                api_key="local",
                base_url=self.config.layer2_local_llm_url,
                model="local-model",
                max_tokens=100,
                temperature=0.3
            )
            # Note: This would require extending Layer 2 to use local LLM
    
    def _configure_layer3(self, cortex: Cortex):
        """Configure Layer 3 with external LLM"""
        if not self.config.external_api_key:
            # Try to get from environment
            if self.config.external_engine == "openai":
                self.config.external_api_key = os.getenv("OPENAI_API_KEY")
            elif self.config.external_engine == "claude":
                self.config.external_api_key = os.getenv("CLAUDE_API_KEY")
        
        if self.config.external_api_key:
            if self.config.external_engine == "openai":
                llm_config = LLMConfig(
                    provider=LLMProvider.OPENAI,
                    api_key=self.config.external_api_key,
                    base_url=self.config.external_endpoint,
                    model=self.config.external_model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    timeout=self.config.timeout
                )
            elif self.config.external_engine == "claude":
                llm_config = LLMConfig(
                    provider=LLMProvider.CLAUDE,
                    api_key=self.config.external_api_key,
                    base_url=self.config.external_endpoint,
                    model=self.config.external_model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    timeout=self.config.timeout
                )
            elif self.config.external_engine == "local":
                llm_config = LLMConfig(
                    provider=LLMProvider.LOCAL,
                    api_key="local",
                    base_url=self.config.external_endpoint,
                    model=self.config.external_model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    timeout=self.config.timeout
                )
            else:
                raise ValueError(f"Unsupported external engine: {self.config.external_engine}")
            
            cortex.add_llm_provider(llm_config, is_primary=True)
    
    def _setup_callbacks(self):
        """Set up callbacks for monitoring and control"""
        async def on_reaction_decision(data):
            """Callback when Layer 2 makes a reaction decision"""
            should_react = data.get("should_react", False)
            if should_react:
                self.stats["layer3_triggered"] += 1
            else:
                self.stats["layer2_only"] += 1
        
        self.cortex.add_callback("on_reaction_decision", on_reaction_decision)
    
    async def process(self, 
                     prompt: str, 
                     context: Optional[Dict[str, Any]] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Process input through Cortex intelligence engine
        
        This is the main interface that OAS will call.
        
        Args:
            prompt: Input prompt/command from OAS
            context: Additional context from OAS
            **kwargs: Additional arguments
            
        Returns:
            Dict with response data compatible with OAS
        """
        start_time = asyncio.get_event_loop().time()
        self.stats["total_requests"] += 1
        
        try:
            # Process through Cortex layers
            result = await self.cortex.process_input(
                data=prompt,
                sense_type="text",
                context=json.dumps(context) if context else None,
                task_type=kwargs.get("task_type", "general")
            )
            
            # Calculate response time
            response_time = asyncio.get_event_loop().time() - start_time
            self._update_average_response_time(response_time)
            
            # Format response for OAS
            return {
                "success": result.success,
                "response": result.final_response,
                "actions": result.suggested_actions,
                "metadata": {
                    "layers_used": result.layers_used,
                    "processing_time": result.processing_time,
                    "confidence": result.layer2_output.get("confidence", 0.0) if result.layer2_output else 0.0,
                    "cortex_stats": self.stats.copy(),
                    "triggered_layer3": "layer3" in result.layers_used
                },
                "error": result.error_message
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "actions": [],
                "metadata": {"error": str(e)},
                "error": f"Cortex processing failed: {str(e)}"
            }
    
    def _update_average_response_time(self, new_time: float):
        """Update average response time"""
        total = self.stats["total_requests"]
        current_avg = self.stats["average_response_time"]
        new_avg = ((current_avg * (total - 1)) + new_time) / total
        self.stats["average_response_time"] = new_avg
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of Cortex OAS Intelligence Engine"""
        cortex_status = self.cortex.get_status()
        
        return {
            "engine_type": "cortex",
            "config": asdict(self.config),
            "stats": self.stats.copy(),
            "cortex_status": cortex_status
        }
    
    def reset_stats(self):
        """Reset processing statistics"""
        self.stats = {
            "total_requests": 0,
            "layer2_only": 0,
            "layer3_triggered": 0,
            "average_response_time": 0.0
        }


# Factory functions for easy OAS integration
def create_cortex_oas_intelligence(config: Union[Dict[str, Any], CortexOASConfig]) -> CortexOASIntelligence:
    """
    Create a Cortex OAS Intelligence Engine
    
    Args:
        config: Configuration for the intelligence engine
        
    Returns:
        Configured CortexOASIntelligence instance
    """
    return CortexOASIntelligence(config)


def create_cortex_oas_function(intelligence: CortexOASIntelligence):
    """
    Create an OAS-compatible function from Cortex intelligence engine
    
    Args:
        intelligence: CortexOASIntelligence instance
        
    Returns:
        Function that can be called by OAS
    """
    async def oas_function(prompt: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        return await intelligence.process(prompt, context, **kwargs)
    
    return oas_function


# Example OAS configuration
EXAMPLE_OAS_CONFIG = {
    "type": "cortex",
    "engine": "cortex-hybrid",
    "config": {
        "processing_mode": "reactive",
        "layer2_threshold": 0.6,
        "enable_layer3": True,
        "layer2_engine": "rule-based",
        "external_engine": "openai",
        "external_model": "gpt-4",
        "external_endpoint": "https://api.openai.com/v1",
        "temperature": 0.7,
        "max_tokens": 150,
        "trigger_keywords": ["help", "urgent", "error", "assist"],
        "priority_patterns": [
            {"pattern": "URGENT|CRITICAL", "priority": "high"},
            {"pattern": "ERROR|FAILURE", "priority": "medium"}
        ]
    }
} 