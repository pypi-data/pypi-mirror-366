# KayGraph Real-time Monitoring Example

This example demonstrates KayGraph's real-time monitoring capabilities, allowing you to track the state of your workflow network without impacting performance.

## Features

- **Real-time State Tracking**: Monitor which nodes are executing, data flow, and success/failure states
- **Non-blocking Monitoring**: Fire-and-forget async pattern ensures <1% performance overhead
- **Multiple Backends**: Support for Redis Pub/Sub, HTTP webhooks, and mock API
- **Live Dashboard**: WebSocket-based dashboard showing network flow visualization
- **Configurable Verbosity**: Control what events are captured and sent
- **Resilient Design**: Monitoring failures don't affect main workflow execution

## Usage

### Basic Example

```python
from monitoring_nodes import MonitoringNode
from utils.monitoring import MonitoringConfig, RedisBackend

# Configure monitoring
config = MonitoringConfig(
    backend=RedisBackend("localhost", 6379),
    enable_data_snapshots=True,
    sample_rate=1.0  # Capture 100% of events
)

# Create nodes that inherit from MonitoringNode
class MyProcessingNode(MonitoringNode):
    def exec(self, data):
        # Your processing logic
        result = process_data(data)
        return result

# Events are automatically sent to monitoring backend
```

### Running the Dashboard

1. Start Redis (if using Redis backend):
   ```bash
   docker run -d -p 6379:6379 redis:alpine
   ```

2. Run the monitoring dashboard:
   ```bash
   python -m utils.dashboard
   ```

3. Open browser to http://localhost:8080 to see real-time monitoring

4. Run your workflow:
   ```bash
   python main.py
   ```

## Architecture

The monitoring system consists of:

1. **MonitoringNode**: Base class that intercepts node lifecycle events
2. **Event Dispatcher**: Async component that sends events to backends
3. **Monitoring Backends**: Pluggable storage (Redis, HTTP, Mock)
4. **Dashboard Server**: WebSocket server for real-time visualization
5. **Web UI**: Interactive dashboard showing network state

## Performance Considerations

- Events are sent asynchronously, never blocking main execution
- Connection pooling minimizes overhead
- Configurable sampling for high-throughput workflows
- Circuit breaker prevents monitoring failures from cascading
- Event batching reduces network calls

## Event Types

- **Lifecycle Events**: node_started, node_preparing, node_executing, node_completed
- **Data Flow Events**: data_input, data_output (with optional snapshots)
- **Error Events**: node_failed, retry_attempted, fallback_triggered
- **Performance Events**: execution_time, queue_depth, throughput_metric

## Configuration Options

```python
MonitoringConfig(
    backend=...,                    # Backend instance
    enable_data_snapshots=False,    # Include data in events
    max_snapshot_size=1024,         # Max bytes for snapshots
    sample_rate=0.1,                # Sample 10% of events
    batch_size=100,                 # Batch events
    flush_interval=1.0,             # Flush every second
    circuit_breaker_threshold=5,    # Failures before circuit opens
    async_workers=4                 # Number of async workers
)
```