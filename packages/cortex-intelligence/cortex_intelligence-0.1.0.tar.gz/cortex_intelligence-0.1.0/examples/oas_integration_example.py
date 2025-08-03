"""
Open Agent Spec Integration Example for Cortex

This example demonstrates how to use Cortex as an intelligence engine
in Open Agent Spec, with intelligent filtering and routing capabilities.
"""

import asyncio
import os
from cortex.oas_integration import (
    CortexOASIntelligence, 
    CortexOASConfig, 
    create_cortex_oas_intelligence,
    create_cortex_oas_function,
    EXAMPLE_OAS_CONFIG
)


async def basic_oas_integration():
    """Basic OAS integration example"""
    print("=== Basic OAS Integration ===")
    
    # Configuration similar to standard OAS intelligence
    config = {
        "type": "cortex",
        "engine": "cortex-hybrid",
        "config": {
            "processing_mode": "reactive",
            "layer2_threshold": 0.6,
            "enable_layer3": True,
            "external_engine": "openai",
            "external_model": "gpt-4",
            "external_endpoint": "https://api.openai.com/v1",
            "temperature": 0.7,
            "max_tokens": 150,
            "trigger_keywords": ["help", "urgent", "error", "assist"]
        }
    }
    
    # Create Cortex OAS Intelligence Engine
    intelligence = create_cortex_oas_intelligence(config)
    
    # Create OAS-compatible function
    oas_function = create_cortex_oas_function(intelligence)
    
    # Test different types of inputs
    test_inputs = [
        "Hello, how are you?",  # Should be handled by Layer 2 only
        "URGENT: System failure detected!",  # Should trigger Layer 3
        "Can you help me with this problem?",  # Should trigger Layer 3
        "Just a normal message",  # Should be handled by Layer 2 only
        "ERROR: Database connection failed",  # Should trigger Layer 3
    ]
    
    for i, prompt in enumerate(test_inputs, 1):
        print(f"\n--- Test {i}: {prompt} ---")
        
        # Simulate OAS calling the intelligence function
        response = await oas_function(
            prompt=prompt,
            context={"user_id": "user123", "session_id": "session456"}
        )
        
        print(f"Success: {response['success']}")
        print(f"Response: {response['response']}")
        print(f"Actions: {response['actions']}")
        print(f"Layers used: {response['metadata']['layers_used']}")
        print(f"Triggered Layer 3: {response['metadata']['triggered_layer3']}")
        print(f"Processing time: {response['metadata']['processing_time']:.3f}s")
    
    # Show statistics
    status = intelligence.get_status()
    print(f"\n=== Statistics ===")
    print(f"Total requests: {status['stats']['total_requests']}")
    print(f"Layer 2 only: {status['stats']['layer2_only']}")
    print(f"Layer 3 triggered: {status['stats']['layer3_triggered']}")
    print(f"Average response time: {status['stats']['average_response_time']:.3f}s")


async def advanced_oas_configuration():
    """Advanced OAS configuration example"""
    print("\n=== Advanced OAS Configuration ===")
    
    # More sophisticated configuration
    advanced_config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.5,
        enable_layer3=True,
        layer2_engine="rule-based",
        external_engine="openai",
        external_model="gpt-4",
        external_endpoint="https://api.openai.com/v1",
        temperature=0.7,
        max_tokens=200,
        trigger_keywords=[
            "help", "emergency", "urgent", "important", "critical", "alert",
            "error", "failure", "problem", "issue", "warning", "assist"
        ],
        priority_patterns=[
            {"pattern": r"URGENT|CRITICAL|EMERGENCY", "priority": "high"},
            {"pattern": r"ERROR|FAILURE|PROBLEM", "priority": "medium"},
            {"pattern": r"HELP|ASSIST|SUPPORT", "priority": "medium"}
        ],
        custom_actions=[
            "analyze_input", "extract_keywords", "classify_intent",
            "suggest_response", "escalate_if_needed"
        ]
    )
    
    # Create intelligence engine
    intelligence = CortexOASIntelligence(advanced_config)
    
    # Test with complex scenarios
    complex_inputs = [
        {
            "prompt": "EMERGENCY: Server cluster is down!",
            "context": {"environment": "production", "severity": "critical"}
        },
        {
            "prompt": "Can you help me understand this error log?",
            "context": {"user_role": "developer", "task": "debugging"}
        },
        {
            "prompt": "Just checking the system status",
            "context": {"user_role": "admin", "task": "monitoring"}
        }
    ]
    
    for i, input_data in enumerate(complex_inputs, 1):
        print(f"\n--- Complex Test {i} ---")
        print(f"Prompt: {input_data['prompt']}")
        print(f"Context: {input_data['context']}")
        
        response = await intelligence.process(
            prompt=input_data['prompt'],
            context=input_data['context']
        )
        
        print(f"Success: {response['success']}")
        print(f"Response: {response['response']}")
        print(f"Actions: {response['actions']}")
        print(f"Confidence: {response['metadata']['confidence']:.2f}")
        print(f"Triggered Layer 3: {response['metadata']['triggered_layer3']}")


