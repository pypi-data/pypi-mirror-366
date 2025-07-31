---
layout: default
title: "Node"
parent: "Fundamentals"
nav_order: 1
---

# Node

A **Node** is the fundamental building block of KayGraph. Each Node has a 3-step lifecycle `prep->exec->post` with comprehensive logging, error handling, and extensibility features:

<div align="center">

</div>

## Core Lifecycle

1. **`prep(shared)`**
   - **Read and preprocess data** from `shared` store.
   - Examples: *query DB, read files, or serialize data into a string*.
   - Return `prep_res`, which is used by `exec()` and `post()`.

2. **`exec(prep_res)`**
   - **Execute compute logic**, with automatic retries and error handling.
   - Examples: *(mostly) LLM calls, remote APIs, tool use*.
   - ⚠️ This shall be only for compute and **NOT** access `shared`.
   - ⚠️ If retries enabled, ensure idempotent implementation.
   - Return `exec_res`, which is passed to `post()`.

3. **`post(shared, prep_res, exec_res)`**
   - **Postprocess and write data** back to `shared`.
   - Examples: *update DB, change states, log results*.
   - **Decide the next action** by returning a *string* (`action = "default"` if *None*).

> **Why 3 steps?** To enforce the principle of *separation of concerns*. Data storage and data processing are operated separately.
>
> All steps are *optional*. E.g., you can only implement `prep` and `post` if you just need to process data.
{: .note }

## Node Identification and Context

Every node in KayGraph has built-in identification and execution context tracking:

```python
class MyNode(Node):
    def __init__(self):
        super().__init__(node_id="my_unique_node")  # Custom node ID

    def prep(self, shared):
        # Access execution context
        start_time = self.get_context("start_time")
        self.set_context("custom_data", "some_value")
        return shared["data"]
```

- **Node IDs**: Automatically generated or custom-specified for better debugging
- **Execution Context**: Store and retrieve context data during node execution
- **Automatic Logging**: Every node logs its execution with timing and parameters

## Built-in Logging System

KayGraph provides comprehensive logging out of the box:

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class MyNode(Node):
    def exec(self, data):
        self.logger.info("Processing data...")  # Automatic logger available
        result = process_data(data)
        self.logger.debug(f"Result: {result}")
        return result
```

**Sample Log Output:**
```
2024-01-01 10:00:00 - MyNode - INFO - Node my_unique_node: Starting execution with params: {'key': 'value'}
2024-01-01 10:00:01 - MyNode - INFO - Processing data...
2024-01-01 10:00:02 - MyNode - INFO - Node my_unique_node: Completed in 2.150s with action: 'default'
```

## Execution Hooks

KayGraph provides hooks for extending node behavior without modifying core logic:

```python
class EnhancedNode(Node):
    def before_prep(self, shared):
        """Called before prep() - setup preprocessing"""
        self.logger.info("Preparing resources...")
        self.set_context("prep_start", time.time())

    def after_exec(self, shared, prep_res, exec_res):
        """Called after exec() but before post() - custom processing"""
        self.logger.info(f"Execution completed with result length: {len(str(exec_res))}")

    def on_error(self, shared, error):
        """Called when execution fails - custom error handling"""
        self.logger.error(f"Node failed with error: {error}")
        # Return True to suppress the error, False to re-raise
        if isinstance(error, TemporaryError):
            return True  # Suppress temporary errors
        return False  # Re-raise critical errors
```

## Parameter Validation

KayGraph includes automatic parameter validation:

```python
class ValidatedNode(Node):
    def exec(self, data):
        # Parameters are automatically validated
        return process(data)

# Usage with validation
node = ValidatedNode()
node.set_params({"timeout": 30, "retries": 3})  # Validates dict type
```

## Context Manager Support

Nodes support context managers for automatic resource management:

```python
class ResourceNode(Node):
    def setup_resources(self):
        """Called when entering context manager"""
        self.connection = connect_to_database()
        self.logger.info("Database connection established")

    def cleanup_resources(self):
        """Called when exiting context manager"""
        if hasattr(self, 'connection'):
            self.connection.close()
            self.logger.info("Database connection closed")

# Usage
with ResourceNode() as node:
    result = node.run(shared)  # Resources automatically managed
```

## Fault Tolerance & Retries

Enhanced retry system with better error reporting:

```python
# Configure retries when creating the node
my_node = SummarizeFile(max_retries=3, wait=10, node_id="summarizer")
```

**Parameters:**
- `max_retries` (int): Max times to run `exec()`. Default is `1` (**no** retry).
- `wait` (int): Time to wait (in **seconds**) before next retry. Default is `0`.
- `node_id` (str): Custom identifier for better debugging.

**Enhanced Error Handling:**
```python
class RobustNode(Node):
    def exec(self, prep_res):
        print(f"Attempt {self.cur_retry + 1}/{self.max_retries}")
        # Your logic here
        if random.random() < 0.7:  # 70% failure rate for demo
            raise Exception("Simulated failure")
        return "Success!"

    def exec_fallback(self, prep_res, exc):
        """Enhanced fallback with detailed error info"""
        self.logger.error(f"All retries failed. Last error: {exc}")
        return f"Fallback result after {self.cur_retry + 1} attempts"
