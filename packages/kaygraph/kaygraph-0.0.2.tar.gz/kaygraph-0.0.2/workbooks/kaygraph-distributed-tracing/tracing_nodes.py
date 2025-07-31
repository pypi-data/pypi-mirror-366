#!/usr/bin/env python3
"""
Distributed tracing nodes for KayGraph using OpenTelemetry.
Provides automatic instrumentation for observability.
"""

import time
import logging
import functools
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
import json

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, Graph, AsyncGraph, BaseNode

# Mock OpenTelemetry imports (in production, use real packages)
# from opentelemetry import trace, baggage, context
# from opentelemetry.trace import Status, StatusCode
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

logger = logging.getLogger(__name__)


# Mock OpenTelemetry classes for demonstration
class MockSpan:
    """Mock span for demonstration."""
    def __init__(self, name: str, kind: str = "INTERNAL"):
        self.name = name
        self.kind = kind
        self.attributes = {}
        self.events = []
        self.status = "OK"
        self.start_time = time.time()
        self.end_time = None
    
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
    
    def add_event(self, name: str, attributes: Optional[Dict] = None):
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        })
    
    def set_status(self, status: str, description: str = ""):
        self.status = status
        if description:
            self.attributes["error.message"] = description
    
    def end(self):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"📊 Span '{self.name}' completed in {duration:.3f}s")


class MockTracer:
    """Mock tracer for demonstration."""
    def __init__(self, service_name: str = "kaygraph"):
        self.service_name = service_name
        self.spans = []
    
    @contextmanager
    def start_span(self, name: str, kind: str = "INTERNAL", attributes: Optional[Dict] = None):
        span = MockSpan(name, kind)
        if attributes:
            for k, v in attributes.items():
                span.set_attribute(k, v)
        
        self.spans.append(span)
        logger.info(f"📍 Starting span: {name}")
        
        try:
            yield span
            span.set_status("OK")
        except Exception as e:
            span.set_status("ERROR", str(e))
            span.set_attribute("error.type", type(e).__name__)
            raise
        finally:
            span.end()
    
    def get_current_span(self):
        return self.spans[-1] if self.spans else None


# Global tracer instance
tracer = MockTracer()


