"""
RAG graph construction using KayGraph.
Separate graphs for indexing and retrieval.
"""

from kaygraph import Graph
from indexing_nodes import LoadDocsNode, ChunkNode, EmbedNode, StoreNode
from retrieval_nodes import QueryNode, EmbedQueryNode, SearchNode, GenerateNode


def create_indexing_graph(
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    batch_size: int = 32,
    index_path: str = "data/rag_index.json"
) -> Graph:
    """
    Create the document indexing graph.
    
    Args:
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        batch_size: Batch size for embedding generation
        index_path: Path to save vector index
        
    Returns:
        Configured indexing graph
    """
    # Create nodes
    load_node = LoadDocsNode(node_id="load_docs")
    chunk_node = ChunkNode(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        node_id="chunk"
    )
    embed_node = EmbedNode(
        batch_size=batch_size,
        node_id="embed"
    )
    store_node = StoreNode(
        index_path=index_path,
        node_id="store"
    )
    
    # Connect nodes
    load_node >> chunk_node >> embed_node >> store_node
    
    # Handle empty document case
    load_node >> ("no_docs", store_node)
    
    # Create graph
    graph = Graph(start=load_node)
    graph.logger.info("Indexing graph created")
    
    return graph


def create_retrieval_graph(
    top_k: int = 5,
    similarity_threshold: float = 0.5,
    max_context_length: int = 3000,
    index_path: str = "data/rag_index.json"
) -> Graph:
    """
    Create the retrieval and answer generation graph.
    
    Args:
        top_k: Number of chunks to retrieve
        similarity_threshold: Minimum similarity score
        max_context_length: Maximum context size for generation
        index_path: Path to vector index
        
    Returns:
        Configured retrieval graph
    """
    # Create nodes
    query_node = QueryNode(node_id="query")
    embed_query_node = EmbedQueryNode(node_id="embed_query")
    search_node = SearchNode(
        top_k=top_k,
        threshold=similarity_threshold,
        node_id="search"
    )
    generate_node = GenerateNode(
        max_context_length=max_context_length,
        node_id="generate"
    )
    
    # Connect nodes
    query_node >> embed_query_node >> search_node >> generate_node
    
    # Create graph
    graph = Graph(start=query_node)
    graph.logger.info("Retrieval graph created")
    
    # Store index path in graph for convenience
    graph.index_path = index_path
    
    return graph


if __name__ == "__main__":
    # Test graph creation
    print("Creating RAG graphs...")
    
    indexing_graph = create_indexing_graph()
    print(f"Indexing graph created with start node: {indexing_graph.start_node.node_id}")
    
    retrieval_graph = create_retrieval_graph()
    print(f"Retrieval graph created with start node: {retrieval_graph.start_node.node_id}")