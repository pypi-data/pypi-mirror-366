"""
LLM utility for RAG answer generation.
"""

from typing import List, Dict, Any, Optional


def call_llm(
    prompt: str,
    context: Optional[str] = None,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 1024,
    temperature: float = 0.3
) -> str:
    """
    Call LLM for answer generation with context.
    
    Args:
        prompt: User query or instruction
        context: Retrieved context for RAG
        model: Model to use
        max_tokens: Maximum response tokens
        temperature: Sampling temperature
        
    Returns:
        Generated answer
    """
    # Placeholder implementation
    # Replace with actual LLM API call
    
    if context:
        full_prompt = f"""Answer the following question based on the provided context.

Context:
{context}

Question: {prompt}

Instructions:
- Base your answer on the provided context
- If the context doesn't contain relevant information, say so
- Be concise and accurate"""
    else:
        full_prompt = prompt
    
    # Mock response based on query patterns
    if "kaygraph" in prompt.lower():
        return """Based on the provided context, KayGraph is an opinionated framework for building context-aware AI applications. It uses a Context Graph + Shared Store architecture where Nodes handle operations (including LLM calls) and Graphs connect nodes through Actions (labeled edges) to create sophisticated workflows.

Key features include:
- Zero dependencies - only uses Python standard library
- Production-ready patterns for common AI workflows
- Support for async operations and batch processing
- Modular node-based architecture for building complex systems"""
    
    return "Based on the context provided, I can help answer your question. The information suggests that this topic relates to the documents you've indexed in the RAG system."


def generate_rag_answer(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    max_context_length: int = 3000
) -> tuple[str, str]:
    """
    Generate answer using retrieved chunks.
    
    Args:
        query: User's question
        retrieved_chunks: List of relevant chunks with content
        max_context_length: Maximum context size
        
    Returns:
        Tuple of (answer, context_used)
    """
    # Build context from chunks
    context_parts = []
    total_length = 0
    
    for i, chunk in enumerate(retrieved_chunks):
        chunk_content = chunk.get("content", "")
        chunk_source = chunk.get("source", f"chunk_{i}")
        similarity = chunk.get("similarity_score", 0.0)
        
        # Format chunk
        formatted_chunk = f"[Source: {chunk_source}, Relevance: {similarity:.2f}]\n{chunk_content}"
        
        # Check if adding would exceed limit
        if total_length + len(formatted_chunk) > max_context_length:
            break
            
        context_parts.append(formatted_chunk)
        total_length += len(formatted_chunk)
    
    # Combine context
    context = "\n\n---\n\n".join(context_parts)
    
    # Generate answer
    answer = call_llm(query, context=context)
    
    return answer, context


if __name__ == "__main__":
    # Test answer generation
    test_chunks = [
        {
            "content": "KayGraph is a framework for building AI applications with zero dependencies.",
            "source": "intro.md",
            "similarity_score": 0.95
        },
        {
            "content": "The core abstraction includes Nodes for operations and Graphs for workflows.",
            "source": "architecture.md",
            "similarity_score": 0.87
        }
    ]
    
    answer, context = generate_rag_answer(
        "What is KayGraph?",
        test_chunks
    )
    
    print("Context used:")
    print(context)
    print("\nGenerated answer:")
    print(answer)