"""
Embeddings tool integration example using KayGraph.

Demonstrates text embedding generation and similarity search
for semantic text analysis workflows.
"""

import json
import logging
from typing import List, Dict, Any
from kaygraph import Node, Graph, BatchNode
from utils.embeddings import EmbeddingGenerator, EmbeddingIndex, cosine_similarity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LoadDocumentsNode(Node):
    """Load documents for embedding."""
    
    def prep(self, shared):
        """Get document source."""
        return shared.get("document_source", "sample")
    
    def exec(self, source):
        """Load documents based on source."""
        if source == "sample":
            # Sample documents for demonstration
            documents = [
                {
                    "id": "doc1",
                    "title": "Introduction to Machine Learning",
                    "content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
                    "category": "AI/ML"
                },
                {
                    "id": "doc2", 
                    "title": "Python Programming Guide",
                    "content": "Python is a high-level programming language known for its simplicity and readability. It's widely used in data science, web development, and automation.",
                    "category": "Programming"
                },
                {
                    "id": "doc3",
                    "title": "Deep Learning Fundamentals",
                    "content": "Deep learning uses neural networks with multiple layers to progressively extract higher-level features from raw input data.",
                    "category": "AI/ML"
                },
                {
                    "id": "doc4",
                    "title": "Web Development with Python",
                    "content": "Python offers powerful frameworks like Django and Flask for building scalable web applications with clean, maintainable code.",
                    "category": "Programming"
                },
                {
                    "id": "doc5",
                    "title": "Natural Language Processing",
                    "content": "NLP combines computational linguistics with machine learning to help computers understand, interpret, and generate human language.",
                    "category": "AI/ML"
                },
                {
                    "id": "doc6",
                    "title": "Data Structures and Algorithms",
                    "content": "Understanding data structures and algorithms is crucial for writing efficient code and solving complex programming problems.",
                    "category": "Programming"
                },
                {
                    "id": "doc7",
                    "title": "Computer Vision Applications",
                    "content": "Computer vision enables machines to interpret and understand visual information from the world, with applications in autonomous vehicles and medical imaging.",
                    "category": "AI/ML"
                },
                {
                    "id": "doc8",
                    "title": "Cloud Computing Basics",
                    "content": "Cloud computing provides on-demand access to computing resources over the internet, enabling scalable and flexible IT infrastructure.",
                    "category": "Infrastructure"
                }
            ]
        elif source == "file":
            # Load from file
            file_path = shared.get("file_path", "documents.json")
            with open(file_path, 'r') as f:
                documents = json.load(f)
        else:
            documents = []
        
        self.logger.info(f"Loaded {len(documents)} documents")
        return documents
    
    def post(self, shared, prep_res, exec_res):
        """Store documents."""
        shared["documents"] = exec_res
        
        print(f"\n📚 Loaded {len(exec_res)} documents:")
        for doc in exec_res[:5]:  # Show first 5
            print(f"  - [{doc['id']}] {doc['title']} ({doc['category']})")
        if len(exec_res) > 5:
            print(f"  ... and {len(exec_res) - 5} more")
        
        return "default"


