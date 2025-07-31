---
layout: default
title: "Advanced Usage & Vision"
nav_order: 10
---

# Advanced Usage & Future Vision

The recent updates to KayGraph focus on moving beyond a minimalist framework towards a more robust, debuggable, and production-ready system. This guide details the new features and outlines a vision for how you can leverage them to build sophisticated, data-driven LLM applications.

## Part 1: New Features for Robust Development

### 1. Enhanced Type Hinting

To improve code clarity, developer experience, and enable static analysis, KayGraph's core classes now include type hints.

- **What it is**: Method signatures are decorated with types from Python's `typing` module (e.g., `def prep(self, shared: T_Shared) -> T_PrepRes:`).
- **Why it's useful**:
    - **Clarity**: Makes it immediately clear what kind of data each method expects and returns.
    - **IDE Support**: Enables better autocompletion and error-checking in modern IDEs like VSCode or PyCharm.
    - **Maintainability**: Helps prevent common bugs when refactoring or extending your graphs.

### 2. Integrated and Configurable Logging

Every `Node` and `Graph` now has its own built-in logger, using Python's standard `logging` module. This provides insight into the runtime behavior of your application without cluttering your code with print statements.

#### How to Enable and Configure Logging

To see the logs, you must configure the root logger in your application's entry point (e.g., `main.py`).

**Basic Configuration (to console):**

```python
# In your main.py
import logging

logging.basicConfig(
    level=logging.INFO, # Use logging.DEBUG for more detail
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Advanced Configuration (to console and file):**

This setup sends `INFO`-level logs to the console and detailed `DEBUG`-level logs to a file.

```python
# In your main.py
import logging

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) # Capture everything

    # Console Handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # File Handler (DEBUG level)
    file_handler = logging.FileHandler('graph.log', mode='w')
    file_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

setup_logging()
```

#### What Is Logged?

-   **`INFO` Level**: High-level execution graph (node starts/ends, transitions, retries).
-   **`DEBUG` Level**: Detailed data passed between `prep`, `exec`, and `post`.
-   **`WARNING` Level**: Non-critical issues (e.g., execution failures that will be retried).
-   **`ERROR` Level**: Critical failures (e.g., max retries reached).

The logging is **non-blocking** and highly performant for most use cases.

### 3. Synchronous Parallelism: `ParallelBatchNode`

For I/O-bound tasks that are not in an `async` context, you can now use `ParallelBatchNode`.

- **What it is**: A `BatchNode` that uses a `concurrent.futures.ThreadPoolExecutor` to run the `exec()` method for each item in the batch concurrently in separate threads.
- **When to use it**: Ideal for batch-processing tasks that involve network requests or file I/O in a standard synchronous application (e.g., downloading a list of URLs, reading multiple small files).
- **Example**:

```python
from kaygraph import ParallelBatchNode
import requests

class DownloadURLsNode(ParallelBatchNode):
    def prep(self, shared):
        return shared["urls_to_download"] # e.g., ["url1", "url2", ...]

    def exec(self, url):
        # This will run in a separate thread for each URL
        response = requests.get(url)
        return response.text

    def post(self, shared, prep_res, exec_res_list):
        shared["downloaded_content"] = exec_res_list
```

### 4. Production-Grade Data Validation: `ValidatedNode`

For mission-critical applications, input and output validation is essential. `ValidatedNode` provides a clean way to add validation logic without cluttering your core business logic.

```python
from kaygraph import ValidatedNode

