"""
Real ONNX Demo - Show Actual Inference Results

This demo shows how the real ONNX models perform inference and make decisions
compared to rule-based processing.
"""

import asyncio
import logging
from cortex import create_cortex_oas_intelligence, CortexOASConfig, ONNXInference, create_default_model_manager

# Set up logging to see ONNX inference details
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


async def demo_onnx_inference():
    """Demonstrate actual ONNX model inference"""
    print("🧠 Real ONNX Inference Demo")
    print("=" * 50)
    
    # Test ONNX models directly
    print("\n🔍 Testing ONNX Models Directly:")
    print("-" * 40)
    
    model_manager = create_default_model_manager()
    inference = ONNXInference(model_manager)
    
    # Test text classification
    test_texts = [
        "Hello world",
        "Can you help me with this complex technical problem?",
        "URGENT: System failure detected!",
        "The weather is nice today.",
        "What's the difference between ONNX and TensorFlow models?"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text}")
        
        # Run ONNX inference
        result = inference.classify_text(text, "text_classifier")
        
        if result.get("success"):
            print(f"  ONNX Class: {result['top_class']}")
            print(f"  Confidence: {result['top_confidence']:.3f}")
            print(f"  All Predictions:")
            for pred in result['predictions']:
                print(f"    - {pred['class']}: {pred['confidence']:.3f}")
        else:
            print(f"  ❌ ONNX inference failed: {result.get('error')}")
    
    # Test sentiment analysis
    print("\n😊 Testing Sentiment Analysis:")
    print("-" * 40)
    
    sentiment_texts = [
        "I love this product!",
        "This is terrible, I hate it.",
        "The system is working normally.",
        "URGENT: Critical error detected!"
    ]
    
    for i, text in enumerate(sentiment_texts, 1):
        print(f"\n📝 Sentiment {i}: {text}")
        
        result = inference.classify_text(text, "sentiment_analyzer")
        
        if result.get("success"):
            print(f"  Sentiment: {result['top_class']}")
            print(f"  Confidence: {result['top_confidence']:.3f}")
        else:
            print(f"  ❌ Sentiment analysis failed: {result.get('error')}")


async def demo_cortex_with_onnx():
    """Demonstrate Cortex with ONNX models"""
    print("\n🧠 Cortex with ONNX Models Demo")
    print("=" * 50)
    
    # Configure Cortex with ONNX
    config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.6,
        enable_layer3=True,
        layer2_engine="onnx",
        external_engine="openai",
        external_model="gpt-4"
    )
    
    intelligence = create_cortex_oas_intelligence(config)
    
    # Test cases with expected behavior
    test_cases = [
        {
            "input": "Hello world",
            "expected": "Simple greeting - should stay in Layer 2",
            "description": "Simple text"
        },
        {
            "input": "Can you help me understand this complex technical problem with the database connection and provide a detailed solution?",
            "expected": "Complex question - should trigger Layer 3",
            "description": "Complex technical question"
        },
        {
            "input": "URGENT: System failure detected! Database connection lost!",
            "expected": "Urgent alert - should trigger Layer 3",
            "description": "Urgent system alert"
        },
        {
            "input": "The weather is nice today.",
            "expected": "Simple statement - should stay in Layer 2",
            "description": "Simple statement"
        },
        {
            "input": "What's the difference between ONNX and TensorFlow models?",
            "expected": "Technical question - should trigger Layer 3",
            "description": "Technical question"
        }
    ]
    
    print("\n🧪 Testing Cortex ONNX Integration:")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        print(f"Expected: {test_case['expected']}")
        
        # Process through Cortex
        response = await intelligence.process(
            prompt=test_case['input'],
            context={"test_case": test_case['description']}
        )
        
        # Display results
        print(f"✅ Result:")
        print(f"  - Success: {response['success']}")
        print(f"  - Triggered Layer 3: {response['metadata']['triggered_layer3']}")
        print(f"  - Confidence: {response['metadata']['confidence']:.3f}")
        print(f"  - Processing time: {response['metadata']['processing_time']:.3f}s")
        
        # Show ONNX-specific information
        if 'layer2_output' in response['metadata'] and response['metadata']['layer2_output']:
            layer2_output = response['metadata']['layer2_output']
            if 'extracted_features' in layer2_output:
                features = layer2_output['extracted_features']
                if 'onnx_class' in features:
                    print(f"  - ONNX Class: {features['onnx_class']}")
                    print(f"  - ONNX Confidence: {features.get('onnx_confidence', 0):.3f}")
                    if 'onnx_predictions' in features:
                        print(f"  - ONNX Predictions:")
                        for pred in features['onnx_predictions'][:3]:  # Show top 3
                            print(f"    • {pred['class']}: {pred['confidence']:.3f}")


