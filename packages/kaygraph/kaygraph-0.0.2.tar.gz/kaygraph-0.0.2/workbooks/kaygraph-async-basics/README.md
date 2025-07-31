# KayGraph Async Basics

This tutorial introduces async programming in KayGraph, perfect for beginners who want to understand how to build efficient, non-blocking workflows. Learn the fundamentals of AsyncNode and AsyncGraph step by step.

## Why Async?

Async programming allows your workflow to:
- **Handle I/O efficiently**: Don't block while waiting for APIs, databases, or files
- **Process concurrently**: Run multiple operations at the same time
- **Scale better**: Handle more requests with fewer resources
- **Stay responsive**: Keep your application responsive during long operations

## Tutorial Structure

### 1. 📚 Basic Concepts (`01_basic_async.py`)
- Understanding async vs sync
- Your first AsyncNode
- Using `await` properly
- Common pitfalls and solutions

### 2. 🔄 Async Workflows (`02_async_workflow.py`)
- Building AsyncGraph
- Connecting async and sync nodes
- Error handling in async context
- Execution flow visualization

### 3. ⚡ Parallel Operations (`03_parallel_tasks.py`)
- AsyncBatchNode for concurrent processing
- AsyncParallelBatchNode for maximum speed
- Managing concurrent limits
- Monitoring parallel execution

### 4. 🌐 Real-World Example (`04_web_scraper.py`)
- Async web scraping workflow
- Rate limiting and retries
- Progress tracking
- Result aggregation

### 5. 🎯 Best Practices (`05_best_practices.py`)
- When to use async vs sync
- Resource management
- Testing async workflows
- Performance optimization

## Quick Start

### Your First Async Node

```python
from kaygraph import AsyncNode

class FetchDataNode(AsyncNode):
    async def exec_async(self, url):
        # Simulate async API call
        import asyncio
        await asyncio.sleep(1)  # Non-blocking wait
        return f"Data from {url}"
```

### Compare with Sync Version

```python
from kaygraph import Node
import time

class FetchDataNodeSync(Node):
    def exec(self, url):
        time.sleep(1)  # Blocks entire thread!
        return f"Data from {url}"
```

## Running the Examples

```bash
# Run basic async example
python 01_basic_async.py

# Run complete workflow
python 02_async_workflow.py

# See parallel processing in action
python 03_parallel_tasks.py

# Run real-world web scraper
python 04_web_scraper.py

# Learn best practices
python 05_best_practices.py
```

## Key Concepts

### AsyncNode Lifecycle

```
prep() → prep_async() → exec_async() → post_async() → post()
         ~~~~~~~~~~~~   ~~~~~~~~~~~~   ~~~~~~~~~~~~
         (optional)     (required)     (optional)
```

### Async vs Sync Nodes

| Feature | Sync Node | Async Node |
|---------|-----------|------------|
| Blocks thread | Yes | No |
| Good for | CPU tasks | I/O tasks |
| Concurrency | No | Yes |
| Complexity | Simple | Moderate |

### When to Use Async

✅ **Use Async for:**
- API calls
- Database queries
- File I/O
- Network requests
- Waiting for external services

❌ **Use Sync for:**
- CPU-intensive calculations
- Simple data transformations
- Quick operations
- When simplicity matters most

## Common Patterns

### 1. Async API Calls
```python
async def exec_async(self, query):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/{query}") as resp:
            return await resp.json()
```

### 2. Concurrent Database Queries
```python
async def exec_async(self, queries):
    tasks = [self.query_db(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return results
```

### 3. Rate-Limited Operations
```python
async def exec_async(self, items):
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent
    async def process_with_limit(item):
        async with semaphore:
            return await self.process_item(item)
    
    tasks = [process_with_limit(item) for item in items]
    return await asyncio.gather(*tasks)
```

## Debugging Tips

1. **Use proper logging**: Async execution order can be surprising
2. **Visualize execution**: Use the visualization tools to see flow
3. **Handle exceptions**: Async exceptions need special care
4. **Test thoroughly**: Async bugs can be intermittent

## Next Steps

After completing this tutorial, explore:
- Advanced async patterns in other examples
- AsyncGraph with mixed node types
- Production async workflows
- Performance optimization techniques