"""
Document chunking utilities for RAG system.
"""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separator: str = "\n\n"
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Target size for each chunk (in characters)
        chunk_overlap: Number of characters to overlap between chunks
        separator: Preferred separator for splitting
        
    Returns:
        List of text chunks
    """
    # First try to split by separator
    if separator and separator in text:
        sections = text.split(separator)
    else:
        # Fallback to sentence splitting
        sections = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for section in sections:
        # If adding this section would exceed chunk size
        if len(current_chunk) + len(section) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap
            if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                overlap_text = current_chunk[-chunk_overlap:]
                current_chunk = overlap_text + " " + section
            else:
                current_chunk = section
        else:
            # Add section to current chunk
            if current_chunk:
                current_chunk += separator + section
            else:
                current_chunk = section
    
    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks


def chunk_document(
    document: Dict[str, Any],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Chunk a document and preserve metadata.
    
    Args:
        document: Document dict with 'content' and optional metadata
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunk dictionaries with metadata
    """
    content = document.get("content", "")
    metadata = {k: v for k, v in document.items() if k != "content"}
    
    # Generate chunks
    text_chunks = chunk_text(content, chunk_size, chunk_overlap)
    
    # Create chunk objects
    chunks = []
    for i, chunk_text in enumerate(text_chunks):
        chunk = {
            "content": chunk_text,
            "chunk_index": i,
            "total_chunks": len(text_chunks),
            **metadata  # Include document metadata
        }
        
        # Add source tracking
        if "source" in metadata:
            chunk["source_chunk"] = f"{metadata['source']}#chunk{i}"
        
        chunks.append(chunk)
    
    return chunks


def smart_chunk_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    min_chunk_size: int = 100
) -> List[Dict[str, Any]]:
    """
    Intelligently chunk multiple documents.
    
    Args:
        documents: List of document dictionaries
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        min_chunk_size: Minimum chunk size to keep
        
    Returns:
        List of all chunks from all documents
    """
    all_chunks = []
    
    for doc_idx, document in enumerate(documents):
        # Add document index if not present
        if "doc_index" not in document:
            document["doc_index"] = doc_idx
        
        # Chunk the document
        chunks = chunk_document(document, chunk_size, chunk_overlap)
        
        # Filter out too-small chunks
        valid_chunks = [
            chunk for chunk in chunks 
            if len(chunk["content"]) >= min_chunk_size
        ]
        
        if len(valid_chunks) < len(chunks):
            logger.warning(f"Filtered out {len(chunks) - len(valid_chunks)} small chunks from document {doc_idx}")
        
        all_chunks.extend(valid_chunks)
    
    logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
    return all_chunks


def create_chunk_windows(chunks: List[Dict[str, Any]], window_size: int = 3) -> List[Dict[str, Any]]:
    """
    Create sliding windows of chunks for better context.
    
    Args:
        chunks: List of chunks
        window_size: Number of chunks to combine
        
    Returns:
        List of windowed chunks
    """
    if window_size <= 1:
        return chunks
    
    windowed_chunks = []
    
    for i in range(len(chunks)):
        # Get window of chunks
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(chunks), start_idx + window_size)
        
        window_chunks = chunks[start_idx:end_idx]
        
        # Combine content
        combined_content = "\n---\n".join(chunk["content"] for chunk in window_chunks)
        
        # Create windowed chunk
        windowed_chunk = {
            "content": combined_content,
            "window_start": start_idx,
            "window_end": end_idx,
            "center_chunk": i,
            "source": chunks[i].get("source", "unknown")
        }
        
        windowed_chunks.append(windowed_chunk)
    
    return windowed_chunks


if __name__ == "__main__":
    # Test chunking
    logging.basicConfig(level=logging.INFO)
    
    sample_text = """
    KayGraph is an opinionated framework for building context-aware AI applications.
    
    The core abstraction is Context Graph + Shared Store, where Nodes handle operations
    (including LLM calls) and Graphs connect nodes through Actions (labeled edges) to
    create sophisticated workflows.
    
    Key features include:
    - Zero dependencies
    - Production-ready patterns
    - Async support
    - Batch processing
    """
    
    # Test basic chunking
    chunks = chunk_text(sample_text, chunk_size=100, chunk_overlap=20)
    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i}: {chunk[:50]}...")
    
    # Test document chunking
    doc = {
        "content": sample_text,
        "source": "kaygraph_docs.md",
        "type": "documentation"
    }
    
    doc_chunks = chunk_document(doc, chunk_size=100)
    print(f"\n\nDocument chunks with metadata:")
    for chunk in doc_chunks[:2]:
        print(f"- {chunk['source_chunk']}: {chunk['content'][:50]}...")