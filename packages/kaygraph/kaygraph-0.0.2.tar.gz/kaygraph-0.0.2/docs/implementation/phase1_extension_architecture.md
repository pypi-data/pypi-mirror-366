# Phase 1: Extension Architecture - Detailed Implementation Guide

This guide provides exact code for implementing the extension architecture for KayGraph.

## Step 1: Create Directory Structure

```bash
# Run these commands from the KayGraph root directory
mkdir -p kaygraph/core
mkdir -p kaygraph/ext/base
mkdir -p kaygraph/ext/persistence/backends
mkdir -p kaygraph/ext/scheduler
mkdir -p kaygraph/ext/ui/api
mkdir -p kaygraph/ext/ui/frontend
mkdir -p kaygraph/ext/distributed/executors
mkdir -p kaygraph/ext/observability
mkdir -p kaygraph/plugins
mkdir -p kaygraph/utils
```

## Step 2: Move Core Files

First, backup the current structure, then move files:

```bash
# Move core files (assuming they exist in kaygraph/)
mv kaygraph/node.py kaygraph/core/
mv kaygraph/graph.py kaygraph/core/
mv kaygraph/base_node.py kaygraph/core/
mv kaygraph/batch_node.py kaygraph/core/
mv kaygraph/async_node.py kaygraph/core/
mv kaygraph/validated_node.py kaygraph/core/
mv kaygraph/metrics_node.py kaygraph/core/
mv kaygraph/exceptions.py kaygraph/core/
```

## Step 3: Create Core Re-exports

### File: `kaygraph/core/__init__.py`
```python
"""
KayGraph core functionality.

This module contains the core classes and functions that make up KayGraph.
All classes here have zero external dependencies.
"""

# Re-export everything that was in the original __init__.py
from .base_node import BaseNode
from .node import Node
from .graph import Graph
from .batch_node import BatchNode, BatchGraph
from .async_node import AsyncNode, AsyncGraph
from .validated_node import ValidatedNode
from .metrics_node import MetricsNode
from .exceptions import (
    KayGraphError,
    NodeExecutionError,
    GraphExecutionError,
    ValidationError
)

__all__ = [
    # Core classes
    "BaseNode",
    "Node", 
    "Graph",
    
    # Batch processing
    "BatchNode",
    "BatchGraph",
    
    # Async support
    "AsyncNode",
    "AsyncGraph",
    
    # Specialized nodes
    "ValidatedNode",
    "MetricsNode",
    
    # Exceptions
    "KayGraphError",
    "NodeExecutionError", 
    "GraphExecutionError",
    "ValidationError",
]

# Version info
__version__ = "1.0.0"
```

