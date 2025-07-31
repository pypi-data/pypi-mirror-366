# KayGraph Utilities

This directory contains utility scripts to enhance your KayGraph development experience.

## Available Tools

### 1. 📝 Template Generator (`generate_templates.py`)

Create starter code for common KayGraph patterns.

**Usage:**
```bash
python generate_templates.py <pattern> <name> [--output-dir PATH]
```

**Available Templates:**
- `node` - Basic node with prep/exec/post lifecycle
- `async_node` - Async node for I/O operations
- `batch_node` - Batch processing for collections
- `agent` - Autonomous agent with observe/think/act loop
- `rag` - Retrieval-Augmented Generation pipeline
- `workflow` - Multi-step workflow orchestration

**Example:**
```bash
# Generate a basic node
python generate_templates.py node DataProcessor

# Generate an agent
python generate_templates.py agent ResearchBot --output-dir ./projects

# Generate a RAG pipeline
python generate_templates.py rag DocumentQA
```

### 2. ✅ Code Validator (`validate_kaygraph.py`)

Check if your code follows KayGraph patterns and best practices.

**Usage:**
```bash
python validate_kaygraph.py <file_or_directory> [--fix] [--verbose]
```

**What it checks:**
- Node classes end with 'Node'
- Required methods: prep(), exec(), post()
- exec() doesn't access shared store
- Proper method signatures
- Graph structure validation
- Docstring presence

**Example:**
```bash
# Validate a single file
python validate_kaygraph.py nodes.py

# Validate entire project
python validate_kaygraph.py ./my_project

# Get fix suggestions
python validate_kaygraph.py ./my_project --fix

# Show all checks (including passed)
python validate_kaygraph.py ./my_project --verbose
```

### 3. 📚 Documentation Generator (`generate_docs_from_code.py`)

Generate documentation from your KayGraph code.

**Usage:**
```bash
python generate_docs_from_code.py <directory> [--output-dir PATH] [--format FORMAT]
```

**Output Formats:**
- `md` - Markdown documentation with node descriptions
- `mermaid` - Mermaid diagram of graph structure (+ HTML viewer)
- `design` - design.md file in KayGraph format
- `json` - JSON specification of project structure
- `all` - Generate all formats (default)

**Example:**
```bash
# Generate all documentation formats
python generate_docs_from_code.py ./my_project

# Generate only Mermaid diagram
python generate_docs_from_code.py ./my_project --format mermaid

# Specify output directory
python generate_docs_from_code.py ./my_project --output-dir ./docs
```

### 4. 🔄 MDC Rules Generator (`update_kaygraph_mdc.py`)

Generate Cursor/AI assistant rules from KayGraph documentation.

**Usage:**
```bash
python update_kaygraph_mdc.py [--docs-dir PATH] [--rules-dir PATH]
```

This creates `.cursor/rules/` with context-aware guidance for AI coding assistants.

## Workflow Examples

### Starting a New Project

```bash
# 1. Generate starter code
python generate_templates.py agent MyAgent

# 2. Develop your implementation
cd generated/myagent
# ... implement your logic ...

# 3. Validate your code
python ../../validate_kaygraph.py .

# 4. Generate documentation
python ../../generate_docs_from_code.py . --output-dir ./docs
```

### Validating Existing Code

```bash
# Check for issues
python validate_kaygraph.py ./my_project

# Get detailed feedback
python validate_kaygraph.py ./my_project --verbose --fix
```

### Documenting Your Project

```bash
# Generate complete documentation
python generate_docs_from_code.py ./my_project

# View the generated Mermaid diagram
open generated_docs/graph_diagram.html
```

## Tips

1. **Use templates** to quickly start with correct patterns
2. **Run validation** before committing code
3. **Generate docs** to visualize your graph structure
4. **Keep MDC rules updated** for better AI assistance

## Contributing

To add new templates or validation rules, please submit a PR with:
- New pattern in `generate_templates.py`
- Corresponding validation in `validate_kaygraph.py`
- Documentation updates