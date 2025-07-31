"""
MCP (Model Context Protocol) nodes for KayGraph.
Enables standardized tool calling and function execution.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from abc import abstractmethod

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, ValidatedNode

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool."""
    name: str
    description: str
    namespace: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    examples: List[Dict[str, Any]] = None
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "namespace": self.namespace,
            "parameters": self.parameters,
            "returns": self.returns,
            "examples": self.examples or [],
            "version": self.version
        }


@dataclass
class MCPToolCall:
    """Represents a tool call request."""
    tool_name: str
    namespace: str
    arguments: Dict[str, Any]
    request_id: str
    
    def validate(self, tool: MCPTool) -> bool:
        """Validate arguments against tool schema."""
        # In production, use jsonschema validation
        required_params = [
            k for k, v in tool.parameters.get("properties", {}).items()
            if k in tool.parameters.get("required", [])
        ]
        
        for param in required_params:
            if param not in self.arguments:
                logger.error(f"Missing required parameter: {param}")
                return False
        
        return True


class MCPClientNode(AsyncNode):
    """Client node for connecting to MCP servers."""
    
    def __init__(self, 
                 server_url: str,
                 auth_token: Optional[str] = None,
                 timeout: int = 30):
        super().__init__(node_id="mcp_client")
        self.server_url = server_url
        self.auth_token = auth_token
        self.timeout = timeout
        self.connected = False
        self._tool_cache: Dict[str, MCPTool] = {}
    
    async def setup_resources(self):
        """Connect to MCP server."""
        logger.info(f"Connecting to MCP server: {self.server_url}")
        # In production, establish actual connection
        self.connected = True
    
    async def cleanup_resources(self):
        """Disconnect from MCP server."""
        logger.info("Disconnecting from MCP server")
        self.connected = False
    
    async def exec_async(self, request: str) -> Dict[str, Any]:
        """Execute MCP request."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        logger.info(f"Sending MCP request: {request}")
        
        # Simulate MCP communication
        import asyncio
        await asyncio.sleep(0.5)
        
        # Mock response based on request type
        if "discover" in request.lower():
            return await self._discover_tools()
        elif "execute" in request.lower():
            return {"status": "executed", "result": "Mock execution result"}
        else:
            return {"status": "unknown_request"}
    
    async def _discover_tools(self) -> Dict[str, Any]:
        """Discover available tools from MCP server."""
        # Mock tool discovery
        tools = [
            MCPTool(
                name="calculate",
                description="Perform mathematical calculations",
                namespace="math",
                parameters={
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression to evaluate"},
                        "precision": {"type": "integer", "description": "Decimal precision"}
                    },
                    "required": ["expression"]
                },
                returns={"type": "number"},
                examples=[{"expression": "2 + 2", "result": 4}]
            ),
            MCPTool(
                name="fetch_data",
                description="Fetch data from external source",
                namespace="data",
                parameters={
                    "type": "object",
                    "properties": {
                        "source": {"type": "string", "description": "Data source URL"},
                        "format": {"type": "string", "enum": ["json", "csv", "xml"]}
                    },
                    "required": ["source"]
                },
                returns={"type": "object"}
            ),
            MCPTool(
                name="search_web",
                description="Search the web for information",
                namespace="web",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                },
                returns={"type": "array", "items": {"type": "object"}}
            )
        ]
        
        # Cache tools
        for tool in tools:
            self._tool_cache[f"{tool.namespace}.{tool.name}"] = tool
        
        return {
            "tools": [tool.to_dict() for tool in tools],
            "total": len(tools)
        }
    
    async def post_async(self, shared: Dict[str, Any], request: str, response: Dict[str, Any]) -> None:
        """Store MCP response."""
        shared["mcp_response"] = response
        
        if "tools" in response:
            shared["available_tools"] = response["tools"]
            logger.info(f"Discovered {len(response['tools'])} tools")


class ToolDiscoveryNode(ValidatedNode):
    """Discover and analyze available MCP tools."""
    
    def __init__(self):
        super().__init__(node_id="tool_discovery")
    
    def validate_input(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate tool definitions."""
        if not tools:
            raise ValueError("No tools discovered")
        
        for tool in tools:
            if "name" not in tool or "parameters" not in tool:
                raise ValueError(f"Invalid tool definition: {tool}")
        
        return tools
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get discovered tools."""
        return shared.get("available_tools", [])
    
    def exec(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and categorize tools."""
        categorized = {
            "math": [],
            "data": [],
            "web": [],
            "file": [],
            "other": []
        }
        
        for tool in tools:
            namespace = tool.get("namespace", "other")
            category = namespace if namespace in categorized else "other"
            categorized[category].append(tool)
        
        # Create tool index
        tool_index = {
            f"{tool['namespace']}.{tool['name']}": tool
            for tool in tools
        }
        
        return {
            "total_tools": len(tools),
            "categories": categorized,
            "tool_index": tool_index,
            "namespaces": list(set(tool.get("namespace", "unknown") for tool in tools))
        }
    
    def post(self, shared: Dict[str, Any], tools: List[Dict], analysis: Dict[str, Any]) -> None:
        """Store tool analysis."""
        shared["tool_analysis"] = analysis
        shared["tool_index"] = analysis["tool_index"]
        
        logger.info(f"Tool categories: {', '.join(f'{k}({len(v)})' for k, v in analysis['categories'].items() if v)}")


