#!/usr/bin/env python3
"""
Lesson 2: Building Async Workflows
Learn how to create AsyncGraphs with mixed node types.
"""

import asyncio
import time
import logging
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, Graph, AsyncGraph

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Sync node for data preparation
class DataPrepNode(Node):
    """Prepare data for processing (sync)."""
    
    def __init__(self):
        super().__init__(node_id="data_prep")
    
    def exec(self, _):
        """Prepare URLs to fetch."""
        logger.info("📋 Preparing data (sync)...")
        return [
            "https://api.example.com/users",
            "https://api.example.com/posts", 
            "https://api.example.com/comments"
        ]
    
    def post(self, shared, prep_res, urls):
        """Store URLs in shared context."""
        shared["urls_to_fetch"] = urls
        shared["fetch_count"] = len(urls)
        return None


# Async node for parallel fetching
class ParallelFetchNode(AsyncNode):
    """Fetch multiple URLs in parallel."""
    
    def __init__(self):
        super().__init__(node_id="parallel_fetch")
    
    async def prep_async(self, shared):
        """Get URLs from shared context."""
        return shared.get("urls_to_fetch", [])
    
    async def exec_async(self, urls):
        """Fetch all URLs concurrently."""
        logger.info(f"🌐 Fetching {len(urls)} URLs in parallel...")
        
        async def fetch_url(url):
            """Simulate fetching a single URL."""
            logger.info(f"  ↗️  Fetching {url}")
            await asyncio.sleep(1.0)  # Simulate network delay
            return {
                "url": url,
                "data": f"Content from {url}",
                "size": len(url) * 100  # Mock size
            }
        
        # Fetch all URLs concurrently
        tasks = [fetch_url(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        logger.info(f"✅ All {len(results)} URLs fetched!")
        return results
    
    async def post_async(self, shared, urls, results):
        """Store results asynchronously."""
        shared["fetch_results"] = results
        total_size = sum(r["size"] for r in results)
        shared["total_size"] = total_size
        logger.info(f"💾 Stored results (total size: {total_size} bytes)")
        return None


# Sync node for processing results
class ProcessResultsNode(Node):
    """Process fetched results (sync)."""
    
    def __init__(self):
        super().__init__(node_id="process_results")
    
    def prep(self, shared):
        """Get fetch results."""
        return shared.get("fetch_results", [])
    
    def exec(self, results):
        """Process the results."""
        logger.info("🔄 Processing results (sync)...")
        
        summary = {
            "total_urls": len(results),
            "total_size": sum(r["size"] for r in results),
            "urls": [r["url"] for r in results]
        }
        
        time.sleep(0.5)  # Simulate processing
        return summary
    
    def post(self, shared, prep_res, summary):
        """Store summary."""
        shared["summary"] = summary
        logger.info(f"📊 Summary: {summary['total_urls']} URLs, {summary['total_size']} bytes")
        return None


# Async node with conditional logic
class ConditionalAsyncNode(AsyncNode):
    """Demonstrate conditional execution in async context."""
    
    def __init__(self):
        super().__init__(node_id="conditional_async")
    
    async def exec_async(self, summary):
        """Check if we need additional processing."""
        if summary["total_urls"] > 2:
            logger.info("🔍 Many URLs detected, performing deep analysis...")
            await asyncio.sleep(1.0)
            return "deep_analysis_needed"
        else:
            logger.info("✨ Standard processing sufficient")
            return "standard"
    
    async def post_async(self, shared, prep_res, result):
        """Determine next action."""
        shared["analysis_type"] = result
        return result  # This determines the next node!


# Final async cleanup node
class CleanupNode(AsyncNode):
    """Async cleanup operations."""
    
    def __init__(self):
        super().__init__(node_id="cleanup")
    
    async def exec_async(self, _):
        """Simulate cleanup."""
        logger.info("🧹 Cleaning up resources...")
        await asyncio.sleep(0.5)
        return "cleaned"


async def build_and_run_workflow():
    """Build and run a complete async workflow."""
    print("\n" + "="*60)
    print("Building Mixed Async/Sync Workflow")
    print("="*60)
    
    # Create nodes
    prep_node = DataPrepNode()
    fetch_node = ParallelFetchNode()
    process_node = ProcessResultsNode()
    conditional_node = ConditionalAsyncNode()
    cleanup_node = CleanupNode()
    
    # Create specialized nodes for different paths
    class DeepAnalysisNode(AsyncNode):
        async def exec_async(self, _):
            logger.info("🔬 Performing deep analysis...")
            await asyncio.sleep(1.5)
            return "deep_analysis_complete"
    
    class StandardAnalysisNode(Node):
        def exec(self, _):
            logger.info("📋 Standard analysis...")
            return "standard_complete"
    
    deep_node = DeepAnalysisNode(node_id="deep_analysis")
    standard_node = StandardAnalysisNode(node_id="standard_analysis")
    
    # Build the graph - note we use AsyncGraph!
    graph = AsyncGraph(start=prep_node)
    
    # Connect nodes
    prep_node >> fetch_node >> process_node >> conditional_node
    
    # Conditional branches
    conditional_node - "deep_analysis_needed" >> deep_node
    conditional_node - "standard" >> standard_node
    
    # Both paths lead to cleanup
    deep_node >> cleanup_node
    standard_node >> cleanup_node
    
    # Visualize the workflow
    print("\n📊 Workflow Structure:")
    print("DataPrep → ParallelFetch → Process → Conditional")
    print("                                         ├─→ DeepAnalysis ─→ Cleanup")
    print("                                         └─→ Standard ─────→ Cleanup")
    
    # Run the workflow
    print("\n🚀 Running workflow...")
    start_time = time.time()
    
    shared_context = {}
    final_action = await graph.run_async(shared_context)
    
    duration = time.time() - start_time
    print(f"\n⏱️  Workflow completed in {duration:.2f}s")
    print(f"📋 Final context keys: {list(shared_context.keys())}")
    

async def demonstrate_error_propagation():
    """Show how errors propagate in async workflows."""
    print("\n" + "="*60)
    print("Error Handling in Async Workflows")
    print("="*60)
    
    class FailingAsyncNode(AsyncNode):
        async def exec_async(self, _):
            logger.info("💥 This node will fail...")
            await asyncio.sleep(0.5)
            raise ValueError("Simulated failure!")
    
    class ErrorHandlerNode(AsyncNode):
        def on_error(self, shared, error):
            logger.error(f"🛡️  Caught error: {error}")
            shared["error_handled"] = True
            return True  # Suppress error
        
        async def exec_async(self, _):
            # This won't run if there's an error
            return "success"
    
    # Build error handling workflow
    failing_node = FailingAsyncNode(node_id="failing")
    handler_node = ErrorHandlerNode(node_id="handler")
    
    graph = AsyncGraph(start=failing_node)
    failing_node >> handler_node
    
    shared = {}
    
    try:
        await graph.run_async(shared)
        print("✅ Workflow completed despite error")
        print(f"🛡️  Error was handled: {shared.get('error_handled', False)}")
    except Exception as e:
        print(f"❌ Unhandled error: {e}")


def main():
    """Run all demonstrations."""
    print("\n🎓 KayGraph Async Basics - Lesson 2")
    print("Building Async Workflows")
    
    # Run demonstrations
    asyncio.run(build_and_run_workflow())
    asyncio.run(demonstrate_error_propagation())
    
    print("\n" + "="*60)
    print("💡 Key Takeaways:")
    print("="*60)
    print("1. Use AsyncGraph when you have ANY async nodes")
    print("2. Mix sync and async nodes freely in AsyncGraph")
    print("3. Conditional logic works the same in async")
    print("4. Error handling is consistent across async/sync")
    print("5. Async workflows can be much faster for I/O")
    print("\n✅ Lesson 2 completed! Next: Parallel batch processing")


if __name__ == "__main__":
    main()