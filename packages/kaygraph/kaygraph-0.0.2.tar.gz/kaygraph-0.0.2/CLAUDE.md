# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KayGraph is an opinionated framework for building context-aware AI applications with production-ready graphs. The core abstraction is **Context Graph + Shared Store**, where Nodes handle operations (including LLM calls) and Graphs connect nodes through Actions (labeled edges) to create sophisticated workflows.

**Key Features:**
- Zero dependencies - pure Python standard library
- Production-ready patterns with 42+ comprehensive examples
- Supports sync, async, batch, and parallel execution
- Built-in resilience with retries, fallbacks, and validation
- Thread-safe execution with node copying

## Development Commands

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_graph_basic.py

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=kaygraph tests/

# Run async tests
pytest tests/test_async.py -v
```

### Installation
```bash
# Install the framework
pip install kaygraph

# Or install from source for development
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Using uv (recommended)
uv pip install kaygraph
```

### Linting and Code Quality
```bash
# Run ruff linter
ruff check kaygraph/

# Fix linting issues automatically
ruff check --fix kaygraph/

# Format code
ruff format kaygraph/
```

### Building and Publishing
```bash
# Build the package
python -m build

# Upload to PyPI (requires account setup)
python -m twine upload dist/*

# Version bumping (update kaygraph/__init__.py)
# Then tag and push:
git tag v0.0.1
git push origin v0.0.1
```

## Architecture & Key Components

### Core Framework (`/kaygraph/__init__.py`)
The framework provides these opinionated abstractions:

#### Base Classes
- **BaseNode**: Foundation with 3-step lifecycle: `prep()` → `exec()` → `post()`
  - Includes hooks: `before_prep()`, `after_exec()`, `on_error()`
  - Context manager support for resource management
  - Execution context storage per node
- **Node**: Standard node with retry and fallback capabilities
  - `max_retries` and `wait` parameters for resilience
  - `exec_fallback()` for graceful degradation
- **Graph**: Orchestrates node execution through Actions
  - Supports operator overloading: `>>` for default, `-` for named actions
  - Copy nodes before execution for thread safety

#### Specialized Nodes
- **BatchNode/Graph**: Process iterables of items
  - `prep()` returns iterable, `exec()` called per item
- **AsyncNode/Graph**: Asynchronous versions for I/O operations
  - Replace methods with `_async` versions
  - `run_async()` for standalone execution
- **ParallelBatchNode/Graph**: Concurrent execution using ThreadPoolExecutor
- **ValidatedNode**: Input/output validation with custom validators
- **MetricsNode**: Execution metrics collection
  - Tracks execution times, retry counts, success/error rates
  - `get_stats()` for comprehensive metrics

### Node Design Principles
1. **prep(shared)**: Read from shared store, prepare data for execution
   - Access shared context to gather required data
   - Return data needed for exec phase
   - Should be lightweight and fast
2. **exec(prep_res)**: Execute compute logic (LLM calls, APIs) - NO shared access
   - Pure function that processes prep_res
   - Can be retried independently
   - Should be idempotent when retries are enabled
3. **post(shared, prep_res, exec_res)**: Write to shared store, return next action
   - Update shared context with results
   - Return action string for next node or None for default
   - Nodes for conditional branching MUST return specific action strings

### Shared Store Design
- Use dictionary for simple systems: `shared = {"key": value}`
- Params are for identifiers, Shared Store is for data
- Don't repeat data - use references or foreign keys
- Thread-safe when used with proper node copying

## Available Examples (42 Total)

The `workbooks/` directory contains comprehensive examples demonstrating all major patterns:

### Core Patterns
- `kaygraph-hello-world/`: Basic workflow patterns
- `kaygraph-workflow/`: Simple task orchestration
- `kaygraph-batch/`: Batch processing fundamentals
- `kaygraph-parallel-batch/`: High-performance parallel processing
- `kaygraph-nested-batch/`: Hierarchical batch workflows
- `kaygraph-async-basics/`: Comprehensive async tutorial

### AI/ML Patterns
- `kaygraph-agent/`: Autonomous AI agent implementation
- `kaygraph-multi-agent/`: Coordinated multi-agent systems
- `kaygraph-rag/`: Complete RAG pipeline with indexing
- `kaygraph-chat/`: Basic conversational interface
- `kaygraph-chat-memory/`: Chat with context management
- `kaygraph-chat-guardrail/`: Safe AI with content filtering
- `kaygraph-thinking/`: Chain-of-thought reasoning
- `kaygraph-think-act-reflect/`: TAR cognitive architecture
- `kaygraph-streaming-llm/`: Real-time LLM streaming
- `kaygraph-majority-vote/`: LLM consensus mechanisms
- `kaygraph-structured-output/`: Type-safe LLM outputs

### Production Features
- `kaygraph-fault-tolerant-workflow/`: Error handling patterns
- `kaygraph-realtime-monitoring/`: Live observability
- `kaygraph-distributed-tracing/`: OpenTelemetry integration
- `kaygraph-resource-management/`: Cleanup and resources
- `kaygraph-production-ready-api/`: FastAPI integration
- `kaygraph-fastapi-background/`: Background task processing
- `kaygraph-metrics-dashboard/`: Performance monitoring
- `kaygraph-supervisor/`: Process supervision
- `kaygraph-validated-pipeline/`: Input/output validation

### UI/UX Integrations
- `kaygraph-human-in-the-loop/`: Approval workflows
- `kaygraph-streamlit-fsm/`: Finite state machines
- `kaygraph-gradio/`: ML interface building
- `kaygraph-voice-chat/`: Speech interfaces
- `kaygraph-visualization/`: Graph debugging tools

### External Integrations
- `kaygraph-google-calendar/`: OAuth2 and calendar API
- `kaygraph-sql-scheduler/`: Database workflows
- `kaygraph-text2sql/`: Natural language queries
- `kaygraph-tool-database/`: Database operations
- `kaygraph-tool-crawler/`: Web scraping
- `kaygraph-tool-search/`: Search integration
- `kaygraph-tool-pdf-vision/`: Document processing
- `kaygraph-tool-embeddings/`: Vector operations
- `kaygraph-mcp/`: Model Context Protocol

### Advanced Patterns
- `kaygraph-distributed-mapreduce/`: Distributed computing
- `kaygraph-code-generator/`: Code synthesis

## Implementation Guidelines

### Node Implementation
```python
class MyNode(Node):
    def prep(self, shared):
        # Read from shared store
        return shared.get("input_data")
    
    def exec(self, prep_res):
        # Process data (LLM calls, etc)
        # This should be idempotent if retries enabled
        return process_data(prep_res)
    
    def post(self, shared, prep_res, exec_res):
        # Write results to shared store
        shared["output_data"] = exec_res
        return "next_action"  # or None for "default"
```

### Graph Connection
```python
# Connect nodes with default action
node1 >> node2 >> node3

# Connect with named actions
node1 >> ("success", node2)
node1 >> ("error", error_handler)

# Complex branching
decision_node >> ("approve", approval_flow)
decision_node >> ("reject", rejection_handler)
decision_node >> ("escalate", manager_review)
```

### Utility Functions
- One file per external API (`utils/call_llm.py`, `utils/search_web.py`)
- Include `if __name__ == "__main__"` test in each utility
- Document input/output and necessity
- NO vendor lock-in - implement your own wrappers

## Best Practices

1. **FAIL FAST**: Avoid try/except in initial implementation
2. **No Complex Features**: Keep it simple, avoid overengineering
3. **Extensive Logging**: Add logging throughout for debugging
4. **Separation of Concerns**: Data storage (shared) vs processing (nodes)
5. **Idempotent exec()**: Required when using retries
6. **Test Utilities**: Each utility should have a simple test
7. **Thread Safety**: Nodes are copied before execution
8. **Resource Cleanup**: Use context managers in nodes
9. **Validation First**: Use ValidatedNode for critical paths
10. **Metrics Always**: Add MetricsNode for production

## Common Patterns

### Agent Pattern
```python
# Decision-making with context and tools
think_node >> analyze_node >> ("use_tool", tool_node)
analyze_node >> ("respond", response_node)
tool_node >> think_node  # Loop back
```

### RAG Pattern
```python
# Offline indexing
extract >> chunk >> embed >> store

# Online retrieval
query >> search >> rerank >> generate
```

### Approval Workflow
```python
# Human-in-the-loop
process >> review >> ("approve", execute)
review >> ("reject", notify)
review >> ("modify", process)  # Loop back
```

### Fault-Tolerant Pipeline
```python
# With retries and fallbacks
class ResilientNode(Node):
    max_retries = 3
    wait = 1.0
    
    def exec_fallback(self, prep_res):
        return {"status": "degraded", "result": None}
```

## Project Structure Template
```
my_project/
├── main.py                  # Entry point
├── nodes/                   # Node definitions
│   ├── __init__.py
│   ├── processing.py        # Business logic nodes
│   ├── validation.py        # Input/output validation
│   └── integration.py       # External service nodes
├── graphs/                  # Graph definitions
│   ├── __init__.py
│   └── workflows.py         # Workflow orchestration
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── call_llm.py         # LLM integration
│   ├── database.py         # DB operations
│   └── monitoring.py       # Metrics/logging
├── tests/                   # Test suite
│   ├── test_nodes.py
│   ├── test_graphs.py
│   └── test_integration.py
├── docs/                    # Documentation
│   └── design.md           # High-level design
├── requirements.txt         # Dependencies
└── README.md               # Project documentation
```

## Debugging Tips

1. **Use Graph Logging**: Enable with `--` operator
   ```python
   graph = Graph()
   -- graph  # Logs graph structure
   ```

2. **Node Execution Context**: Access via `_execution_context`
   ```python
   def after_exec(self):
       logger.info(f"Execution took: {self._execution_context['duration']}s")
   ```

3. **Shared Store Inspection**: Log at each phase
   ```python
   def post(self, shared, prep_res, exec_res):
       logger.debug(f"Shared state: {shared.keys()}")
   ```

4. **Action Flow Tracing**: Log action decisions
   ```python
   def post(self, shared, prep_res, exec_res):
       action = "approve" if exec_res["score"] > 0.8 else "review"
       logger.info(f"Routing to action: {action}")
       return action
   ```

## Performance Optimization

1. **Use AsyncNode** for I/O-bound operations
2. **Use ParallelBatchNode** for CPU-bound batch processing
3. **Minimize shared store size** - use references not copies
4. **Profile with MetricsNode** to identify bottlenecks
5. **Cache expensive computations** in utility functions

## Security Considerations

1. **Never store secrets in shared store** - use environment variables
2. **Validate all external inputs** with ValidatedNode
3. **Sanitize data before logging** to prevent leaks
4. **Use timeout parameters** for external calls
5. **Implement rate limiting** for API calls

## Common Pitfalls to Avoid

1. **Modifying shared in exec()** - This breaks retry logic
2. **Not returning actions from conditional nodes** - Causes routing failures
3. **Circular dependencies in graphs** - Use careful action design
4. **Overcomplicating node design** - Keep nodes focused
5. **Ignoring thread safety** - Always let Graph copy nodes
6. **Forgetting cleanup** - Use context managers
7. **Not testing edge cases** - Test failures and timeouts

## Version Management

Current version: 0.0.1

When updating:
1. Update version in `kaygraph/__init__.py`
2. Update CHANGELOG.md
3. Tag release: `git tag v0.0.1`
4. Build: `python -m build`
5. Upload: `python -m twine upload dist/*`

## Important Notes

- The framework has ZERO dependencies - only Python standard library
- All utility functions (LLM calls, embeddings, etc.) must be implemented by you
- When humans can't specify the graph, AI agents can't automate it
- Node instances are copied before execution for thread safety
- Use `--` operator to log graph structure during development
- Conditional nodes must explicitly return action strings from `post()`
- Default transitions (>>) expect `post()` to return None
- This is an opinionated framework - embrace the patterns

## Getting Help

- Review examples in `workbooks/` for patterns
- Check test files for usage examples
- Use logging extensively during development
- Keep nodes simple and focused
- When in doubt, fail fast and log clearly