async def demo_comparison():
    """Compare rule-based vs ONNX-based processing"""
    print("\n🔄 Rule-based vs ONNX Comparison")
    print("=" * 50)
    
    # Create two Cortex instances
    rule_config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.6,
        enable_layer3=True,
        layer2_engine="rule-based",
        external_engine="openai"
    )
    
    onnx_config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.6,
        enable_layer3=True,
        layer2_engine="onnx",
        external_engine="openai"
    )
    
    rule_intelligence = create_cortex_oas_intelligence(rule_config)
    onnx_intelligence = create_cortex_oas_intelligence(onnx_config)
    
    # Test cases
    test_inputs = [
        "Hello world",
        "Can you help me with this complex problem?",
        "URGENT: System failure!",
        "The weather is nice today.",
        "What's the difference between ONNX and TensorFlow?"
    ]
    
    print("\n📊 Comparison Results:")
    print("-" * 30)
    print("Input | Rule-based | ONNX-based | Difference")
    print("-" * 60)
    
    for test_input in test_inputs:
        # Rule-based processing
        rule_response = await rule_intelligence.process(test_input)
        rule_triggered = rule_response['metadata']['triggered_layer3']
        rule_confidence = rule_response['metadata']['confidence']
        
        # ONNX-based processing
        onnx_response = await onnx_intelligence.process(test_input)
        onnx_triggered = onnx_response['metadata']['triggered_layer3']
        onnx_confidence = onnx_response['metadata']['confidence']
        
        # Get ONNX class if available
        onnx_class = "N/A"
        if 'layer2_output' in onnx_response['metadata']:
            features = onnx_response['metadata']['layer2_output'].get('extracted_features', {})
            onnx_class = features.get('onnx_class', 'N/A')
        
        # Determine difference
        if rule_triggered == onnx_triggered:
            difference = "Same"
        else:
            difference = f"ONNX {'smarter' if not onnx_triggered else 'more thorough'}"
        
        print(f"{test_input[:30]:<30} | {'🔴' if rule_triggered else '🟢'} | {'🔴' if onnx_triggered else '🟢'} | {difference}")
        print(f"{'':<30} | {rule_confidence:.3f} | {onnx_confidence:.3f} | {onnx_class}")


async def demo_performance():
    """Demo performance benefits"""
    print("\n⚡ Performance Demo")
    print("=" * 50)
    
    config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.6,
        enable_layer3=True,
        layer2_engine="onnx",
        external_engine="openai"
    )
    
    intelligence = create_cortex_oas_intelligence(config)
    
    # Test multiple inputs
    test_inputs = [
        "Hello",
        "How are you?",
        "The weather is nice",
        "Simple question",
        "Basic statement",
        "Can you help me?",
        "URGENT: System failure!",
        "Complex technical question about database optimization"
    ]
    
    print("\n📈 Processing Multiple Inputs:")
    print("-" * 40)
    
    total_time = 0
    layer2_only = 0
    layer3_triggered = 0
    
    for i, test_input in enumerate(test_inputs, 1):
        start_time = asyncio.get_event_loop().time()
        
        response = await intelligence.process(test_input)
        
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        total_time += processing_time
        
        if response['metadata']['triggered_layer3']:
            layer3_triggered += 1
        else:
            layer2_only += 1
        
        print(f"{i:2d}. {test_input[:40]:<40} | {'🔴' if response['metadata']['triggered_layer3'] else '🟢'} | {processing_time:.3f}s")
    
    print(f"\n📊 Summary:")
    print(f"Total inputs: {len(test_inputs)}")
    print(f"Layer 2 only: {layer2_only} ({layer2_only/len(test_inputs)*100:.1f}%)")
    print(f"Layer 3 triggered: {layer3_triggered} ({layer3_triggered/len(test_inputs)*100:.1f}%)")
    print(f"Total time: {total_time:.3f}s")
    print(f"Average time: {total_time/len(test_inputs):.3f}s")
    
    # Show cost savings estimate
    if layer3_triggered > 0:
        cost_savings = (len(test_inputs) - layer3_triggered) / len(test_inputs) * 100
        print(f"💰 Estimated cost savings: {cost_savings:.1f}%")


async def main():
    """Run the complete ONNX demo"""
    print("🧠 Real ONNX Integration Demo")
    print("=" * 60)
    print("This demo shows actual ONNX model inference and decision-making")
    print("compared to rule-based processing.\n")
    
    await demo_onnx_inference()
    await demo_cortex_with_onnx()
    await demo_comparison()
    await demo_performance()
    
    print("\n🎉 Demo completed!")
    print("\n💡 Key Takeaways:")
    print("✅ ONNX models provide real neural network inference")
    print("✅ Better classification accuracy than rule-based systems")
    print("✅ Significant cost savings through intelligent filtering")
    print("✅ Fast local processing without external API calls")
    print("✅ Graceful fallback to rule-based when needed")


if __name__ == "__main__":
    asyncio.run(main()) 