# KayGraph MCP (Model Context Protocol) Integration

This example demonstrates how to integrate Model Context Protocol (MCP) with KayGraph, enabling standardized tool calling and function execution across different AI models and applications.

## What is MCP?

Model Context Protocol is an emerging standard for:
- **Tool Discovery**: Models can discover available tools dynamically
- **Function Calling**: Standardized way to invoke functions
- **Context Sharing**: Share context between models and tools
- **Type Safety**: Strongly typed tool interfaces

## Features Demonstrated

1. **MCP Server Integration**: Connect to MCP tool servers
2. **Dynamic Tool Discovery**: Discover and use tools at runtime
3. **Tool Execution**: Execute tools with proper type checking
4. **Result Handling**: Process tool results in workflows
5. **Multi-Tool Orchestration**: Coordinate multiple tools

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Query Node    │────▶│ Tool Discovery  │────▶│ Tool Selection  │
│ (User Request)  │     │ (MCP Client)    │     │ (LLM Decision)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                              ┌──────────────────────────┴───────────┐
                              │                                      │
                    ┌─────────▼────────┐                  ┌─────────▼────────┐
                    │ Tool Execution   │                  │ Multi-Tool       │
                    │ (Single Tool)    │                  │ Orchestration    │
                    └─────────┬────────┘                  └─────────┬────────┘
                              │                                      │
                              └──────────────┬───────────────────────┘
                                            │
                                    ┌───────▼────────┐
                                    │ Result Handler │
                                    │ (Format Output)│
                                    └────────────────┘
```

## Usage

### Basic MCP Tool Usage
```bash
# Start with local MCP server
python main.py --mcp-server localhost:3333

# Use specific tool namespace
python main.py --namespace math_tools --query "Calculate factorial of 10"

# Enable tool discovery
python main.py --discover-tools --query "What tools are available?"
```

### Advanced Features
```bash
# Multi-tool orchestration
python main.py --query "Analyze sales data and create a chart"

# Custom tool server
python main.py --mcp-config config.json

# Debug mode to see tool calls
python main.py --debug --query "Get current weather"
```

## MCP Tool Examples

### 1. File System Tools
- Read/write files
- List directories
- Search content

### 2. Database Tools
- Query execution
- Schema inspection
- Data manipulation

### 3. API Tools
- HTTP requests
- Authentication
- Response parsing

### 4. Computation Tools
- Math operations
- Data analysis
- Image processing

## Configuration

```json
{
  "mcp_servers": [
    {
      "name": "local_tools",
      "url": "localhost:3333",
      "auth": {
        "type": "bearer",
        "token": "your-token"
      }
    },
    {
      "name": "cloud_tools",
      "url": "mcp.example.com",
      "namespaces": ["math", "data", "web"]
    }
  ]
}
```

## Creating MCP Tools

### Tool Definition
```python
@mcp_tool(
    name="calculate_statistics",
    description="Calculate statistics for a dataset",
    parameters={
        "data": {"type": "array", "items": {"type": "number"}},
        "operations": {"type": "array", "items": {"type": "string"}}
    }
)
def calculate_statistics(data: List[float], operations: List[str]) -> Dict:
    """Calculate requested statistics."""
    results = {}
    if "mean" in operations:
        results["mean"] = sum(data) / len(data)
    if "median" in operations:
        results["median"] = sorted(data)[len(data)//2]
    return results
```

## Integration with KayGraph

The MCP integration provides:
- **MCPClientNode**: Connect to MCP servers
- **ToolDiscoveryNode**: Discover available tools
- **ToolExecutionNode**: Execute selected tools
- **ToolOrchestrationNode**: Coordinate multiple tools

## Best Practices

1. **Tool Versioning**: Always specify tool versions
2. **Error Handling**: Handle tool failures gracefully
3. **Rate Limiting**: Respect tool server limits
4. **Caching**: Cache tool discoveries
5. **Security**: Validate tool inputs/outputs

## Security Considerations

- **Authentication**: Use proper auth for tool servers
- **Input Validation**: Sanitize all tool inputs
- **Output Verification**: Verify tool outputs
- **Sandboxing**: Run untrusted tools in sandbox
- **Audit Logging**: Log all tool executions