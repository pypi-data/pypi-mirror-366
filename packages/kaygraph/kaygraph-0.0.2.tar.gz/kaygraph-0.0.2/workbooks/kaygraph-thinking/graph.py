"""
Chain-of-Thought graph construction using KayGraph.
"""

from kaygraph import Graph
from nodes import StartNode, ChainOfThoughtNode, EndNode


def create_chain_of_thought_graph() -> Graph:
    """
    Create the Chain-of-Thought reasoning graph.
    
    The graph structure:
    - StartNode initializes the process
    - ChainOfThoughtNode loops on itself with "continue" action
    - ChainOfThoughtNode transitions to EndNode with "done" action
    """
    # Create nodes
    start = StartNode(node_id="start")
    cot = ChainOfThoughtNode(node_id="chain_of_thought")
    end = EndNode(node_id="end")
    
    # Connect nodes
    start >> cot
    cot >> ("continue", cot)  # Self-loop for continued thinking
    cot >> ("done", end)      # Exit when solution is found
    
    # Create and configure graph
    graph = Graph(start=start)
    graph.logger.info("Chain-of-Thought graph created")
    
    return graph, cot  # Return both graph and cot node for metrics access


if __name__ == "__main__":
    # Test graph creation
    graph, _ = create_chain_of_thought_graph()
    print("Graph created successfully!")
    print(f"Start node: {graph.start_node.node_id}")
    print(f"Total nodes: 3 (start, chain_of_thought, end)")