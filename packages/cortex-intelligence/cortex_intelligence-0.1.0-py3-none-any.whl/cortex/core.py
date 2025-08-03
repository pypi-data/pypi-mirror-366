"""
Cortex Core: Main intelligence engine that integrates all three layers
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from .layers.layer1 import SenseLayer
from .layers.layer2 import InterpretationLayer, ReactionLevel
from .layers.layer3 import ReasoningLayer, LLMConfig, LLMProvider


class ProcessingMode(Enum):
    """Processing modes for Cortex"""
    REACTIVE = "reactive"  # React only when Layer 2 decides
    PROACTIVE = "proactive"  # Always process through all layers
    SELECTIVE = "selective"  # Use custom filtering logic


@dataclass
class CortexConfig:
    """Configuration for Cortex intelligence engine"""
    processing_mode: ProcessingMode = ProcessingMode.REACTIVE
    layer2_threshold: float = 0.5
    enable_layer3: bool = True
    max_processing_time: float = 30.0  # seconds
    enable_learning: bool = False
    memory_size: int = 1000


@dataclass
class ProcessingResult:
    """Result of processing through Cortex layers"""
    success: bool
    input_data: Dict[str, Any]
    layer1_output: Dict[str, Any]
    layer2_output: Optional[Dict[str, Any]] = None
    layer3_output: Optional[Dict[str, Any]] = None
    final_response: str = ""
    suggested_actions: List[str] = None
    processing_time: float = 0.0
    layers_used: List[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.suggested_actions is None:
            self.suggested_actions = []
        if self.layers_used is None:
            self.layers_used = []


class Cortex:
    """
    Main Cortex intelligence engine
    
    Integrates three layers:
    1. SenseLayer: Raw data processing
    2. InterpretationLayer: Base-level interpretation and reaction decisions
    3. ReasoningLayer: External LLM reasoning for complex tasks
    """
    
    def __init__(self, config: CortexConfig = None):
        self.config = config or CortexConfig()
        
        # Initialize layers
        self.layer1 = SenseLayer()
        self.layer2 = InterpretationLayer(self.config.layer2_threshold)
        self.layer3 = ReasoningLayer() if self.config.enable_layer3 else None
        
        # Processing state
        self.is_running = False
        self.processing_queue = asyncio.Queue()
        self.processing_history = []
        self.performance_metrics = {
            "total_processed": 0,
            "layer1_processed": 0,
            "layer2_reactions": 0,
            "layer3_reasoning": 0,
            "average_processing_time": 0.0,
            "errors": 0
        }
        
        # Callbacks for different events
        self.callbacks = {
            "on_input": [],
            "on_layer1_complete": [],
            "on_reaction_decision": [],
            "on_reasoning_complete": [],
            "on_final_response": [],
            "on_error": []
        }
    
    def add_llm_provider(self, config: LLMConfig, is_primary: bool = False):
        """Add an LLM provider to Layer 3"""
        if not self.layer3:
            raise ValueError("Layer 3 is disabled. Enable it in CortexConfig.")
        self.layer3.add_provider(config, is_primary)
    
    def add_callback(self, event: str, callback: Callable):
        """Add callback for processing events"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
        else:
            raise ValueError(f"Unknown event: {event}")
    
    def activate_senses(self, senses: List[str] = None):
        """Activate specific senses or all senses"""
        if senses:
            for sense in senses:
                self.layer1.activate_sense(sense)
        else:
            self.layer1.activate_all()
    
    async def process_input(self, 
                           data: Any, 
                           sense_type: Optional[str] = None,
                           context: Optional[str] = None,
                           task_type: str = "general") -> ProcessingResult:
        """
        Process input through the Cortex intelligence pipeline
        
        Args:
            data: Input data (image, audio, text, etc.)
            sense_type: Specific sense to use for Layer 1
            context: Additional context for processing
            task_type: Type of task for Layer 3 reasoning
            
        Returns:
            ProcessingResult with outputs from each layer
        """
        start_time = time.time()
        result = ProcessingResult(
            success=False,
            input_data={"data_type": str(type(data)), "timestamp": start_time},
            layer1_output={},
            layers_used=[]
        )
        
        try:
            # Trigger input callbacks
            await self._trigger_callbacks("on_input", data)
            
            # Layer 1: Sensory processing
            layer1_output = self.layer1.process_input(data, sense_type)
            result.layer1_output = layer1_output
            result.layers_used.append("layer1")
            self.performance_metrics["layer1_processed"] += 1
            
            if "error" in layer1_output:
                result.error_message = f"Layer 1 error: {layer1_output['error']}"
                return result
            
            await self._trigger_callbacks("on_layer1_complete", layer1_output)
            
            # Layer 2: Interpretation and reaction decision
            if self._should_use_layer2():
                interpretation_result = await self.layer2.interpret_and_decide(layer1_output)
                result.layer2_output = interpretation_result.to_dict()
                result.layers_used.append("layer2")
                
                # Check if we should react
                should_proceed = self._should_proceed_to_layer3(interpretation_result, result)
                
                await self._trigger_callbacks("on_reaction_decision", {
                    "should_react": interpretation_result.should_react,
                    "reaction_level": interpretation_result.reaction_level.name,
                    "will_proceed": should_proceed
                })
                
                if not should_proceed:
                    result.success = True
                    result.final_response = interpretation_result.reasoning
                    result.suggested_actions = interpretation_result.suggested_actions
                    result.processing_time = time.time() - start_time
                    
                    # Update performance metrics
                    self.performance_metrics["total_processed"] += 1
                    self._update_average_processing_time(result.processing_time)
                    
                    # Store in history
                    self._add_to_history(result)
                    
                    return result
                
                self.performance_metrics["layer2_reactions"] += 1
            
            # Layer 3: External LLM reasoning
            if self.layer3 and self.config.enable_layer3:
                reasoning_response = await self.layer3.reason(
                    sensory_data=layer1_output,
                    interpretation_result=result.layer2_output or {},
                    context=context,
                    task_type=task_type
                )
                
                result.layer3_output = asdict(reasoning_response)
                result.layers_used.append("layer3")
                
                if reasoning_response.success:
                    result.final_response = reasoning_response.response_text
                    result.suggested_actions.extend(reasoning_response.suggested_actions)
                    self.performance_metrics["layer3_reasoning"] += 1
                else:
                    result.error_message = reasoning_response.error_message
                
                await self._trigger_callbacks("on_reasoning_complete", reasoning_response)
            
            result.success = True
            result.processing_time = time.time() - start_time
            
            # Update performance metrics
            self.performance_metrics["total_processed"] += 1
            self._update_average_processing_time(result.processing_time)
            
            await self._trigger_callbacks("on_final_response", result)
            
        except Exception as e:
            result.error_message = f"Processing error: {str(e)}"
            result.processing_time = time.time() - start_time
            self.performance_metrics["errors"] += 1
            await self._trigger_callbacks("on_error", {"error": str(e), "result": result})
        
        # Store in history
        self._add_to_history(result)
        
        return result
    
    def _should_use_layer2(self) -> bool:
        """Determine if Layer 2 should be used"""
        return self.config.processing_mode in [ProcessingMode.REACTIVE, ProcessingMode.PROACTIVE]
    
    def _should_proceed_to_layer3(self, interpretation_result, current_result) -> bool:
        """Determine if processing should continue to Layer 3"""
        if not self.layer3 or not self.config.enable_layer3:
            return False
        
        if self.config.processing_mode == ProcessingMode.PROACTIVE:
            return True
        elif self.config.processing_mode == ProcessingMode.REACTIVE:
            return interpretation_result.should_react
        else:  # SELECTIVE
            # Custom logic can be implemented here
            return interpretation_result.reaction_level in [ReactionLevel.HIGH, ReactionLevel.CRITICAL]
    
    async def _trigger_callbacks(self, event: str, data: Any):
        """Trigger callbacks for an event"""
        for callback in self.callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                print(f"Callback error for {event}: {e}")
    
    def _update_average_processing_time(self, new_time: float):
        """Update average processing time metric"""
        total = self.performance_metrics["total_processed"]
        current_avg = self.performance_metrics["average_processing_time"]
        new_avg = ((current_avg * (total - 1)) + new_time) / total
        self.performance_metrics["average_processing_time"] = new_avg
    
    def _add_to_history(self, result: ProcessingResult):
        """Add processing result to history"""
        self.processing_history.append({
            "timestamp": time.time(),
            "result": asdict(result),
            "success": result.success
        })
        
        # Maintain history size based on config
        max_history = getattr(self.config, 'memory_size', 1000)
        if len(self.processing_history) > max_history:
            self.processing_history.pop(0)
    
    async def batch_process(self, inputs: List[Dict[str, Any]]) -> List[ProcessingResult]:
        """Process multiple inputs in batch"""
        tasks = []
        for input_item in inputs:
            data = input_item.get("data")
            sense_type = input_item.get("sense_type")
            context = input_item.get("context")
            task_type = input_item.get("task_type", "general")
            
            task = self.process_input(data, sense_type, context, task_type)
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all Cortex components"""
        status = {
            "cortex": {
                "config": asdict(self.config),
                "is_running": self.is_running,
                "performance_metrics": self.performance_metrics.copy()
            },
            "layer1": self.layer1.get_status(),
            "layer2": self.layer2.get_status()
        }
        
        if self.layer3:
            status["layer3"] = self.layer3.get_status()
        
        return status
    
    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent processing history"""
        return self.processing_history[-limit:] if self.processing_history else []
    
    def reset_metrics(self):
        """Reset performance metrics"""
        self.performance_metrics = {
            "total_processed": 0,
            "layer1_processed": 0,
            "layer2_reactions": 0,
            "layer3_reasoning": 0,
            "average_processing_time": 0.0,
            "errors": 0
        }
    
    def configure_layer2_sensitivity(self, threshold: float):
        """Adjust Layer 2 sensitivity threshold"""
        self.layer2.adjust_sensitivity(threshold)
        self.config.layer2_threshold = threshold


