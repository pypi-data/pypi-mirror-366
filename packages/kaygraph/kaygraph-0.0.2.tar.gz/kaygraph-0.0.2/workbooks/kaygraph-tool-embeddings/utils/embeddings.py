"""
Embeddings utility for text vectorization.

This module provides embedding generation using various methods,
from simple TF-IDF to mock neural embeddings.
"""

import hashlib
import math
import json
from typing import List, Dict, Any, Tuple
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using various methods."""
    
    def __init__(self, method: str = "mock", dimension: int = 384):
        """
        Initialize embedding generator.
        
        Args:
            method: Embedding method ('mock', 'tfidf', 'hash')
            dimension: Embedding dimension
        """
        self.method = method
        self.dimension = dimension
        self.vocabulary = {}
        self.idf_scores = {}
        
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if self.method == "mock":
            return self._mock_embedding(text)
        elif self.method == "tfidf":
            return self._tfidf_embedding(text)
        elif self.method == "hash":
            return self._hash_embedding(text)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        # Build vocabulary for TF-IDF if needed
        if self.method == "tfidf":
            self._build_vocabulary(texts)
        
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
            
        return embeddings
    
    def _mock_embedding(self, text: str) -> List[float]:
        """
        Generate mock embedding that simulates real embeddings.
        
        Uses deterministic hash-based approach to create
        consistent embeddings for the same text.
        """
        # Create seed from text
        seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        
        # Generate pseudo-random values
        import random
        random.seed(seed)
        
        # Create base embedding
        embedding = []
        
        # Add some structure based on text features
        text_lower = text.lower()
        
        # Feature extraction
        features = {
            "length": len(text) / 100.0,
            "words": len(text.split()) / 20.0,
            "question": 1.0 if "?" in text else 0.0,
            "exclamation": 1.0 if "!" in text else 0.0,
            "technical": sum(1 for word in ["code", "function", "api", "data"] if word in text_lower) / 4.0,
            "sentiment_pos": sum(1 for word in ["good", "great", "excellent", "love"] if word in text_lower) / 4.0,
            "sentiment_neg": sum(1 for word in ["bad", "poor", "hate", "terrible"] if word in text_lower) / 4.0,
        }
        
        # Generate embedding with structure
        for i in range(self.dimension):
            # Base random value
            value = random.gauss(0, 0.3)
            
            # Add feature influences
            if i < len(features) * 10:
                feature_idx = i // 10
                if feature_idx < len(features):
                    feature_name = list(features.keys())[feature_idx]
                    value += features[feature_name] * 0.5
            
            # Add some word-based patterns
            if i < len(text):
                char_value = ord(text[i % len(text)]) / 128.0 - 0.5
                value += char_value * 0.1
            
            # Normalize
            value = max(-1.0, min(1.0, value))
            embedding.append(value)
        
        # L2 normalize
        norm = math.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _tfidf_embedding(self, text: str) -> List[float]:
        """Generate TF-IDF based embedding."""
        words = text.lower().split()
        word_counts = Counter(words)
        
        # Create sparse vector
        embedding = [0.0] * self.dimension
        
        for word, count in word_counts.items():
            if word in self.vocabulary:
                # TF-IDF score
                tf = count / len(words)
                idf = self.idf_scores.get(word, 1.0)
                score = tf * idf
                
                # Hash word to position
                position = hash(word) % self.dimension
                embedding[position] += score
        
        # Normalize
        norm = math.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _hash_embedding(self, text: str) -> List[float]:
        """Generate hash-based embedding."""
        # Multiple hash functions
        embedding = []
        
        for i in range(self.dimension):
            # Create unique hash for each dimension
            hasher = hashlib.sha256()
            hasher.update(f"{text}:{i}".encode())
            hash_value = int(hasher.hexdigest()[:8], 16)
            
            # Convert to float in [-1, 1]
            normalized = (hash_value / (2**32 - 1)) * 2 - 1
            embedding.append(normalized)
        
        return embedding
    
    def _build_vocabulary(self, texts: List[str]):
        """Build vocabulary and IDF scores for TF-IDF."""
        # Document frequency
        doc_freq = Counter()
        
        for text in texts:
            words = set(text.lower().split())
            for word in words:
                doc_freq[word] += 1
        
        # Build vocabulary and IDF scores
        num_docs = len(texts)
        for word, freq in doc_freq.items():
            self.vocabulary[word] = len(self.vocabulary)
            self.idf_scores[word] = math.log(num_docs / freq)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score between -1 and 1
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same dimension")
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def find_similar(
    query_embedding: List[float],
    embeddings: List[List[float]],
    texts: List[str],
    top_k: int = 5
) -> List[Tuple[str, float]]:
    """
    Find most similar texts based on embeddings.
    
    Args:
        query_embedding: Query vector
        embeddings: List of document embeddings
        texts: List of document texts
        top_k: Number of results to return
        
    Returns:
        List of (text, similarity_score) tuples
    """
    similarities = []
    
    for i, embedding in enumerate(embeddings):
        score = cosine_similarity(query_embedding, embedding)
        similarities.append((texts[i], score))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]


class EmbeddingIndex:
    """Simple in-memory embedding index for similarity search."""
    
    def __init__(self, embedding_generator: EmbeddingGenerator):
        """Initialize index with embedding generator."""
        self.generator = embedding_generator
        self.embeddings = []
        self.texts = []
        self.metadata = []
    
    def add(self, text: str, metadata: Dict[str, Any] = None):
        """Add text to index."""
        embedding = self.generator.embed_text(text)
        self.embeddings.append(embedding)
        self.texts.append(text)
        self.metadata.append(metadata or {})
    
    def add_batch(self, texts: List[str], metadata_list: List[Dict[str, Any]] = None):
        """Add multiple texts to index."""
        embeddings = self.generator.embed_batch(texts)
        self.embeddings.extend(embeddings)
        self.texts.extend(texts)
        
        if metadata_list:
            self.metadata.extend(metadata_list)
        else:
            self.metadata.extend([{}] * len(texts))
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts."""
        if not self.embeddings:
            return []
        
        query_embedding = self.generator.embed_text(query)
        
        results = []
        for i, embedding in enumerate(self.embeddings):
            score = cosine_similarity(query_embedding, embedding)
            results.append({
                "text": self.texts[i],
                "score": score,
                "metadata": self.metadata[i],
                "index": i
            })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    def save(self, path: str):
        """Save index to file."""
        data = {
            "embeddings": self.embeddings,
            "texts": self.texts,
            "metadata": self.metadata,
            "generator_config": {
                "method": self.generator.method,
                "dimension": self.generator.dimension
            }
        }
        
        with open(path, 'w') as f:
            json.dump(data, f)
    
    def load(self, path: str):
        """Load index from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        self.embeddings = data["embeddings"]
        self.texts = data["texts"]
        self.metadata = data["metadata"]


# Convenience functions

def create_embeddings(texts: List[str], method: str = "mock") -> List[List[float]]:
    """Create embeddings for a list of texts."""
    generator = EmbeddingGenerator(method=method)
    return generator.embed_batch(texts)


def create_index(texts: List[str], method: str = "mock") -> EmbeddingIndex:
    """Create an embedding index from texts."""
    generator = EmbeddingGenerator(method=method)
    index = EmbeddingIndex(generator)
    index.add_batch(texts)
    return index


if __name__ == "__main__":
    # Test embedding generation
    print("Testing Embedding Generator")
    print("=" * 50)
    
    # Sample texts
    texts = [
        "Python is a great programming language",
        "Machine learning with Python is powerful",
        "I love coding in Python",
        "The weather is nice today",
        "What is the meaning of life?"
    ]
    
    # Test different methods
    for method in ["mock", "tfidf", "hash"]:
        print(f"\n{method.upper()} Embeddings:")
        generator = EmbeddingGenerator(method=method, dimension=128)
        embeddings = generator.embed_batch(texts)
        
        print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")
        
        # Test similarity
        query = "Python programming is awesome"
        query_embedding = generator.embed_text(query)
        
        print(f"\nQuery: '{query}'")
        print("Similar texts:")
        
        similar = find_similar(query_embedding, embeddings, texts, top_k=3)
        for text, score in similar:
            print(f"  {score:.3f}: {text}")
    
    # Test index
    print("\n\nTesting Embedding Index:")
    index = create_index(texts)
    
    results = index.search("coding with Python", top_k=3)
    print("\nSearch results for 'coding with Python':")
    for result in results:
        print(f"  {result['score']:.3f}: {result['text']}")