"""
Hello World example using KayGraph.

The simplest possible KayGraph application demonstrating:
- Basic node creation
- Graph construction
- Shared state usage
"""

from kaygraph import Node, Graph
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class HelloNode(Node):
    """A simple node that says hello."""
    
    def prep(self, shared):
        """Get name from shared state."""
        return shared.get("name", "World")
    
    def exec(self, name):
        """Create greeting message."""
        return f"Hello, {name}!"
    
    def post(self, shared, prep_res, exec_res):
        """Store greeting in shared state."""
        shared["greeting"] = exec_res
        print(exec_res)
        return "default"


class GoodbyeNode(Node):
    """A simple node that says goodbye."""
    
    def prep(self, shared):
        """Get name from shared state."""
        return shared.get("name", "World")
    
    def exec(self, name):
        """Create farewell message."""
        return f"Goodbye, {name}! Have a great day!"
    
    def post(self, shared, prep_res, exec_res):
        """Store farewell and print."""
        shared["farewell"] = exec_res
        print(exec_res)
        return None


def main():
    """Run the Hello World example."""
    print("KayGraph Hello World")
    print("=" * 30)
    
    # Create nodes
    hello = HelloNode(node_id="hello")
    goodbye = GoodbyeNode(node_id="goodbye")
    
    # Connect nodes
    hello >> goodbye
    
    # Create graph
    graph = Graph(start=hello)
    
    # Run with different names
    names = ["World", "KayGraph", "Developer"]
    
    for name in names:
        print(f"\nRunning for: {name}")
        print("-" * 20)
        
        # Initialize shared state
        shared = {"name": name}
        
        # Run graph
        graph.run(shared)
        
        # Show final state
        print(f"Final state: {shared}")


if __name__ == "__main__":
    main()