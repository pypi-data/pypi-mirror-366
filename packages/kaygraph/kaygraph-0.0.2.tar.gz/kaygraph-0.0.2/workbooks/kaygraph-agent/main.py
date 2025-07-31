"""
Research agent example using KayGraph.

This example demonstrates an autonomous agent that can:
- Analyze queries to determine information needs
- Search the web when necessary
- Synthesize findings into comprehensive answers
"""

import sys
import logging
from typing import Dict, Any
from graph import create_agent_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def print_agent_response(shared: Dict[str, Any]):
    """Pretty print the agent's response with context."""
    print("\n" + "=" * 60)
    print("AGENT RESPONSE")
    print("=" * 60)
    
    # Show thought process
    if shared.get("thought_process"):
        print(f"\n💭 Thought Process: {shared['thought_process']}")
    
    # Show if search was performed
    if shared.get("needs_search"):
        print(f"\n🔍 Search performed: Yes")
        if shared.get("search_results"):
            print(f"   Found {len(shared['search_results'])} results")
    else:
        print(f"\n🔍 Search performed: No (using existing knowledge)")
    
    # Show final answer
    print(f"\n📝 Answer:\n{shared.get('final_answer', 'No answer generated')}")
    print("\n" + "=" * 60)


def main():
    """Run the research agent example."""
    # Get query from command line or prompt
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python main.py [query]")
            print("\nExamples:")
            print('  python main.py "What is KayGraph?"')
            print('  python main.py "What is the weather in Tokyo?"')
            print('  python main.py "Explain quantum computing"')
            return 0
        query = " ".join(sys.argv[1:])
    else:
        print("KayGraph Research Agent")
        print("-" * 30)
        query = input("Enter your question: ").strip()
        if not query:
            print("No query provided. Exiting.")
            return 1
    
    print(f"\n🤖 Processing query: {query}")
    
    # Create the agent graph
    graph = create_agent_graph(max_search_results=5)
    
    # Initialize shared state
    shared = {"query": query}
    
    try:
        # Run the agent
        final_action = graph.run(shared)
        
        # Display results
        print_agent_response(shared)
        
        # Show performance stats if available
        print("\n📊 Execution Summary:")
        print(f"   - Query analyzed: ✓")
        print(f"   - Search needed: {'✓' if shared.get('needs_search') else '✗'}")
        if shared.get("search_results"):
            print(f"   - Results found: {len(shared['search_results'])}")
        print(f"   - Answer generated: ✓")
        
    except Exception as e:
        logging.error(f"Error during agent execution: {e}")
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())