class ProductionAPINode(ValidatedNode):
    def __init__(self):
        super().__init__(max_retries=3, wait=1, node_id="api_processor")
    
    def validate_input(self, prep_res):
        """Validate input before processing"""
        if not isinstance(prep_res, dict):
            raise ValueError("Input must be a dictionary")
        
        # Check for required fields
        required_fields = ["user_id", "request_type", "data"]
        for field in required_fields:
            if field not in prep_res:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate user_id format
        if not prep_res["user_id"].startswith("user_"):
            raise ValueError("Invalid user_id format")
        
        return prep_res
    
    def validate_output(self, exec_res):
        """Validate output before returning"""
        if not isinstance(exec_res, dict):
            raise ValueError("Output must be a dictionary")
        
        # Ensure required response fields
        if "status" not in exec_res or "data" not in exec_res:
            raise ValueError("Response missing required fields")
        
        # Validate status values
        if exec_res["status"] not in ["success", "error", "pending"]:
            raise ValueError("Invalid status value")
        
        return exec_res
    
    def prep(self, shared):
        return {
            "user_id": shared.get("user_id"),
            "request_type": shared.get("request_type"),
            "data": shared.get("payload", {})
        }
    
    def exec(self, validated_input):
        # Your core business logic here
        # Input is guaranteed to be valid
        result = process_api_request(validated_input)
        return {
            "status": "success",
            "data": result,
            "processed_at": time.time()
        }
    
    def post(self, shared, prep_res, exec_res):
        # Output is guaranteed to be valid
        shared["api_response"] = exec_res
```

**Benefits of ValidatedNode:**
- **Fail Fast**: Validation errors are caught early, preventing downstream issues
- **Clear Error Messages**: Validation failures provide specific error information
- **Separation of Concerns**: Validation logic is separate from business logic
- **Automatic Retry**: Failed validations don't trigger retries (unlike exec failures)

### 5. Performance Monitoring: `MetricsNode`

For production systems, monitoring performance is crucial. `MetricsNode` provides built-in metrics collection and analysis.

```python
from kaygraph import MetricsNode
import time

class MonitoredLLMNode(MetricsNode):
    def __init__(self):
        super().__init__(
            collect_metrics=True,  # Enable metrics collection
            max_retries=3,
            wait=2,
            node_id="llm_processor"
        )
    
    def prep(self, shared):
        return shared.get("prompt", "")
    
    def exec(self, prompt):
        # Simulate LLM call with potential failures
        if len(prompt) > 1000:
            raise ValueError("Prompt too long")
        
        # Simulate processing time
        time.sleep(0.5 + len(prompt) * 0.001)
        
        return f"Response to: {prompt[:50]}..."
    
    def post(self, shared, prep_res, exec_res):
        shared["llm_response"] = exec_res

# Usage and monitoring
llm_node = MonitoredLLMNode()

# Simulate multiple executions
test_prompts = [
    "Short prompt",
    "Medium length prompt with more content",
    "Very long prompt with lots of content" * 20,  # Will fail validation
    "Another short prompt",
    "Final test prompt"
]

for i, prompt in enumerate(test_prompts):
    shared = {"prompt": prompt}
    try:
        llm_node.run(shared)
        print(f"Run {i+1}: Success")
    except Exception as e:
        print(f"Run {i+1}: Failed - {e}")

# Analyze performance metrics
stats = llm_node.get_stats()
print("\n=== Performance Analysis ===")
print(f"Total executions: {stats['total_executions']}")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Average execution time: {stats['avg_execution_time']:.3f}s")
print(f"Min execution time: {stats['min_execution_time']:.3f}s")
print(f"Max execution time: {stats['max_execution_time']:.3f}s")
print(f"Total retries needed: {stats['total_retries']}")
```

**Sample Output:**
```
Run 1: Success
Run 2: Success
Run 3: Failed - Prompt too long
Run 4: Success
Run 5: Success

=== Performance Analysis ===
Total executions: 5
Success rate: 80.0%
Average execution time: 0.523s
Min execution time: 0.501s
Max execution time: 0.562s
Total retries needed: 0
```

### 6. Combining Advanced Features

Here's a production-ready example that combines all advanced features:

```python
from kaygraph import ValidatedNode, MetricsNode, Graph
import logging
import time

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('production.log')
    ]
)

