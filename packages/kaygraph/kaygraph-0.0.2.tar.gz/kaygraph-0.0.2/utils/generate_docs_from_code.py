#!/usr/bin/env python3
"""
KayGraph Documentation Generator - Generate docs from code

Usage:
    python generate_docs_from_code.py <directory> [--output-dir PATH] [--format md|mermaid|all]
    
Examples:
    python generate_docs_from_code.py ./my_project
    python generate_docs_from_code.py ./my_project --format mermaid
    python generate_docs_from_code.py ./my_project --output-dir ./docs
"""

import ast
import os
import sys
from pathlib import Path
import argparse
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime


class KayGraphAnalyzer(ast.NodeVisitor):
    """Analyze KayGraph code structure"""
    
    def __init__(self):
        self.nodes = {}  # node_name: {class_name, description, methods, connections}
        self.graphs = {}  # graph_name: {nodes, connections}
        self.imports = {}
        self.current_class = None
        self.connections = []  # List of (from_node, action, to_node)
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module == "kaygraph":
            for alias in node.names:
                name = alias.asname or alias.name
                self.imports[name] = f"kaygraph.{alias.name}"
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Extract Node class information"""
        self.current_class = node.name
        
        # Check if it's a Node class
        for base in node.bases:
            base_name = self._get_name(base)
            if base_name and "Node" in base_name:
                # Extract node information
                docstring = ast.get_docstring(node) or "No description"
                methods = self._extract_methods(node)
                
                self.nodes[node.name] = {
                    "class_name": node.name,
                    "base_class": base_name,
                    "description": docstring.split('\n')[0],
                    "full_docstring": docstring,
                    "methods": methods,
                    "line_number": node.lineno
                }
                break
        
        self.generic_visit(node)
        self.current_class = None
    
    def visit_BinOp(self, node):
        """Extract >> connections"""
        if isinstance(node.op, ast.RShift):  # >>
            left = self._get_name(node.left)
            right = node.right
            
            if isinstance(right, ast.Tuple) and len(right.elts) == 2:
                # Named action: node1 >> ("action", node2)
                action = self._get_string_value(right.elts[0])
                to_node = self._get_name(right.elts[1])
                if left and action and to_node:
                    self.connections.append((left, action, to_node))
            else:
                # Default action: node1 >> node2
                to_node = self._get_name(right)
                if left and to_node:
                    self.connections.append((left, "default", to_node))
        
        self.generic_visit(node)
    
    def _get_name(self, node):
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return None
    
    def _get_string_value(self, node):
        """Extract string value from AST node"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):  # Python < 3.8
            return node.s
        return None
    
    def _extract_methods(self, class_node):
        """Extract method information from class"""
        methods = {}
        
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name in ["prep", "exec", "post"]:
                    docstring = ast.get_docstring(item) or ""
                    params = [arg.arg for arg in item.args.args[1:]]  # Skip self
                    
                    methods[item.name] = {
                        "params": params,
                        "docstring": docstring,
                        "line_number": item.lineno
                    }
        
        return methods


