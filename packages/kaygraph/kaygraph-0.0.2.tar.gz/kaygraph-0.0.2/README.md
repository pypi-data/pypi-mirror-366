# KayGraph

An opinionated framework for building context-aware AI applications with production-ready graphs.

[![PyPI version](https://img.shields.io/pypi/v/kaygraph)](https://pypi.org/project/kaygraph/)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## What is KayGraph?

KayGraph provides powerful abstractions for orchestrating complex AI workflows through **Context Graphs** - a pattern that seamlessly integrates operations, LLM calls, and state management into production-ready applications.

### Core Philosophy

- **Context-Aware Graphs**: Build sophisticated AI systems where every node has access to shared context
- **Opinionated Patterns**: Production-tested patterns for common AI workflows
- **Zero Dependencies**: Pure Python implementation with no external dependencies
- **Bring Your Own Tools**: Integrate any LLM, database, or service you prefer

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that provides better dependency resolution and faster installations:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install KayGraph
uv pip install kaygraph

# Or install from source with development dependencies
git clone https://github.com/KayOS-AI/KayGraph.git
cd KayGraph/kaygraph-library
uv pip install -e ".[dev]"
```

### Using pip

```bash
pip install kaygraph
```

Or install from source:

```bash
git clone https://github.com/KayOS-AI/KayGraph.git
cd KayGraph/kaygraph-library
pip install -e .
```

## Quick Start

```python
from kaygraph import Node, Graph

# Define a simple node
class AnalyzeNode(Node):
    def prep(self, shared):
        # Read from shared context
        return shared.get("input_text")

    def exec(self, text):
        # Process data (e.g., LLM call)
        return analyze_sentiment(text)

    def post(self, shared, prep_res, exec_res):
        # Write to shared context
        shared["sentiment"] = exec_res
        return "complete"  # Next action

# Create and run a graph
graph = Graph()
analyze = AnalyzeNode("analyzer")
graph.add_node(analyze)

shared = {"input_text": "KayGraph makes AI development intuitive!"}
graph.run(shared)
print(shared["sentiment"])  # Output: "positive"
```

## Key Features

### 🏗️ Core Abstractions

- **Node**: Atomic unit of work with 3-phase lifecycle (prep → exec → post)
- **Graph**: Orchestrates node execution through labeled actions
- **Shared Store**: Context-aware state management across nodes

### 🎯 Production Patterns

- **Agent**: Autonomous decision-making systems
- **RAG**: Retrieval-augmented generation pipelines
- **Workflows**: Multi-step task orchestration
- **Batch Processing**: Efficient data processing at scale
- **Async Operations**: Non-blocking I/O operations

### 🚀 Enterprise Features

- **ValidatedNode**: Input/output validation
- **MetricsNode**: Performance monitoring
- **Comprehensive Logging**: Built-in debugging support
- **Error Handling**: Graceful failure recovery
- **Resource Management**: Context managers for cleanup

## Documentation

### Core Concepts
- [Node Design](docs/fundamentals/node.md) - Understanding the 3-phase lifecycle
- [Graph Orchestration](docs/fundamentals/graph.md) - Connecting nodes with actions
- [Shared Store](docs/fundamentals/communication.md) - Managing shared context

### Common Patterns
- [Building Agents](docs/patterns/agent.md)
- [RAG Pipelines](docs/patterns/rag.md)
- [Workflows](docs/patterns/graph.md)
- [Map-Reduce](docs/patterns/mapreduce.md)

### Advanced Topics
- [Async Operations](docs/fundamentals/async.md)
- [Batch Processing](docs/fundamentals/batch.md)
- [Parallel Execution](docs/fundamentals/parallel.md)
- [Production Best Practices](docs/production/)

## Development with AI Assistants

KayGraph is designed for **Agentic Coding** - where humans design and AI agents implement.

### Generate Cursor Rules

```bash
# Generate AI coding assistant rules from documentation
python utils/update_kaygraph_mdc.py
```

This creates `.cursor/rules/` with context-aware guidance for AI assistants.

## Project Structure

```
kaygraph-library/
├── kaygraph/          # Core framework
│   └── __init__.py    # All abstractions in one file
├── docs/              # Comprehensive documentation
├── tests/             # Unit tests
├── utils/             # Helper scripts
└── .cursor/rules/     # AI assistant guidance
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ by the KayOS Team
