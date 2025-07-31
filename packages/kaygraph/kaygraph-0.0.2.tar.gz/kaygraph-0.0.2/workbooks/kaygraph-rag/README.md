# KayGraph RAG (Retrieval-Augmented Generation)

This workbook demonstrates how to build a complete RAG system using KayGraph with separate indexing and retrieval pipelines.

## What it does

The RAG system:
- **Indexes documents**: Chunks text, generates embeddings, stores in vector DB
- **Semantic search**: Finds relevant chunks based on query similarity
- **Contextual answers**: Generates responses using retrieved information
- **Source attribution**: Tracks which documents were used

## How to run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure utilities (in `utils/` folder):
   - `embeddings.py`: Add your embedding API
   - `call_llm.py`: Add your LLM API
   - `vector_store.py`: Optionally use a production vector DB

3. Index your documents:
```bash
# Index default sample documents
python main.py index

# Or index your own documents
python main.py index /path/to/your/docs/
```

4. Query the system:
```bash
python main.py query "What is KayGraph?"

# Show retrieved context
python main.py query "Explain KayGraph nodes" --show-context
```

## How it works

### Two-Graph Architecture

#### 1. Indexing Graph
```
LoadDocsNode → ChunkNode → EmbedNode → StoreNode
```

- **LoadDocsNode**: Loads .txt, .md, .rst files from directory
- **ChunkNode**: Splits into overlapping chunks (500 chars, 50 overlap)
- **EmbedNode**: Generates embeddings in batches
- **StoreNode**: Saves to vector database

#### 2. Retrieval Graph
```
QueryNode → EmbedQueryNode → SearchNode → GenerateNode
```

- **QueryNode**: Validates and processes user query
- **EmbedQueryNode**: Generates query embedding
- **SearchNode**: Finds top-k similar chunks
- **GenerateNode**: Creates answer with context

### Key Features

1. **Modular Design**: Separate indexing and retrieval workflows
2. **Batch Processing**: Efficient embedding generation
3. **Similarity Search**: Cosine similarity for relevance
4. **Context Management**: Smart truncation for LLM limits
5. **Source Tracking**: Know which documents were used

### Vector Store

The example includes a simple in-memory vector store with:
- JSON persistence
- Cosine similarity search
- Basic statistics tracking

For production, replace with:
- Pinecone, Weaviate, or Chroma
- PostgreSQL with pgvector
- Elasticsearch with vector search

### Features from KayGraph

- **BatchNode**: Efficient batch embedding generation
- **Graph separation**: Clean indexing vs retrieval
- **Error handling**: Robust document processing
- **Logging**: Detailed execution tracking

## Customization

### Document Types

Add more file types in `LoadDocsNode`:
```python
self.doc_extensions = ['.txt', '.md', '.pdf', '.docx']
```

### Chunking Strategy

Adjust in `create_indexing_graph()`:
```python
chunk_size=1000,        # Larger chunks
chunk_overlap=100,      # More overlap
```

### Search Parameters

Configure in `create_retrieval_graph()`:
```python
top_k=10,               # More results
similarity_threshold=0.7,  # Higher threshold
```

### Advanced Features

1. **Hybrid Search**: Combine keyword and semantic search
2. **Reranking**: Use cross-encoder for better ranking
3. **Query Expansion**: Generate related queries
4. **Document Filtering**: Add metadata filters
5. **Incremental Indexing**: Update without full reindex

## Example Output

### Indexing
```
📚 Indexing documents from: data/
==================================================

✅ Indexing complete!
   - Documents indexed: 3
   - Total chunks: 12
   - Index saved to: data/rag_index.json

📊 Index Statistics:
   - Vector dimension: 384
   - Memory usage: 0.15 MB
   - Sources indexed:
     • kaygraph_intro.txt: 4 chunks
     • kaygraph_nodes.txt: 5 chunks
     • kaygraph_patterns.txt: 3 chunks
```

### Querying
```
🔍 Processing query: What are KayGraph nodes?
==================================================

📋 Retrieved 5 relevant chunks

📚 Sources used:
   • kaygraph_nodes.txt
   • kaygraph_intro.txt

💬 Answer:
----------------------------------------
KayGraph provides several types of nodes for building AI applications:

1. **BaseNode** - The fundamental building block of any KayGraph application
2. **Node** - Standard node with retry and fallback capabilities for reliability
3. **BatchNode** - Efficiently processes iterables of items
4. **AsyncNode** - Handles asynchronous operations
5. **ValidatedNode** - Provides input/output validation
6. **MetricsNode** - Collects execution metrics for monitoring

Each node follows a consistent 3-step lifecycle:
- `prep()`: Read data from the shared store
- `exec()`: Execute the core logic (including LLM calls)
- `post()`: Write results back and determine the next action

This design enables modular, testable, and reusable components.
----------------------------------------
```

## Performance Tips

1. **Embedding Cache**: Cache embeddings to avoid recomputation
2. **Batch Size**: Tune for your embedding API limits
3. **Async Embeddings**: Use AsyncNode for parallel generation
4. **Vector DB**: Use production vector database for scale
5. **Chunk Windows**: Experiment with overlapping windows