def analyze_file(filepath: Path) -> Dict[str, Any]:
    """Analyze a single Python file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        analyzer = KayGraphAnalyzer()
        analyzer.visit(tree)
        
        return {
            "nodes": analyzer.nodes,
            "connections": analyzer.connections,
            "imports": analyzer.imports
        }
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return {"nodes": {}, "connections": [], "imports": {}}


def analyze_project(directory: Path) -> Dict[str, Any]:
    """Analyze entire project directory"""
    project_data = {
        "nodes": {},
        "connections": [],
        "graphs": {},
        "files": {}
    }
    
    py_files = list(directory.rglob("*.py"))
    
    for filepath in py_files:
        if "__pycache__" in str(filepath):
            continue
        
        file_data = analyze_file(filepath)
        relative_path = filepath.relative_to(directory)
        
        # Merge data
        project_data["nodes"].update(file_data["nodes"])
        project_data["connections"].extend(file_data["connections"])
        project_data["files"][str(relative_path)] = file_data


    return project_data


def generate_markdown_docs(project_data: Dict[str, Any], output_dir: Path):
    """Generate Markdown documentation"""
    
    # Create main documentation file
    main_doc = output_dir / "kaygraph_docs.md"
    
    with open(main_doc, 'w') as f:
        f.write("# KayGraph Project Documentation\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Table of Contents
        f.write("## Table of Contents\n\n")
        f.write("1. [Nodes](#nodes)\n")
        f.write("2. [Graph Structure](#graph-structure)\n")
        f.write("3. [File Structure](#file-structure)\n\n")
        
        # Nodes section
        f.write("## Nodes\n\n")
        
        # Group nodes by base class
        nodes_by_type = {}
        for node_name, node_info in project_data["nodes"].items():
            base = node_info.get("base_class", "Node")
            if base not in nodes_by_type:
                nodes_by_type[base] = []
            nodes_by_type[base].append((node_name, node_info))
        
        for base_class, nodes in sorted(nodes_by_type.items()):
            f.write(f"### {base_class} Implementations\n\n")
            
            for node_name, node_info in sorted(nodes):
                f.write(f"#### {node_name}\n\n")
                f.write(f"**Description**: {node_info['description']}\n\n")
                
                # Methods
                if node_info.get("methods"):
                    f.write("**Methods**:\n\n")
                    
                    for method_name in ["prep", "exec", "post"]:
                        if method_name in node_info["methods"]:
                            method = node_info["methods"][method_name]
                            params = ", ".join(method["params"])
                            f.write(f"- `{method_name}({params})`")
                            if method["docstring"]:
                                f.write(f": {method['docstring'].split(chr(10))[0]}")
                            f.write("\n")
                
                f.write("\n")
        
        # Graph Structure section
        f.write("## Graph Structure\n\n")
        
        if project_data["connections"]:
            f.write("### Connections\n\n")
            f.write("| From Node | Action | To Node |\n")
            f.write("|-----------|--------|----------|\n")
            
            for from_node, action, to_node in project_data["connections"]:
                f.write(f"| {from_node} | {action} | {to_node} |\n")
            
            f.write("\n")
        
        # File Structure section
        f.write("## File Structure\n\n")
        
        for filepath, file_data in sorted(project_data["files"].items()):
            if file_data["nodes"]:
                f.write(f"### {filepath}\n\n")
                f.write("**Nodes**:\n")
                for node_name in sorted(file_data["nodes"].keys()):
                    f.write(f"- {node_name}\n")
                f.write("\n")
    
    print(f"✓ Generated Markdown documentation: {main_doc}")


def generate_mermaid_diagram(project_data: Dict[str, Any], output_dir: Path):
    """Generate Mermaid diagram of graph structure"""
    
    mermaid_file = output_dir / "graph_diagram.mmd"
    
    with open(mermaid_file, 'w') as f:
        f.write("```mermaid\ngraph TD\n")
        
        # Define node styles based on type
        node_styles = {}
        style_index = 0
        
        # Add nodes with descriptions
        for node_name, node_info in project_data["nodes"].items():
            base_class = node_info.get("base_class", "Node")
            
            # Create style for base class if not exists
            if base_class not in node_styles:
                node_styles[base_class] = f"style{style_index}"
                style_index += 1
            
            # Truncate description for diagram
            desc = node_info['description'][:30]
            if len(node_info['description']) > 30:
                desc += "..."
            
            f.write(f'    {node_name}["{node_name}<br/><i>{desc}</i>"]\n')
        
        f.write("\n")
        
        # Add connections
        for from_node, action, to_node in project_data["connections"]:
            if from_node in project_data["nodes"] and to_node in project_data["nodes"]:
                if action == "default":
                    f.write(f"    {from_node} --> {to_node}\n")
                else:
                    f.write(f'    {from_node} -->|"{action}"| {to_node}\n')
        
        f.write("\n")
        
        # Apply styles
        style_colors = {
            "Node": "#E3F2FD",
            "AsyncNode": "#FFF3E0",
            "BatchNode": "#E8F5E9",
            "ValidatedNode": "#FCE4EC"
        }
        
        for base_class, style_name in node_styles.items():
            color = style_colors.get(base_class, "#F5F5F5")
            nodes_of_type = [n for n, info in project_data["nodes"].items() 
                           if info.get("base_class") == base_class]
            
            if nodes_of_type:
                f.write(f"\n    %% {base_class} styling\n")
                for node in nodes_of_type:
                    f.write(f"    style {node} fill:{color},stroke:#333,stroke-width:2px\n")
        
        f.write("```\n")
    
    print(f"✓ Generated Mermaid diagram: {mermaid_file}")
    
    # Also create an HTML file for easy viewing
    html_file = output_dir / "graph_diagram.html"
    with open(html_file, 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>KayGraph Project Diagram</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true });
    </script>
</head>
<body>
    <h1>KayGraph Project Structure</h1>
    <div class="mermaid">
""")
        
        # Add the mermaid content without the ```mermaid wrapper
        with open(mermaid_file, 'r') as mmd:
            content = mmd.read()
            content = content.replace("```mermaid\n", "").replace("\n```", "")
            f.write(content)
        
        f.write("""
    </div>
</body>
</html>""")
    
    print(f"✓ Generated HTML diagram viewer: {html_file}")


