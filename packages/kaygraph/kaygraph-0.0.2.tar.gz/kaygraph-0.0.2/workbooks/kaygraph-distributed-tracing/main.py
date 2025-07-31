#!/usr/bin/env python3
"""
Main example for distributed tracing in KayGraph.
"""

import argparse
import logging
import time
import json
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, Graph, AsyncNode, AsyncGraph
from tracing_nodes import (
    TracedNode, AsyncTracedNode, TracedGraph, AsyncTracedGraph,
    configure_tracing, trace_operation, tracer,
    DataFetchNode, ProcessingNode, ErrorNode
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Example workflow nodes
class SearchNode(TracedNode):
    """Search for information."""
    
    def exec(self, query: str) -> Dict:
        with trace_operation("search_external_api") as span:
            span.set_attribute("api.endpoint", "search.example.com")
            span.set_attribute("api.method", "GET")
            
            # Simulate API call
            time.sleep(0.3)
            
            results = {
                "query": query,
                "results": [
                    {"title": "KayGraph Documentation", "url": "docs.kaygraph.com"},
                    {"title": "Building AI Workflows", "url": "blog.example.com/ai"},
                    {"title": "Graph Processing Guide", "url": "guide.example.com"}
                ],
                "timestamp": time.time()
            }
            
            span.set_attribute("results.count", len(results["results"]))
            span.add_event("search_completed")
            
            return results


class AnalyzeNode(TracedNode):
    """Analyze search results."""
    
    def exec(self, search_results: Dict) -> Dict:
        with trace_operation("content_analysis") as span:
            span.set_attribute("input.result_count", len(search_results.get("results", [])))
            
            # Simulate analysis phases
            with trace_operation("relevance_scoring"):
                time.sleep(0.2)
                for i, result in enumerate(search_results["results"]):
                    result["relevance_score"] = 0.9 - (i * 0.1)
            
            with trace_operation("content_extraction"):
                time.sleep(0.15)
                for result in search_results["results"]:
                    result["summary"] = f"Summary of {result['title']}"
            
            with trace_operation("ranking"):
                time.sleep(0.1)
                search_results["results"].sort(
                    key=lambda x: x["relevance_score"], 
                    reverse=True
                )
            
            analysis = {
                "original_query": search_results["query"],
                "analyzed_results": search_results["results"],
                "analysis_metadata": {
                    "total_results": len(search_results["results"]),
                    "avg_relevance": sum(r["relevance_score"] for r in search_results["results"]) / len(search_results["results"]),
                    "analysis_time": time.time()
                }
            }
            
            span.set_attribute("analysis.avg_relevance", analysis["analysis_metadata"]["avg_relevance"])
            return analysis


class SummarizeNode(TracedNode):
    """Summarize analysis results."""
    
    def exec(self, analysis: Dict) -> str:
        with trace_operation("generate_summary") as span:
            span.set_attribute("results.count", len(analysis["analyzed_results"]))
            
            # Simulate summarization
            time.sleep(0.25)
            
            summary_parts = [
                f"Query: '{analysis['original_query']}'",
                f"Found {len(analysis['analyzed_results'])} relevant results.",
                f"Average relevance score: {analysis['analysis_metadata']['avg_relevance']:.2f}",
                "\nTop results:"
            ]
            
            for i, result in enumerate(analysis["analyzed_results"][:3]):
                summary_parts.append(
                    f"{i+1}. {result['title']} (score: {result['relevance_score']:.2f})"
                )
            
            summary = "\n".join(summary_parts)
            
            span.set_attribute("summary.length", len(summary))
            span.add_event("summary_generated", {"char_count": len(summary)})
            
            return summary


# Build example workflows
def build_search_workflow():
    """Build a traced search workflow."""
    search = SearchNode(node_id="search")
    analyze = AnalyzeNode(node_id="analyze")
    summarize = SummarizeNode(node_id="summarize")
    
    graph = TracedGraph(start=search)
    search >> analyze >> summarize
    
    return graph


def build_error_workflow():
    """Build a workflow that demonstrates error tracing."""
    
    class StartNode(TracedNode):
        def exec(self, data):
            logger.info("Starting error demonstration workflow")
            return data
    
    class RiskyNode(TracedNode):
        def exec(self, data):
            with trace_operation("risky_operation") as span:
                span.set_attribute("risk.level", "high")
                
                if data.get("simulate_error", False):
                    span.add_event("error_triggered", {"reason": "simulation"})
                    raise RuntimeError("Simulated error for tracing")
                
                return {"status": "success", "data": data}
    
    class RecoveryNode(TracedNode):
        def exec(self, error_info):
            with trace_operation("error_recovery") as span:
                span.set_attribute("recovery.strategy", "retry")
                logger.info("Attempting recovery from error")
                time.sleep(0.5)
                return {"recovered": True, "original_error": str(error_info)}
    
    start = StartNode(node_id="start")
    risky = RiskyNode(node_id="risky", max_retries=2)
    recovery = RecoveryNode(node_id="recovery")
    
    # Override exec_fallback to route to recovery
    original_fallback = risky.exec_fallback
    def exec_fallback_with_recovery(prep_res, exc):
        with trace_operation("fallback_routing") as span:
            span.set_attribute("error.type", type(exc).__name__)
            return {"error": str(exc), "prep_res": prep_res}
    risky.exec_fallback = exec_fallback_with_recovery
    
    graph = TracedGraph(start=start)
    start >> risky >> recovery
    
    return graph


def build_async_workflow():
    """Build an async traced workflow."""
    
    class AsyncSearchNode(AsyncTracedNode):
        async def exec_async(self, queries):
            import asyncio
            
            with trace_operation("parallel_search") as span:
                span.set_attribute("query.count", len(queries))
                
                async def search_one(query):
                    with trace_operation(f"search_query_{query}") as query_span:
                        query_span.set_attribute("query", query)
                        await asyncio.sleep(0.2)  # Simulate API call
                        return {"query": query, "results": f"Results for {query}"}
                
                # Search in parallel
                results = await asyncio.gather(*[search_one(q) for q in queries])
                
                span.set_attribute("results.total", len(results))
                return results
    
    class AsyncAggregateNode(AsyncTracedNode):
        async def exec_async(self, results):
            with trace_operation("aggregate_results") as span:
                span.set_attribute("input.count", len(results))
                
                import asyncio
                await asyncio.sleep(0.1)  # Simulate processing
                
                aggregated = {
                    "total_results": len(results),
                    "queries": [r["query"] for r in results],
                    "combined_results": results
                }
                
                return aggregated
    
    search = AsyncSearchNode(node_id="async_search")
    aggregate = AsyncAggregateNode(node_id="async_aggregate")
    
    graph = AsyncTracedGraph(start=search)
    search >> aggregate
    
    return graph


def display_trace_summary(trace_data):
    """Display a summary of the trace."""
    print("\n" + "="*60)
    print("📊 TRACE SUMMARY")
    print("="*60)
    
    # Group spans by node
    node_spans = {}
    for span in tracer.spans:
        node_name = span.attributes.get("node.class", "Unknown")
        if node_name not in node_spans:
            node_spans[node_name] = []
        node_spans[node_name].append(span)
    
    # Display per-node statistics
    print("\n📍 Node Execution Statistics:")
    for node, spans in node_spans.items():
        total_time = sum((s.end_time - s.start_time) for s in spans if s.end_time)
        avg_time = total_time / len(spans) if spans else 0
        errors = sum(1 for s in spans if s.status == "ERROR")
        
        print(f"\n  {node}:")
        print(f"    • Executions: {len(spans)}")
        print(f"    • Total time: {total_time:.3f}s")
        print(f"    • Average time: {avg_time:.3f}s")
        if errors:
            print(f"    • Errors: {errors}")
    
    # Display span tree
    print("\n🌳 Span Tree:")
    for i, span in enumerate(tracer.spans):
        indent = "  " * (i % 3)  # Simple indentation
        duration = (span.end_time - span.start_time) if span.end_time else 0
        status_icon = "✅" if span.status == "OK" else "❌"
        print(f"{indent}{status_icon} {span.name} ({duration:.3f}s)")
        
        # Show key attributes
        for key in ["node.id", "query", "results.count", "error.type"]:
            if key in span.attributes:
                print(f"{indent}    {key}: {span.attributes[key]}")
    
    # Export trace data
    trace_file = f"trace_{int(time.time())}.json"
    trace_export = {
        "service": tracer.service_name,
        "start_time": min(s.start_time for s in tracer.spans) if tracer.spans else 0,
        "end_time": max(s.end_time for s in tracer.spans if s.end_time) if tracer.spans else 0,
        "span_count": len(tracer.spans),
        "spans": [
            {
                "name": s.name,
                "start_time": s.start_time,
                "duration": (s.end_time - s.start_time) if s.end_time else 0,
                "status": s.status,
                "attributes": s.attributes,
                "events": s.events
            }
            for s in tracer.spans
        ]
    }
    
    with open(trace_file, 'w') as f:
        json.dump(trace_export, f, indent=2)
    
    print(f"\n💾 Full trace exported to: {trace_file}")
    print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KayGraph Distributed Tracing Example"
    )
    
    parser.add_argument(
        "--workflow",
        choices=["search", "error", "async"],
        default="search",
        help="Workflow to run"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        default="What is KayGraph?",
        help="Query for search workflow"
    )
    
    parser.add_argument(
        "--simulate-error",
        action="store_true",
        help="Simulate errors in workflows"
    )
    
    parser.add_argument(
        "--exporter",
        choices=["console", "jaeger", "zipkin"],
        default="console",
        help="Trace exporter to use"
    )
    
    parser.add_argument(
        "--endpoint",
        type=str,
        default="http://localhost:4317",
        help="Exporter endpoint"
    )
    
    parser.add_argument(
        "--debug-spans",
        action="store_true",
        help="Enable debug-level spans"
    )
    
    args = parser.parse_args()
    
    # Configure tracing
    configure_tracing(
        service_name=f"kaygraph-{args.workflow}",
        endpoint=args.endpoint,
        sampler_ratio=1.0 if args.debug_spans else 0.1
    )
    
    print(f"🚀 Running {args.workflow} workflow with tracing...")
    print(f"📡 Exporting to: {args.exporter} ({args.endpoint})")
    
    # Run selected workflow
    if args.workflow == "search":
        graph = build_search_workflow()
        shared = {"query": args.query}
        result = graph.run(shared)
        print(f"\n📝 Summary:\n{result}")
        
    elif args.workflow == "error":
        graph = build_error_workflow()
        shared = {"simulate_error": args.simulate_error}
        result = graph.run(shared)
        print(f"\n🔧 Recovery result: {result}")
        
    elif args.workflow == "async":
        import asyncio
        graph = build_async_workflow()
        queries = [args.query, "How to trace workflows?", "OpenTelemetry guide"]
        shared = {"queries": queries}
        result = asyncio.run(graph.run_async(shared))
        print(f"\n📊 Aggregated: {result['total_results']} results from {len(result['queries'])} queries")
    
    # Display trace summary
    display_trace_summary(tracer.spans)
    
    # In production, you would view traces in Jaeger UI at http://localhost:16686
    print("\n💡 In production, view traces at: http://localhost:16686")


if __name__ == "__main__":
    main()