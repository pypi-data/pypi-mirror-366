"""
Simple in-memory vector store for RAG system.
In production, use a proper vector database like Pinecone, Weaviate, or Chroma.
"""

import json
import os
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """
    Simple in-memory vector store with persistence.
    """
    
    def __init__(self, dimension: int = 384, index_path: Optional[str] = None):
        """
        Initialize vector store.
        
        Args:
            dimension: Embedding dimension
            index_path: Path to save/load index
        """
        self.dimension = dimension
        self.index_path = index_path
        self.chunks = []
        self.embeddings = []
        self.metadata = {
            "dimension": dimension,
            "total_chunks": 0
        }
        
        # Load existing index if available
        if index_path and os.path.exists(index_path):
            self.load()
    
    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add chunks with their embeddings to the store.
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: Corresponding embeddings
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Validate embedding dimensions
        for emb in embeddings:
            if len(emb) != self.dimension:
                raise ValueError(f"Expected embedding dimension {self.dimension}, got {len(emb)}")
        
        # Add to store
        self.chunks.extend(chunks)
        self.embeddings.extend(embeddings)
        self.metadata["total_chunks"] = len(self.chunks)
        
        logger.info(f"Added {len(chunks)} chunks to vector store (total: {self.metadata['total_chunks']})")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar chunks with scores
        """
        if not self.chunks:
            logger.warning("Vector store is empty")
            return []
        
        # Import here to avoid circular dependency
        from .embeddings import cosine_similarity
        
        # Calculate similarities
        similarities = []
        for i, chunk_embedding in enumerate(self.embeddings):
            similarity = cosine_similarity(query_embedding, chunk_embedding)
            if similarity >= threshold:
                similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top results
        results = []
        for idx, score in similarities[:top_k]:
            result = self.chunks[idx].copy()
            result["similarity_score"] = score
            result["chunk_id"] = idx
            results.append(result)
        
        logger.info(f"Found {len(results)} chunks above threshold {threshold}")
        return results
    
    def save(self):
        """Save vector store to disk."""
        if not self.index_path:
            logger.warning("No index path specified, skipping save")
            return
        
        # Create directory if needed
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save data
        data = {
            "metadata": self.metadata,
            "chunks": self.chunks,
            "embeddings": self.embeddings
        }
        
        with open(self.index_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved vector store to {self.index_path}")
    
    def load(self):
        """Load vector store from disk."""
        if not os.path.exists(self.index_path):
            logger.warning(f"Index file not found: {self.index_path}")
            return
        
        with open(self.index_path, 'r') as f:
            data = json.load(f)
        
        self.metadata = data["metadata"]
        self.chunks = data["chunks"]
        self.embeddings = data["embeddings"]
        self.dimension = self.metadata["dimension"]
        
        logger.info(f"Loaded {len(self.chunks)} chunks from {self.index_path}")
    
    def clear(self):
        """Clear the vector store."""
        self.chunks = []
        self.embeddings = []
        self.metadata["total_chunks"] = 0
        logger.info("Vector store cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        stats = {
            "total_chunks": len(self.chunks),
            "dimension": self.dimension,
            "memory_usage_mb": self._estimate_memory_usage(),
            "index_path": self.index_path
        }
        
        if self.chunks:
            # Get source distribution
            sources = {}
            for chunk in self.chunks:
                source = chunk.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
            stats["sources"] = sources
        
        return stats
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        # Rough estimation
        embedding_size = len(self.embeddings) * self.dimension * 4  # 4 bytes per float
        chunk_size = len(str(self.chunks).encode())  # Rough estimate
        total_bytes = embedding_size + chunk_size
        return total_bytes / (1024 * 1024)


if __name__ == "__main__":
    # Test vector store
    logging.basicConfig(level=logging.INFO)
    
    # Create store
    store = SimpleVectorStore(dimension=3, index_path="test_index.json")
    
    # Add test data
    test_chunks = [
        {"content": "First chunk", "source": "doc1"},
        {"content": "Second chunk", "source": "doc1"},
        {"content": "Third chunk", "source": "doc2"}
    ]
    
    test_embeddings = [
        [0.1, 0.2, 0.3],
        [0.2, 0.3, 0.4],
        [0.9, 0.8, 0.7]
    ]
    
    store.add_chunks(test_chunks, test_embeddings)
    
    # Test search
    query_embedding = [0.15, 0.25, 0.35]
    results = store.search(query_embedding, top_k=2)
    
    print("Search results:")
    for result in results:
        print(f"- {result['content']} (score: {result['similarity_score']:.3f})")
    
    # Show stats
    print("\nStore stats:", store.get_stats())
    
    # Clean up
    if os.path.exists("test_index.json"):
        os.remove("test_index.json")