### File: `kaygraph/__init__.py`
```python
"""
KayGraph - A lightweight framework for building AI applications.

KayGraph provides a simple yet powerful abstraction for creating
AI workflows with nodes and graphs. The core library has zero
dependencies and can be extended with optional features.

Basic usage:
    >>> from kaygraph import Node, Graph
    >>> 
    >>> class MyNode(Node):
    ...     def exec(self, data):
    ...         return {"result": data["input"] * 2}
    >>> 
    >>> graph = Graph(start=MyNode())
    >>> graph.run({"input": 21})
    {"input": 21, "result": 42}

For production features, install extensions:
    pip install kaygraph[scheduler]    # Cron-based scheduling
    pip install kaygraph[persistence]  # State persistence
    pip install kaygraph[ui]          # Web dashboard
    pip install kaygraph[all]         # All extensions
"""

# Import core functionality
from kaygraph.core import (
    # Core classes
    BaseNode,
    Node,
    Graph,
    
    # Batch processing
    BatchNode,
    BatchGraph,
    
    # Async support  
    AsyncNode,
    AsyncGraph,
    
    # Specialized nodes
    ValidatedNode,
    MetricsNode,
    
    # Exceptions
    KayGraphError,
    NodeExecutionError,
    GraphExecutionError,
    ValidationError,
    
    # Version
    __version__,
)

# Extension imports are lazy-loaded
from kaygraph.utils.imports import LazyLoader

# Lazy load extensions
ext = LazyLoader("kaygraph.ext")
plugins = LazyLoader("kaygraph.plugins")

__all__ = [
    # Core classes
    "BaseNode",
    "Node",
    "Graph",
    
    # Batch processing
    "BatchNode", 
    "BatchGraph",
    
    # Async support
    "AsyncNode",
    "AsyncGraph",
    
    # Specialized nodes
    "ValidatedNode",
    "MetricsNode",
    
    # Exceptions
    "KayGraphError",
    "NodeExecutionError",
    "GraphExecutionError", 
    "ValidationError",
    
    # Extensions (lazy loaded)
    "ext",
    "plugins",
]

# Convenience function for checking available extensions
def list_extensions():
    """List installed KayGraph extensions."""
    extensions = {
        "scheduler": "Cron-based job scheduling",
        "persistence": "State persistence backends", 
        "ui": "Web dashboard and API",
        "distributed": "Distributed execution",
        "observability": "Tracing and metrics",
    }
    
    installed = []
    for name, description in extensions.items():
        try:
            __import__(f"kaygraph.ext.{name}")
            installed.append((name, description))
        except ImportError:
            pass
    
    return installed


def show_info():
    """Display KayGraph information and installed extensions."""
    print(f"KayGraph v{__version__}")
    print("\nCore Features:")
    print("  ✓ Zero-dependency graph execution")
    print("  ✓ Synchronous and async nodes")
    print("  ✓ Batch processing")
    print("  ✓ Validation and metrics")
    
    extensions = list_extensions()
    if extensions:
        print("\nInstalled Extensions:")
        for name, desc in extensions:
            print(f"  ✓ {name}: {desc}")
    else:
        print("\nNo extensions installed.")
        print("Install with: pip install kaygraph[all]")
```

### File: `kaygraph/utils/imports.py`
```python
"""
Import utilities for lazy loading and optional dependencies.
"""

import importlib
import sys
from types import ModuleType
from typing import Any, Optional


class LazyLoader(ModuleType):
    """
    Lazy loader for modules that may not be installed.
    
    This allows referencing optional modules without importing them
    until they are actually used.
    """
    
    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module: Optional[ModuleType] = None
        super().__init__(module_name)
    
    def _load(self):
        """Load the module if not already loaded."""
        if self._module is None:
            try:
                self._module = importlib.import_module(self._module_name)
            except ImportError as e:
                # Extract extension name
                parts = self._module_name.split(".")
                if len(parts) >= 3 and parts[1] == "ext":
                    ext_name = parts[2]
                    raise ImportError(
                        f"Extension '{ext_name}' is not installed. "
                        f"Install with: pip install kaygraph[{ext_name}]"
                    ) from e
                else:
                    raise
        return self._module
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute from the loaded module."""
        module = self._load()
        return getattr(module, name)
    
    def __dir__(self):
        """List available attributes."""
        module = self._load()
        return dir(module)


def optional_import(module_name: str, package: str = None):
    """
    Import a module that may not be installed.
    
    Args:
        module_name: Name of the module to import
        package: Package name for installation instructions
        
    Returns:
        The imported module or None if not available
        
    Example:
        redis = optional_import("redis", "redis")
        if redis is None:
            print("Redis not available, using memory backend")
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        if package:
            print(f"Optional dependency '{module_name}' not installed.")
            print(f"Install with: pip install {package}")
        return None


def require_extension(extension_name: str):
    """
    Decorator that checks if an extension is installed.
    
    Args:
        extension_name: Name of the required extension
        
    Example:
        @require_extension("scheduler")
        def create_scheduled_graph():
            from kaygraph.ext.scheduler import schedule
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                importlib.import_module(f"kaygraph.ext.{extension_name}")
            except ImportError:
                raise RuntimeError(
                    f"This feature requires the '{extension_name}' extension. "
                    f"Install with: pip install kaygraph[{extension_name}]"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### File: `kaygraph/ext/__init__.py`
```python
"""
KayGraph Extensions.

This namespace contains optional extensions that add production-ready
features to KayGraph. Each extension can be installed separately:

- persistence: State persistence with multiple backends
- scheduler: Cron-based job scheduling  
- ui: Web dashboard and monitoring
- distributed: Distributed graph execution
- observability: Metrics and tracing

Extensions are designed to be optional and composable. You can use
any combination of extensions based on your needs.
"""