class TracedNode(Node):
    """Base node with automatic tracing capabilities."""
    
    def __init__(self, *args, trace_attributes: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.trace_attributes = trace_attributes or {}
    
    def _run(self, shared: Dict[str, Any]) -> Any:
        """Run with automatic tracing."""
        span_name = f"{self.__class__.__name__}.run"
        
        with tracer.start_span(span_name, attributes={
            "node.id": self.node_id,
            "node.class": self.__class__.__name__,
            "node.params": json.dumps(self.params),
            **self.trace_attributes
        }) as span:
            # Add execution context
            span.set_attribute("execution.start_time", time.time())
            
            try:
                # Run the actual node logic
                result = super()._run(shared)
                
                # Record success metrics
                span.set_attribute("execution.success", True)
                span.add_event("execution_completed", {
                    "has_result": result is not None
                })
                
                return result
                
            except Exception as e:
                # Record error details
                span.set_attribute("execution.success", False)
                span.set_attribute("error.type", type(e).__name__)
                span.add_event("execution_failed", {
                    "error": str(e)
                })
                raise
            
            finally:
                # Record execution metrics
                if hasattr(self, 'cur_retry'):
                    span.set_attribute("execution.retry_count", self.cur_retry)
                
                execution_time = time.time() - span.start_time
                span.set_attribute("execution.duration_ms", execution_time * 1000)
    
    def prep(self, shared: Dict[str, Any]) -> Any:
        """Prep phase with tracing."""
        with tracer.start_span(f"{self.__class__.__name__}.prep") as span:
            span.set_attribute("phase", "prep")
            result = super().prep(shared)
            span.set_attribute("prep.has_result", result is not None)
            return result
    
    def exec(self, prep_res: Any) -> Any:
        """Exec phase with tracing."""
        with tracer.start_span(f"{self.__class__.__name__}.exec") as span:
            span.set_attribute("phase", "exec")
            result = super().exec(prep_res)
            span.set_attribute("exec.has_result", result is not None)
            return result
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> Any:
        """Post phase with tracing."""
        with tracer.start_span(f"{self.__class__.__name__}.post") as span:
            span.set_attribute("phase", "post")
            result = super().post(shared, prep_res, exec_res)
            span.set_attribute("post.action", result or "default")
            return result


class AsyncTracedNode(AsyncNode):
    """Async node with automatic tracing."""
    
    def __init__(self, *args, trace_attributes: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.trace_attributes = trace_attributes or {}
    
    async def _run_async(self, shared: Dict[str, Any]) -> Any:
        """Run with automatic async tracing."""
        span_name = f"{self.__class__.__name__}.run_async"
        
        with tracer.start_span(span_name, attributes={
            "node.id": self.node_id,
            "node.class": self.__class__.__name__,
            "node.async": True,
            **self.trace_attributes
        }) as span:
            try:
                result = await super()._run_async(shared)
                span.set_attribute("execution.success", True)
                return result
            except Exception as e:
                span.set_attribute("execution.success", False)
                span.set_attribute("error.type", type(e).__name__)
                raise


class TracedGraph(Graph):
    """Graph with distributed tracing across all nodes."""
    
    def _orch(self, shared: Dict[str, Any], params: Optional[Dict] = None) -> Any:
        """Orchestrate with tracing."""
        with tracer.start_span(f"{self.__class__.__name__}.orchestrate", kind="SERVER") as span:
            span.set_attribute("graph.start_node", self.start_node.node_id if self.start_node else "none")
            span.set_attribute("graph.node_count", len(self._get_all_nodes()))
            
            # Add trace context to shared
            shared["_trace_context"] = {
                "trace_id": f"trace_{int(time.time()*1000000)}",
                "span_id": f"span_{int(time.time()*1000000)}",
                "service": tracer.service_name
            }
            
            try:
                result = super()._orch(shared, params)
                span.set_attribute("graph.success", True)
                return result
            except Exception as e:
                span.set_attribute("graph.success", False)
                raise
    
    def _get_all_nodes(self) -> list:
        """Get all nodes in the graph."""
        nodes = []
        visited = set()
        
        def traverse(node):
            if node and id(node) not in visited:
                visited.add(id(node))
                nodes.append(node)
                for successor in node.successors.values():
                    traverse(successor)
        
        traverse(self.start_node)
        return nodes


class AsyncTracedGraph(AsyncGraph):
    """Async graph with distributed tracing."""
    
    async def _orch_async(self, shared: Dict[str, Any], params: Optional[Dict] = None) -> Any:
        """Orchestrate async with tracing."""
        with tracer.start_span(f"{self.__class__.__name__}.orchestrate_async", kind="SERVER") as span:
            span.set_attribute("graph.async", True)
            
            # Add trace context
            shared["_trace_context"] = {
                "trace_id": f"trace_{int(time.time()*1000000)}",
                "span_id": f"span_{int(time.time()*1000000)}",
                "service": tracer.service_name
            }
            
            return await super()._orch_async(shared, params)


# Decorator for adding tracing to existing nodes
def trace_node(span_name: Optional[str] = None, attributes: Optional[Dict] = None):
    """Decorator to add tracing to node methods."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            name = span_name or f"{self.__class__.__name__}.{func.__name__}"
            attrs = attributes or {}
            attrs["node.method"] = func.__name__
            
            with tracer.start_span(name, attributes=attrs) as span:
                try:
                    result = func(self, *args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        
        return wrapper
    return decorator


# Example traced nodes
class DataFetchNode(TracedNode):
    """Example node that fetches data with tracing."""
    
    @trace_node(attributes={"operation": "fetch"})
    def exec(self, query: str) -> Dict[str, Any]:
        """Fetch data with detailed tracing."""
        current_span = tracer.get_current_span()
        if current_span:
            current_span.set_attribute("query", query)
            current_span.set_attribute("query.length", len(query))
        
        # Simulate data fetching
        logger.info(f"Fetching data for: {query}")
        time.sleep(0.5)  # Simulate network delay
        
        result = {
            "query": query,
            "results": [
                {"id": 1, "title": "Result 1", "score": 0.95},
                {"id": 2, "title": "Result 2", "score": 0.87},
                {"id": 3, "title": "Result 3", "score": 0.72}
            ],
            "total": 3
        }
        
        if current_span:
            current_span.set_attribute("results.count", len(result["results"]))
            current_span.add_event("data_fetched", {
                "result_count": len(result["results"])
            })
        
        return result


class ProcessingNode(TracedNode):
    """Example node that processes data with tracing."""
    
    def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with tracing."""
        with tracer.start_span("data_processing") as span:
            span.set_attribute("input.size", len(str(data)))
            
            # Simulate processing steps
            with tracer.start_span("validate_data") as validation_span:
                validation_span.set_attribute("data.keys", list(data.keys()))
                time.sleep(0.1)
                valid = True
                validation_span.set_attribute("validation.result", valid)
            
            with tracer.start_span("transform_data") as transform_span:
                time.sleep(0.2)
                processed = {
                    "original": data,
                    "processed_at": time.time(),
                    "transformations": ["normalize", "enrich", "validate"]
                }
                transform_span.set_attribute("transformations.count", 3)
            
            span.set_attribute("output.size", len(str(processed)))
            return processed


class ErrorNode(TracedNode):
    """Example node that demonstrates error tracing."""
    
    def exec(self, data: Any) -> Any:
        """Simulate an error for tracing."""
        with tracer.start_span("risky_operation") as span:
            span.set_attribute("risk.level", "high")
            
            # Simulate some work
            time.sleep(0.1)
            
            # Simulate an error
            if "fail" in str(data).lower():
                span.add_event("error_detected", {"reason": "fail keyword found"})
                raise ValueError("Simulated error for tracing demonstration")
            
            return {"status": "success"}


# Tracing configuration
def configure_tracing(
    service_name: str = "kaygraph",
    endpoint: str = "http://localhost:4317",
    sampler_ratio: float = 1.0,
    export_interval: int = 5000,
    max_queue_size: int = 2048,
    max_export_batch_size: int = 512
):
    """Configure OpenTelemetry tracing."""
    global tracer
    
    # In production, this would configure real OpenTelemetry
    logger.info(f"🔧 Configuring tracing for service: {service_name}")
    logger.info(f"📡 Exporting to: {endpoint}")
    logger.info(f"📊 Sampling ratio: {sampler_ratio}")
    
    # Update mock tracer
    tracer.service_name = service_name
    
    # In production:
    # - Set up TracerProvider with resource info
    # - Configure BatchSpanProcessor with OTLP exporter
    # - Set up context propagation
    # - Configure sampling
    
    return tracer


# Utility functions for manual tracing
@contextmanager
def trace_operation(name: str, attributes: Optional[Dict] = None):
    """Context manager for tracing operations."""
    with tracer.start_span(name, attributes=attributes) as span:
        yield span


def get_current_trace_context() -> Dict[str, str]:
    """Get current trace context for propagation."""
    # In production, this would get real trace context
    return {
        "trace_id": f"trace_{int(time.time()*1000000)}",
        "span_id": f"span_{int(time.time()*1000000)}",
        "trace_flags": "01"
    }


def inject_trace_context(headers: Dict[str, str]) -> Dict[str, str]:
    """Inject trace context into headers for propagation."""
    context = get_current_trace_context()
    headers["traceparent"] = f"00-{context['trace_id']}-{context['span_id']}-{context['trace_flags']}"
    return headers


if __name__ == "__main__":
    # Configure tracing
    configure_tracing(service_name="kaygraph-demo")
    
    # Create traced workflow
    fetch = DataFetchNode(node_id="fetch")
    process = ProcessingNode(node_id="process")
    error = ErrorNode(node_id="error")
    
    # Build graph
    graph = TracedGraph(start=fetch)
    fetch >> process
    
    # Run with tracing
    print("🚀 Running traced workflow...")
    shared = {"query": "test data"}
    graph.run(shared)
    
    # Display trace summary
    print(f"\n📊 Trace Summary:")
    print(f"Total spans created: {len(tracer.spans)}")
    for span in tracer.spans:
        duration = (span.end_time - span.start_time) if span.end_time else 0
        print(f"  - {span.name}: {duration:.3f}s ({span.status})")