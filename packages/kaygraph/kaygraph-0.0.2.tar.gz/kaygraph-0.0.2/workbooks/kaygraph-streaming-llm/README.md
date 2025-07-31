# KayGraph Streaming LLM

This example demonstrates how KayGraph enhances streaming LLM applications with production-ready features like metrics collection, validation, guardrails, and robust error handling. It builds upon PocketFlow's streaming concept but adds enterprise-grade capabilities.

## Features Demonstrated

1. **Enhanced Streaming**: Stream tokens while collecting real-time metrics
2. **Token Validation**: Validate LLM outputs in real-time during streaming
3. **Streaming Guardrails**: Content filtering and safety checks on streaming text
4. **Performance Monitoring**: Track streaming latency, throughput, and quality
5. **Error Recovery**: Handle streaming failures gracefully with fallbacks

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ PromptProcessor │────▶│  StreamingLLM    │────▶│ ResponseHandler │
│ (ValidatedNode) │     │ (MetricsNode +   │     │ (Guardrails +   │
│                 │     │  Circuit Breaker)│     │  Validation)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
    [Prompt Guard]         [Stream Metrics]        [Content Safety]
                                                           │
                          ┌──────────────────┐             │
                          │ TokenAggregator  │◀────────────┘
                          │ (Real-time       │
                          │  Processing)     │
                          └──────────────────┘
```

## Usage

```bash
# Install dependencies  
pip install -r requirements.txt

# Run basic streaming demo
python main.py

# Run with guardrails enabled
python main.py --enable-guardrails

# Simulate streaming failures
python main.py --simulate-failures

# Monitor streaming performance
python main.py --monitor-performance

# Test with different models
python main.py --model gpt-4 --temperature 0.7
```

## Key Concepts

### Enhanced Streaming Benefits
- Real-time metrics collection during streaming
- Token-by-token validation and filtering
- Streaming performance optimization
- Graceful handling of streaming interruptions

### Production Patterns
- Circuit breakers for LLM API protection
- Content safety guardrails
- Streaming rate limiting
- Quality assessment during generation

## Example Streaming Features

1. **Token Metrics**: Latency, throughput, quality scores per token
2. **Content Filtering**: Real-time toxicity and safety checks
3. **Adaptive Streaming**: Adjust parameters based on performance
4. **Error Recovery**: Resume streaming after interruptions