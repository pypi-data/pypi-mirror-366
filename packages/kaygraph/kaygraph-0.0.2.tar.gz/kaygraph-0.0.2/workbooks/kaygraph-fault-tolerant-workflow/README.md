# KayGraph Fault-Tolerant Workflow

This example demonstrates KayGraph's advanced error handling and fault tolerance capabilities using execution hooks, circuit breakers, and graceful degradation patterns. It showcases how to build resilient workflows that can handle failures gracefully.

## Features Demonstrated

1. **Execution Hooks**: before_prep, after_exec, on_error hooks for custom logic
2. **Circuit Breakers**: Prevent cascading failures with automatic circuit breaking
3. **Graceful Degradation**: Fallback strategies when services are unavailable
4. **Error Recovery**: Retry patterns and recovery mechanisms
5. **Failure Isolation**: Prevent single node failures from breaking entire workflows

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ DataCollector   │────▶│  ProcessingNode  │────▶│ DeliveryNode    │
│ (Circuit Breaker│     │ (Retry + Fallback│     │ (Multi-Channel) │
│  + Fallback)    │     │  + Error Hook)   │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
   [Health Check]           [Recovery Logic]        [Channel Failover]
                                                           │
                          ┌──────────────────┐             │
                          │  ErrorHandler    │◀────────────┘
                          │  (Central Error  │
                          │   Management)    │
                          └──────────────────┘
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run normal workflow
python main.py

# Simulate various failure types
python main.py --simulate-failures --failure-type network
python main.py --simulate-failures --failure-type processing
python main.py --simulate-failures --failure-type storage

# Enable circuit breaker mode
python main.py --enable-circuit-breaker

# Test recovery patterns
python main.py --test-recovery
```

## Key Concepts

### Execution Hooks
- **before_prep**: Validate conditions before processing
- **after_exec**: Post-processing validation and logging
- **on_error**: Custom error handling and recovery logic

### Fault Tolerance Patterns
- **Circuit Breaker**: Fail fast when service is down
- **Bulkhead**: Isolate failures to prevent cascade
- **Timeout**: Prevent hanging operations
- **Retry with Backoff**: Intelligent retry strategies

## Example Error Scenarios

1. **Network Failures**: API timeouts, connection errors
2. **Data Issues**: Corrupted or missing data
3. **Resource Exhaustion**: Memory, disk, or connection limits
4. **Service Degradation**: Slow response times, partial failures