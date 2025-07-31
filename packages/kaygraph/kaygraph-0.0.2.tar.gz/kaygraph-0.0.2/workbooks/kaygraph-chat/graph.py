"""
Chat graph construction using KayGraph.
"""

from kaygraph import Graph
from nodes import InputNode, ChatNode, OutputNode


def create_chat_graph(system_prompt: str = None) -> Graph:
    """
    Create a conversational chat graph.
    
    Args:
        system_prompt: Optional custom system prompt for the chatbot
        
    Returns:
        Configured chat graph
    """
    # Create nodes
    input_node = InputNode(node_id="input")
    chat_node = ChatNode(system_prompt=system_prompt, node_id="chat")
    output_node = OutputNode(node_id="output")
    
    # Connect nodes for main conversation loop
    input_node >> chat_node >> output_node
    
    # Handle conversation continuation
    output_node >> ("continue", input_node)  # Loop back for next turn
    
    # Handle exit flow
    input_node >> ("exit", output_node)  # Direct to output when exiting
    
    # Create graph
    graph = Graph(start=input_node)
    graph.logger.info("Chat graph created")
    
    return graph


if __name__ == "__main__":
    # Test graph creation
    graph = create_chat_graph()
    print("Chat graph created successfully!")
    print(f"Start node: {graph.start_node.node_id}")