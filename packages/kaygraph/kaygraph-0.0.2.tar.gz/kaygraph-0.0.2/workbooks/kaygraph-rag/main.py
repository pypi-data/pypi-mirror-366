"""
RAG (Retrieval-Augmented Generation) example using KayGraph.

This example demonstrates:
- Document indexing pipeline
- Semantic search with embeddings
- Context-aware answer generation
"""

import sys
import os
import logging
from graphs import create_indexing_graph, create_retrieval_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def index_documents(doc_directory: str = "data/", index_path: str = "data/rag_index.json"):
    """Run the indexing pipeline."""
    print(f"\n📚 Indexing documents from: {doc_directory}")
    print("=" * 60)
    
    # Create indexing graph
    graph = create_indexing_graph(
        chunk_size=500,
        chunk_overlap=50,
        batch_size=32,
        index_path=index_path
    )
    
    # Initialize shared state
    shared = {"doc_directory": doc_directory}
    
    try:
        # Run indexing
        final_action = graph.run(shared)
        
        # Display results
        if shared.get("doc_count", 0) == 0:
            print("❌ No documents found to index!")
            return False
        
        print(f"\n✅ Indexing complete!")
        print(f"   - Documents indexed: {shared.get('doc_count', 0)}")
        print(f"   - Total chunks: {shared.get('chunk_count', 0)}")
        print(f"   - Index saved to: {index_path}")
        
        # Show index stats
        if "index_stats" in shared:
            stats = shared["index_stats"]
            print(f"\n📊 Index Statistics:")
            print(f"   - Vector dimension: {stats['dimension']}")
            print(f"   - Memory usage: {stats['memory_usage_mb']:.2f} MB")
            if "sources" in stats:
                print(f"   - Sources indexed:")
                for source, count in stats["sources"].items():
                    print(f"     • {source}: {count} chunks")
        
        return True
        
    except Exception as e:
        logging.error(f"Error during indexing: {e}")
        print(f"\n❌ Indexing failed: {e}")
        return False


def query_rag(query: str, index_path: str = "data/rag_index.json"):
    """Run the retrieval pipeline."""
    print(f"\n🔍 Processing query: {query}")
    print("=" * 60)
    
    # Create retrieval graph
    graph = create_retrieval_graph(
        top_k=5,
        similarity_threshold=0.3,
        max_context_length=3000,
        index_path=index_path
    )
    
    # Initialize shared state
    shared = {
        "query": query,
        "index_path": index_path
    }
    
    try:
        # Run retrieval
        final_action = graph.run(shared)
        
        # Display results
        print(f"\n📋 Retrieved {shared.get('num_results', 0)} relevant chunks")
        
        if shared.get("sources_used"):
            print(f"\n📚 Sources used:")
            for source in shared["sources_used"]:
                print(f"   • {source}")
        
        print(f"\n💬 Answer:")
        print("-" * 40)
        print(shared.get("answer", "No answer generated"))
        print("-" * 40)
        
        # Optionally show context
        if "--show-context" in sys.argv and shared.get("context"):
            print(f"\n📄 Context used:")
            print("-" * 40)
            print(shared["context"][:500] + "..." if len(shared["context"]) > 500 else shared["context"])
            print("-" * 40)
        
        return True
        
    except Exception as e:
        logging.error(f"Error during retrieval: {e}")
        print(f"\n❌ Query failed: {e}")
        return False


def main():
    """Run the RAG example."""
    if len(sys.argv) < 2:
        print("KayGraph RAG Example")
        print("-" * 30)
        print("\nUsage:")
        print("  Index documents:  python main.py index [doc_directory]")
        print("  Query RAG:       python main.py query \"your question\"")
        print("  Show context:    python main.py query \"your question\" --show-context")
        print("\nExamples:")
        print('  python main.py index data/')
        print('  python main.py query "What is KayGraph?"')
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "index":
        # Index documents
        doc_dir = sys.argv[2] if len(sys.argv) > 2 else "data/"
        
        # Create data directory if it doesn't exist
        os.makedirs(doc_dir, exist_ok=True)
        
        # Create sample documents if directory is empty
        if not os.listdir(doc_dir):
            print(f"Creating sample documents in {doc_dir}...")
            
            sample_docs = {
                "kaygraph_intro.txt": """KayGraph is an opinionated framework for building context-aware AI applications with production-ready graphs.

The core abstraction is Context Graph + Shared Store, where Nodes handle operations (including LLM calls) and Graphs connect nodes through Actions (labeled edges) to create sophisticated workflows.

Key features include:
- Zero dependencies - only Python standard library
- Production-ready patterns for common AI workflows
- Support for async operations and batch processing
- Modular node-based architecture""",
                
                "kaygraph_nodes.txt": """KayGraph provides several node types:

1. BaseNode - The fundamental building block
2. Node - Standard node with retry and fallback capabilities
3. BatchNode - Processes iterables of items
4. AsyncNode - For asynchronous operations
5. ValidatedNode - Input/output validation
6. MetricsNode - Execution metrics collection

Each node follows a 3-step lifecycle:
- prep(): Read from shared store
- exec(): Execute core logic
- post(): Write results and determine next action""",
                
                "kaygraph_patterns.txt": """Common KayGraph patterns:

1. Agent Pattern - Autonomous decision-making with context
2. RAG Pattern - Retrieval-Augmented Generation with vector search
3. MapReduce Pattern - Distributed processing of large datasets
4. Chain-of-Thought - Step-by-step reasoning for complex problems
5. Multi-Agent - Coordination between multiple specialized agents

These patterns can be combined to create sophisticated AI applications."""
            }
            
            for filename, content in sample_docs.items():
                filepath = os.path.join(doc_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"  Created: {filepath}")
        
        # Run indexing
        success = index_documents(doc_dir)
        return 0 if success else 1
    
    elif command == "query":
        # Query the RAG system
        if len(sys.argv) < 3:
            print("Error: Please provide a query")
            return 1
        
        # Join all remaining args as the query
        query = " ".join(sys.argv[2:]).replace("--show-context", "").strip()
        
        # Check if index exists
        index_path = "data/rag_index.json"
        if not os.path.exists(index_path):
            print(f"\n❌ No index found at {index_path}")
            print("Please run 'python main.py index' first to create the index.")
            return 1
        
        # Run query
        success = query_rag(query, index_path)
        return 0 if success else 1
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'index' or 'query'")
        return 1


if __name__ == "__main__":
    sys.exit(main())