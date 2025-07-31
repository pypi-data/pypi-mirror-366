"""
Agent graph construction using KayGraph.
"""

from kaygraph import Graph
from nodes import QueryNode, ThinkNode, SearchNode, SynthesizeNode, AnswerNode


def create_agent_graph(max_search_results: int = 5) -> Graph:
    """
    Create an autonomous agent graph that can search and answer questions.
    
    Args:
        max_search_results: Maximum number of search results to retrieve
        
    Returns:
        Configured agent graph
    """
    # Create nodes
    query_node = QueryNode(node_id="query")
    think_node = ThinkNode(node_id="think")
    search_node = SearchNode(max_results=max_search_results, node_id="search")
    synthesize_node = SynthesizeNode(node_id="synthesize")
    answer_node = AnswerNode(node_id="answer")
    
    # Connect nodes
    # Main flow: query -> think -> decide path
    query_node >> think_node
    
    # Path 1: Direct answer (no search needed)
    think_node >> ("answer", answer_node)
    
    # Path 2: Search required
    think_node >> ("search", search_node)
    search_node >> synthesize_node >> answer_node
    
    # Create graph
    graph = Graph(start=query_node)
    graph.logger.info("Agent graph created with conditional search path")
    
    return graph


if __name__ == "__main__":
    # Test graph creation
    graph = create_agent_graph()
    print("Agent graph created successfully!")
    print(f"Start node: {graph.start_node.node_id}")
    print("Graph paths:")
    print("  - Direct: query -> think -> answer")
    print("  - Search: query -> think -> search -> synthesize -> answer")