from kaygraph.utils.imports import LazyLoader

# Lazy load all extensions
persistence = LazyLoader("kaygraph.ext.persistence")
scheduler = LazyLoader("kaygraph.ext.scheduler")
ui = LazyLoader("kaygraph.ext.ui")
distributed = LazyLoader("kaygraph.ext.distributed")
observability = LazyLoader("kaygraph.ext.observability")

__all__ = [
    "persistence",
    "scheduler", 
    "ui",
    "distributed",
    "observability",
]
```

### File: `kaygraph/ext/base.py`
```python
"""
Base classes and protocols for KayGraph extensions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
import logging


class Extension(ABC):
    """
    Base class for KayGraph extensions.
    
    All extensions should inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the extension.
        
        Args:
            config: Extension-specific configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the extension.
        
        This is called once when the extension is first used.
        Should set up any necessary resources.
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the extension.
        
        Clean up any resources used by the extension.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the extension name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Return the extension version."""
        pass
    
    @property
    def is_initialized(self) -> bool:
        """Check if the extension is initialized."""
        return self._initialized
    
    def ensure_initialized(self) -> None:
        """Ensure the extension is initialized."""
        if not self._initialized:
            self.logger.info(f"Initializing {self.name} extension v{self.version}")
            self.initialize()
            self._initialized = True


class ExtensionRegistry:
    """
    Registry for managing extensions.
    
    This allows extensions to register themselves and provides
    a central place to manage extension lifecycle.
    """
    
    def __init__(self):
        self._extensions: Dict[str, Extension] = {}
        self.logger = logging.getLogger("ExtensionRegistry")
    
    def register(self, extension: Extension) -> None:
        """Register an extension."""
        if extension.name in self._extensions:
            self.logger.warning(
                f"Extension '{extension.name}' already registered, replacing"
            )
        
        self._extensions[extension.name] = extension
        self.logger.info(f"Registered extension: {extension.name} v{extension.version}")
    
    def get(self, name: str) -> Optional[Extension]:
        """Get an extension by name."""
        extension = self._extensions.get(name)
        if extension:
            extension.ensure_initialized()
        return extension
    
    def list(self) -> Dict[str, Extension]:
        """List all registered extensions."""
        return self._extensions.copy()
    
    def shutdown_all(self) -> None:
        """Shutdown all extensions."""
        for name, extension in self._extensions.items():
            if extension.is_initialized:
                self.logger.info(f"Shutting down extension: {name}")
                try:
                    extension.shutdown()
                except Exception as e:
                    self.logger.error(f"Error shutting down {name}: {e}")


# Global extension registry
registry = ExtensionRegistry()


def get_extension(name: str) -> Optional[Extension]:
    """Get an extension from the global registry."""
    return registry.get(name)


def register_extension(extension: Extension) -> None:
    """Register an extension in the global registry."""
    registry.register(extension)
```

### File: `kaygraph/plugins/__init__.py`
```python
"""
KayGraph Plugin System.

Plugins are user-defined extensions that can add new functionality
to KayGraph without modifying the core library.

Creating a plugin:
    1. Create a package named 'kaygraph_yourplugin'
    2. Define a plugin_info() function that returns metadata
    3. Implement your plugin functionality
    4. Install the package