class ToolSelectionNode(Node):
    """Select appropriate tools based on user query."""
    
    def __init__(self):
        super().__init__(node_id="tool_selection")
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get query and available tools."""
        return {
            "query": shared.get("user_query", ""),
            "tool_index": shared.get("tool_index", {}),
            "tool_analysis": shared.get("tool_analysis", {})
        }
    
    def exec(self, data: Dict[str, Any]) -> List[str]:
        """Select tools based on query analysis."""
        query = data["query"].lower()
        tool_index = data["tool_index"]
        selected_tools = []
        
        # Simple keyword matching (in production, use LLM)
        if any(word in query for word in ["calculate", "math", "compute"]):
            if "math.calculate" in tool_index:
                selected_tools.append("math.calculate")
        
        if any(word in query for word in ["search", "find", "look up"]):
            if "web.search_web" in tool_index:
                selected_tools.append("web.search_web")
        
        if any(word in query for word in ["data", "fetch", "retrieve"]):
            if "data.fetch_data" in tool_index:
                selected_tools.append("data.fetch_data")
        
        # If no specific tools selected, use general search
        if not selected_tools and "web.search_web" in tool_index:
            selected_tools.append("web.search_web")
        
        logger.info(f"Selected tools for '{query}': {selected_tools}")
        return selected_tools
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, selected_tools: List[str]) -> str:
        """Store selected tools and determine action."""
        shared["selected_tools"] = selected_tools
        
        if not selected_tools:
            return "no_tools"
        elif len(selected_tools) == 1:
            return "single_tool"
        else:
            return "multi_tool"


class ToolExecutionNode(AsyncNode):
    """Execute selected MCP tools."""
    
    def __init__(self):
        super().__init__(node_id="tool_execution", max_retries=2)
    
    async def prep_async(self, shared: Dict[str, Any]) -> List[MCPToolCall]:
        """Prepare tool calls."""
        selected_tools = shared.get("selected_tools", [])
        tool_index = shared.get("tool_index", {})
        user_query = shared.get("user_query", "")
        
        tool_calls = []
        
        for tool_id in selected_tools:
            if tool_id not in tool_index:
                continue
            
            tool = tool_index[tool_id]
            namespace, name = tool_id.split(".")
            
            # Generate arguments based on query (mock)
            arguments = self._generate_arguments(tool, user_query)
            
            tool_call = MCPToolCall(
                tool_name=name,
                namespace=namespace,
                arguments=arguments,
                request_id=f"{tool_id}_{time.time()}"
            )
            
            tool_calls.append(tool_call)
        
        return tool_calls
    
    def _generate_arguments(self, tool: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Generate tool arguments from query."""
        # In production, use LLM to extract arguments
        
        if tool["name"] == "calculate":
            # Extract math expression
            return {"expression": query, "precision": 2}
        elif tool["name"] == "search_web":
            return {"query": query, "max_results": 5}
        elif tool["name"] == "fetch_data":
            return {"source": "example.com/data", "format": "json"}
        else:
            return {}
    
    async def exec_async(self, tool_calls: List[MCPToolCall]) -> List[Dict[str, Any]]:
        """Execute tool calls."""
        results = []
        
        for call in tool_calls:
            logger.info(f"Executing tool: {call.namespace}.{call.tool_name}")
            
            # Simulate tool execution
            import asyncio
            await asyncio.sleep(0.5)
            
            # Mock results based on tool
            if call.tool_name == "calculate":
                result = {
                    "success": True,
                    "result": eval(call.arguments.get("expression", "0")),  # Don't use eval in production!
                    "tool": f"{call.namespace}.{call.tool_name}"
                }
            elif call.tool_name == "search_web":
                result = {
                    "success": True,
                    "result": [
                        {"title": "Result 1", "url": "example.com/1"},
                        {"title": "Result 2", "url": "example.com/2"}
                    ],
                    "tool": f"{call.namespace}.{call.tool_name}"
                }
            else:
                result = {
                    "success": True,
                    "result": {"data": "Mock data"},
                    "tool": f"{call.namespace}.{call.tool_name}"
                }
            
            results.append(result)
        
        return results
    
    async def post_async(self, shared: Dict[str, Any], tool_calls: List[MCPToolCall], 
                        results: List[Dict[str, Any]]) -> None:
        """Store execution results."""
        shared["tool_results"] = results
        
        # Summary
        successful = sum(1 for r in results if r.get("success", False))
        logger.info(f"Executed {len(tool_calls)} tools: {successful} successful")


