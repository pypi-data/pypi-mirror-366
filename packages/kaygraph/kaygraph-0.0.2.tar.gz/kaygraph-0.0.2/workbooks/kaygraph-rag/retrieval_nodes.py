"""
Retrieval pipeline nodes for RAG system using KayGraph.
"""

import logging
from typing import Dict, Any, List
from kaygraph import Node, ValidatedNode
from utils.embeddings import generate_embedding
from utils.call_llm import generate_rag_answer
from utils.vector_store import SimpleVectorStore


class QueryNode(ValidatedNode):
    """Process and validate user query."""
    
    def validate_input(self, prep_res: str) -> str:
        """Validate query is not empty."""
        if not prep_res or not prep_res.strip():
            raise ValueError("Query cannot be empty")
        return prep_res.strip()
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get query from shared state."""
        return shared.get("query", "")
    
    def exec(self, prep_res: str) -> str:
        """Process query."""
        self.logger.info(f"Processing query: {prep_res}")
        return prep_res
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Store processed query."""
        shared["query"] = exec_res
        return "default"


class EmbedQueryNode(Node):
    """Generate embedding for the query."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get query to embed."""
        return shared["query"]
    
    def exec(self, prep_res: str) -> List[float]:
        """Generate query embedding."""
        embedding = generate_embedding(prep_res)
        self.logger.info(f"Generated query embedding (dim={len(embedding)})")
        return embedding
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: List[float]) -> str:
        """Store query embedding."""
        shared["query_embedding"] = exec_res
        return "default"


class SearchNode(Node):
    """Search for relevant chunks in vector store."""
    
    def __init__(self, top_k: int = 5, threshold: float = 0.5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.top_k = top_k
        self.threshold = threshold
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare search parameters."""
        return {
            "query_embedding": shared["query_embedding"],
            "vector_store": shared.get("vector_store"),
            "index_path": shared.get("index_path", "data/rag_index.json")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        # Get or load vector store
        vector_store = prep_res.get("vector_store")
        
        if not vector_store:
            # Try to load from disk
            self.logger.info(f"Loading vector store from {prep_res['index_path']}")
            vector_store = SimpleVectorStore(index_path=prep_res["index_path"])
            vector_store.load()
        
        # Search for similar chunks
        results = vector_store.search(
            query_embedding=prep_res["query_embedding"],
            top_k=self.top_k,
            threshold=self.threshold
        )
        
        self.logger.info(f"Found {len(results)} relevant chunks")
        
        # Log top results
        for i, result in enumerate(results[:3]):
            self.logger.debug(f"Result {i+1}: {result.get('source')} "
                            f"(score: {result['similarity_score']:.3f})")
        
        return results
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: List[Dict]) -> str:
        """Store search results."""
        shared["relevant_chunks"] = exec_res
        shared["num_results"] = len(exec_res)
        
        if not exec_res:
            self.logger.warning("No relevant chunks found")
            shared["context"] = ""
        
        return "default"


class GenerateNode(Node):
    """Generate answer using retrieved context."""
    
    def __init__(self, max_context_length: int = 3000, *args, **kwargs):
        super().__init__(max_retries=2, wait=1, *args, **kwargs)
        self.max_context_length = max_context_length
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for answer generation."""
        return {
            "query": shared["query"],
            "relevant_chunks": shared.get("relevant_chunks", [])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, str]:
        """Generate answer with context."""
        answer, context = generate_rag_answer(
            query=prep_res["query"],
            retrieved_chunks=prep_res["relevant_chunks"],
            max_context_length=self.max_context_length
        )
        
        self.logger.info(f"Generated answer using {len(prep_res['relevant_chunks'])} chunks")
        
        return {
            "answer": answer,
            "context": context
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict[str, str]) -> str:
        """Store final answer and context."""
        shared["answer"] = exec_res["answer"]
        shared["context"] = exec_res["context"]
        
        # Add source attribution
        if shared.get("relevant_chunks"):
            sources = set()
            for chunk in shared["relevant_chunks"][:3]:  # Top 3 sources
                source = chunk.get("source", "unknown")
                sources.add(source)
            shared["sources_used"] = list(sources)
        
        return "default"
    
    def exec_fallback(self, prep_res: Dict[str, Any], exc: Exception) -> Dict[str, str]:
        """Fallback when generation fails."""
        self.logger.error(f"Generation failed: {exc}")
        
        # Provide basic answer without LLM
        if prep_res["relevant_chunks"]:
            # Use top chunk as answer
            top_chunk = prep_res["relevant_chunks"][0]
            answer = f"Based on the search results:\n\n{top_chunk['content']}\n\n(Note: Full answer generation failed)"
            context = top_chunk["content"]
        else:
            answer = "I couldn't find relevant information to answer your query."
            context = ""
        
        return {
            "answer": answer,
            "context": context
        }