The plugin will be automatically discovered and can be loaded
using the plugin system.
"""

from .registry import PluginRegistry, discover_plugins, load_plugin

# Global plugin registry
registry = PluginRegistry()

# Auto-discover plugins on import
registry.discover()

__all__ = [
    "registry",
    "discover_plugins",
    "load_plugin",
]
```

### File: `kaygraph/plugins/registry.py`
```python
"""
Plugin discovery and management for KayGraph.
"""

import importlib
import pkgutil
import sys
from typing import Dict, Any, Optional, List
import logging


class PluginInfo:
    """Information about a plugin."""
    
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str = None,
        requires: List[str] = None,
        provides: Dict[str, Any] = None,
    ):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.requires = requires or []
        self.provides = provides or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "requires": self.requires,
            "provides": self.provides,
        }


class PluginRegistry:
    """Registry for discovering and managing plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded: Dict[str, Any] = {}
        self.logger = logging.getLogger("PluginRegistry")
    
    def discover(self) -> None:
        """
        Discover installed plugins.
        
        Looks for packages starting with 'kaygraph_' and attempts
        to load their plugin information.
        """
        discovered = 0
        
        # Search for kaygraph_* packages
        for finder, name, ispkg in pkgutil.iter_modules():
            if name.startswith("kaygraph_") and ispkg:
                try:
                    # Import the module
                    module = importlib.import_module(name)
                    
                    # Look for plugin_info function
                    if hasattr(module, "plugin_info"):
                        info = module.plugin_info()
                        if isinstance(info, dict):
                            plugin = PluginInfo(**info)
                        elif isinstance(info, PluginInfo):
                            plugin = info
                        else:
                            self.logger.warning(
                                f"Plugin {name} has invalid plugin_info"
                            )
                            continue
                        
                        self.plugins[name] = plugin
                        discovered += 1
                        self.logger.info(
                            f"Discovered plugin: {plugin.name} v{plugin.version}"
                        )
                    
                except Exception as e:
                    self.logger.error(f"Error loading plugin {name}: {e}")
        
        self.logger.info(f"Discovered {discovered} plugins")
    
    def load(self, name: str) -> Any:
        """
        Load a plugin.
        
        Args:
            name: Plugin name (package name)
            
        Returns:
            The loaded plugin module
        """
        if name in self.loaded:
            return self.loaded[name]
        
        if name not in self.plugins:
            raise ValueError(f"Plugin '{name}' not found")
        
        plugin_info = self.plugins[name]
        
        # Check requirements
        for req in plugin_info.requires:
            if req not in self.loaded and req != "kaygraph":
                self.logger.warning(
                    f"Plugin '{name}' requires '{req}' which is not loaded"
                )
        
        # Load the module
        try:
            module = importlib.import_module(name)
            
            # Initialize if needed
            if hasattr(module, "initialize"):
                module.initialize()
            
            self.loaded[name] = module
            self.logger.info(f"Loaded plugin: {name}")
            
            return module
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin '{name}': {e}")
            raise
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all discovered plugins."""
        return list(self.plugins.values())
    
    def get_plugin_info(self, name: str) -> Optional[PluginInfo]:
        """Get information about a plugin."""
        return self.plugins.get(name)
    
    def is_loaded(self, name: str) -> bool:
        """Check if a plugin is loaded."""
        return name in self.loaded


def discover_plugins() -> List[PluginInfo]:
    """Discover all available plugins."""
    registry = PluginRegistry()
    registry.discover()
    return registry.list_plugins()


def load_plugin(name: str) -> Any:
    """Load a plugin by name."""
    registry = PluginRegistry()
    registry.discover()
    return registry.load(name)
```

### File: `kaygraph/config.py`
```python
"""
Configuration management for KayGraph.

