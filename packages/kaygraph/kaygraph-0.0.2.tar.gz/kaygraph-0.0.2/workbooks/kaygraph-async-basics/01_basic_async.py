#!/usr/bin/env python3
"""
Lesson 1: Basic Async Concepts in KayGraph
Learn the fundamentals of async programming with AsyncNode.
"""

import asyncio
import time
import logging
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode

# Setup logging to see execution order
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Example 1: Synchronous Node (Blocking)
class SlowSyncNode(Node):
    """A slow synchronous node that blocks execution."""
    
    def __init__(self, task_name: str, duration: float = 2.0):
        super().__init__(node_id=f"sync_{task_name}")
        self.task_name = task_name
        self.duration = duration
    
    def exec(self, data):
        """This blocks the entire thread!"""
        logger.info(f"🚫 {self.task_name} starting (blocking for {self.duration}s)...")
        time.sleep(self.duration)  # Blocks!
        logger.info(f"✅ {self.task_name} completed")
        return f"Result from {self.task_name}"


# Example 2: Asynchronous Node (Non-blocking)
class FastAsyncNode(AsyncNode):
    """An async node that doesn't block execution."""
    
    def __init__(self, task_name: str, duration: float = 2.0):
        super().__init__(node_id=f"async_{task_name}")
        self.task_name = task_name
        self.duration = duration
    
    async def exec_async(self, data):
        """This doesn't block - other tasks can run!"""
        logger.info(f"⚡ {self.task_name} starting (async wait {self.duration}s)...")
        await asyncio.sleep(self.duration)  # Non-blocking!
        logger.info(f"✅ {self.task_name} completed")
        return f"Result from {self.task_name}"


# Example 3: Real-world Async Node
class WebFetchNode(AsyncNode):
    """Fetch data from web API asynchronously."""
    
    def __init__(self, api_name: str):
        super().__init__(node_id=f"fetch_{api_name}")
        self.api_name = api_name
    
    async def prep_async(self, shared):
        """Async prep - prepare the request."""
        logger.info(f"📋 Preparing request to {self.api_name}")
        # Could do async operations here too
        return {
            "url": f"https://api.example.com/{self.api_name}",
            "timeout": 5
        }
    
    async def exec_async(self, request_data):
        """Fetch data from API (simulated)."""
        logger.info(f"🌐 Fetching from {request_data['url']}...")
        
        # Simulate API call
        await asyncio.sleep(1.5)
        
        # In real code:
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(request_data['url']) as response:
        #         return await response.json()
        
        return {
            "status": "success",
            "data": f"Mock data from {self.api_name}",
            "timestamp": time.time()
        }
    
    async def post_async(self, shared, prep_res, exec_res):
        """Async post-processing."""
        logger.info(f"💾 Storing results from {self.api_name}")
        shared[f"{self.api_name}_data"] = exec_res
        return None


# Example 4: Async Node with Error Handling
class RobustAsyncNode(AsyncNode):
    """Async node with proper error handling."""
    
    def __init__(self):
        super().__init__(node_id="robust_async", max_retries=3)
    
    async def exec_async(self, data):
        """Execute with potential failures."""
        attempt = self.cur_retry + 1
        logger.info(f"🔄 Attempt {attempt}/{self.max_retries}")
        
        # Simulate 50% failure rate
        import random
        if random.random() < 0.5:
            raise Exception("Simulated API failure")
        
        await asyncio.sleep(0.5)
        return "Success!"
    
    async def exec_fallback_async(self, prep_res, exc):
        """Async fallback when all retries fail."""
        logger.error(f"❌ All retries failed: {exc}")
        return "Fallback result"


async def demonstrate_sync_vs_async():
    """Show the difference between sync and async execution."""
    print("\n" + "="*60)
    print("DEMO 1: Sync vs Async Execution")
    print("="*60)
    
    # Test synchronous execution
    print("\n1️⃣ Running 3 SYNC nodes sequentially...")
    start_time = time.time()
    
    sync_nodes = [
        SlowSyncNode("Task_A", 1.0),
        SlowSyncNode("Task_B", 1.0),
        SlowSyncNode("Task_C", 1.0)
    ]
    
    for node in sync_nodes:
        node.run({})
    
    sync_duration = time.time() - start_time
    print(f"⏱️  Sync execution took: {sync_duration:.2f}s")
    
    # Test asynchronous execution
    print("\n2️⃣ Running 3 ASYNC nodes concurrently...")
    start_time = time.time()
    
    async_nodes = [
        FastAsyncNode("Task_X", 1.0),
        FastAsyncNode("Task_Y", 1.0),
        FastAsyncNode("Task_Z", 1.0)
    ]
    
    # Run all async nodes concurrently
    tasks = [node.run_async({}) for node in async_nodes]
    await asyncio.gather(*tasks)
    
    async_duration = time.time() - start_time
    print(f"⏱️  Async execution took: {async_duration:.2f}s")
    
    print(f"\n🚀 Speedup: {sync_duration/async_duration:.1f}x faster!")


async def demonstrate_real_world_async():
    """Show real-world async patterns."""
    print("\n" + "="*60)
    print("DEMO 2: Real-world Async Pattern")
    print("="*60)
    
    # Create shared context
    shared = {}
    
    # Simulate fetching from multiple APIs
    api_nodes = [
        WebFetchNode("users"),
        WebFetchNode("products"),
        WebFetchNode("analytics")
    ]
    
    print("\n📡 Fetching from 3 APIs concurrently...")
    start_time = time.time()
    
    # Run all API calls concurrently
    tasks = [node.run_async(shared) for node in api_nodes]
    await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    print(f"\n⏱️  All APIs fetched in: {duration:.2f}s")
    print(f"📊 Data collected: {list(shared.keys())}")


async def demonstrate_error_handling():
    """Show async error handling."""
    print("\n" + "="*60)
    print("DEMO 3: Async Error Handling")
    print("="*60)
    
    robust_node = RobustAsyncNode()
    
    print("\n🛡️  Running node with automatic retries...")
    result = await robust_node.run_async({})
    print(f"📤 Final result: {result}")


def main():
    """Run all demonstrations."""
    print("\n🎓 KayGraph Async Basics - Lesson 1")
    print("Understanding Async vs Sync Execution")
    
    # Create event loop and run demos
    asyncio.run(demonstrate_sync_vs_async())
    asyncio.run(demonstrate_real_world_async())
    asyncio.run(demonstrate_error_handling())
    
    print("\n" + "="*60)
    print("💡 Key Takeaways:")
    print("="*60)
    print("1. Async nodes don't block - multiple can run concurrently")
    print("2. Use async for I/O operations (API calls, DB queries)")
    print("3. Async nodes can have async prep/post methods too")
    print("4. Error handling works the same with async")
    print("5. Mix async and sync nodes in the same graph")
    print("\n✅ Lesson 1 completed! Next: Building async workflows")


if __name__ == "__main__":
    main()