#!/usr/bin/env python3
"""
Main example for KayGraph MCP integration.
Demonstrates tool discovery, selection, and execution.
"""

import logging
import asyncio
from pathlib import Path
import argparse
import json

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import AsyncGraph
from mcp_nodes import (
    MCPClientNode, ToolDiscoveryNode, ToolSelectionNode,
    ToolExecutionNode, ResultFormatterNode
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def build_mcp_workflow():
    """Build the MCP workflow graph."""
    # Create nodes
    mcp_client = MCPClientNode("mock://localhost:3333")
    discover_node = ToolDiscoveryNode()
    select_node = ToolSelectionNode()
    execute_node = ToolExecutionNode()
    format_node = ResultFormatterNode()
    
    # Build graph
    graph = AsyncGraph(start=mcp_client)
    
    # Connect nodes
    mcp_client >> discover_node >> select_node
    
    # Handle different selection outcomes
    select_node - "single_tool" >> execute_node
    select_node - "multi_tool" >> execute_node
    select_node - "no_tools" >> format_node
    
    # Execute always leads to format
    execute_node >> format_node
    
    return graph


async def interactive_mode():
    """Run MCP in interactive mode."""
    print("\n🤖 KayGraph MCP Interactive Mode")
    print("=" * 50)
    print("Available commands:")
    print("  - 'quit' or 'exit' to stop")
    print("  - 'tools' to list available tools")
    print("  - Any other text to process with MCP")
    print("=" * 50)
    
    # Build workflow once
    graph = await build_mcp_workflow()
    
    # Store discovered tools
    tool_cache = {}
    
    while True:
        try:
            query = input("\n📝 Enter query: ").strip()
            
            if query.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            # Prepare shared context
            shared = {"user_query": query}
            
            # Special command to show tools
            if query.lower() == 'tools':
                if not tool_cache:
                    # Discover tools first
                    shared["user_query"] = "discover"
                    await graph.run_async(shared)
                    tool_cache = shared.get("tool_index", {})
                
                print("\n📋 Available tools:")
                for tool_id, tool in tool_cache.items():
                    print(f"  - {tool_id}: {tool['description']}")
                continue
            
            # Run the workflow
            print("\n🔄 Processing...")
            await graph.run_async(shared)
            
            # Display results
            if "final_response" in shared:
                print("\n📊 Results:")
                print(shared["final_response"])
            
            # Update tool cache if discovered
            if "tool_index" in shared:
                tool_cache = shared["tool_index"]
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n❌ Error: {e}")


async def batch_mode(queries):
    """Run MCP in batch mode."""
    print("\n🤖 KayGraph MCP Batch Mode")
    print("=" * 50)
    
    # Build workflow
    graph = await build_mcp_workflow()
    
    # Process each query
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Processing: {query}")
        
        shared = {"user_query": query}
        await graph.run_async(shared)
        
        result = {
            "query": query,
            "response": shared.get("final_response", "No response"),
            "tools_used": shared.get("selected_tools", [])
        }
        results.append(result)
        
        print(f"✅ Complete. Tools used: {', '.join(result['tools_used']) or 'None'}")
    
    return results


async def demo_mode():
    """Run demonstration of MCP capabilities."""
    print("\n🎭 KayGraph MCP Demo Mode")
    print("=" * 50)
    
    demo_queries = [
        "Calculate the factorial of 7",
        "Search for Python async programming tutorials",
        "Fetch data from the user API endpoint",
        "What's the weather like?",  # No specific tool
        "Calculate 15 * 23 + 47 and search for prime numbers"  # Multi-tool
    ]
    
    print(f"Running {len(demo_queries)} demo queries...\n")
    
    results = await batch_mode(demo_queries)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Demo Summary:")
    print("=" * 50)
    
    for result in results:
        print(f"\n❓ Query: {result['query']}")
        print(f"🛠️  Tools: {', '.join(result['tools_used']) or 'None'}")
        print(f"📝 Response preview: {result['response'][:100]}...")


async def config_mode(config_file):
    """Run with configuration file."""
    print(f"\n📋 Loading configuration from: {config_file}")
    
    with open(config_file) as f:
        config = json.load(f)
    
    # Extract settings
    server_url = config.get("mcp_servers", [{}])[0].get("url", "mock://localhost:3333")
    queries = config.get("queries", [])
    
    print(f"🔗 Server: {server_url}")
    print(f"📝 Queries: {len(queries)}")
    
    # Build custom workflow
    mcp_client = MCPClientNode(server_url)
    discover_node = ToolDiscoveryNode()
    select_node = ToolSelectionNode()
    execute_node = ToolExecutionNode()
    format_node = ResultFormatterNode()
    
    graph = AsyncGraph(start=mcp_client)
    mcp_client >> discover_node >> select_node
    select_node - "single_tool" >> execute_node
    select_node - "multi_tool" >> execute_node
    select_node - "no_tools" >> format_node
    execute_node >> format_node
    
    # Process queries
    if queries:
        results = []
        for query in queries:
            shared = {"user_query": query}
            await graph.run_async(shared)
            results.append(shared.get("final_response"))
        
        print("\n📊 Results:")
        for i, (query, result) in enumerate(zip(queries, results), 1):
            print(f"\n[{i}] {query}")
            print(f"→ {result}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KayGraph MCP Integration Example"
    )
    
    parser.add_argument(
        "--mode", 
        choices=["interactive", "demo", "batch", "config"],
        default="interactive",
        help="Execution mode"
    )
    
    parser.add_argument(
        "--queries",
        nargs="+",
        help="Queries for batch mode"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run appropriate mode
    if args.mode == "interactive":
        asyncio.run(interactive_mode())
    elif args.mode == "demo":
        asyncio.run(demo_mode())
    elif args.mode == "batch":
        if not args.queries:
            print("❌ Error: --queries required for batch mode")
            sys.exit(1)
        asyncio.run(batch_mode(args.queries))
    elif args.mode == "config":
        if not args.config:
            print("❌ Error: --config required for config mode")
            sys.exit(1)
        asyncio.run(config_mode(args.config))


if __name__ == "__main__":
    main()