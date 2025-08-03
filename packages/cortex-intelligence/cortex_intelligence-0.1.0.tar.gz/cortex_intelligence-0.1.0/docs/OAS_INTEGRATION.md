# Cortex Open Agent Spec Integration Guide

This guide explains how to integrate Cortex as an intelligence engine in Open Agent Spec, providing intelligent filtering and routing capabilities.

## Overview

Cortex acts as an intelligent filtering layer between your OAS agent and external LLM providers. Instead of routing every request directly to external LLMs, Cortex:

1. **Processes input through Layer 1** (sensory processing)
2. **Analyzes with Layer 2** (internal intelligence - rule-based or ONNX models)
3. **Decides whether to trigger Layer 3** (external LLM) based on complexity and importance
4. **Provides intelligent responses** with suggested actions

## Architecture

```
OAS Agent → Cortex Intelligence Engine → External LLM (if needed)
                ↓
            Layer 1: Sensory Processing
                ↓
            Layer 2: Internal Intelligence (Rule-based/ONNX)
                ↓
            Layer 3: External LLM (OpenAI, Claude, etc.)
```

## Configuration

### Basic OAS Configuration

```yaml
# Your OAS agent configuration
name: "my_cortex_agent"
intelligence:
  type: "cortex"
  engine: "cortex-hybrid"
  config:
    processing_mode: "reactive"
    layer2_threshold: 0.6
    enable_layer3: true
    external_engine: "openai"
    external_model: "gpt-4"
    external_endpoint: "https://api.openai.com/v1"
    temperature: 0.7
    max_tokens: 150
    trigger_keywords: ["help", "urgent", "error", "assist"]
```

### Advanced Configuration

```yaml
intelligence:
  type: "cortex"
  engine: "cortex-hybrid"
  config:
    # Core settings
    processing_mode: "reactive"  # reactive, proactive, selective
    layer2_threshold: 0.6
    enable_layer3: true
    max_processing_time: 30.0
    
    # Layer 2 (Internal Intelligence)
    layer2_engine: "rule-based"  # rule-based, onnx, local-llm
    layer2_model_path: "/path/to/onnx/models"  # Optional
    
    # Layer 3 (External LLM)
    external_engine: "openai"  # openai, claude, azure, local
    external_model: "gpt-4"
    external_endpoint: "https://api.openai.com/v1"
    external_api_key: "${OPENAI_API_KEY}"
    
    # LLM Configuration
    temperature: 0.7
    max_tokens: 150
    timeout: 30
    
    # Behavior Configuration
    trigger_keywords:
      - "help"
      - "emergency"
      - "urgent"
      - "important"
      - "critical"
      - "alert"
      - "error"
      - "failure"
      - "problem"
      - "issue"
      - "warning"
      - "assist"
    
    priority_patterns:
      - pattern: "URGENT|CRITICAL|EMERGENCY"
        priority: "high"
      - pattern: "ERROR|FAILURE|PROBLEM"
        priority: "medium"
      - pattern: "HELP|ASSIST|SUPPORT"
        priority: "medium"
    
    custom_actions:
      - "analyze_input"
      - "extract_keywords"
      - "classify_intent"
      - "suggest_response"
      - "escalate_if_needed"
```

## Usage Examples

### Python Integration

```python
import asyncio
from cortex import create_cortex_oas_intelligence, create_cortex_oas_function

async def setup_cortex_agent():
    # Configuration
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
    
    # Create Cortex intelligence engine
    intelligence = create_cortex_oas_intelligence(config)
    
    # Create OAS-compatible function
    oas_function = create_cortex_oas_function(intelligence)
    
    return oas_function

async def process_user_input(oas_function, user_input, context=None):
    # Process input through Cortex
    response = await oas_function(
        prompt=user_input,
        context=context or {}
    )
    
    print(f"Success: {response['success']}")
    print(f"Response: {response['response']}")
    print(f"Actions: {response['actions']}")
    print(f"Layers used: {response['metadata']['layers_used']}")
    print(f"Triggered Layer 3: {response['metadata']['triggered_layer3']}")
    
    return response

# Usage
async def main():
    oas_function = await setup_cortex_agent()
    
    # Test different inputs
    await process_user_input(oas_function, "Hello, how are you?")
    await process_user_input(oas_function, "URGENT: System failure detected!")
    await process_user_input(oas_function, "Can you help me with this problem?")

asyncio.run(main())
```

### Direct OAS Integration

```python
from cortex import CortexOASIntelligence, CortexOASConfig

# Create configuration
config = CortexOASConfig(
    processing_mode="reactive",
    layer2_threshold=0.6,
    enable_layer3=True,
    external_engine="openai",
    external_model="gpt-4",
    external_endpoint="https://api.openai.com/v1",
    temperature=0.7,
    max_tokens=150,
    trigger_keywords=["help", "urgent", "error", "assist"]
)

# Create intelligence engine
intelligence = CortexOASIntelligence(config)

# Process inputs
async def handle_user_input(user_input, context=None):
    response = await intelligence.process(
        prompt=user_input,
        context=context
    )
    return response
```

## Processing Modes

### 1. Reactive Mode (Default)
- **Behavior**: Only uses Layer 3 when Layer 2 determines it's necessary
- **Use Case**: Cost-effective, intelligent filtering
- **Example**: Simple greetings handled by Layer 2, complex problems trigger Layer 3

