"""
Embedding utilities for RAG system.
This is a placeholder - replace with actual embedding service.
"""

import hashlib
import time
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


def generate_embedding(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text to embed
        model: Embedding model to use
        
    Returns:
        Embedding vector (list of floats)
    """
    # Placeholder implementation
    # Replace with actual embedding API:
    # - OpenAI Embeddings API
    # - Cohere Embed API
    # - HuggingFace Sentence Transformers
    # - Google's Universal Sentence Encoder
    
    # For demo: create deterministic fake embedding based on text
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Convert to 384-dimensional vector (common embedding size)
    embedding = []
    for i in range(0, min(len(hash_hex), 384), 2):
        if i < len(hash_hex) - 1:
            value = int(hash_hex[i:i+2], 16) / 255.0 - 0.5
        else:
            value = 0.0
        embedding.append(value)
    
    # Pad to 384 dimensions
    while len(embedding) < 384:
        embedding.append(0.0)
    
    # Simulate API delay
    time.sleep(0.01)
    
    logger.debug(f"Generated embedding for text of length {len(text)}")
    return embedding[:384]


def generate_embeddings_batch(texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently.
    
    Args:
        texts: List of texts to embed
        model: Embedding model to use
        
    Returns:
        List of embedding vectors
    """
    # In production, use batch API for efficiency
    embeddings = []
    for i, text in enumerate(texts):
        embeddings.append(generate_embedding(text, model))
        if (i + 1) % 10 == 0:
            logger.info(f"Generated {i + 1}/{len(texts)} embeddings")
    
    return embeddings


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score between -1 and 1
    """
    # Simple implementation
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    
    if magnitude1 * magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def find_similar_chunks(
    query_embedding: List[float],
    chunk_embeddings: List[List[float]],
    chunks: List[dict],
    top_k: int = 5,
    threshold: float = 0.5
) -> List[dict]:
    """
    Find most similar chunks to query.
    
    Args:
        query_embedding: Query embedding vector
        chunk_embeddings: List of chunk embeddings
        chunks: List of chunk dictionaries
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        
    Returns:
        List of relevant chunks with similarity scores
    """
    # Calculate similarities
    similarities = []
    for i, chunk_embedding in enumerate(chunk_embeddings):
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        if similarity >= threshold:
            similarities.append((i, similarity))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get top chunks
    results = []
    for idx, score in similarities[:top_k]:
        chunk_with_score = chunks[idx].copy()
        chunk_with_score['similarity_score'] = score
        results.append(chunk_with_score)
    
    logger.info(f"Found {len(results)} relevant chunks (threshold={threshold})")
    return results


if __name__ == "__main__":
    # Test embedding generation
    logging.basicConfig(level=logging.INFO)
    
    test_text = "KayGraph is a framework for building AI applications."
    embedding = generate_embedding(test_text)
    print(f"Generated embedding of dimension: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")
    
    # Test similarity
    text1 = "KayGraph helps build AI apps"
    text2 = "KayGraph is an AI framework"
    text3 = "The weather is nice today"
    
    emb1 = generate_embedding(text1)
    emb2 = generate_embedding(text2)
    emb3 = generate_embedding(text3)
    
    print(f"\nSimilarity between related texts: {cosine_similarity(emb1, emb2):.3f}")
    print(f"Similarity between unrelated texts: {cosine_similarity(emb1, emb3):.3f}")