class ResultFormatterNode(Node):
    """Format tool results for presentation."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get all results to format."""
        return {
            "query": shared.get("user_query", ""),
            "tool_results": shared.get("tool_results", []),
            "selected_tools": shared.get("selected_tools", [])
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Format results into readable response."""
        if not data["tool_results"]:
            return "I couldn't find any tools to help with your request."
        
        response_parts = [f"Based on your query: '{data['query']}'"]
        response_parts.append(f"\nI used {len(data['tool_results'])} tools:\n")
        
        for result in data["tool_results"]:
            tool_name = result.get("tool", "unknown")
            
            if result.get("success"):
                response_parts.append(f"✅ {tool_name}:")
                
                # Format based on result type
                tool_result = result.get("result")
                if isinstance(tool_result, (int, float)):
                    response_parts.append(f"   Result: {tool_result}")
                elif isinstance(tool_result, list):
                    response_parts.append(f"   Found {len(tool_result)} results")
                    for item in tool_result[:3]:  # Show first 3
                        if isinstance(item, dict):
                            response_parts.append(f"   - {item.get('title', str(item))}")
                else:
                    response_parts.append(f"   Result: {tool_result}")
            else:
                response_parts.append(f"❌ {tool_name}: Failed")
        
        return "\n".join(response_parts)
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, formatted: str) -> None:
        """Store formatted response."""
        shared["final_response"] = formatted


if __name__ == "__main__":
    # Test MCP nodes
    import asyncio
    import logging
    logging.basicConfig(level=logging.INFO)
    
    async def test_mcp():
        # Create MCP client
        client = MCPClientNode("mock://localhost:3333")
        
        # Test connection
        await client.setup_resources()
        
        # Test tool discovery
        shared = {}
        await client.run_async(shared)
        
        print(f"Discovered tools: {len(shared.get('available_tools', []))}")
        
        # Cleanup
        await client.cleanup_resources()
    
    asyncio.run(test_mcp())