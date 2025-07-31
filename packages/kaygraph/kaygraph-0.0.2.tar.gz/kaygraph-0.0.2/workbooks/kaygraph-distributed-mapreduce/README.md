# KayGraph Distributed MapReduce

This example demonstrates KayGraph's distributed execution capabilities for large-scale data processing using the MapReduce pattern. It showcases how KayGraph can coordinate work across multiple workers while maintaining metrics, validation, and fault tolerance.

## Features Demonstrated

1. **Distributed Execution**: Coordinate MapReduce tasks across multiple workers
2. **Work Distribution**: Intelligent partitioning and load balancing
3. **Fault Tolerance**: Handle worker failures and task redistribution
4. **Metrics Aggregation**: Collect and aggregate metrics from distributed workers
5. **Result Validation**: Validate intermediate and final results across workers

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ DataPartitioner │────▶│  MapCoordinator  │────▶│ReduceCoordinator│
│ (Split work)    │     │ (Distribute map  │     │ (Aggregate      │
│                 │     │  tasks)          │     │  results)       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
   [Validation]            [Worker Pool]            [Final Validation]
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ Worker 1 │ │ Worker 2 │ │ Worker N │
              │(Map Task)│ │(Map Task)│ │(Map Task)│
              └──────────┘ └──────────┘ └──────────┘
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic MapReduce example
python main.py

# Run with multiple workers
python main.py --workers 4

# Simulate worker failures
python main.py --simulate-failures

# Large dataset processing
python main.py --dataset-size 10000 --workers 8

# Monitor distributed execution
python main.py --monitor-workers
```

## Key Concepts

### Distributed Benefits
- Parallel processing across multiple workers
- Automatic load balancing and work distribution
- Fault tolerance with worker recovery
- Scalable to large datasets

### Production Patterns
- Worker health monitoring
- Task checkpointing and recovery
- Resource usage optimization
- Distributed metrics collection

## Example Use Cases

1. **Log Analysis**: Process large log files across multiple workers
2. **Data Aggregation**: Aggregate statistics from distributed datasets
3. **Text Processing**: Distributed NLP processing pipelines
4. **Batch Analytics**: Large-scale data analytics workflows