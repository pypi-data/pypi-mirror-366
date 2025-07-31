#!/usr/bin/env python3
"""
KayGraph visualization tool.
Generates visual representations of graph structures in multiple formats.
"""

import json
import argparse
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import logging

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, Node, BaseNode

logger = logging.getLogger(__name__)


class GraphVisualizer:
    """Visualize KayGraph structures in various formats."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.nodes_visited: Set[str] = set()
        self.edges: List[Tuple[str, str, str]] = []
        self._analyze_graph()
    
    def _analyze_graph(self):
        """Analyze graph structure starting from the start node."""
        if not self.graph.start_node:
            raise ValueError("Graph has no start node")
        
        self._traverse_node(self.graph.start_node)
    
    def _traverse_node(self, node: BaseNode, visited: Optional[Set[str]] = None):
        """Recursively traverse the graph to collect nodes and edges."""
        if visited is None:
            visited = set()
        
        node_id = node.node_id
        
        if node_id in visited:
            return
        
        visited.add(node_id)
        self.nodes_visited.add(node_id)
        
        # Traverse successors
        for action, successor in node.successors.items():
            successor_id = successor.node_id
            self.edges.append((node_id, successor_id, action))
            self._traverse_node(successor, visited)
    
    def to_mermaid(self) -> str:
        """Generate Mermaid diagram syntax."""
        lines = ["graph TD"]
        
        # Add nodes with better labels
        node_labels = {}
        for node_id in self.nodes_visited:
            # Extract class name for better display
            clean_label = node_id.split('_')[0] if '_' in node_id else node_id
            node_labels[node_id] = clean_label
            lines.append(f'    {self._sanitize_id(node_id)}["{clean_label}"]')
        
        lines.append("")  # Empty line for readability
        
        # Add edges with labels
        for from_node, to_node, action in self.edges:
            from_id = self._sanitize_id(from_node)
            to_id = self._sanitize_id(to_node)
            
            if action == "default":
                lines.append(f'    {from_id} --> {to_id}')
            else:
                lines.append(f'    {from_id} -->|{action}| {to_id}')
        
        # Add styling
        lines.extend([
            "",
            "    %% Styling",
            "    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px;",
            "    classDef start fill:#90EE90,stroke:#333,stroke-width:3px;",
            "    classDef end fill:#FFB6C1,stroke:#333,stroke-width:3px;",
            f"    class {self._sanitize_id(self.graph.start_node.node_id)} start;"
        ])
        
        return "\n".join(lines)
    
    def to_dot(self) -> str:
        """Generate Graphviz DOT format."""
        lines = ["digraph KayGraph {"]
        lines.extend([
            '    rankdir=TB;',
            '    node [shape=box, style="rounded,filled", fillcolor=lightblue];',
            '    edge [fontsize=10];',
            ''
        ])
        
        # Add nodes
        for node_id in self.nodes_visited:
            label = node_id.split('_')[0] if '_' in node_id else node_id
            
            # Special styling for start node
            if node_id == self.graph.start_node.node_id:
                lines.append(f'    "{node_id}" [label="{label}", fillcolor=lightgreen, penwidth=3];')
            else:
                lines.append(f'    "{node_id}" [label="{label}"];')
        
        lines.append("")
        
        # Add edges
        for from_node, to_node, action in self.edges:
            if action == "default":
                lines.append(f'    "{from_node}" -> "{to_node}";')
            else:
                lines.append(f'    "{from_node}" -> "{to_node}" [label="{action}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    def to_ascii(self) -> str:
        """Generate ASCII art representation."""
        # Simple ASCII representation for terminal display
        lines = ["KayGraph Structure:", "=" * 50, ""]
        
        # Build adjacency info
        adjacency = {}
        for from_node, to_node, action in self.edges:
            if from_node not in adjacency:
                adjacency[from_node] = []
            adjacency[from_node].append((to_node, action))
        
        # Start from the root and display
        def print_node(node_id, prefix="", visited=None):
            if visited is None:
                visited = set()
            
            if node_id in visited:
                lines.append(f"{prefix}[↻ {node_id}]  (cycle)")
                return
            
            visited.add(node_id)
            label = node_id.split('_')[0] if '_' in node_id else node_id
            
            if node_id == self.graph.start_node.node_id:
                lines.append(f"{prefix}[▶ {label}]  (start)")
            else:
                lines.append(f"{prefix}[□ {label}]")
            
            if node_id in adjacency:
                for i, (next_node, action) in enumerate(adjacency[node_id]):
                    is_last = i == len(adjacency[node_id]) - 1
                    
                    if action != "default":
                        lines.append(f"{prefix}  ├─({action})─>")
                    
                    new_prefix = prefix + ("  └──" if is_last else "  ├──")
                    print_node(next_node, new_prefix, visited.copy())
        
        print_node(self.graph.start_node.node_id)
        
        return "\n".join(lines)
    
    def to_html_interactive(self) -> str:
        """Generate interactive HTML visualization using D3.js."""
        # Prepare graph data for D3
        nodes = [{"id": node_id, "label": node_id.split('_')[0] if '_' in node_id else node_id}
                 for node_id in self.nodes_visited]
        
        links = [{"source": from_node, "target": to_node, "label": action}
                 for from_node, to_node, action in self.edges]
        
        graph_data = {"nodes": nodes, "links": links, "start": self.graph.start_node.node_id}
        
        html_template = '''<!DOCTYPE html>
<html>
<head>
    <title>KayGraph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        #graph {
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 5px;
        }
        .node {
            cursor: pointer;
        }
        .node circle {
            fill: #69b3a2;
            stroke: #333;
            stroke-width: 2px;
        }
        .node.start circle {
            fill: #90EE90;
            stroke-width: 3px;
        }
        .node text {
            font: 12px sans-serif;
            text-anchor: middle;
        }
        .link {
            fill: none;
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 2px;
        }
        .link-label {
            font: 10px sans-serif;
            fill: #666;
        }
        .controls {
            margin-bottom: 10px;
        }
        button {
            margin-right: 10px;
            padding: 5px 15px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>KayGraph Visualization</h1>
    <div class="controls">
        <button onclick="resetZoom()">Reset Zoom</button>
        <button onclick="fitToScreen()">Fit to Screen</button>
    </div>
    <svg id="graph"></svg>
    
    <script>
        const graphData = ''' + json.dumps(graph_data) + ''';
        
        const width = document.getElementById('graph').clientWidth;
        const height = 600;
        
        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);
        
        const g = svg.append("g");
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });
        
        svg.call(zoom);
        
        // Create arrow markers
        svg.append("defs").selectAll("marker")
            .data(["end"])
            .enter().append("marker")
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 30)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5");
        
        // Initialize force simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        // Create links
        const link = g.append("g")
            .selectAll("line")
            .data(graphData.links)
            .enter().append("line")
            .attr("class", "link")
            .attr("marker-end", "url(#end)");
        
        // Create link labels
        const linkLabel = g.append("g")
            .selectAll("text")
            .data(graphData.links.filter(d => d.label !== "default"))
            .enter().append("text")
            .attr("class", "link-label")
            .text(d => d.label);
        
        // Create nodes
        const node = g.append("g")
            .selectAll(".node")
            .data(graphData.nodes)
            .enter().append("g")
            .attr("class", d => d.id === graphData.start ? "node start" : "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        node.append("circle")
            .attr("r", 20);
        
        node.append("text")
            .attr("dy", 5)
            .text(d => d.label);
        
        // Add titles for hover
        node.append("title")
            .text(d => `Node: ${d.id}`);
        
        // Update positions on tick
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            linkLabel
                .attr("x", d => (d.source.x + d.target.x) / 2)
                .attr("y", d => (d.source.y + d.target.y) / 2);
            
            node
                .attr("transform", d => `translate(${d.x},${d.y})`);
        });
        
        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Control functions
        function resetZoom() {
            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity);
        }
        
        function fitToScreen() {
            const bounds = g.node().getBBox();
            const fullWidth = width;
            const fullHeight = height;
            const widthScale = fullWidth / bounds.width;
            const heightScale = fullHeight / bounds.height;
            const scale = 0.9 * Math.min(widthScale, heightScale);
            const translate = [fullWidth / 2 - scale * (bounds.x + bounds.width / 2),
                               fullHeight / 2 - scale * (bounds.y + bounds.height / 2)];
            
            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
        }
        
        // Fit to screen on load
        setTimeout(fitToScreen, 500);
    </script>
</body>
</html>'''
        
        return html_template
    
    def _sanitize_id(self, node_id: str) -> str:
        """Sanitize node ID for use in diagram formats."""
        return node_id.replace(" ", "_").replace("-", "_")
    
    def save(self, filename: str, format: str = "mermaid"):
        """Save visualization to file."""
        output_map = {
            "mermaid": (self.to_mermaid(), ".md"),
            "dot": (self.to_dot(), ".dot"),
            "ascii": (self.to_ascii(), ".txt"),
            "html": (self.to_html_interactive(), ".html")
        }
        
        if format not in output_map:
            raise ValueError(f"Unknown format: {format}")
        
        content, ext = output_map[format]
        
        # Ensure filename has correct extension
        output_path = Path(filename)
        if not output_path.suffix:
            output_path = output_path.with_suffix(ext)
        
        output_path.write_text(content)
        logger.info(f"Saved {format} visualization to {output_path}")


def visualize_example_graph():
    """Create and visualize an example graph."""
    from kaygraph import Node, Graph
    
    # Create example nodes
    class StartNode(Node):
        def __init__(self):
            super().__init__(node_id="Start")
        def post(self, shared, prep_res, exec_res):
            return "process"
    
    class ProcessNode(Node):
        def __init__(self):
            super().__init__(node_id="Process")
        def post(self, shared, prep_res, exec_res):
            return "check"
    
    class CheckNode(Node):
        def __init__(self):
            super().__init__(node_id="Check")
        def post(self, shared, prep_res, exec_res):
            if shared.get("status") == "success":
                return "success"
            else:
                return "retry"
    
    class SuccessNode(Node):
        def __init__(self):
            super().__init__(node_id="Success")
    
    class RetryNode(Node):
        def __init__(self):
            super().__init__(node_id="Retry")
        def post(self, shared, prep_res, exec_res):
            return "reprocess"
    
    # Build graph
    start = StartNode()
    process = ProcessNode()
    check = CheckNode()
    success = SuccessNode()
    retry = RetryNode()
    
    graph = Graph(start=start)
    start - "process" >> process
    process - "check" >> check
    check - "success" >> success
    check - "retry" >> retry
    retry - "reprocess" >> process  # Create a loop
    
    return graph


def main():
    """Main entry point for visualization tool."""
    parser = argparse.ArgumentParser(description="Visualize KayGraph structures")
    parser.add_argument("--example", action="store_true",
                       help="Visualize built-in example graph")
    parser.add_argument("--format", choices=["mermaid", "dot", "ascii", "html", "all"],
                       default="mermaid", help="Output format")
    parser.add_argument("--output", default="graph_visualization",
                       help="Output filename (without extension)")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    # Create graph
    if args.example:
        graph = visualize_example_graph()
    else:
        print("Note: Currently only --example mode is supported.")
        print("Integration with existing graphs coming soon!")
        return
    
    # Visualize
    viz = GraphVisualizer(graph)
    
    if args.format == "all":
        # Generate all formats
        for fmt in ["mermaid", "dot", "ascii", "html"]:
            viz.save(args.output, fmt)
            print(f"Generated {fmt} visualization")
    else:
        # Generate specific format
        viz.save(args.output, args.format)
        
        # Print ASCII to console for immediate feedback
        if args.format == "ascii":
            print(viz.to_ascii())
        elif args.format == "mermaid":
            print("\nMermaid diagram saved. You can visualize it at:")
            print("https://mermaid.live/")
            print("\nOr include in markdown:")
            print("```mermaid")
            print(viz.to_mermaid())
            print("```")


if __name__ == "__main__":
    main()