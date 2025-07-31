"""
Indexing pipeline nodes for RAG system using KayGraph.
"""

import os
import glob
import logging
from typing import Dict, Any, List
from kaygraph import Node, BatchNode
from utils.chunking import smart_chunk_documents
from utils.embeddings import generate_embeddings_batch
from utils.vector_store import SimpleVectorStore


class LoadDocsNode(Node):
    """Load documents from a directory."""
    
    def __init__(self, doc_extensions: List[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_extensions = doc_extensions or ['.txt', '.md', '.rst']
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get document directory from shared state."""
        return shared.get("doc_directory", "data/")
    
    def exec(self, prep_res: str) -> List[Dict[str, Any]]:
        """Load all documents from directory."""
        documents = []
        
        # Find all matching files
        for ext in self.doc_extensions:
            pattern = os.path.join(prep_res, f"*{ext}")
            files = glob.glob(pattern)
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create document object
                    doc = {
                        "content": content,
                        "source": os.path.basename(file_path),
                        "path": file_path,
                        "type": ext[1:],  # Remove dot
                        "size": len(content)
                    }
                    documents.append(doc)
                    self.logger.info(f"Loaded {file_path} ({len(content)} chars)")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load {file_path}: {e}")
        
        self.logger.info(f"Loaded {len(documents)} documents")
        return documents
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: List[Dict]) -> str:
        """Store loaded documents."""
        shared["documents"] = exec_res
        shared["doc_count"] = len(exec_res)
        
        if not exec_res:
            self.logger.warning("No documents found to index")
            return "no_docs"
        
        return "default"


class ChunkNode(Node):
    """Split documents into chunks for processing."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get documents to chunk."""
        return shared.get("documents", [])
    
    def exec(self, prep_res: List[Dict]) -> List[Dict[str, Any]]:
        """Chunk all documents."""
        chunks = smart_chunk_documents(
            prep_res,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        self.logger.info(f"Created {len(chunks)} chunks from {len(prep_res)} documents")
        return chunks
    
    def post(self, shared: Dict[str, Any], prep_res: List[Dict], exec_res: List[Dict]) -> str:
        """Store chunks."""
        shared["chunks"] = exec_res
        shared["chunk_count"] = len(exec_res)
        return "default"


class EmbedNode(BatchNode):
    """Generate embeddings for chunks in batches."""
    
    def __init__(self, batch_size: int = 32, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size
    
    def prep(self, shared: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """Prepare chunks for batch embedding."""
        chunks = shared.get("chunks", [])
        
        # Split into batches
        batches = []
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batches.append(batch)
        
        self.logger.info(f"Prepared {len(batches)} batches for embedding")
        return batches
    
    def exec(self, batch: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for a batch of chunks."""
        # Extract text content
        texts = [chunk["content"] for chunk in batch]
        
        # Generate embeddings
        embeddings = generate_embeddings_batch(texts)
        
        self.logger.debug(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def post(self, shared: Dict[str, Any], prep_res: List[List[Dict]], exec_res: List[List[List[float]]]) -> str:
        """Flatten and store all embeddings."""
        # Flatten nested lists
        all_embeddings = []
        for batch_embeddings in exec_res:
            all_embeddings.extend(batch_embeddings)
        
        shared["embeddings"] = all_embeddings
        self.logger.info(f"Generated {len(all_embeddings)} embeddings total")
        return "default"


class StoreNode(Node):
    """Store chunks and embeddings in vector database."""
    
    def __init__(self, index_path: str = "data/rag_index.json", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index_path = index_path
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare chunks and embeddings for storage."""
        return {
            "chunks": shared.get("chunks", []),
            "embeddings": shared.get("embeddings", [])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> SimpleVectorStore:
        """Store in vector database."""
        chunks = prep_res["chunks"]
        embeddings = prep_res["embeddings"]
        
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunk count {len(chunks)} doesn't match embedding count {len(embeddings)}")
        
        # Create or load vector store
        if embeddings:
            dimension = len(embeddings[0])
        else:
            dimension = 384  # Default dimension
            
        store = SimpleVectorStore(dimension=dimension, index_path=self.index_path)
        
        # Clear and add new data
        store.clear()
        store.add_chunks(chunks, embeddings)
        
        # Save to disk
        store.save()
        
        self.logger.info(f"Stored {len(chunks)} chunks in vector store")
        return store
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: SimpleVectorStore) -> str:
        """Store vector store reference and stats."""
        shared["vector_store"] = exec_res
        shared["index_stats"] = exec_res.get_stats()
        
        self.logger.info(f"Indexing complete. Stats: {shared['index_stats']}")
        return "default"