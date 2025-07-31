---
layout: default
title: "Monitoring"
parent: "Production"
nav_order: 2
---

# Production Monitoring and Metrics

KayGraph provides comprehensive monitoring capabilities through built-in logging, metrics collection, and performance analysis tools essential for production deployments.

## Built-in Logging System

Every KayGraph node and graph includes automatic logging with detailed execution information.

### Logging Configuration

```python
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Advanced configuration for production
def setup_production_logging():
    """Configure production-grade logging"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler('kaygraph.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    
    # Error-specific handler
    error_handler = logging.FileHandler('kaygraph_errors.log', mode='a')
    error_handler.setLevel(logging.ERROR)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    for handler in [console_handler, file_handler, error_handler]:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

setup_production_logging()
```

### Log Levels and Content

- **DEBUG**: Detailed data passed between prep, exec, and post
- **INFO**: Node execution start/end, transitions, timing
- **WARNING**: Non-critical issues, retries, missing transitions
- **ERROR**: Critical failures, validation errors, exceptions

**Sample Log Output:**
```
2024-01-01 10:00:00,123 - DataProcessor - INFO - [main.py:45] - Node data_processor: Starting execution with params: {'batch_size': 100}
2024-01-01 10:00:00,125 - DataProcessor - DEBUG - [main.py:48] - Node data_processor: prep() returned: {'data': [...], 'count': 100}
2024-01-01 10:00:01,250 - DataProcessor - DEBUG - [main.py:52] - Node data_processor: exec() returned: {'processed': 100, 'status': 'success'}
2024-01-01 10:00:01,252 - DataProcessor - INFO - [main.py:55] - Node data_processor: Completed in 1.127s with action: 'default'
```

## MetricsNode for Performance Monitoring

`MetricsNode` provides built-in performance metrics collection and analysis.

### Basic Metrics Collection

```python
from kaygraph import MetricsNode
import time

class MonitoredProcessor(MetricsNode):
    def __init__(self):
        super().__init__(
            collect_metrics=True,  # Enable metrics collection
            max_retries=3,
            wait=1,
            node_id="monitored_processor"
        )
    
    def exec(self, data):
        # Simulate processing time
        time.sleep(0.1 + len(str(data)) * 0.001)
        
        # Simulate occasional failures
        if len(str(data)) > 1000:
            raise ValueError("Data too large")
        
        return f"Processed: {data}"

# Usage
processor = MonitoredProcessor()

# Run multiple times to collect metrics
for i in range(10):
    shared = {"data": f"sample_data_{i}"}
    try:
        processor.run(shared)
    except Exception as e:
        print(f"Run {i} failed: {e}")

# Analyze metrics
stats = processor.get_stats()
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Avg execution time: {stats['avg_execution_time']:.3f}s")
print(f"Total retries: {stats['total_retries']}")
```

### Available Metrics

```python
{
    'total_executions': 10,
    'success_rate': 0.9,              # 90% success rate
    'avg_execution_time': 0.125,      # Average time in seconds
    'min_execution_time': 0.101,      # Fastest execution
    'max_execution_time': 0.187,      # Slowest execution
    'total_retries': 3                # Total retry attempts
}
```

## Advanced Monitoring Patterns

### Custom Metrics Collection

```python
class AdvancedMetricsNode(MetricsNode):
    def __init__(self):
        super().__init__(collect_metrics=True, node_id="advanced_metrics")
        self.custom_metrics = {
            "data_sizes": [],
            "processing_rates": [],
            "error_types": {},
            "peak_memory": 0
        }
    
    def before_prep(self, shared):
        """Collect pre-processing metrics"""
        self.set_context("start_memory", self._get_memory_usage())
        self.set_context("start_time", time.time())
    
    def after_exec(self, shared, prep_res, exec_res):
        """Collect post-processing metrics"""
        # Calculate processing rate
        processing_time = time.time() - self.get_context("start_time", 0)
        data_size = len(str(prep_res))
        
        if processing_time > 0:
            rate = data_size / processing_time
            self.custom_metrics["processing_rates"].append(rate)
        
        # Track data sizes
        self.custom_metrics["data_sizes"].append(data_size)
        
        # Track memory usage
        current_memory = self._get_memory_usage()
        if current_memory > self.custom_metrics["peak_memory"]:
            self.custom_metrics["peak_memory"] = current_memory
    
    def on_error(self, shared, error):
        """Track error types"""
        error_type = type(error).__name__
        self.custom_metrics["error_types"][error_type] = \
            self.custom_metrics["error_types"].get(error_type, 0) + 1
        return False
    
    def _get_memory_usage(self):
        """Get current memory usage in MB"""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def get_detailed_stats(self):
        """Get comprehensive statistics"""
        base_stats = self.get_stats()
        
        # Add custom metrics
        if self.custom_metrics["data_sizes"]:
            base_stats.update({
                "avg_data_size": sum(self.custom_metrics["data_sizes"]) / len(self.custom_metrics["data_sizes"]),
                "max_data_size": max(self.custom_metrics["data_sizes"]),
                "min_data_size": min(self.custom_metrics["data_sizes"])
            })
        
        if self.custom_metrics["processing_rates"]:
            base_stats.update({
                "avg_processing_rate": sum(self.custom_metrics["processing_rates"]) / len(self.custom_metrics["processing_rates"]),
                "max_processing_rate": max(self.custom_metrics["processing_rates"])
            })
        
        base_stats.update({
            "peak_memory_mb": self.custom_metrics["peak_memory"],
            "error_breakdown": self.custom_metrics["error_types"]
        })
        
        return base_stats
```

