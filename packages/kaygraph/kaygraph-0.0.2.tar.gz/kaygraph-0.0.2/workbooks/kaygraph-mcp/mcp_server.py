#!/usr/bin/env python3
"""
Mock MCP server for testing.
In production, this would be a real MCP-compliant server.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MCPRequest:
    """MCP request structure."""
    method: str
    params: Dict[str, Any]
    id: str


@dataclass 
class MCPResponse:
    """MCP response structure."""
    result: Any
    error: Any = None
    id: str = ""


class MockMCPServer:
    """Mock MCP server implementation."""
    
    def __init__(self, port: int = 3333):
        self.port = port
        self.tools = self._init_tools()
        self.running = False
    
    def _init_tools(self) -> List[Dict[str, Any]]:
        """Initialize available tools."""
        return [
            {
                "name": "calculate",
                "namespace": "math",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"},
                        "precision": {"type": "integer", "default": 2}
                    },
                    "required": ["expression"]
                },
                "returns": {"type": "number"}
            },
            {
                "name": "fibonacci",
                "namespace": "math",
                "description": "Calculate Fibonacci sequence",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "n": {"type": "integer", "minimum": 0}
                    },
                    "required": ["n"]
                },
                "returns": {"type": "array", "items": {"type": "integer"}}
            },
            {
                "name": "search_web",
                "namespace": "web",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "max_results": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                },
                "returns": {"type": "array"}
            },
            {
                "name": "fetch_data",
                "namespace": "data",
                "description": "Fetch data from external source",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "format": {"type": "string", "enum": ["json", "csv", "xml"]}
                    },
                    "required": ["source"]
                },
                "returns": {"type": "object"}
            },
            {
                "name": "read_file",
                "namespace": "file",
                "description": "Read file contents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "encoding": {"type": "string", "default": "utf-8"}
                    },
                    "required": ["path"]
                },
                "returns": {"type": "string"}
            },
            {
                "name": "query_database",
                "namespace": "db",
                "description": "Execute database query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "params": {"type": "array", "default": []}
                    },
                    "required": ["query"]
                },
                "returns": {"type": "array"}
            }
        ]
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP request."""
        logger.info(f"Handling request: {request.method}")
        
        try:
            if request.method == "tools.discover":
                result = await self.discover_tools(request.params)
            elif request.method == "tools.execute":
                result = await self.execute_tool(request.params)
            else:
                raise ValueError(f"Unknown method: {request.method}")
            
            return MCPResponse(result=result, id=request.id)
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return MCPResponse(
                result=None,
                error={"message": str(e), "code": -32603},
                id=request.id
            )
    
    async def discover_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Discover available tools."""
        namespace_filter = params.get("namespace")
        
        if namespace_filter:
            filtered_tools = [
                t for t in self.tools 
                if t["namespace"] == namespace_filter
            ]
        else:
            filtered_tools = self.tools
        
        return {
            "tools": filtered_tools,
            "total": len(filtered_tools)
        }
    
    async def execute_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool."""
        tool_name = params.get("tool")
        namespace = params.get("namespace")
        arguments = params.get("arguments", {})
        
        tool_id = f"{namespace}.{tool_name}"
        
        # Simulate tool execution
        if tool_id == "math.calculate":
            # UNSAFE: Don't use eval in production!
            try:
                result = eval(arguments.get("expression", "0"))
                return {"success": True, "result": result}
            except:
                return {"success": False, "error": "Invalid expression"}
                
        elif tool_id == "math.fibonacci":
            n = arguments.get("n", 10)
            fib = [0, 1]
            for i in range(2, n):
                fib.append(fib[-1] + fib[-2])
            return {"success": True, "result": fib[:n]}
            
        elif tool_id == "web.search_web":
            query = arguments.get("query", "")
            return {
                "success": True,
                "result": [
                    {"title": f"Result 1 for: {query}", "url": "example.com/1"},
                    {"title": f"Result 2 for: {query}", "url": "example.com/2"},
                    {"title": f"Result 3 for: {query}", "url": "example.com/3"}
                ]
            }
            
        elif tool_id == "data.fetch_data":
            return {
                "success": True,
                "result": {
                    "source": arguments.get("source"),
                    "data": {"example": "data", "timestamp": "2024-01-01"}
                }
            }
            
        elif tool_id == "file.read_file":
            return {
                "success": True,
                "result": f"Mock contents of {arguments.get('path')}"
            }
            
        elif tool_id == "db.query_database":
            return {
                "success": True,
                "result": [
                    {"id": 1, "name": "Record 1"},
                    {"id": 2, "name": "Record 2"}
                ]
            }
        else:
            return {"success": False, "error": f"Unknown tool: {tool_id}"}
    
    async def start(self):
        """Start the mock server."""
        self.running = True
        logger.info(f"Mock MCP server started on port {self.port}")
        
        # In a real implementation, this would start a network server
        while self.running:
            await asyncio.sleep(1)
    
    def stop(self):
        """Stop the server."""
        self.running = False
        logger.info("Mock MCP server stopped")


async def test_server():
    """Test the mock server."""
    server = MockMCPServer()
    
    # Test tool discovery
    print("\n1. Testing tool discovery...")
    request = MCPRequest(
        method="tools.discover",
        params={},
        id="test-1"
    )
    response = await server.handle_request(request)
    print(f"Found {len(response.result['tools'])} tools")
    
    # Test tool execution
    print("\n2. Testing math calculation...")
    request = MCPRequest(
        method="tools.execute",
        params={
            "tool": "calculate",
            "namespace": "math",
            "arguments": {"expression": "2 + 2 * 3"}
        },
        id="test-2"
    )
    response = await server.handle_request(request)
    print(f"Result: {response.result}")
    
    # Test web search
    print("\n3. Testing web search...")
    request = MCPRequest(
        method="tools.execute",
        params={
            "tool": "search_web",
            "namespace": "web",
            "arguments": {"query": "Python async programming"}
        },
        id="test-3"
    )
    response = await server.handle_request(request)
    print(f"Results: {len(response.result['result'])} items")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    asyncio.run(test_server())