```

## Specialized Node Types

### ValidatedNode

For input/output validation:

```python
from kaygraph import ValidatedNode

class DataProcessor(ValidatedNode):
    def validate_input(self, prep_res):
        """Validate input before exec()"""
        if not isinstance(prep_res, dict):
            raise ValueError("Input must be a dictionary")
        if 'required_field' not in prep_res:
            raise ValueError("Missing required field")
        return prep_res

    def validate_output(self, exec_res):
        """Validate output after exec()"""
        if not exec_res or len(exec_res) < 10:
            raise ValueError("Output too short")
        return exec_res

    def exec(self, validated_input):
        # Process validated input
        return f"Processed: {validated_input['required_field']}"
```

### MetricsNode

For performance monitoring:

```python
from kaygraph import MetricsNode

class MonitoredNode(MetricsNode):
    def __init__(self):
        super().__init__(collect_metrics=True, node_id="monitored_task")

    def exec(self, data):
        # Your processing logic
        return process_data(data)

# Usage and metrics retrieval
node = MonitoredNode()
for i in range(10):
    node.run(shared)

# Get comprehensive statistics
stats = node.get_stats()
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Avg execution time: {stats['avg_execution_time']:.3f}s")
print(f"Total retries: {stats['total_retries']}")
```

**Sample Metrics Output:**
```python
{
    'total_executions': 10,
    'success_rate': 0.8,
    'avg_execution_time': 1.245,
    'min_execution_time': 0.892,
    'max_execution_time': 2.103,
    'total_retries': 3
}
```

## Complete Example: Production-Ready Node

```python
import logging
from kaygraph import ValidatedNode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ProductionSummarizer(ValidatedNode):
    def __init__(self):
        super().__init__(
            max_retries=3,
            wait=2,
            node_id="production_summarizer"
        )

    def setup_resources(self):
        """Setup resources when using context manager"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.logger.info("OpenAI client initialized")

    def cleanup_resources(self):
        """Cleanup resources"""
        if hasattr(self, 'client'):
            del self.client
            self.logger.info("OpenAI client cleaned up")

    def before_prep(self, shared):
        """Pre-processing hook"""
        self.set_context("processing_start", time.time())

    def validate_input(self, text):
        """Validate input text"""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        if len(text.strip()) < 50:
            raise ValueError("Text too short for meaningful summary")
        return text.strip()

    def prep(self, shared):
        """Extract text to summarize"""
        return shared.get("document_text", "")

    def exec(self, validated_text):
        """Call LLM with error handling"""
        prompt = f"Summarize this text in 2-3 sentences: {validated_text}"

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3
        )

        return response.choices[0].message.content

    def validate_output(self, summary):
        """Validate summary quality"""
        if not summary or len(summary.strip()) < 20:
            raise ValueError("Summary too short")
        return summary.strip()

    def exec_fallback(self, prep_res, exc):
        """Provide fallback summary"""
        self.logger.error(f"Summarization failed: {exc}")
        return "Unable to generate summary due to processing error."

    def after_exec(self, shared, prep_res, exec_res):
        """Post-execution processing"""
        processing_time = time.time() - self.get_context("processing_start", 0)
        self.logger.info(f"Summary generated in {processing_time:.2f}s")

    def post(self, shared, prep_res, exec_res):
        """Store results"""
        shared["summary"] = exec_res
        shared["summary_metadata"] = {
            "length": len(exec_res),
            "node_id": self.node_id,
            "retries_used": self.cur_retry
        }

    def on_error(self, shared, error):
        """Custom error handling"""
        self.logger.error(f"Critical error in {self.node_id}: {error}")
        shared["error_info"] = {
            "error": str(error),
            "node_id": self.node_id,
            "retry_count": self.cur_retry
        }
        return False  # Don't suppress the error

# Usage
shared = {"document_text": "Long document text here..."}

# With context manager for automatic resource management
with ProductionSummarizer() as summarizer:
    result = summarizer.run(shared)

print(f"Summary: {shared['summary']}")
print(f"Metadata: {shared['summary_metadata']}")
```

This production-ready example demonstrates all KayGraph node features:
- Custom node IDs and logging
- Parameter and input/output validation
- Execution hooks for extensibility
- Context manager support for resource management
- Comprehensive error handling with fallbacks
- Execution context tracking
- Built-in retry mechanisms with exponential backoff

## Best Practices

1. **Always set node_id** for better debugging and monitoring
2. **Use ValidatedNode** for production systems requiring data validation
3. **Implement proper error handling** with meaningful fallbacks
4. **Use context managers** for automatic resource cleanup
5. **Configure logging early** in your application
6. **Monitor performance** with MetricsNode for optimization insights
7. **Implement hooks** for cross-cutting concerns like authentication or caching
