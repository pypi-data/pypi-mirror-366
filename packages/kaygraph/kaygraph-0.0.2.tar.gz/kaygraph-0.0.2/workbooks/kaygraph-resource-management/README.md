# KayGraph Resource Management

This example demonstrates KayGraph's context manager support for automatic resource management. It showcases how to properly handle database connections, file handles, API clients, and other resources with automatic cleanup on success or failure.

## Features Demonstrated

1. **Context Manager Support**: Using `with` statements for automatic resource management
2. **Resource Pooling**: Sharing connections across nodes in a graph
3. **Automatic Cleanup**: Resources cleaned up even when exceptions occur
4. **Resource Lifecycle**: Setup and teardown hooks for resource management
5. **Connection Monitoring**: Track resource usage and connection health

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ DatabaseReader  │────▶│   FileProcessor  │────▶│  ApiUploader    │
│ (DB Connection) │     │ (File Handles)   │     │ (HTTP Client)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
    [Auto Cleanup]         [Auto Cleanup]         [Auto Cleanup]
                                                           │
                          ┌──────────────────┐             │
                          │ ResourceMonitor  │◀────────────┘
                          │ (Shared Pool)    │
                          └──────────────────┘
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the example
python main.py

# Run with resource failures to see cleanup in action
python main.py --simulate-failures

# Monitor resource usage
python main.py --monitor-resources
```

## Key Concepts

### Context Manager Benefits
- Automatic resource cleanup on success or failure
- Exception-safe resource handling
- Consistent resource lifecycle management
- Memory and connection leak prevention

### Resource Patterns
- Database connection pooling
- File handle management
- HTTP client session reuse
- Temporary resource allocation

## Example Resources

1. **Database Connections**: PostgreSQL, Redis connections with pooling
2. **File Handles**: Reading/writing large files with proper cleanup
3. **HTTP Clients**: API clients with session management
4. **Memory Resources**: Large data structures with cleanup
5. **Locks and Semaphores**: Concurrency control resources