### Graph-Level Monitoring

```python
class MonitoredGraph(Graph):
    def __init__(self, start=None):
        super().__init__(start)
        self.graph_metrics = {
            "executions": 0,
            "total_time": 0,
            "node_performance": {},
            "transition_counts": {},
            "failure_points": {}
        }
    
    def _orch(self, shared, params=None):
        """Override orchestration with monitoring"""
        start_time = time.time()
        self.graph_metrics["executions"] += 1
        
        current_node = copy.copy(self.start_node)
        node_params = params or {**self.params}
        last_action = None
        
        while current_node:
            node_name = current_node.node_id or current_node.__class__.__name__
            
            # Track node performance
            node_start = time.time()
            
            try:
                current_node.set_params(node_params)
                last_action = current_node._run(shared)
                
                # Record successful execution
                node_time = time.time() - node_start
                if node_name not in self.graph_metrics["node_performance"]:
                    self.graph_metrics["node_performance"][node_name] = []
                self.graph_metrics["node_performance"][node_name].append(node_time)
                
            except Exception as e:
                # Track failure points
                self.graph_metrics["failure_points"][node_name] = \
                    self.graph_metrics["failure_points"].get(node_name, 0) + 1
                raise
            
            # Track transitions
            transition_key = f"{node_name}->{last_action}"
            self.graph_metrics["transition_counts"][transition_key] = \
                self.graph_metrics["transition_counts"].get(transition_key, 0) + 1
            
            current_node = copy.copy(self.get_next_node(current_node, last_action))
        
        # Record total execution time
        total_time = time.time() - start_time
        self.graph_metrics["total_time"] += total_time
        
        return last_action
    
    def get_graph_stats(self):
        """Get comprehensive graph statistics"""
        if self.graph_metrics["executions"] == 0:
            return {"status": "no_executions"}
        
        stats = {
            "total_executions": self.graph_metrics["executions"],
            "avg_execution_time": self.graph_metrics["total_time"] / self.graph_metrics["executions"],
            "total_time": self.graph_metrics["total_time"]
        }
        
        # Node performance analysis
        node_stats = {}
        for node_name, times in self.graph_metrics["node_performance"].items():
            node_stats[node_name] = {
                "executions": len(times),
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times)
            }
        stats["node_performance"] = node_stats
        
        # Transition analysis
        stats["transition_counts"] = self.graph_metrics["transition_counts"]
        
        # Failure analysis
        if self.graph_metrics["failure_points"]:
            stats["failure_points"] = self.graph_metrics["failure_points"]
        
        return stats
```

## Production Monitoring Tools

### Health Check Endpoints

```python
from kaygraph import Graph, MetricsNode
import json

class HealthCheckNode(MetricsNode):
    def __init__(self):
        super().__init__(collect_metrics=True, node_id="health_check")
    
    def exec(self, _):
        """Simple health check"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0"
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["health_status"] = exec_res

def create_health_check_graph():
    """Create a health check graph for monitoring"""
    health_node = HealthCheckNode()
    return Graph(start=health_node)

# Usage in web framework (e.g., FastAPI)
from fastapi import FastAPI

app = FastAPI()
health_graph = create_health_check_graph()

@app.get("/health")
async def health_check():
    shared = {}
    health_graph.run(shared)
    
    # Add metrics
    health_node = health_graph.start_node
    stats = health_node.get_stats()
    
    return {
        **shared["health_status"],
        "metrics": stats
    }
```

### Alerting Integration