class ProductionDataProcessor(ValidatedNode, MetricsNode):
    """A production-ready node with validation, metrics, and comprehensive error handling"""
    
    def __init__(self):
        # Initialize both parent classes
        ValidatedNode.__init__(self, max_retries=3, wait=2, node_id="data_processor")
        MetricsNode.__init__(self, collect_metrics=True)
        
    def setup_resources(self):
        """Setup external resources"""
        self.api_client = initialize_api_client()
        self.logger.info("API client initialized")
    
    def cleanup_resources(self):
        """Cleanup external resources"""
        if hasattr(self, 'api_client'):
            self.api_client.close()
            self.logger.info("API client closed")
    
    def validate_input(self, prep_res):
        """Comprehensive input validation"""
        if not isinstance(prep_res, dict):
            raise ValueError("Input must be a dictionary")
        
        required_fields = ["data", "processing_type", "user_id"]
        for field in required_fields:
            if field not in prep_res:
                raise ValueError(f"Missing required field: {field}")
        
        # Type-specific validations
        if not isinstance(prep_res["data"], list):
            raise ValueError("Data must be a list")
        
        if len(prep_res["data"]) > 1000:
            raise ValueError("Data too large (max 1000 items)")
        
        return prep_res
    
    def validate_output(self, exec_res):
        """Ensure output meets quality standards"""
        if not isinstance(exec_res, dict):
            raise ValueError("Output must be a dictionary")
        
        if "processed_data" not in exec_res:
            raise ValueError("Missing processed_data in output")
        
        if "metadata" not in exec_res:
            raise ValueError("Missing metadata in output")
        
        return exec_res
    
    def before_prep(self, shared):
        """Pre-processing hook"""
        self.set_context("processing_start", time.time())
        self.logger.info("Starting data processing pipeline")
    
    def after_exec(self, shared, prep_res, exec_res):
        """Post-execution analysis"""
        processing_time = time.time() - self.get_context("processing_start", 0)
        items_processed = len(prep_res.get("data", []))
        
        self.logger.info(
            f"Processed {items_processed} items in {processing_time:.2f}s "
            f"({items_processed/processing_time:.1f} items/sec)"
        )
    
    def on_error(self, shared, error):
        """Comprehensive error handling"""
        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "retry_count": self.cur_retry,
            "user_id": shared.get("user_id", "unknown")
        }
        
        self.logger.error(f"Processing error: {error_context}")
        
        # Store error info for analysis
        shared["error_info"] = error_context
        
        # Suppress certain types of errors
        if isinstance(error, (ValueError, TypeError)):
            return True  # Don't retry validation errors
        
        return False  # Retry other errors
    
    def prep(self, shared):
        """Extract and prepare data for processing"""
        return {
            "data": shared.get("raw_data", []),
            "processing_type": shared.get("processing_type", "default"),
            "user_id": shared.get("user_id"),
            "options": shared.get("options", {})
        }
    
    def exec(self, validated_input):
        """Core data processing logic"""
        data = validated_input["data"]
        processing_type = validated_input["processing_type"]
        
        # Simulate processing
        processed_items = []
        for item in data:
            if processing_type == "enhanced":
                processed_item = enhance_data(item)
            else:
                processed_item = standard_process(item)
            
            processed_items.append(processed_item)
        
        return {
            "processed_data": processed_items,
            "metadata": {
                "processing_type": processing_type,
                "items_count": len(processed_items),
                "processed_at": time.time(),
                "node_id": self.node_id
            }
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store results and update metrics"""
        shared["processed_data"] = exec_res["processed_data"]
        shared["processing_metadata"] = exec_res["metadata"]
        
        # Log summary
        self.logger.info(
            f"Successfully processed {exec_res['metadata']['items_count']} items"
        )

# Usage in a production graph
def create_production_pipeline():
    """Create a production-ready data processing pipeline"""
    
    # Validation and processing node
    processor = ProductionDataProcessor()
    
    # Create graph with resource management
    graph = Graph(start=processor)
    graph.node_id = "production_pipeline"
    
    return graph

# Example usage
if __name__ == "__main__":
    # Sample data
    shared = {
        "raw_data": [{"id": i, "value": f"item_{i}"} for i in range(100)],
        "processing_type": "enhanced",
        "user_id": "user_12345",
        "options": {"quality": "high"}
    }
    
    # Create and run pipeline with resource management
    pipeline = create_production_pipeline()
    
    with pipeline:
        result = pipeline.run(shared)
    
    # Analyze results
    processor = pipeline.start_node
    stats = processor.get_stats()
    
    print("\n=== Production Pipeline Results ===")
    print(f"Items processed: {len(shared['processed_data'])}")
    print(f"Execution time: {stats['avg_execution_time']:.3f}s")
    print(f"Success rate: {stats['success_rate']:.1%}")
    print(f"Retries needed: {stats['total_retries']}")
```

## Part 2: Vision for a Production-Ready LLMOps Platform

The logging system is more than just a debugging tool; it's the foundation for building a comprehensive evaluation and monitoring system. The logs represent a structured, chronological **event stream** of your application's behavior. By capturing and analyzing this stream, you can gain deep insights into your system.

### 1. Log-Driven Dynamic Visualization

While static graph visualizations are useful for understanding the defined graph, a dynamic visualization shows what *actually* happened at runtime.

-   **Concept**: Create a custom `logging.Handler` that captures log events in a list. After a graph runs, feed this list into a script that generates a diagram (e.g., using Graphviz or Mermaid).
-   **Benefits**:
    -   **Debug Dynamic Agents**: See the exact path an agent took through complex branches and loops.
    -   **Visualize Failures**: The diagram can automatically color-code nodes that failed or were retried.
    -   **Data Graph Analysis**: Annotate the graph edges with the data that was passed between nodes (from `DEBUG` logs).

### 2. Advanced Persistence: Logging to a Database

For true scalability and analysis, you can stream logs directly into a database like SQLite or PostgreSQL.

-   **How**: Implement a custom `logging.Handler` that connects to your database and executes `INSERT` statements for each log record.
-   **Benefits**:
    -   **Queryable History**: Your entire application history becomes queryable with SQL.
    -   **Scalability**: Handles vastly more data than in-memory or file-based logs.
    -   **Decoupling**: The core application remains simple, while the powerful data analysis happens separately.

A conceptual `SQLiteHandler`:
```python
import logging
import sqlite3
import json

class SQLiteHandler(logging.Handler):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        # ... database connection and table creation logic ...

    def emit(self, record):
        # Extract structured data from the log record
        # and insert it into the database.
        # Use the 'extra' parameter in logging calls to pass this data.
        ...
```

### 3. The Log Database as a Context Engine (Long-Term Memory)

Your log database is your application's memory. An agent can query this memory to inform its decisions.

-   **Concept**: A node's `prep()` method connects to the log database and retrieves relevant historical context.
-   **Example Use Case**: A customer service agent could start by querying the log DB: `SELECT * FROM graph_logs WHERE user_id = '123' ORDER BY timestamp DESC LIMIT 5;`. This gives it instant context about the user's recent interactions before it even calls an LLM.

### 4. The Log Database as an EVAL System

This is the ultimate goal: using the captured data to continuously evaluate and improve your system.

-   **Performance Monitoring**:
    -   **Latency**: `SELECT node_name, AVG(execution_time) FROM logs GROUP BY node_name;`
    -   **Failure Rates**: `SELECT node_name, COUNT(*) FROM logs WHERE level = 'ERROR' GROUP BY node_name;`
-   **Cost Analysis**:
    -   If you log token counts from your LLM calls, you can run queries like: `SELECT SUM(total_tokens) * 0.002 / 1000 FROM logs;` to calculate the exact cost of a run.
-   **Quality Assurance & A/B Testing**:
    -   Add a `human_feedback` table to your database with columns like `log_id`, `rating`, `correction`.
    -   After a human reviews the output of a run, they populate this table.
    -   You can now run powerful queries to find what works: `SELECT prompt_template, AVG(rating) FROM logs JOIN human_feedback ON ... GROUP BY prompt_template;`. This allows for data-driven prompt engineering and model selection.

By adopting this vision, you transform `kaygraph` from a simple execution framework into the engine of a robust, self-improving LLM application.
