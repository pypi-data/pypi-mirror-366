# KayGraph Tool Integration - Text Embeddings

Demonstrates text embedding generation and semantic similarity search using KayGraph for building AI-powered search and analysis workflows.

## What it does

This example showcases:
- **Embedding Generation**: Convert text to vector representations
- **Similarity Search**: Find semantically similar documents
- **Index Building**: Create searchable embedding databases
- **Space Analysis**: Analyze relationships in embedding space

## Features

- Multiple embedding methods (mock neural, TF-IDF, hash-based)
- Efficient similarity search with cosine similarity
- Document categorization and clustering analysis
- Batch processing for multiple queries
- Persistent index storage

## How to run

```bash
python main.py
```

## Architecture

```
LoadDocumentsNode → GenerateEmbeddingsNode → BuildIndexNode → SearchDocumentsBatchNode → AnalyzeEmbeddingsNode
```

### Node Descriptions

1. **LoadDocumentsNode**: Load documents from various sources
2. **GenerateEmbeddingsNode**: Create vector embeddings for texts
3. **BuildIndexNode**: Build searchable index structure
4. **SearchDocumentsBatchNode**: Process multiple search queries
5. **AnalyzeEmbeddingsNode**: Analyze embedding space properties

## Embedding Methods

### 1. Mock Neural Embeddings
Simulates real neural embeddings with:
- Deterministic generation (same text → same embedding)
- Feature extraction (length, sentiment, technical terms)
- L2 normalization
- Realistic distribution

### 2. TF-IDF Embeddings
Traditional approach using:
- Term frequency-inverse document frequency
- Sparse vector representation
- Vocabulary building
- Fast computation

### 3. Hash-based Embeddings
Locality-sensitive hashing:
- Multiple hash functions
- Fixed-size representations
- No vocabulary needed
- Memory efficient

## Example Output

```
🧮 KayGraph Embeddings Tool Integration
============================================================
This example demonstrates text embedding generation
and semantic similarity search.

📚 Loaded 8 documents:
  - [doc1] Introduction to Machine Learning (AI/ML)
  - [doc2] Python Programming Guide (Programming)
  - [doc3] Deep Learning Fundamentals (AI/ML)
  - [doc4] Web Development with Python (Programming)
  - [doc5] Natural Language Processing (AI/ML)
  ... and 3 more

🔢 Generated Embeddings:
  - Method: mock
  - Dimension: 384
  - Documents: 8
  - Avg magnitude: 1.000

🗂️  Built searchable index with 8 documents

🔍 Search Results:
============================================================

Query: 'How to build neural networks with Python?'
  Found 3 similar documents:
  1. [doc3] Deep Learning Fundamentals
     Category: AI/ML
     Similarity: 0.825
  2. [doc1] Introduction to Machine Learning
     Category: AI/ML
     Similarity: 0.793
  3. [doc2] Python Programming Guide
     Category: Programming
     Similarity: 0.756

Query: 'Web development frameworks and tools'
  Found 3 similar documents:
  1. [doc4] Web Development with Python
     Category: Programming
     Similarity: 0.841
  2. [doc2] Python Programming Guide
     Category: Programming
     Similarity: 0.687
  3. [doc6] Data Structures and Algorithms
     Category: Programming
     Similarity: 0.592

📊 Embedding Space Analysis:
============================================================

Overview:
  - Total embeddings: 8
  - Embedding dimension: 384
  - Categories: 3

Category Cohesion (how similar documents within category are):
  - AI/ML:
    • Average similarity: 0.812
    • Range: [0.756, 0.891]
  - Programming:
    • Average similarity: 0.724
    • Range: [0.687, 0.782]

Inter-category Similarities:
  - AI/ML ↔ Programming: 0.632
  - AI/ML ↔ Infrastructure: 0.421
  - Programming ↔ Infrastructure: 0.389

💾 Saved embedding index to: document_embeddings.json

✨ Embeddings example complete!
```

## Use Cases

- **Semantic Search**: Find documents by meaning, not keywords
- **Document Clustering**: Group similar documents automatically
- **Recommendation Systems**: Suggest related content
- **Duplicate Detection**: Find similar or duplicate content
- **Question Answering**: Match questions to relevant documents

## Integration with Real Embeddings

Replace mock embeddings with real ones:

```python
# Using OpenAI embeddings
class OpenAIEmbeddingGenerator(EmbeddingGenerator):
    def embed_text(self, text: str) -> List[float]:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response['data'][0]['embedding']

# Using Sentence Transformers
from sentence_transformers import SentenceTransformer

class SentenceTransformerGenerator(EmbeddingGenerator):
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
```

## Performance Considerations

### Scaling Tips

1. **Batch Processing**: Embed multiple texts at once
2. **Caching**: Store computed embeddings
3. **Approximate Search**: Use libraries like FAISS for large-scale
4. **Dimensionality Reduction**: Use PCA/UMAP for visualization
5. **Quantization**: Reduce memory with int8 embeddings

### Example with FAISS

```python
import faiss

# Build FAISS index
dimension = 384
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Fast search
distances, indices = index.search(query_embedding, k=5)
```

## Advanced Features

### 1. Hybrid Search
Combine embeddings with keyword search:
```python
def hybrid_search(query, alpha=0.7):
    semantic_results = embedding_search(query)
    keyword_results = keyword_search(query)
    return merge_results(semantic_results, keyword_results, alpha)
```

### 2. Fine-tuning
Improve embeddings for specific domains:
```python
def fine_tune_embeddings(base_embeddings, labels):
    # Use contrastive learning or other techniques
    # to adjust embeddings for your use case
    pass
```

### 3. Multi-modal Embeddings
Combine text with other modalities:
```python
def create_multimodal_embedding(text, image):
    text_emb = text_encoder(text)
    image_emb = image_encoder(image)
    return concatenate([text_emb, image_emb])
```

## Best Practices

1. **Preprocessing**: Clean and normalize text before embedding
2. **Chunking**: Split long documents into semantic chunks
3. **Metadata**: Store additional context with embeddings
4. **Evaluation**: Test retrieval quality with known queries
5. **Updates**: Plan for incremental index updates

## Dependencies

This example uses no external dependencies. For production:
- `numpy`: Efficient array operations
- `faiss`: Fast similarity search
- `sentence-transformers`: Pre-trained models
- `openai`: OpenAI embedding API