```python
class AlertingNode(MetricsNode):
    def __init__(self, alert_threshold=0.8):
        super().__init__(collect_metrics=True, node_id="alerting_processor")
        self.alert_threshold = alert_threshold
        self.alert_cooldown = 300  # 5 minutes
        self.last_alert = 0
    
    def after_exec(self, shared, prep_res, exec_res):
        """Check if alerting is needed"""
        stats = self.get_stats()
        
        # Check success rate
        if (stats.get('success_rate', 1.0) < self.alert_threshold and 
            time.time() - self.last_alert > self.alert_cooldown):
            
            self._send_alert(stats)
            self.last_alert = time.time()
    
    def _send_alert(self, stats):
        """Send alert (implement your alerting system)"""
        alert_data = {
            "node_id": self.node_id,
            "success_rate": stats.get('success_rate', 0),
            "threshold": self.alert_threshold,
            "avg_execution_time": stats.get('avg_execution_time', 0),
            "total_executions": stats.get('total_executions', 0),
            "timestamp": time.time()
        }
        
        # Send to your alerting system (Slack, PagerDuty, etc.)
        self.logger.error(f"ALERT: Performance threshold breached: {alert_data}")
        # webhook_send(alert_data)
```

### Metrics Export

```python
class MetricsExporter:
    """Export metrics to external monitoring systems"""
    
    def __init__(self, nodes, graphs):
        self.nodes = nodes
        self.graphs = graphs
    
    def export_prometheus_metrics(self):
        """Export metrics in Prometheus format"""
        metrics = []
        
        for node in self.nodes:
            if hasattr(node, 'get_stats'):
                stats = node.get_stats()
                node_name = node.node_id or node.__class__.__name__
                
                metrics.append(f'kaygraph_node_executions_total{{node="{node_name}"}} {stats.get("total_executions", 0)}')
                metrics.append(f'kaygraph_node_success_rate{{node="{node_name}"}} {stats.get("success_rate", 0)}')
                metrics.append(f'kaygraph_node_avg_duration_seconds{{node="{node_name}"}} {stats.get("avg_execution_time", 0)}')
        
        return '\n'.join(metrics)
    
    def export_json_metrics(self):
        """Export metrics as JSON"""
        export_data = {
            "timestamp": time.time(),
            "nodes": {},
            "graphs": {}
        }
        
        # Export node metrics
        for node in self.nodes:
            if hasattr(node, 'get_stats'):
                node_name = node.node_id or node.__class__.__name__
                export_data["nodes"][node_name] = node.get_stats()
        
        # Export graph metrics
        for graph in self.graphs:
            if hasattr(graph, 'get_graph_stats'):
                graph_name = graph.node_id or graph.__class__.__name__
                export_data["graphs"][graph_name] = graph.get_graph_stats()
        
        return json.dumps(export_data, indent=2)

# Usage
exporter = MetricsExporter(nodes=[processor_node], graphs=[main_graph])
prometheus_data = exporter.export_prometheus_metrics()
json_data = exporter.export_json_metrics()
```

## Monitoring Best Practices

### 1. Set Up Comprehensive Logging Early

```python
def setup_production_monitoring():
    """Set up production monitoring configuration"""
    # Configure logging
    setup_production_logging()
    
    # Set log levels for different environments
    if os.getenv("ENVIRONMENT") == "production":
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Enable metrics collection globally
    os.environ["KAYGRAPH_COLLECT_METRICS"] = "true"
```

### 2. Monitor Key Performance Indicators

- **Execution Time**: Track processing latency
- **Success Rate**: Monitor error rates and reliability
- **Throughput**: Measure items processed per second
- **Resource Usage**: Monitor memory and CPU usage
- **Error Patterns**: Analyze failure modes

### 3. Implement Alerting Thresholds

```python
MONITORING_THRESHOLDS = {
    "success_rate_min": 0.95,      # 95% minimum success rate
    "avg_execution_time_max": 5.0,  # 5 second max average time
    "error_rate_max": 0.05,        # 5% maximum error rate
    "memory_usage_max": 1024       # 1GB max memory usage
}
```

### 4. Use Structured Logging

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ]
)

class StructuredLoggingNode(Node):
    def __init__(self):
        super().__init__(node_id="structured_logger")
        self.structured_logger = structlog.get_logger()
    
    def _run(self, shared):
        self.structured_logger.info(
            "node_execution_start",
            node_id=self.node_id,
            params=self.params,
            shared_keys=list(shared.keys())
        )
        
        try:
            result = super()._run(shared)
            self.structured_logger.info(
                "node_execution_success",
                node_id=self.node_id,
                action=result
            )
            return result
        except Exception as e:
            self.structured_logger.error(
                "node_execution_error",
                node_id=self.node_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
```

By implementing comprehensive monitoring with KayGraph's built-in tools, you can maintain visibility into your production systems, quickly identify issues, and optimize performance for reliable, scalable LLM applications.