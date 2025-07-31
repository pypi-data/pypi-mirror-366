# KayGraph Distributed Tracing

This example demonstrates distributed tracing for KayGraph workflows using OpenTelemetry, enabling deep observability into complex graph executions across multiple nodes and services.

## What is Distributed Tracing?

Distributed tracing allows you to:
- **Track requests** across multiple nodes and services
- **Visualize execution flow** with timing information
- **Debug performance issues** by identifying bottlenecks
- **Monitor errors** and their propagation through the graph
- **Understand dependencies** between nodes

## Features

1. **Automatic Instrumentation**: Trace all node executions
2. **Context Propagation**: Track requests across async boundaries
3. **Performance Metrics**: Measure execution times
4. **Error Tracking**: Capture and trace exceptions
5. **Visualization**: Export to Jaeger, Zipkin, or other backends

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   KayGraph  │────▶│ OpenTelemetry│────▶│   Jaeger    │
│    Nodes    │     │   Collector  │     │   Backend   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                          │
       └──────────── Trace Context ───────────────┘
```

## Quick Start

### 1. Start Jaeger (for visualization)
```bash
# Using Docker
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest

# Access UI at http://localhost:16686
```

### 2. Run Traced Workflow
```bash
# Basic tracing
python main.py

# Trace a specific workflow
python main.py --workflow rag --query "What is KayGraph?"

# Enable debug spans
python main.py --debug-spans

# Export to different backend
python main.py --exporter zipkin --endpoint http://localhost:9411
```

## Usage Examples

### Basic Node Tracing
```python
from kaygraph_tracing import TracedNode

class MyNode(TracedNode):
    def exec(self, data):
        # Automatically traced!
        return process_data(data)
```

### Manual Span Creation
```python
from kaygraph_tracing import tracer

class DetailedNode(TracedNode):
    def exec(self, data):
        with tracer.start_span("data_validation") as span:
            span.set_attribute("data.size", len(data))
            validated = self.validate(data)
        
        with tracer.start_span("processing") as span:
            result = self.process(validated)
            span.set_attribute("result.type", type(result).__name__)
        
        return result
```

### Async Tracing
```python
class AsyncTracedNode(AsyncTracedNode):
    async def exec_async(self, data):
        # Context automatically propagated
        async with tracer.start_span("async_operation"):
            result = await external_api_call(data)
        return result
```

### Graph-Level Tracing
```python
# Entire graph execution is traced
graph = TracedGraph(start=node1)
node1 >> node2 >> node3

# Run with tracing
graph.run({"input": "data"})
```

## Trace Attributes

Each span automatically includes:
- `node.id`: Node identifier
- `node.class`: Node class name
- `node.params`: Node parameters
- `execution.duration`: Execution time
- `execution.retry_count`: Number of retries
- `error.type`: Exception type (if failed)
- `error.message`: Error message (if failed)

## Advanced Features

### 1. Baggage Propagation
```python
# Set baggage that propagates to all child spans
with tracer.start_span("root") as span:
    baggage.set_baggage("user.id", "12345")
    baggage.set_baggage("request.id", "abc-123")
```

### 2. Custom Samplers
```python
# Sample only 10% of traces
sampler = TraceIdRatioBasedSampler(0.1)

# Sample based on attributes
sampler = CustomSampler(
    lambda span: span.attributes.get("priority") == "high"
)
```

### 3. Trace Correlation
```python
# Correlate logs with traces
logger.info("Processing started", extra={
    "trace_id": span.get_span_context().trace_id,
    "span_id": span.get_span_context().span_id
})
```

### 4. Metrics Integration
```python
# Record metrics with trace context
meter = metrics.get_meter(__name__)
counter = meter.create_counter("requests_total")

with tracer.start_span("process") as span:
    counter.add(1, {"trace_id": span.get_span_context().trace_id})
```

## Visualization in Jaeger

1. **Service Map**: See how nodes connect
2. **Trace Timeline**: Visualize execution flow
3. **Span Details**: Inspect attributes and logs
4. **Compare Traces**: Find performance regressions
5. **Dependency Graph**: Understand service dependencies

## Performance Considerations

- **Sampling**: Use sampling in production to reduce overhead
- **Async Export**: Use batch span processor for better performance
- **Attribute Limits**: Limit attribute sizes to prevent memory issues
- **Context Propagation**: Minimize context size

## Integration with Other Examples

Tracing works seamlessly with:
- **Multi-Agent**: Trace agent interactions
- **RAG**: Track retrieval and generation steps
- **Async Workflows**: Maintain context across async boundaries
- **Fault-Tolerant**: Trace retry attempts and fallbacks

## Configuration

```python
# Configure tracing
configure_tracing(
    service_name="kaygraph-app",
    endpoint="http://localhost:4317",
    sampler_ratio=0.1,  # Sample 10% of traces
    export_interval=5000,  # Export every 5 seconds
    max_queue_size=2048,
    max_export_batch_size=512
)
```

## Best Practices

1. **Meaningful Span Names**: Use descriptive, consistent names
2. **Appropriate Attributes**: Add relevant context without overdoing it
3. **Error Handling**: Always record exceptions in spans
4. **Sampling Strategy**: Balance visibility with performance
5. **Span Relationships**: Use links for loosely coupled operations

## Troubleshooting

- **No traces showing**: Check Jaeger is running and accessible
- **Missing spans**: Ensure context propagation is working
- **Performance impact**: Adjust sampling rate or use async export
- **Memory usage**: Limit span attributes and use batch export