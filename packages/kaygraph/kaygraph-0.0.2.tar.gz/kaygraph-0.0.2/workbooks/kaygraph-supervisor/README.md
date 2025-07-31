# KayGraph Supervisor Pattern

Demonstrates the supervisor pattern for managing unreliable worker agents with retry logic and result validation.

## What it does

The supervisor pattern handles:
- **Task Assignment**: Distributes research tasks to worker agents
- **Worker Management**: Tracks worker performance and reliability
- **Retry Logic**: Automatically retries failed tasks with different workers
- **Result Validation**: Ensures quality of worker outputs
- **Performance Tracking**: Monitors success rates and selects best workers

## How to run

```bash
python main.py
```

## Architecture

```
                    SupervisorNode
                    ↙     ↓     ↘
            Worker1   Worker2   Worker3
                    ↘     ↓     ↙
                    SupervisorNode
                          ↓
                   ValidationNode → ReportNode
```

## Key Components

### SupervisorNode (MetricsNode)
- Assigns tasks to workers
- Monitors task completion
- Implements retry strategy
- Selects workers based on performance
- Consolidates successful results

### WorkerNode
- Executes research tasks
- Simulates unreliable behavior (configurable reliability)
- Reports results back to supervisor
- Can fail with various error types

### ValidationNode
- Validates research results
- Checks data completeness
- Ensures quality thresholds
- Identifies issues

### ReportNode
- Generates supervision summary
- Shows worker performance stats
- Displays final results

## Features

- **Smart Worker Selection**: Chooses workers based on success history
- **Configurable Reliability**: Simulate different worker success rates
- **Quality Validation**: Ensure results meet standards
- **Performance Metrics**: Track supervisor efficiency
- **Detailed Reporting**: Comprehensive supervision summary

## Configuration

```python
# Create supervisor with custom settings
graph = create_supervisor_graph(
    num_workers=5,           # Number of worker agents
    worker_reliability=0.8   # 80% success rate
)

# Supervisor settings
supervisor = SupervisorNode(
    max_attempts=10,         # Maximum retry attempts
    node_id="supervisor"
)
```

## Example Output

```
Supervision Report
==================

Topic: Quantum Computing Applications
Status: SUCCESS
Total Attempts: 3

Worker Performance:
  - worker1: 0/1 success (0.0%)
  - worker2: 1/2 success (50.0%)
  - worker3: 0/0 success (0.0%)

Final Result:
  Worker: worker2
  Confidence: 0.85
  Findings:
    - Fact 1 about Quantum Computing Applications
    - Fact 2 about Quantum Computing Applications
    - Important insight about Quantum Computing Applications
```

## Use Cases

- **Distributed Web Scraping**: Manage unreliable scrapers
- **API Integration**: Handle flaky external services
- **Data Processing**: Coordinate parallel workers
- **Content Generation**: Ensure quality from AI agents
- **Testing**: Coordinate test execution agents

## Customization

### Custom Task Types
Modify `utils/tasks.py` to add:
- Different task complexities
- Domain-specific requirements
- Custom validation rules

### Worker Behaviors
Extend `WorkerNode` to simulate:
- Network delays
- Partial failures
- Quality variations
- Resource constraints

### Selection Strategies
Implement custom worker selection:
- Load balancing
- Skill-based routing
- Cost optimization
- Geographic distribution

Perfect for building robust multi-agent systems!