"""
Basic tests for Cortex intelligence engine
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, AsyncMock
from PIL import Image

from cortex import Cortex, create_simple_cortex, create_cortex_function
from cortex.core import CortexConfig, ProcessingMode
from cortex.layers.layer1 import SenseLayer, VisionSense, AudioSense, TextSense
from cortex.layers.layer2 import InterpretationLayer, ReactionLevel
from cortex.layers.layer3 import ReasoningLayer, LLMConfig, LLMProvider


class TestSenseLayer:
    """Test Layer 1 - Sensory processing"""
    
    def test_sense_layer_initialization(self):
        """Test SenseLayer initialization"""
        layer = SenseLayer()
        assert len(layer.senses) == 3
        assert "vision" in layer.senses
        assert "audio" in layer.senses
        assert "text" in layer.senses
        assert len(layer.active_senses) == 0
    
    def test_activate_senses(self):
        """Test sense activation"""
        layer = SenseLayer()
        layer.activate_sense("vision")
        assert "vision" in layer.active_senses
        assert layer.senses["vision"].active
        
        layer.activate_all()
        assert len(layer.active_senses) == 3
    
    def test_text_processing(self):
        """Test text processing"""
        layer = SenseLayer()
        layer.activate_sense("text")
        
        result = layer.process_input("Hello world! This is a test message.")
        
        assert result["type"] == "text"
        assert result["processed"] == True
        assert result["word_count"] > 0
        assert result["char_count"] > 0
    
    def test_image_processing(self):
        """Test image processing"""
        layer = SenseLayer()
        layer.activate_sense("vision")
        
        # Create test image
        test_image = Image.new('RGB', (100, 100), color='red')
        result = layer.process_input(test_image)
        
        assert result["type"] == "image"
        assert result["processed"] == True
        assert result["width"] == 100
        assert result["height"] == 100
    
    def test_audio_processing(self):
        """Test audio processing"""
        layer = SenseLayer()
        layer.activate_sense("audio")
        
        # Create test audio data
        audio_data = np.random.rand(1000).astype(np.float32)
        result = layer.process_input(audio_data, "audio")
        
        assert result["type"] == "audio"
        assert result["processed"] == True
        assert "duration" in result
        assert "amplitude_mean" in result


class TestInterpretationLayer:
    """Test Layer 2 - Interpretation"""
    
    @pytest.fixture
    def interpretation_layer(self):
        return InterpretationLayer(global_threshold=0.5)
    
    @pytest.mark.asyncio
    async def test_text_interpretation(self, interpretation_layer):
        """Test text interpretation"""
        sensory_data = {
            "type": "text",
            "word_count": 100,
            "has_punctuation": True,
            "has_numbers": True,
            "processed": True
        }
        
        result = await interpretation_layer.interpret_and_decide(sensory_data)
        
        assert result.confidence > 0
        assert isinstance(result.should_react, bool)
        assert result.reaction_level in ReactionLevel
    
    @pytest.mark.asyncio
    async def test_image_interpretation(self, interpretation_layer):
        """Test image interpretation"""
        sensory_data = {
            "type": "image",
            "width": 1920,
            "height": 1080,
            "brightness": 150,
            "processed": True
        }
        
        result = await interpretation_layer.interpret_and_decide(sensory_data)
        
        assert result.confidence > 0
        assert isinstance(result.should_react, bool)
    
    def test_sensitivity_adjustment(self, interpretation_layer):
        """Test sensitivity threshold adjustment"""
        original_threshold = interpretation_layer.global_threshold
        interpretation_layer.adjust_sensitivity(0.8)
        assert interpretation_layer.global_threshold == 0.8
        
        interpretation_layer.adjust_sensitivity(1.5)  # Should be clamped to 1.0
        assert interpretation_layer.global_threshold == 1.0


class TestReasoningLayer:
    """Test Layer 3 - Reasoning"""
    
    def test_reasoning_layer_initialization(self):
        """Test ReasoningLayer initialization"""
        layer = ReasoningLayer()
        assert len(layer.providers) == 0
        assert layer.primary_provider is None
    
    def test_add_mock_provider(self):
        """Test adding providers"""
        layer = ReasoningLayer()
        
        # We can't test real providers without API keys, so we'll test the structure
        config = LLMConfig(
            provider=LLMProvider.LOCAL,
            api_key="test_key",
            base_url="http://localhost:8000"
        )
        
        layer.add_provider(config, is_primary=True)
        
        assert LLMProvider.LOCAL in layer.providers
        assert layer.primary_provider == LLMProvider.LOCAL


class TestCortexCore:
    """Test main Cortex functionality"""
    
    @pytest.fixture
    def cortex(self):
        config = CortexConfig(
            processing_mode=ProcessingMode.REACTIVE,
            enable_layer3=False  # Disable for basic testing
        )
        cortex = Cortex(config)
        cortex.activate_senses()
        return cortex
    
    @pytest.mark.asyncio
    async def test_basic_processing(self, cortex):
        """Test basic input processing"""
        result = await cortex.process_input("This is a test message")
        
        assert result.success == True
        assert "layer1" in result.layers_used
        assert "layer2" in result.layers_used
        assert result.layer1_output["type"] == "text"
        assert result.processing_time >= 0  # Allow for very fast processing
    
    @pytest.mark.asyncio
    async def test_image_processing(self, cortex):
        """Test image processing through Cortex"""
        test_image = Image.new('RGB', (200, 200), color='blue')
        result = await cortex.process_input(test_image)
        
        assert result.success == True
        assert result.layer1_output["type"] == "image"
        assert result.layer1_output["width"] == 200
        assert result.layer1_output["height"] == 200
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, cortex):
        """Test batch processing"""
        inputs = [
            {"data": "Message 1"},
            {"data": "Message 2"},
            {"data": "Message 3"}
        ]
        
        results = await cortex.batch_process(inputs)
        
        assert len(results) == 3
        for result in results:
            assert result.success == True
    
    def test_status_reporting(self, cortex):
        """Test status reporting"""
        status = cortex.get_status()
        
        assert "cortex" in status
        assert "layer1" in status
        assert "layer2" in status
        assert "performance_metrics" in status["cortex"]
    
    def test_callback_system(self, cortex):
        """Test callback system"""
        callback_called = False
        
        def test_callback(data):
            nonlocal callback_called
            callback_called = True
        
        cortex.add_callback("on_input", test_callback)
        
        # Verify callback was added
        assert len(cortex.callbacks["on_input"]) == 1


class TestOpenAgentSpecIntegration:
    """Test Open Agent Spec integration"""
    
    @pytest.mark.asyncio
    async def test_cortex_function_creation(self):
        """Test creating Open Agent Spec compatible function"""
        cortex = create_simple_cortex(enable_layer3=False)
        cortex_function = create_cortex_function(cortex)
        
        # Test the function
        response = await cortex_function(
            prompt="Test message",
            context={"test": "context"}
        )
        
        assert "success" in response
        assert "response" in response
        assert "actions" in response
        assert "metadata" in response
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in Open Agent Spec function"""
        cortex = create_simple_cortex(enable_layer3=False)
        cortex_function = create_cortex_function(cortex)
        
        # This should handle errors gracefully
        response = await cortex_function(prompt=None)  # Invalid input
        
        assert "success" in response
        assert "error" in response


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_create_simple_cortex(self):
        """Test simple Cortex creation"""
        cortex = create_simple_cortex(enable_layer3=False)
        
        assert isinstance(cortex, Cortex)
        assert cortex.layer1 is not None
        assert cortex.layer2 is not None
        assert len(cortex.layer1.active_senses) == 3  # All senses should be active
    
    def test_create_simple_cortex_with_layer3(self):
        """Test Cortex creation with Layer 3 enabled"""
        cortex = create_simple_cortex(
            openai_api_key="test_key",
            enable_layer3=True
        )
        
        assert cortex.layer3 is not None
        assert len(cortex.layer3.providers) > 0


class TestPerformanceMetrics:
    """Test performance tracking"""
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        """Test that metrics are properly tracked"""
        cortex = create_simple_cortex(enable_layer3=False)
        
        # Initial metrics should be zero
        initial_metrics = cortex.performance_metrics
        assert initial_metrics["total_processed"] == 0
        
        # Process some inputs
        await cortex.process_input("Test 1")
        await cortex.process_input("Test 2")
        
        # Check metrics were updated
        updated_metrics = cortex.performance_metrics
        assert updated_metrics["total_processed"] == 2
        assert updated_metrics["layer1_processed"] == 2
        assert updated_metrics["average_processing_time"] > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])