# Open Agent Spec Interface Functions
def create_cortex_function(cortex_instance: Cortex):
    """
    Create a function compatible with Open Agent Spec
    
    Returns a function that can be called by Open Agent Spec with prompts/commands
    """
    
    async def cortex_intelligence_function(prompt: str, 
                                         context: Dict[str, Any] = None,
                                         **kwargs) -> Dict[str, Any]:
        """
        Open Agent Spec compatible function for Cortex
        
        Args:
            prompt: Input prompt/command from Open Agent Spec
            context: Additional context from Open Agent Spec
            **kwargs: Additional arguments
            
        Returns:
            Dict with response data compatible with Open Agent Spec
        """
        try:
            # Process the prompt as text input
            result = await cortex_instance.process_input(
                data=prompt,
                sense_type="text",
                context=json.dumps(context) if context else None,
                task_type=kwargs.get("task_type", "general")
            )
            
            # Format response for Open Agent Spec
            return {
                "success": result.success,
                "response": result.final_response,
                "actions": result.suggested_actions,
                "metadata": {
                    "layers_used": result.layers_used,
                    "processing_time": result.processing_time,
                    "confidence": result.layer2_output.get("confidence", 0.0) if result.layer2_output else 0.0
                },
                "error": result.error_message
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "actions": [],
                "metadata": {},
                "error": f"Cortex processing failed: {str(e)}"
            }
    
    return cortex_intelligence_function


def create_simple_cortex(openai_api_key: str = None, 
                        claude_api_key: str = None,
                        enable_layer3: bool = True) -> Cortex:
    """
    Create a simple Cortex instance with basic configuration
    
    Args:
        openai_api_key: OpenAI API key (optional)
        claude_api_key: Claude API key (optional)
        enable_layer3: Whether to enable Layer 3 reasoning
        
    Returns:
        Configured Cortex instance
    """
    config = CortexConfig(
        processing_mode=ProcessingMode.REACTIVE,
        layer2_threshold=0.6,
        enable_layer3=enable_layer3
    )
    
    cortex = Cortex(config)
    cortex.activate_senses()  # Activate all senses
    
    # Add LLM providers if API keys are provided
    if enable_layer3:
        if openai_api_key:
            openai_config = LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key=openai_api_key,
                model="gpt-3.5-turbo",
                max_tokens=500,
                temperature=0.7
            )
            cortex.add_llm_provider(openai_config, is_primary=True)
        
        if claude_api_key:
            claude_config = LLMConfig(
                provider=LLMProvider.CLAUDE,
                api_key=claude_api_key,
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                temperature=0.7
            )
            cortex.add_llm_provider(claude_config, is_primary=not openai_api_key)
    
    return cortex