async def oas_agent_simulation():
    """Simulate how an OAS agent would use Cortex"""
    print("\n=== OAS Agent Simulation ===")
    
    # Simulate OAS agent configuration
    agent_config = {
        "name": "cortex_agent",
        "intelligence": {
            "type": "cortex",
            "engine": "cortex-hybrid",
            "config": {
                "processing_mode": "reactive",
                "layer2_threshold": 0.6,
                "enable_layer3": True,
                "external_engine": "openai",
                "external_model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 150
            }
        },
        "tools": ["web_search", "file_operations", "database_query"],
        "memory": {"type": "conversation", "max_tokens": 1000}
    }
    
    # Create intelligence engine from agent config
    intelligence = create_cortex_oas_intelligence(agent_config["intelligence"]["config"])
    
    # Simulate agent processing different user inputs
    user_interactions = [
        {
            "user_input": "What's the weather like?",
            "session_context": {"user_id": "user123", "previous_messages": 2}
        },
        {
            "user_input": "URGENT: The website is down!",
            "session_context": {"user_id": "user123", "previous_messages": 3, "user_role": "admin"}
        },
        {
            "user_input": "Can you help me debug this error?",
            "session_context": {"user_id": "user456", "previous_messages": 1, "user_role": "developer"}
        }
    ]
    
    for i, interaction in enumerate(user_interactions, 1):
        print(f"\n--- Agent Interaction {i} ---")
        print(f"User: {interaction['user_input']}")
        print(f"Context: {interaction['session_context']}")
        
        # Agent processes the input through Cortex
        response = await intelligence.process(
            prompt=interaction['user_input'],
            context=interaction['session_context']
        )
        
        print(f"Agent Decision:")
        print(f"  - Use Layer 3: {response['metadata']['triggered_layer3']}")
        print(f"  - Confidence: {response['metadata']['confidence']:.2f}")
        print(f"  - Suggested Actions: {response['actions']}")
        print(f"  - Response: {response['response']}")
        
        # Simulate agent taking actions based on Cortex output
        if response['metadata']['triggered_layer3']:
            print("  - Agent: Using external LLM for complex reasoning")
            print("  - Agent: May use additional tools based on analysis")
        else:
            print("  - Agent: Using internal logic for simple response")
            print("  - Agent: No external API calls needed")


async def performance_monitoring():
    """Demonstrate performance monitoring capabilities"""
    print("\n=== Performance Monitoring ===")
    
    # Create intelligence engine
    config = CortexOASConfig(
        processing_mode="reactive",
        layer2_threshold=0.6,
        enable_layer3=True,
        external_engine="openai"
    )
    
    intelligence = CortexOASIntelligence(config)
    
    # Process multiple inputs to generate performance data
    test_prompts = [
        "Hello world",
        "URGENT: System alert!",
        "Normal message",
        "ERROR: Something went wrong",
        "Just checking in",
        "CRITICAL: Database failure",
        "Simple question",
        "HELP: Need assistance"
    ]
    
    print("Processing test inputs...")
    for prompt in test_prompts:
        await intelligence.process(prompt)
    
    # Get performance statistics
    status = intelligence.get_status()
    stats = status['stats']
    
    print(f"\nPerformance Statistics:")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Layer 2 Only: {stats['layer2_only']} ({stats['layer2_only']/stats['total_requests']*100:.1f}%)")
    print(f"  Layer 3 Triggered: {stats['layer3_triggered']} ({stats['layer3_triggered']/stats['total_requests']*100:.1f}%)")
    print(f"  Average Response Time: {stats['average_response_time']:.3f}s")
    
    # Get detailed Cortex status
    cortex_status = status['cortex_status']
    print(f"\nCortex Layer Status:")
    print(f"  Layer 1 (Senses): {cortex_status['layer1']['active_senses']}")
    print(f"  Layer 2 (Interpretation): {cortex_status['layer2']['reaction_patterns']}")
    if 'layer3' in cortex_status:
        print(f"  Layer 3 (Reasoning): {cortex_status['layer3']['configured_providers']}")


async def main():
    """Run all OAS integration examples"""
    print("Cortex Open Agent Spec Integration Examples")
    print("=" * 50)
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Note: OPENAI_API_KEY not set. Layer 3 examples will use fallback responses.")
        print("Set OPENAI_API_KEY to test full external LLM integration.\n")
    
    await basic_oas_integration()
    await advanced_oas_configuration()
    await oas_agent_simulation()
    await performance_monitoring()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nTo use Cortex with Open Agent Spec:")
    print("1. Configure your OAS agent with Cortex intelligence")
    print("2. Set up API keys for external LLM providers")
    print("3. Customize trigger keywords and patterns")
    print("4. Monitor performance and adjust thresholds")


if __name__ == "__main__":
    asyncio.run(main()) 