### 2. Proactive Mode
- **Behavior**: Always processes through all layers
- **Use Case**: Maximum intelligence, higher cost
- **Example**: Every input gets full analysis

### 3. Selective Mode
- **Behavior**: Uses custom logic to determine Layer 3 usage
- **Use Case**: Custom filtering rules
- **Example**: Only technical questions trigger Layer 3

## Layer 2 Intelligence Options

### Rule-based (Default)
- **Description**: Uses predefined rules and patterns
- **Pros**: Fast, no external dependencies, predictable
- **Cons**: Limited intelligence, requires manual configuration

### ONNX Models
- **Description**: Uses local ONNX models for classification
- **Pros**: More intelligent, still fast, no external API calls
- **Cons**: Requires model files, limited to trained tasks

### Local LLM
- **Description**: Uses local LLM (Ollama, etc.) for Layer 2
- **Pros**: More intelligent than rules, no external API calls
- **Cons**: Requires local LLM setup, slower than rules

## Layer 3 External LLM Providers

### OpenAI
```yaml
external_engine: "openai"
external_model: "gpt-4"
external_endpoint: "https://api.openai.com/v1"
external_api_key: "${OPENAI_API_KEY}"
```

### Claude
```yaml
external_engine: "claude"
external_model: "claude-3-sonnet-20240229"
external_endpoint: "https://api.anthropic.com/v1"
external_api_key: "${CLAUDE_API_KEY}"
```

### Local LLM
```yaml
external_engine: "local"
external_model: "llama2"
external_endpoint: "http://localhost:11434"
```

## Response Format

Cortex returns responses in OAS-compatible format:

```json
{
  "success": true,
  "response": "Analysis and response from Cortex",
  "actions": ["suggested_action_1", "suggested_action_2"],
  "metadata": {
    "layers_used": ["layer1", "layer2", "layer3"],
    "processing_time": 1.23,
    "confidence": 0.85,
    "cortex_stats": {
      "total_requests": 100,
      "layer2_only": 70,
      "layer3_triggered": 30,
      "average_response_time": 0.5
    },
    "triggered_layer3": true
  },
  "error": null
}
```

## Performance Monitoring

### Get Statistics
```python
status = intelligence.get_status()
stats = status['stats']

print(f"Total requests: {stats['total_requests']}")
print(f"Layer 2 only: {stats['layer2_only']}")
print(f"Layer 3 triggered: {stats['layer3_triggered']}")
print(f"Average response time: {stats['average_response_time']:.3f}s")
```

### Reset Statistics
```python
intelligence.reset_stats()
```

## Best Practices

### 1. Configure Trigger Keywords
Choose keywords that indicate when complex reasoning is needed:
```yaml
trigger_keywords:
  - "help"
  - "urgent"
  - "error"
  - "problem"
  - "assist"
  - "critical"
```

### 2. Adjust Layer 2 Threshold
- **Lower threshold (0.3-0.5)**: More likely to trigger Layer 3
- **Higher threshold (0.7-0.9)**: Less likely to trigger Layer 3

### 3. Monitor Performance
Regularly check statistics to optimize configuration:
```python
# Check Layer 3 usage percentage
layer3_percentage = (stats['layer3_triggered'] / stats['total_requests']) * 100
print(f"Layer 3 usage: {layer3_percentage:.1f}%")
```

### 4. Use Context
Pass relevant context to improve decision-making:
```python
context = {
    "user_role": "admin",
    "environment": "production",
    "previous_messages": 3
}
response = await intelligence.process(prompt, context)
```

## Troubleshooting

### Common Issues

1. **Layer 3 not triggering**
   - Check `layer2_threshold` value
   - Verify `trigger_keywords` configuration
   - Ensure `enable_layer3` is true

2. **External LLM errors**
   - Verify API keys are set
   - Check endpoint URLs
   - Ensure network connectivity

3. **Slow performance**
   - Consider using rule-based Layer 2
   - Reduce `max_tokens` for Layer 3
   - Use local LLM for Layer 2

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Example OAS Agent Configuration

```yaml
name: "cortex_support_agent"
description: "Intelligent support agent using Cortex for smart routing"

intelligence:
  type: "cortex"
  engine: "cortex-hybrid"
  config:
    processing_mode: "reactive"
    layer2_threshold: 0.6
    enable_layer3: true
    external_engine: "openai"
    external_model: "gpt-4"
    external_endpoint: "https://api.openai.com/v1"
    temperature: 0.7
    max_tokens: 150
    trigger_keywords:
      - "help"
      - "urgent"
      - "error"
      - "problem"
      - "assist"
      - "support"
    priority_patterns:
      - pattern: "URGENT|CRITICAL|EMERGENCY"
        priority: "high"
      - pattern: "ERROR|FAILURE|PROBLEM"
        priority: "medium"

tools:
  - name: "web_search"
    description: "Search the web for information"
  - name: "file_operations"
    description: "Read and write files"
  - name: "database_query"
    description: "Query the database"

memory:
  type: "conversation"
  max_tokens: 1000

instructions: |
  You are an intelligent support agent that uses Cortex for smart request routing.
  Simple questions are handled internally, while complex issues are escalated to external LLM.
  Always be helpful and provide clear, actionable responses.
```

This configuration creates an agent that intelligently routes requests based on complexity and urgency, providing cost-effective and responsive support. 