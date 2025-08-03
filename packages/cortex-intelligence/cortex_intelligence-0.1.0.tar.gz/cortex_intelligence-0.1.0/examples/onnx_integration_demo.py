"""
ONNX Integration Demo for Cortex

This script demonstrates how Cortex uses ONNX models for Layer 2 intelligence
to make better decisions about when to trigger Layer 3 (external LLM).
"""

import asyncio
import logging
from cortex import create_cortex_oas_intelligence, CortexOASConfig

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


async def demo_onnx_integration():
    """Demonstrate ONNX integration with Cortex"""
    print("🧠 Cortex ONNX Integration Demo")
    print("=" * 50)
    
    # Configuration with ONNX enabled
    config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.6,
        enable_layer3=True,
        layer2_engine="onnx",  # Enable ONNX models
        external_engine="openai",
        external_model="gpt-4",
        temperature=0.7,
        max_tokens=150
    )
    
    print(f"📋 Configuration:")
    print(f"  - Layer 2 Engine: {config.layer2_engine}")
    print(f"  - Layer 2 Threshold: {config.layer2_threshold}")
    print(f"  - Enable Layer 3: {config.enable_layer3}")
    print()
    
    # Create Cortex intelligence engine
    print("🚀 Initializing Cortex with ONNX models...")
    intelligence = create_cortex_oas_intelligence(config)
    
    # Test different types of inputs
    test_cases = [
        {
            "name": "Simple Text",
            "input": "Hello, how are you?",
            "expected": "Should be handled by Layer 2 only"
        },
        {
            "name": "Complex Question",
            "input": "Can you help me understand this complex technical problem with the database connection and provide a detailed solution?",
            "expected": "Should trigger Layer 3 due to complexity"
        },
        {
            "name": "Urgent Alert",
            "input": "URGENT: System failure detected! Database connection lost!",
            "expected": "Should trigger Layer 3 due to urgency"
        },
        {
            "name": "Short Statement",
            "input": "The weather is nice today.",
            "expected": "Should be handled by Layer 2 only"
        },
        {
            "name": "Technical Question",
            "input": "What's the difference between ONNX and TensorFlow models?",
            "expected": "Should trigger Layer 3 due to technical complexity"
        }
    ]
    
    print("\n🧪 Testing ONNX-powered Layer 2 intelligence:")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Input: {test_case['input']}")
        print(f"Expected: {test_case['expected']}")
        
        # Process through Cortex
        response = await intelligence.process(
            prompt=test_case['input'],
            context={"test_case": test_case['name']}
        )
        
        # Display results
        print(f"✅ Result:")
        print(f"  - Success: {response['success']}")
        print(f"  - Response: {response['response']}")
        print(f"  - Layers used: {response['metadata']['layers_used']}")
        print(f"  - Triggered Layer 3: {response['metadata']['triggered_layer3']}")
        print(f"  - Confidence: {response['metadata']['confidence']:.2f}")
        print(f"  - Processing time: {response['metadata']['processing_time']:.3f}s")
        
        # Show ONNX-specific information if available
        if 'layer2_output' in response['metadata'] and response['metadata']['layer2_output']:
            layer2_output = response['metadata']['layer2_output']
            if 'extracted_features' in layer2_output:
                features = layer2_output['extracted_features']
                if 'onnx_class' in features:
                    print(f"  - ONNX Class: {features['onnx_class']}")
                    print(f"  - ONNX Confidence: {features.get('onnx_confidence', 0):.2f}")
    
    # Show final statistics
    print("\n📊 Final Statistics:")
    print("-" * 30)
    status = intelligence.get_status()
    stats = status['stats']
    
    print(f"Total requests: {stats['total_requests']}")
    print(f"Layer 2 only: {stats['layer2_only']} ({stats['layer2_only']/stats['total_requests']*100:.1f}%)")
    print(f"Layer 3 triggered: {stats['layer3_triggered']} ({stats['layer3_triggered']/stats['total_requests']*100:.1f}%)")
    print(f"Average response time: {stats['average_response_time']:.3f}s")
    
    # Show Cortex layer status
    print("\n🔍 Cortex Layer Status:")
    print("-" * 30)
    cortex_status = status['cortex_status']
    
    # Check if ONNX models are loaded
    layer2_status = cortex_status['layer2']
    interpreters = layer2_status.get('interpreters', {})
    
    for interpreter_name, interpreter_status in interpreters.items():
        print(f"{interpreter_name}: {'ONNX Loaded' if interpreter_status.get('loaded', False) else 'Rule-based'}")
    
    print("\n🎯 Key Benefits of ONNX Integration:")
    print("-" * 40)
    print("✅ More intelligent decision-making")
    print("✅ Better classification of input complexity")
    print("✅ Reduced false positives/negatives")
    print("✅ Faster processing than external LLM calls")
    print("✅ Cost savings through better filtering")
    print("✅ Local processing (no external API calls for Layer 2)")


async def demo_comparison():
    """Compare rule-based vs ONNX-based Layer 2"""
    print("\n🔄 Rule-based vs ONNX Comparison")
    print("=" * 50)
    
    # Test with rule-based Layer 2
    print("\n📋 Rule-based Layer 2:")
    rule_config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.6,
        enable_layer3=True,
        layer2_engine="rule-based",
        external_engine="openai"
    )
    
    rule_intelligence = create_cortex_oas_intelligence(rule_config)
    
    # Test with ONNX Layer 2
    print("\n🧠 ONNX-based Layer 2:")
    onnx_config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.6,
        enable_layer3=True,
        layer2_engine="onnx",
        external_engine="openai"
    )
    
    onnx_intelligence = create_cortex_oas_intelligence(onnx_config)
    
    # Test cases
    test_inputs = [
        "Hello world",
        "Can you help me with this complex problem?",
        "URGENT: System failure!",
        "The weather is nice today."
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n📝 Test {i}: {test_input}")
        
        # Rule-based processing
        rule_response = await rule_intelligence.process(test_input)
        rule_triggered = rule_response['metadata']['triggered_layer3']
        
        # ONNX-based processing
        onnx_response = await onnx_intelligence.process(test_input)
        onnx_triggered = onnx_response['metadata']['triggered_layer3']
        
        print(f"  Rule-based: {'🔴 Layer 3' if rule_triggered else '🟢 Layer 2'}")
        print(f"  ONNX-based: {'🔴 Layer 3' if onnx_triggered else '🟢 Layer 2'}")
        
        if rule_triggered != onnx_triggered:
            print(f"  ⚠️  Different decision! ONNX made a {'smarter' if not onnx_triggered else 'more thorough'} choice")


async def main():
    """Run the ONNX integration demo"""
    print("🧠 Cortex ONNX Integration Demo")
    print("=" * 50)
    print("This demo shows how Cortex uses ONNX models for intelligent filtering")
    print("between Layer 2 (internal) and Layer 3 (external LLM) processing.\n")
    
    await demo_onnx_integration()
    await demo_comparison()
    
    print("\n🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("1. Add actual ONNX model files to the 'models/' directory")
    print("2. Configure model paths in your Cortex setup")
    print("3. Fine-tune thresholds for your specific use case")
    print("4. Monitor performance and adjust as needed")


if __name__ == "__main__":
    asyncio.run(main()) 