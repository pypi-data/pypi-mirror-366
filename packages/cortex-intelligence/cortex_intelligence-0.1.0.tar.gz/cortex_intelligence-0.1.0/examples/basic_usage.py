"""
Basic usage example for Cortex intelligence engine
"""

import asyncio
import os
from cortex import create_simple_cortex, create_cortex_function


async def basic_text_processing():
    """Example of basic text processing"""
    print("=== Basic Text Processing ===")
    
    # Create a simple Cortex instance (without LLM providers for this example)
    cortex = create_simple_cortex(enable_layer3=False)
    
    # Process some text input
    result = await cortex.process_input(
        data="This is an important message about system failure!",
        sense_type="text"
    )
    
    print(f"Success: {result.success}")
    print(f"Layers used: {result.layers_used}")
    print(f"Layer 1 output: {result.layer1_output}")
    print(f"Layer 2 output: {result.layer2_output}")
    print(f"Final response: {result.final_response}")
    print(f"Processing time: {result.processing_time:.3f}s")
    print()


async def image_processing():
    """Example of image processing using PIL"""
    print("=== Image Processing ===")
    
    try:
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        test_image = Image.new('RGB', (800, 600), color='red')
        
        cortex = create_simple_cortex(enable_layer3=False)
        
        result = await cortex.process_input(
            data=test_image,
            sense_type="vision"
        )
        
        print(f"Success: {result.success}")
        print(f"Layers used: {result.layers_used}")
        print(f"Image analysis: {result.layer1_output}")
        print(f"Should react: {result.layer2_output.get('should_react', False)}")
        print(f"Processing time: {result.processing_time:.3f}s")
        print()
        
    except ImportError:
        print("PIL not available for image processing example")
        print()


async def audio_processing():
    """Example of audio processing"""
    print("=== Audio Processing ===")
    
    # Create synthetic audio data
    import numpy as np
    sample_rate = 16000
    duration = 2.0  # seconds
    frequency = 440  # Hz (A note)
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    cortex = create_simple_cortex(enable_layer3=False)
    
    result = await cortex.process_input(
        data=audio_data,
        sense_type="audio"
    )
    
    print(f"Success: {result.success}")
    print(f"Layers used: {result.layers_used}")
    print(f"Audio analysis: {result.layer1_output}")
    print(f"Should react: {result.layer2_output.get('should_react', False)}")
    print(f"Processing time: {result.processing_time:.3f}s")
    print()


async def llm_reasoning_example():
    """Example with LLM reasoning (requires API keys)"""
    print("=== LLM Reasoning Example ===")
    
    # Check for API keys in environment
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("CLAUDE_API_KEY")
    
    if not openai_key and not claude_key:
        print("No LLM API keys found in environment. Skipping LLM example.")
        print("Set OPENAI_API_KEY or CLAUDE_API_KEY to test Layer 3 reasoning.")
        print()
        return
    
    # Create Cortex with LLM support
    cortex = create_simple_cortex(
        openai_api_key=openai_key,
        claude_api_key=claude_key,
        enable_layer3=True
    )
    
    # Process text that should trigger Layer 3 reasoning
    result = await cortex.process_input(
        data="Help! There's an emergency situation that requires immediate analysis.",
        context="This is a critical alert from a monitoring system.",
        task_type="emergency_response"
    )
    
    print(f"Success: {result.success}")
    print(f"Layers used: {result.layers_used}")
    print(f"Layer 2 reaction: {result.layer2_output.get('should_react', False)}")
    if result.layer3_output:
        print(f"LLM reasoning: {result.layer3_output.get('response_text', '')}")
        print(f"Confidence: {result.layer3_output.get('confidence', 0.0)}")
        print(f"Suggested actions: {result.suggested_actions}")
    print(f"Processing time: {result.processing_time:.3f}s")
    print()


async def open_agent_spec_example():
    """Example of Open Agent Spec integration"""
    print("=== Open Agent Spec Integration ===")
    
    # Create Cortex instance
    cortex = create_simple_cortex(enable_layer3=False)
    
    # Create Open Agent Spec compatible function
    cortex_function = create_cortex_function(cortex)
    
    # Simulate Open Agent Spec calling the function
    context = {
        "user_id": "user123",
        "session_id": "session456",
        "task": "analyze_input"
    }
    
    response = await cortex_function(
        prompt="Analyze this system log: ERROR: Database connection failed",
        context=context,
        task_type="log_analysis"
    )
    
    print(f"OAS Response: {response}")
    print()


async def batch_processing_example():
    """Example of batch processing"""
    print("=== Batch Processing ===")
    
    cortex = create_simple_cortex(enable_layer3=False)
    
    # Prepare batch inputs
    inputs = [
        {"data": "Normal message", "sense_type": "text"},
        {"data": "URGENT: System alert!", "sense_type": "text"},
        {"data": "Hello world", "sense_type": "text"},
        {"data": "ERROR: Critical failure detected", "sense_type": "text"}
    ]
    
    # Process batch
    results = await cortex.batch_process(inputs)
    
    print(f"Processed {len(results)} inputs:")
    for i, result in enumerate(results):
        should_react = result.layer2_output.get('should_react', False) if result.layer2_output else False
        print(f"  {i+1}. '{inputs[i]['data'][:30]}...' -> React: {should_react}")
    print()


async def status_and_metrics_example():
    """Example of status monitoring and metrics"""
    print("=== Status and Metrics ===")
    
    cortex = create_simple_cortex(enable_layer3=False)
    
    # Process some data to generate metrics
    await cortex.process_input("Test message 1")
    await cortex.process_input("URGENT: Test message 2")
    await cortex.process_input("Test message 3")
    
    # Get status
    status = cortex.get_status()
    print("Cortex Status:")
    print(f"  Performance metrics: {status['cortex']['performance_metrics']}")
    print(f"  Layer 1 active senses: {status['layer1']['active_senses']}")
    print(f"  Layer 2 reaction patterns: {status['layer2']['reaction_patterns']}")
    
    # Get recent history
    history = cortex.get_recent_history(limit=3)
    print(f"\nRecent processing history ({len(history)} items):")
    for item in history:
        success = item['result']['success']
        layers = item['result']['layers_used']
        print(f"  - Success: {success}, Layers: {layers}")
    print()


async def main():
    """Run all examples"""
    print("Cortex Intelligence Engine Examples")
    print("==================================")
    print()
    
    await basic_text_processing()
    await image_processing()
    await audio_processing()
    await llm_reasoning_example()
    await open_agent_spec_example()
    await batch_processing_example()
    await status_and_metrics_example()
    
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())