def generate_design_doc(project_data: Dict[str, Any], output_dir: Path):
    """Generate a design.md file in KayGraph style"""
    
    design_file = output_dir / "design.md"
    
    with open(design_file, 'w') as f:
        f.write("# Design Document\n\n")
        f.write(f"Generated from code on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## High-Level Requirements\n\n")
        f.write("*[Inferred from code structure]*\n\n")
        
        # Infer requirements from nodes
        node_types = set()
        for node_info in project_data["nodes"].values():
            base = node_info.get("base_class", "Node")
            node_types.add(base)
        
        if "AsyncNode" in node_types:
            f.write("- Asynchronous processing capabilities\n")
        if "BatchNode" in node_types:
            f.write("- Batch processing of multiple items\n")
        if "ValidatedNode" in node_types:
            f.write("- Input/output validation\n")
        
        f.write("\n## Graph Structure\n\n")
        f.write("```mermaid\ngraph TD\n")
        
        # Simplified mermaid for design doc
        for node_name in project_data["nodes"]:
            f.write(f"    {node_name}\n")
        
        for from_node, action, to_node in project_data["connections"]:
            if from_node in project_data["nodes"] and to_node in project_data["nodes"]:
                if action == "default":
                    f.write(f"    {from_node} --> {to_node}\n")
                else:
                    f.write(f'    {from_node} -->|"{action}"| {to_node}\n')
        
        f.write("```\n\n")
        
        f.write("## Node Descriptions\n\n")
        
        for node_name, node_info in sorted(project_data["nodes"].items()):
            f.write(f"- **{node_name}**: {node_info['description']}\n")
        
        f.write("\n## Utility Functions\n\n")
        f.write("*[Analyze utils/ directory for detailed list]*\n\n")
        
        # Check for common utility patterns
        has_llm = any("llm" in str(f).lower() for f in project_data["files"])
        has_embed = any("embed" in str(f).lower() for f in project_data["files"])
        has_search = any("search" in str(f).lower() for f in project_data["files"])
        
        if has_llm:
            f.write("- LLM integration (call_llm.py)\n")
        if has_embed:
            f.write("- Embedding generation\n")
        if has_search:
            f.write("- Search functionality\n")
    
    print(f"✓ Generated design document: {design_file}")


def generate_json_spec(project_data: Dict[str, Any], output_dir: Path):
    """Generate JSON specification of the project"""
    
    json_file = output_dir / "kaygraph_spec.json"
    
    # Clean data for JSON serialization
    clean_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_nodes": len(project_data["nodes"]),
            "total_connections": len(project_data["connections"]),
            "total_files": len(project_data["files"])
        },
        "nodes": {},
        "connections": project_data["connections"],
        "files": {}
    }
    
    # Clean node data
    for node_name, node_info in project_data["nodes"].items():
        clean_data["nodes"][node_name] = {
            "class_name": node_info["class_name"],
            "base_class": node_info.get("base_class", "Node"),
            "description": node_info["description"],
            "methods": {
                method_name: {
                    "params": method_data["params"],
                    "has_docstring": bool(method_data["docstring"])
                }
                for method_name, method_data in node_info.get("methods", {}).items()
            }
        }
    
    # Clean file data
    for filepath, file_data in project_data["files"].items():
        if file_data["nodes"]:
            clean_data["files"][filepath] = {
                "nodes": list(file_data["nodes"].keys())
            }
    
    with open(json_file, 'w') as f:
        json.dump(clean_data, f, indent=2)
    
    print(f"✓ Generated JSON specification: {json_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation from KayGraph code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output formats:
  md       - Markdown documentation with node descriptions
  mermaid  - Mermaid diagram of graph structure  
  design   - design.md file in KayGraph format
  json     - JSON specification of project structure
  all      - Generate all formats (default)

Examples:
  python generate_docs_from_code.py ./my_project
  python generate_docs_from_code.py ./my_project --format mermaid
  python generate_docs_from_code.py ./my_project --output-dir ./docs --format all
"""
    )
    
    parser.add_argument("directory",
                       help="Project directory to analyze")
    parser.add_argument("--output-dir", "-o",
                       default="./generated_docs",
                       help="Output directory for documentation (default: ./generated_docs)")
    parser.add_argument("--format", "-f",
                       choices=["md", "mermaid", "design", "json", "all"],
                       default="all",
                       help="Documentation format to generate (default: all)")
    
    args = parser.parse_args()
    
    project_dir = Path(args.directory)
    output_dir = Path(args.output_dir)
    
    if not project_dir.exists():
        print(f"Error: Directory '{project_dir}' does not exist")
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Analyzing KayGraph project: {project_dir}")
    
    # Analyze project
    project_data = analyze_project(project_dir)
    
    if not project_data["nodes"]:
        print("⚠️  No KayGraph nodes found in the project")
        sys.exit(1)
    
    print(f"\n📊 Found {len(project_data['nodes'])} nodes and {len(project_data['connections'])} connections")
    
    # Generate documentation based on format
    if args.format in ["md", "all"]:
        generate_markdown_docs(project_data, output_dir)
    
    if args.format in ["mermaid", "all"]:
        generate_mermaid_diagram(project_data, output_dir)
    
    if args.format in ["design", "all"]:
        generate_design_doc(project_data, output_dir)
    
    if args.format in ["json", "all"]:
        generate_json_spec(project_data, output_dir)
    
    print(f"\n✅ Documentation generated in: {output_dir}")
    print("\n📝 Next steps:")
    print("1. Review generated documentation")
    print("2. Add missing descriptions to node docstrings")
    print("3. Update design.md with actual requirements")


if __name__ == "__main__":
    main()