# KayGraph Metrics Dashboard

This example demonstrates KayGraph's production-ready metrics collection and monitoring capabilities using MetricsNode. It showcases how to build observable, measurable workflows with real-time performance tracking.

## Features Demonstrated

1. **MetricsNode Usage**: Automatic collection of execution times, retry counts, and success rates
2. **Real-time Dashboard**: Web-based dashboard showing node performance metrics
3. **Complex Graph Monitoring**: Track metrics across interconnected nodes
4. **Performance Analysis**: Identify bottlenecks and optimization opportunities
5. **Production Patterns**: Best practices for observable workflows

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  DataIngestion  │────▶│ DataValidation   │────▶│ DataProcessing  │
│  (MetricsNode)  │     │  (MetricsNode)   │     │  (MetricsNode)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         └───────────────────────┴─────────────────────────┘
                                 │
                          ┌──────▼──────┐
                          │   Metrics   │
                          │  Dashboard  │
                          └─────────────┘
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the example
python main.py

# Open dashboard in browser
# http://localhost:8000
```

## Key Concepts

### MetricsNode Benefits
- Automatic timing of prep(), exec(), and post() methods
- Retry tracking for fault tolerance analysis
- Success/failure rate calculation
- No manual instrumentation needed

### Production Patterns
- Graceful degradation with metrics
- Performance baselines and alerts
- Resource usage tracking
- SLA monitoring

## Example Output

The dashboard shows:
- Execution time histograms per node
- Success rate gauges
- Retry attempt charts
- Graph-wide performance metrics
- Real-time updates as workflow runs