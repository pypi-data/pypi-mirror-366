#!/usr/bin/env python3
"""
Execution tracer for KayGraph workflows.
Traces and visualizes the execution flow with timing and state information.
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import BaseNode, Graph

logger = logging.getLogger(__name__)


class ExecutionEvent:
    """Represents an execution event during graph traversal."""
    
    def __init__(self, 
                 node_id: str,
                 event_type: str,
                 timestamp: float,
                 data: Optional[Dict[str, Any]] = None):
        self.node_id = node_id
        self.event_type = event_type  # "enter", "exit", "error"
        self.timestamp = timestamp
        self.data = data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "data": self.data
        }


class ExecutionTracer:
    """Traces KayGraph execution for visualization and debugging."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.events: List[ExecutionEvent] = []
        self.state_snapshots: Dict[str, Any] = {}
        self.start_time: Optional[float] = None
        self._original_run = None
        self._patch_graph()
    
    def _patch_graph(self):
        """Monkey-patch graph nodes to add tracing."""
        # Store original methods
        self._original_methods = {}
        
        # Patch all nodes in the graph
        def patch_node(node: BaseNode):
            if node.node_id in self._original_methods:
                return  # Already patched
            
            # Store original methods
            self._original_methods[node.node_id] = {
                "_run": node._run,
                "on_error": node.on_error
            }
            
            # Create traced versions
            original_run = node._run
            original_on_error = node.on_error
            
            def traced_run(shared):
                # Record entry
                self._record_event(node.node_id, "enter", {
                    "shared_state": self._serialize_state(shared),
                    "params": node.params
                })
                
                try:
                    # Execute original
                    result = original_run(shared)
                    
                    # Record exit
                    self._record_event(node.node_id, "exit", {
                        "result": str(result),
                        "shared_state": self._serialize_state(shared)
                    })
                    
                    return result
                    
                except Exception as e:
                    # Record error
                    self._record_event(node.node_id, "error", {
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                    raise
            
            def traced_on_error(shared, error):
                self._record_event(node.node_id, "error_handled", {
                    "error": str(error),
                    "suppressed": False
                })
                result = original_on_error(shared, error)
                if result:
                    self.events[-1].data["suppressed"] = True
                return result
            
            # Apply patches
            node._run = traced_run
            node.on_error = traced_on_error
            
            # Recursively patch successors
            for successor in node.successors.values():
                patch_node(successor)
        
        # Start patching from the start node
        if self.graph.start_node:
            patch_node(self.graph.start_node)
    
    def _record_event(self, node_id: str, event_type: str, data: Dict[str, Any]):
        """Record an execution event."""
        if self.start_time is None:
            self.start_time = time.time()
        
        event = ExecutionEvent(
            node_id=node_id,
            event_type=event_type,
            timestamp=time.time() - self.start_time,
            data=data
        )
        self.events.append(event)
        
        # Store state snapshot
        if "shared_state" in data:
            snapshot_key = f"{node_id}_{event_type}_{len(self.events)}"
            self.state_snapshots[snapshot_key] = data["shared_state"]
    
    def _serialize_state(self, state: Any) -> Any:
        """Serialize state for storage (handle non-JSON types)."""
        if isinstance(state, dict):
            return {k: self._serialize_state(v) for k, v in state.items()}
        elif isinstance(state, list):
            return [self._serialize_state(v) for v in state]
        elif isinstance(state, (str, int, float, bool, type(None))):
            return state
        else:
            return str(state)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution trace."""
        if not self.events:
            return {"status": "no_execution"}
        
        # Calculate node statistics
        node_stats = {}
        for event in self.events:
            node_id = event.node_id
            if node_id not in node_stats:
                node_stats[node_id] = {
                    "count": 0,
                    "total_time": 0,
                    "errors": 0
                }
            
            if event.event_type == "enter":
                # Find matching exit event
                exit_event = next(
                    (e for e in self.events 
                     if e.node_id == node_id and 
                     e.event_type == "exit" and 
                     e.timestamp > event.timestamp),
                    None
                )
                if exit_event:
                    duration = exit_event.timestamp - event.timestamp
                    node_stats[node_id]["total_time"] += duration
                    node_stats[node_id]["count"] += 1
            elif event.event_type == "error":
                node_stats[node_id]["errors"] += 1
        
        total_time = self.events[-1].timestamp if self.events else 0
        
        return {
            "total_execution_time": total_time,
            "total_events": len(self.events),
            "nodes_executed": len(node_stats),
            "node_statistics": node_stats,
            "execution_path": [e.node_id for e in self.events if e.event_type == "enter"]
        }
    
    def generate_timeline_html(self) -> str:
        """Generate HTML timeline visualization."""
        events_data = [e.to_dict() for e in self.events]
        
        html_template = '''<!DOCTYPE html>
<html>
<head>
    <title>KayGraph Execution Timeline</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .summary {
            margin-bottom: 20px;
            padding: 15px;
            background: #e8f4f8;
            border-radius: 5px;
        }
        #timeline {
            height: 400px;
        }
        #events-list {
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
        }
        .event {
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #ccc;
            background: #f9f9f9;
        }
        .event.enter { border-color: #4CAF50; }
        .event.exit { border-color: #2196F3; }
        .event.error { border-color: #f44336; }
        .event-header {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .event-data {
            font-size: 12px;
            color: #666;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>KayGraph Execution Timeline</h1>
        
        <div class="summary" id="summary"></div>
        
        <h2>Execution Timeline</h2>
        <div id="timeline"></div>
        
        <h2>Event Details</h2>
        <div id="events-list"></div>
    </div>
    
    <script>
        const events = ''' + json.dumps(events_data) + ''';
        
        // Process events for timeline
        const timelineData = [];
        const nodeColors = {};
        const colorPalette = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#00BCD4'];
        let colorIndex = 0;
        
        // Group events by node
        const nodeEvents = {};
        events.forEach(event => {
            if (!nodeEvents[event.node_id]) {
                nodeEvents[event.node_id] = [];
            }
            nodeEvents[event.node_id].push(event);
            
            // Assign color
            if (!nodeColors[event.node_id]) {
                nodeColors[event.node_id] = colorPalette[colorIndex % colorPalette.length];
                colorIndex++;
            }
        });
        
        // Create timeline bars
        Object.entries(nodeEvents).forEach(([nodeId, nodeEventList]) => {
            nodeEventList.forEach((event, idx) => {
                if (event.event_type === 'enter') {
                    // Find corresponding exit
                    const exitEvent = nodeEventList.find(
                        e => e.event_type === 'exit' && e.timestamp > event.timestamp
                    );
                    
                    if (exitEvent) {
                        timelineData.push({
                            x: [event.timestamp, exitEvent.timestamp],
                            y: [nodeId, nodeId],
                            mode: 'lines',
                            line: {
                                color: nodeColors[nodeId],
                                width: 20
                            },
                            name: nodeId,
                            showlegend: idx === 0,
                            hovertemplate: `${nodeId}<br>Duration: %{x}<br><extra></extra>`
                        });
                    }
                }
            });
        });
        
        // Create timeline plot
        const layout = {
            title: 'Node Execution Timeline',
            xaxis: {
                title: 'Time (seconds)',
                showgrid: true
            },
            yaxis: {
                title: 'Nodes',
                showgrid: true
            },
            hovermode: 'closest'
        };
        
        Plotly.newPlot('timeline', timelineData, layout);
        
        // Display events list
        const eventsList = document.getElementById('events-list');
        events.forEach(event => {
            const eventDiv = document.createElement('div');
            eventDiv.className = `event ${event.event_type}`;
            
            const timestamp = event.timestamp.toFixed(3);
            
            eventDiv.innerHTML = `
                <div class="event-header">
                    [${timestamp}s] ${event.node_id} - ${event.event_type}
                </div>
                <div class="event-data">${JSON.stringify(event.data, null, 2)}</div>
            `;
            
            eventsList.appendChild(eventDiv);
        });
        
        // Calculate and display summary
        const summary = calculateSummary(events);
        document.getElementById('summary').innerHTML = `
            <h3>Execution Summary</h3>
            <p><strong>Total Time:</strong> ${summary.totalTime.toFixed(3)}s</p>
            <p><strong>Nodes Executed:</strong> ${summary.nodesExecuted}</p>
            <p><strong>Total Events:</strong> ${events.length}</p>
            <p><strong>Errors:</strong> ${summary.errors}</p>
            <p><strong>Execution Path:</strong> ${summary.path.join(' → ')}</p>
        `;
        
        function calculateSummary(events) {
            const nodeSet = new Set();
            const path = [];
            let errors = 0;
            let totalTime = 0;
            
            events.forEach(event => {
                nodeSet.add(event.node_id);
                if (event.event_type === 'enter') {
                    path.push(event.node_id);
                }
                if (event.event_type === 'error') {
                    errors++;
                }
                totalTime = Math.max(totalTime, event.timestamp);
            });
            
            return {
                totalTime,
                nodesExecuted: nodeSet.size,
                errors,
                path
            };
        }
    </script>
</body>
</html>'''
        
        return html_template
    
    def save_trace(self, filename: str):
        """Save execution trace to file."""
        trace_data = {
            "start_time": datetime.fromtimestamp(
                self.start_time or time.time()
            ).isoformat(),
            "events": [e.to_dict() for e in self.events],
            "summary": self.get_execution_summary(),
            "state_snapshots": self.state_snapshots
        }
        
        output_path = Path(filename)
        
        if output_path.suffix == ".json":
            # Save as JSON
            with open(output_path, 'w') as f:
                json.dump(trace_data, f, indent=2)
        elif output_path.suffix == ".html":
            # Save as HTML timeline
            output_path.write_text(self.generate_timeline_html())
        else:
            # Default to JSON
            output_path = output_path.with_suffix(".json")
            with open(output_path, 'w') as f:
                json.dump(trace_data, f, indent=2)
        
        logger.info(f"Saved execution trace to {output_path}")
    
    def print_summary(self):
        """Print execution summary to console."""
        summary = self.get_execution_summary()
        
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"Total Time: {summary['total_execution_time']:.3f}s")
        print(f"Nodes Executed: {summary['nodes_executed']}")
        print(f"Total Events: {summary['total_events']}")
        print(f"\nExecution Path:")
        for i, node in enumerate(summary['execution_path']):
            print(f"  {i+1}. {node}")
        
        print(f"\nNode Statistics:")
        for node_id, stats in summary['node_statistics'].items():
            print(f"  {node_id}:")
            print(f"    Executions: {stats['count']}")
            print(f"    Total Time: {stats['total_time']:.3f}s")
            if stats['count'] > 0:
                print(f"    Avg Time: {stats['total_time']/stats['count']:.3f}s")
            if stats['errors'] > 0:
                print(f"    Errors: {stats['errors']}")


def trace_example():
    """Run example with tracing."""
    from kaygraph import Node, Graph
    
    # Create example nodes
    class SlowNode(Node):
        def exec(self, prep_res):
            time.sleep(0.5)  # Simulate work
            return "processed"
        
        def post(self, shared, prep_res, exec_res):
            shared["result"] = exec_res
            return None
    
    class FastNode(Node):
        def exec(self, prep_res):
            time.sleep(0.1)
            return "done"
    
    # Build and trace
    slow = SlowNode(node_id="SlowProcessor")
    fast = FastNode(node_id="FastProcessor")
    
    graph = Graph(start=slow)
    slow >> fast
    
    # Trace execution
    tracer = ExecutionTracer(graph)
    shared = {"input": "test_data"}
    
    print("Executing traced workflow...")
    graph.run(shared)
    
    # Show results
    tracer.print_summary()
    tracer.save_trace("execution_trace.json")
    tracer.save_trace("execution_timeline.html")
    
    print("\nTrace files saved:")
    print("  - execution_trace.json")
    print("  - execution_timeline.html")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Trace KayGraph execution")
    parser.add_argument("--example", action="store_true",
                       help="Run example tracing")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    if args.example:
        trace_example()
    else:
        print("Note: Currently only --example mode is supported.")
        print("Integration with existing workflows coming soon!")