This module handles configuration from environment variables,
config files, and runtime settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class Config:
    """
    KayGraph configuration.
    
    Configuration is loaded from (in order of precedence):
    1. Environment variables (KAYGRAPH_*)
    2. Config file (kaygraph.json)
    3. Default values
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger("Config")
        self._config: Dict[str, Any] = {}
        self._load_defaults()
        self._load_from_file(config_file)
        self._load_from_env()
        self._detect_extensions()
    
    def _load_defaults(self) -> None:
        """Load default configuration."""
        self._config = {
            # Core settings
            "debug": False,
            "log_level": "INFO",
            
            # Extension settings (only used if extension is installed)
            "scheduler": {
                "enabled": False,
                "backend": "memory",
                "timezone": "UTC",
            },
            "persistence": {
                "backend": "memory",
                "ttl": 86400,  # 24 hours
            },
            "ui": {
                "enabled": False,
                "host": "0.0.0.0",
                "port": 8080,
            },
            "distributed": {
                "executor": "local",
                "workers": 4,
            },
            "observability": {
                "tracing_enabled": False,
                "metrics_enabled": False,
                "metrics_port": 9090,
            },
        }
    
    def _load_from_file(self, config_file: Optional[str]) -> None:
        """Load configuration from file."""
        if config_file is None:
            # Look for default locations
            locations = [
                "kaygraph.json",
                ".kaygraph.json",
                "~/.kaygraph/config.json",
                "/etc/kaygraph/config.json",
            ]
            
            for location in locations:
                path = Path(location).expanduser()
                if path.exists():
                    config_file = str(path)
                    break
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file) as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
                    self.logger.info(f"Loaded config from {config_file}")
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        prefix = "KAYGRAPH_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert KAYGRAPH_SCHEDULER_BACKEND to scheduler.backend
                parts = key[len(prefix):].lower().split("_")
                
                # Navigate to the right config section
                current = self._config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the value
                last_part = parts[-1]
                
                # Try to parse as JSON first (for complex values)
                try:
                    current[last_part] = json.loads(value)
                except json.JSONDecodeError:
                    # Handle booleans
                    if value.lower() in ("true", "false"):
                        current[last_part] = value.lower() == "true"
                    # Handle numbers
                    elif value.isdigit():
                        current[last_part] = int(value)
                    else:
                        current[last_part] = value
    
    def _detect_extensions(self) -> None:
        """Detect which extensions are installed."""
        extensions = []
        
        extension_names = [
            "scheduler", "persistence", "ui", 
            "distributed", "observability"
        ]
        
        for name in extension_names:
            try:
                __import__(f"kaygraph.ext.{name}")
                extensions.append(name)
            except ImportError:
                pass
        
        self._config["installed_extensions"] = extensions
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration into existing."""
        for key, value in new_config.items():
            if isinstance(value, dict) and key in self._config:
                if isinstance(self._config[key], dict):
                    self._config[key].update(value)
                else:
                    self._config[key] = value
            else:
                self._config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Supports dot notation: config.get("scheduler.backend")
        """
        parts = key.split(".")
        current = self._config
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Supports dot notation: config.set("scheduler.backend", "redis")
        """
        parts = key.split(".")
        current = self._config
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    @property
    def debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get("debug", False)
    
    @property
    def installed_extensions(self) -> List[str]:
        """Get list of installed extensions."""
        return self.get("installed_extensions", [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary."""
        return self._config.copy()


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def configure(**kwargs) -> None:
    """
    Configure KayGraph settings.
    
    Example:
        configure(debug=True, scheduler={"backend": "redis"})
    """
    for key, value in kwargs.items():
        if isinstance(value, dict) and key in config._config:
            config._config[key].update(value)
        else:
            config.set(key, value)
```

## Next Steps

After implementing Phase 1:

1. **Test the new structure** - Ensure all existing examples still work
2. **Update imports** - Change any direct imports to use the new structure
3. **Create extension stubs** - Add __init__.py files for each extension
4. **Update setup.py** - Add the new package structure and extras_require

This modular architecture will allow KayGraph to grow with production features while keeping the core simple and dependency-free!