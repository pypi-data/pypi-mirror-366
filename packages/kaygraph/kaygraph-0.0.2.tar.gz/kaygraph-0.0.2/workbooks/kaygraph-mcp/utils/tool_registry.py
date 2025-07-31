"""
Tool registry for managing MCP tools.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Additional metadata for tools."""
    author: str = ""
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    replacement: Optional[str] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    performance: Dict[str, float] = field(default_factory=dict)  # avg_time, success_rate


class ToolRegistry:
    """Registry for managing MCP tools."""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, ToolMetadata] = {}
        self.validators: Dict[str, Callable] = {}
        self.middlewares: List[Callable] = []
    
    def register_tool(self, 
                     namespace: str,
                     name: str,
                     description: str,
                     parameters: Dict[str, Any],
                     returns: Dict[str, Any],
                     metadata: Optional[ToolMetadata] = None,
                     validator: Optional[Callable] = None):
        """Register a new tool."""
        tool_id = f"{namespace}.{name}"
        
        if tool_id in self.tools:
            logger.warning(f"Overwriting existing tool: {tool_id}")
        
        self.tools[tool_id] = {
            "name": name,
            "namespace": namespace,
            "description": description,
            "parameters": parameters,
            "returns": returns,
            "id": tool_id
        }
        
        if metadata:
            self.metadata[tool_id] = metadata
        
        if validator:
            self.validators[tool_id] = validator
        
        logger.info(f"Registered tool: {tool_id}")
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool by ID."""
        return self.tools.get(tool_id)
    
    def list_tools(self, 
                   namespace: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List tools with optional filters."""
        tools = list(self.tools.values())
        
        # Filter by namespace
        if namespace:
            tools = [t for t in tools if t["namespace"] == namespace]
        
        # Filter by tags
        if tags:
            filtered = []
            for tool in tools:
                tool_id = tool["id"]
                if tool_id in self.metadata:
                    tool_tags = self.metadata[tool_id].tags
                    if any(tag in tool_tags for tag in tags):
                        filtered.append(tool)
            tools = filtered
        
        return tools
    
    def validate_arguments(self, tool_id: str, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments."""
        tool = self.get_tool(tool_id)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_id}")
        
        # Basic schema validation
        params = tool["parameters"]
        required = params.get("required", [])
        properties = params.get("properties", {})
        
        # Check required parameters
        for req in required:
            if req not in arguments:
                logger.error(f"Missing required parameter: {req}")
                return False
        
        # Check types (simplified)
        for key, value in arguments.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type:
                    if not self._check_type(value, expected_type):
                        logger.error(f"Invalid type for {key}: expected {expected_type}")
                        return False
        
        # Custom validation
        if tool_id in self.validators:
            try:
                return self.validators[tool_id](arguments)
            except Exception as e:
                logger.error(f"Validation error: {e}")
                return False
        
        return True
    
    def _check_type(self, value: Any, expected: str) -> bool:
        """Simple type checking."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_type = type_map.get(expected, object)
        return isinstance(value, expected_type)
    
    def add_middleware(self, middleware: Callable):
        """Add middleware for tool execution."""
        self.middlewares.append(middleware)
    
    def export_registry(self, path: str):
        """Export registry to file."""
        data = {
            "tools": self.tools,
            "metadata": {
                k: {
                    "author": v.author,
                    "version": v.version,
                    "tags": v.tags,
                    "deprecated": v.deprecated,
                    "replacement": v.replacement
                }
                for k, v in self.metadata.items()
            }
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported registry to: {path}")
    
    def import_registry(self, path: str):
        """Import registry from file."""
        with open(path) as f:
            data = json.load(f)
        
        # Import tools
        for tool_id, tool_data in data.get("tools", {}).items():
            namespace, name = tool_id.split(".", 1)
            self.register_tool(
                namespace=namespace,
                name=name,
                description=tool_data["description"],
                parameters=tool_data["parameters"],
                returns=tool_data["returns"]
            )
        
        # Import metadata
        for tool_id, meta_data in data.get("metadata", {}).items():
            if tool_id in self.tools:
                self.metadata[tool_id] = ToolMetadata(**meta_data)
        
        logger.info(f"Imported {len(self.tools)} tools from: {path}")


# Global registry instance
global_registry = ToolRegistry()


def register_tool_decorator(namespace: str, **kwargs):
    """Decorator for registering tools."""
    def decorator(func: Callable):
        # Extract function metadata
        name = kwargs.get("name", func.__name__)
        description = kwargs.get("description", func.__doc__ or "")
        parameters = kwargs.get("parameters", {})
        returns = kwargs.get("returns", {"type": "any"})
        metadata = kwargs.get("metadata")
        
        # Register the tool
        global_registry.register_tool(
            namespace=namespace,
            name=name,
            description=description,
            parameters=parameters,
            returns=returns,
            metadata=metadata,
            validator=kwargs.get("validator")
        )
        
        # Return the original function
        return func
    
    return decorator


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Register some example tools
    @register_tool_decorator(
        namespace="example",
        description="Add two numbers",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        },
        returns={"type": "number"}
    )
    def add(a: float, b: float) -> float:
        return a + b
    
    # Test registry
    print(f"Registered tools: {len(global_registry.tools)}")
    print(f"Tools: {list(global_registry.tools.keys())}")
    
    # Test validation
    print(f"Valid args: {global_registry.validate_arguments('example.add', {'a': 1, 'b': 2})}")
    print(f"Invalid args: {global_registry.validate_arguments('example.add', {'a': 'not a number'})}")