class GenerateEmbeddingsNode(Node):
    """Generate embeddings for documents."""
    
    def __init__(self, embedding_method: str = "mock", dimension: int = 384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embedding_method = embedding_method
        self.dimension = dimension
    
    def prep(self, shared):
        """Get documents to embed."""
        return shared.get("documents", [])
    
    def exec(self, documents):
        """Generate embeddings for all documents."""
        if not documents:
            return {"embeddings": [], "generator": None}
        
        # Initialize generator
        generator = EmbeddingGenerator(
            method=self.embedding_method,
            dimension=self.dimension
        )
        
        # Prepare texts for embedding
        texts = []
        for doc in documents:
            # Combine title and content for richer embeddings
            text = f"{doc['title']}. {doc['content']}"
            texts.append(text)
        
        self.logger.info(f"Generating {self.embedding_method} embeddings for {len(texts)} documents")
        
        # Generate embeddings
        embeddings = generator.embed_batch(texts)
        
        # Calculate statistics
        stats = {
            "method": self.embedding_method,
            "dimension": self.dimension,
            "num_documents": len(documents),
            "avg_magnitude": sum(
                sum(x*x for x in emb)**0.5 for emb in embeddings
            ) / len(embeddings)
        }
        
        return {
            "embeddings": embeddings,
            "generator": generator,
            "statistics": stats
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store embeddings."""
        shared["embeddings"] = exec_res["embeddings"]
        shared["embedding_generator"] = exec_res["generator"]
        shared["embedding_stats"] = exec_res["statistics"]
        
        stats = exec_res["statistics"]
        print(f"\n🔢 Generated Embeddings:")
        print(f"  - Method: {stats['method']}")
        print(f"  - Dimension: {stats['dimension']}")
        print(f"  - Documents: {stats['num_documents']}")
        print(f"  - Avg magnitude: {stats['avg_magnitude']:.3f}")
        
        return "default"


class BuildIndexNode(Node):
    """Build searchable index from embeddings."""
    
    def prep(self, shared):
        """Get data for index."""
        return {
            "documents": shared.get("documents", []),
            "embeddings": shared.get("embeddings", []),
            "generator": shared.get("embedding_generator")
        }
    
    def exec(self, data):
        """Build the index."""
        if not data["documents"] or not data["embeddings"]:
            return {"index": None, "error": "No data to index"}
        
        # Create index
        index = EmbeddingIndex(data["generator"])
        
        # Add documents with metadata
        for i, doc in enumerate(data["documents"]):
            text = f"{doc['title']}. {doc['content']}"
            # Store pre-computed embedding
            index.texts.append(text)
            index.embeddings.append(data["embeddings"][i])
            index.metadata.append({
                "id": doc["id"],
                "title": doc["title"],
                "category": doc["category"]
            })
        
        self.logger.info(f"Built index with {len(index.texts)} documents")
        
        return {"index": index, "size": len(index.texts)}
    
    def post(self, shared, prep_res, exec_res):
        """Store index."""
        shared["embedding_index"] = exec_res["index"]
        
        print(f"\n🗂️  Built searchable index with {exec_res['size']} documents")
        
        return "default"


class SearchDocumentsBatchNode(BatchNode):
    """Search for similar documents using embeddings."""
    
    def prep(self, shared):
        """Get queries and index."""
        queries = shared.get("search_queries", [])
        index = shared.get("embedding_index")
        
        if not queries:
            # Default queries
            queries = [
                "How to build neural networks?",
                "Python web development frameworks",
                "Machine learning algorithms",
                "Cloud infrastructure setup"
            ]
        
        # Pair each query with the index
        return [(query, index) for query in queries]
    
    def exec(self, item):
        """Search for a single query."""
        query, index = item
        
        if not index:
            return {
                "query": query,
                "results": [],
                "error": "No index available"
            }
        
        # Search
        results = index.search(query, top_k=3)
        
        return {
            "query": query,
            "results": results,
            "num_results": len(results)
        }
    
    def post(self, shared, prep_res, exec_res):
        """Display search results."""
        shared["search_results"] = exec_res
        
        print(f"\n🔍 Search Results:")
        print("=" * 60)
        
        for result in exec_res:
            print(f"\nQuery: '{result['query']}'")
            
            if result.get("error"):
                print(f"  Error: {result['error']}")
                continue
            
            print(f"  Found {result['num_results']} similar documents:")
            
            for i, doc in enumerate(result['results'], 1):
                print(f"  {i}. [{doc['metadata']['id']}] {doc['metadata']['title']}")
                print(f"     Category: {doc['metadata']['category']}")
                print(f"     Similarity: {doc['score']:.3f}")
        
        return "default"


class AnalyzeEmbeddingsNode(Node):
    """Analyze embedding space and relationships."""
    
    def prep(self, shared):
        """Get embeddings and documents."""
        return {
            "embeddings": shared.get("embeddings", []),
            "documents": shared.get("documents", [])
        }
    
    def exec(self, data):
        """Analyze embedding relationships."""
        embeddings = data["embeddings"]
        documents = data["documents"]
        
        if not embeddings:
            return {"analysis": None}
        
        analysis = {
            "num_embeddings": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0,
            "category_centroids": {},
            "pairwise_similarities": [],
            "category_cohesion": {}
        }
        
        # Group by category
        category_embeddings = {}
        for i, doc in enumerate(documents):
            category = doc["category"]
            if category not in category_embeddings:
                category_embeddings[category] = []
            category_embeddings[category].append(embeddings[i])
        
        # Calculate category centroids and cohesion
        for category, cat_embeddings in category_embeddings.items():
            # Centroid (average embedding)
            centroid = [
                sum(emb[j] for emb in cat_embeddings) / len(cat_embeddings)
                for j in range(len(cat_embeddings[0]))
            ]
            analysis["category_centroids"][category] = centroid
            
            # Cohesion (average pairwise similarity within category)
            if len(cat_embeddings) > 1:
                similarities = []
                for i in range(len(cat_embeddings)):
                    for j in range(i + 1, len(cat_embeddings)):
                        sim = cosine_similarity(cat_embeddings[i], cat_embeddings[j])
                        similarities.append(sim)
                
                analysis["category_cohesion"][category] = {
                    "avg_similarity": sum(similarities) / len(similarities),
                    "min_similarity": min(similarities),
                    "max_similarity": max(similarities)
                }
        
        # Inter-category similarities
        categories = list(category_embeddings.keys())
        for i in range(len(categories)):
            for j in range(i + 1, len(categories)):
                cat1, cat2 = categories[i], categories[j]
                centroid1 = analysis["category_centroids"][cat1]
                centroid2 = analysis["category_centroids"][cat2]
                
                similarity = cosine_similarity(centroid1, centroid2)
                analysis["pairwise_similarities"].append({
                    "category1": cat1,
                    "category2": cat2,
                    "similarity": similarity
                })
        
        return {"analysis": analysis}
    
    def post(self, shared, prep_res, exec_res):
        """Display analysis results."""
        analysis = exec_res["analysis"]
        
        if not analysis:
            print("\n❌ No embeddings to analyze")
            return None
        
        print(f"\n📊 Embedding Space Analysis:")
        print("=" * 60)
        
        print(f"\nOverview:")
        print(f"  - Total embeddings: {analysis['num_embeddings']}")
        print(f"  - Embedding dimension: {analysis['dimension']}")
        print(f"  - Categories: {len(analysis['category_centroids'])}")
        
        print(f"\nCategory Cohesion (how similar documents within category are):")
        for category, cohesion in analysis["category_cohesion"].items():
            print(f"  - {category}:")
            print(f"    • Average similarity: {cohesion['avg_similarity']:.3f}")
            print(f"    • Range: [{cohesion['min_similarity']:.3f}, {cohesion['max_similarity']:.3f}]")
        
        print(f"\nInter-category Similarities:")
        for pair in sorted(analysis["pairwise_similarities"], 
                         key=lambda x: x["similarity"], reverse=True):
            print(f"  - {pair['category1']} ↔ {pair['category2']}: {pair['similarity']:.3f}")
        
        shared["embedding_analysis"] = analysis
        return None


def create_embedding_graph():
    """Create the embedding analysis graph."""
    # Create nodes
    load_docs = LoadDocumentsNode(node_id="load_docs")
    gen_embeddings = GenerateEmbeddingsNode(
        embedding_method="mock",
        dimension=384,
        node_id="gen_embeddings"
    )
    build_index = BuildIndexNode(node_id="build_index")
    search_docs = SearchDocumentsBatchNode(node_id="search_docs")
    analyze_embeddings = AnalyzeEmbeddingsNode(node_id="analyze_embeddings")
    
    # Connect nodes
    load_docs >> gen_embeddings >> build_index >> search_docs >> analyze_embeddings
    
    return Graph(start=load_docs)


def main():
    """Run the embeddings tool integration example."""
    print("🧮 KayGraph Embeddings Tool Integration")
    print("=" * 60)
    print("This example demonstrates text embedding generation")
    print("and semantic similarity search.\n")
    
    # Create graph
    graph = create_embedding_graph()
    
    # Shared context with search queries
    shared = {
        "document_source": "sample",
        "search_queries": [
            "How to build neural networks with Python?",
            "Web development frameworks and tools",
            "Understanding machine learning algorithms",
            "Cloud infrastructure and deployment",
            "Natural language processing techniques",
            "Programming best practices"
        ]
    }
    
    # Run the graph
    graph.run(shared)
    
    # Save index for reuse
    if shared.get("embedding_index"):
        index_path = "document_embeddings.json"
        shared["embedding_index"].save(index_path)
        print(f"\n💾 Saved embedding index to: {index_path}")
    
    print("\n✨ Embeddings example complete!")


if __name__ == "__main__":
    main()