"""
Code templates and generation utilities.

This module provides templates and generators for creating
code from requirements and designs.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ArchitectureDesigner:
    """Design code architecture from requirements."""
    
    def design(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create architecture design from requirements.
        
        Args:
            requirements: Parsed requirements
            
        Returns:
            Architecture design with components
        """
        code_type = requirements.get("type", "function")
        
        design = {
            "pattern": self._select_pattern(requirements),
            "components": [],
            "dependencies": [],
            "structure": {}
        }
        
        # Design based on type
        if code_type == "function":
            design["components"] = self._design_function_components(requirements)
        elif code_type == "class":
            design["components"] = self._design_class_components(requirements)
        elif code_type == "api":
            design["components"] = self._design_api_components(requirements)
        elif code_type == "script":
            design["components"] = self._design_script_components(requirements)
        
        # Add common components based on features
        self._add_feature_components(design, requirements.get("features", []))
        
        return design
    
    def _select_pattern(self, requirements: Dict[str, Any]) -> str:
        """Select appropriate design pattern."""
        features = requirements.get("features", [])
        
        if "database" in features:
            return "repository"
        elif "auth" in features:
            return "middleware"
        elif "caching" in features:
            return "decorator"
        elif requirements.get("type") == "class":
            specs = requirements.get("specifications", {})
            if specs.get("rate_limit"):
                return "singleton"
            return "factory" if len(specs.get("methods", [])) > 3 else "standard"
        
        return "standard"
    
    def _design_function_components(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design components for a function."""
        components = [{
            "name": requirements.get("name", "my_function"),
            "type": "function",
            "responsibility": "Main function implementation"
        }]
        
        # Add helper functions if needed
        specs = requirements.get("specifications", {})
        if specs.get("algorithm") == "dynamic_programming":
            components.append({
                "name": f"_{requirements.get('name', 'function')}_memo",
                "type": "cache",
                "responsibility": "Memoization cache"
            })
        
        return components
    
    def _design_class_components(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design components for a class."""
        class_name = requirements.get("name", "MyClass")
        components = [{
            "name": class_name,
            "type": "class",
            "responsibility": "Main class implementation"
        }]
        
        # Add methods
        methods = requirements.get("specifications", {}).get("methods", [])
        for method in methods:
            components.append({
                "name": method,
                "type": "method",
                "responsibility": f"Handle {method} operation"
            })
        
        return components
    
    def _design_api_components(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design components for an API endpoint."""
        return [
            {
                "name": requirements.get("name", "api_endpoint"),
                "type": "endpoint",
                "responsibility": "Handle HTTP requests"
            },
            {
                "name": "validate_request",
                "type": "function",
                "responsibility": "Validate input data"
            },
            {
                "name": "process_request",
                "type": "function",
                "responsibility": "Business logic processing"
            },
            {
                "name": "format_response",
                "type": "function",
                "responsibility": "Format output data"
            }
        ]
    
    def _design_script_components(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design components for a script."""
        return [
            {
                "name": "main",
                "type": "function",
                "responsibility": "Script entry point"
            },
            {
                "name": "parse_args",
                "type": "function",
                "responsibility": "Parse command line arguments"
            },
            {
                "name": requirements.get("name", "process"),
                "type": "function",
                "responsibility": "Main processing logic"
            }
        ]
    
    def _add_feature_components(self, design: Dict[str, Any], features: List[str]) -> None:
        """Add components based on required features."""
        if "logging" in features:
            design["components"].append({
                "name": "setup_logging",
                "type": "function",
                "responsibility": "Configure logging"
            })
        
        if "error_handling" in features:
            design["components"].append({
                "name": "handle_errors",
                "type": "decorator",
                "responsibility": "Error handling wrapper"
            })
        
        if "validation" in features:
            design["components"].append({
                "name": "validate_input",
                "type": "function",
                "responsibility": "Input validation"
            })


class CodeGenerator:
    """Generate code from requirements and design."""
    
    def __init__(self):
        """Initialize with language templates."""
        self.templates = {
            "python": {
                "function": self._python_function_template,
                "class": self._python_class_template,
                "api": self._python_api_template,
                "script": self._python_script_template
            },
            "javascript": {
                "function": self._javascript_function_template,
                "class": self._javascript_class_template,
                "api": self._javascript_api_template,
                "component": self._javascript_component_template
            }
        }
    
    def generate(self, requirements: Dict[str, Any], design: Dict[str, Any], 
                 previous_error: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate code from requirements and design.
        
        Args:
            requirements: Parsed requirements
            design: Architecture design
            previous_error: Previous generation error
            
        Returns:
            Generated code with metadata
        """
        language = requirements.get("language", "python")
        code_type = requirements.get("type", "function")
        
        # Get appropriate template
        template_func = self.templates.get(language, {}).get(code_type)
        if not template_func:
            # Fallback to function template
            template_func = self.templates[language]["function"]
        
        # Generate code
        code = template_func(requirements, design)
        
        # Fix previous errors if any
        if previous_error:
            code = self._fix_for_error(code, previous_error, language)
        
        return {
            "code": code,
            "language": language,
            "imports": self._extract_imports(code, language),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "requirements_hash": hash(str(requirements))
            }
        }
    
    def _python_function_template(self, req: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate Python function code."""
        name = req.get("name", "my_function")
        params = req.get("parameters", [])
        features = req.get("features", [])
        specs = req.get("specifications", {})
        
        # Build function
        code_lines = []
        
        # Add imports
        imports = []
        if "async" in features:
            imports.append("import asyncio")
        if "logging" in features:
            imports.append("import logging")
        if specs.get("algorithm") == "dynamic_programming":
            imports.append("from functools import lru_cache")
        
        if imports:
            code_lines.extend(imports)
            code_lines.append("")
        
        # Add decorator if needed
        if specs.get("algorithm") == "dynamic_programming":
            code_lines.append("@lru_cache(maxsize=None)")
        
        # Function definition
        if "async" in features:
            func_def = f"async def {name}({', '.join(params) if params else ''})"
        else:
            func_def = f"def {name}({', '.join(params) if params else ''})"
        
        code_lines.append(f"{func_def}:")
        
        # Docstring
        code_lines.append(f'    """')
        code_lines.append(f'    {req.get("original_description", "Function implementation")}')
        if params:
            code_lines.append('    ')
            code_lines.append('    Args:')
            for param in params:
                code_lines.append(f'        {param}: Parameter description')
        if specs.get("return_type"):
            code_lines.append('    ')
            code_lines.append('    Returns:')
            code_lines.append(f'        {specs["return_type"]}: Return value description')
        code_lines.append('    """')
        
        # Implementation
        if "fibonacci" in name.lower():
            code_lines.extend(self._fibonacci_implementation(params))
        elif "scrape" in name.lower():
            code_lines.extend(self._scraper_implementation(params, features))
        else:
            # Generic implementation
            code_lines.append('    # TODO: Implement function logic')
            if params:
                code_lines.append(f'    # Process parameters: {", ".join(params)}')
            code_lines.append('    result = None')
            if "async" in features:
                code_lines.append('    # await async_operation()')
            code_lines.append('    return result')
        
        return '\n'.join(code_lines)
    
    def _python_class_template(self, req: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate Python class code."""
        name = req.get("name", "MyClass")
        methods = req.get("specifications", {}).get("methods", [])
        features = req.get("features", [])
        pattern = design.get("pattern", "standard")
        
        code_lines = []
        
        # Add imports
        imports = []
        if "logging" in features:
            imports.append("import logging")
        if pattern == "singleton":
            imports.append("from typing import Optional")
        if "rate_limit" in req.get("specifications", {}):
            imports.append("import time")
            imports.append("from collections import deque")
        
        if imports:
            code_lines.extend(imports)
            code_lines.append("")
        
        # Class definition
        code_lines.append(f"class {name}:")
        code_lines.append(f'    """')
        code_lines.append(f'    {req.get("original_description", "Class implementation")}')
        code_lines.append('    """')
        
        # Singleton pattern
        if pattern == "singleton":
            code_lines.append('    ')
            code_lines.append('    _instance: Optional["' + name + '"] = None')
            code_lines.append('    ')
            code_lines.append('    def __new__(cls):')
            code_lines.append('        if cls._instance is None:')
            code_lines.append('            cls._instance = super().__new__(cls)')
            code_lines.append('        return cls._instance')
        
        # Constructor
        code_lines.append('    ')
        code_lines.append('    def __init__(self):')
        code_lines.append('        """Initialize the ' + name + '."""')
        
        # Initialize based on type
        if "todo" in name.lower() and "list" in name.lower():
            code_lines.append('        self.todos = []')
            code_lines.append('        self.completed = []')
        elif "rate" in name.lower() and "limit" in name.lower():
            specs = req.get("specifications", {})
            rate_limit = specs.get("rate_limit", {})
            count = rate_limit.get("count", 100)
            period = rate_limit.get("period", "minute")
            
            code_lines.append(f'        self.max_requests = {count}')
            code_lines.append(f'        self.time_window = {self._get_seconds(period)}  # {period}')
            code_lines.append('        self.requests = deque()')
        else:
            code_lines.append('        # Initialize instance variables')
            code_lines.append('        pass')
        
        # Add methods
        if methods:
            for method in methods:
                code_lines.extend(self._generate_method(method, name, req))
        else:
            # Add default method
            code_lines.append('    ')
            code_lines.append('    def process(self, data):')
            code_lines.append('        """Process the data."""')
            code_lines.append('        # TODO: Implement processing logic')
            code_lines.append('        return data')
        
        return '\n'.join(code_lines)
    
    def _python_api_template(self, req: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate Python API endpoint code."""
        name = req.get("name", "api_endpoint")
        features = req.get("features", [])
        
        code_lines = []
        
        # Framework selection
        if "fastapi" in req.get("language", ""):
            framework = "fastapi"
        elif "flask" in req.get("language", ""):
            framework = "flask"
        else:
            framework = "flask"  # Default
        
        # Imports
        if framework == "fastapi":
            code_lines.extend([
                "from fastapi import FastAPI, HTTPException",
                "from pydantic import BaseModel",
                "from typing import Optional"
            ])
        else:
            code_lines.extend([
                "from flask import Flask, request, jsonify",
                "from functools import wraps"
            ])
        
        if "auth" in features:
            code_lines.append("import jwt")
            code_lines.append("from datetime import datetime, timedelta")
        
        code_lines.append("")
        
        # App initialization
        if framework == "fastapi":
            code_lines.append("app = FastAPI()")
            code_lines.append("")
            
            # Request model
            code_lines.append("class RequestModel(BaseModel):")
            code_lines.append("    # Define request fields")
            code_lines.append("    data: str")
            code_lines.append("")
        else:
            code_lines.append("app = Flask(__name__)")
            code_lines.append("")
        
        # Auth decorator if needed
        if "auth" in features:
            code_lines.extend(self._generate_auth_decorator(framework))
        
        # Endpoint implementation
        if framework == "fastapi":
            code_lines.append(f"@app.post('/{name}')")
            if "auth" in features:
                code_lines.append("@require_auth")
            code_lines.append(f"async def {name}(request: RequestModel):")
        else:
            code_lines.append(f"@app.route('/{name}', methods=['POST'])")
            if "auth" in features:
                code_lines.append("@require_auth")
            code_lines.append(f"def {name}():")
        
        code_lines.append(f'    """Handle {name} endpoint."""')
        code_lines.append('    try:')
        
        if framework == "fastapi":
            code_lines.append('        # Process request')
            code_lines.append('        result = process_data(request.data)')
            code_lines.append('        return {"status": "success", "data": result}')
        else:
            code_lines.append('        # Get request data')
            code_lines.append('        data = request.get_json()')
            code_lines.append('        ')
            code_lines.append('        # Process request')
            code_lines.append('        result = process_data(data)')
            code_lines.append('        ')
            code_lines.append('        return jsonify({"status": "success", "data": result})')
        
        code_lines.append('    except Exception as e:')
        
        if framework == "fastapi":
            code_lines.append('        raise HTTPException(status_code=500, detail=str(e))')
        else:
            code_lines.append('        return jsonify({"status": "error", "message": str(e)}), 500')
        
        # Helper function
        code_lines.append('')
        code_lines.append('')
        code_lines.append('def process_data(data):')
        code_lines.append('    """Process the input data."""')
        code_lines.append('    # TODO: Implement processing logic')
        code_lines.append('    return data')
        
        return '\n'.join(code_lines)
    
    def _python_script_template(self, req: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate Python script code."""
        name = req.get("name", "script")
        features = req.get("features", [])
        
        code_lines = [
            "#!/usr/bin/env python3",
            '"""',
            f'{req.get("original_description", "Script implementation")}',
            '"""',
            '',
            'import argparse',
            'import sys'
        ]
        
        if "logging" in features:
            code_lines.append('import logging')
        if "async" in features:
            code_lines.append('import asyncio')
        
        code_lines.extend(['', ''])
        
        # Argument parser
        code_lines.append('def parse_args():')
        code_lines.append('    """Parse command line arguments."""')
        code_lines.append('    parser = argparse.ArgumentParser(')
        code_lines.append(f'        description="{req.get("original_description", "Script")}"')
        code_lines.append('    )')
        code_lines.append('    ')
        code_lines.append('    # Add arguments')
        code_lines.append('    parser.add_argument("input", help="Input file or data")')
        code_lines.append('    parser.add_argument("-o", "--output", help="Output file")')
        code_lines.append('    parser.add_argument("-v", "--verbose", action="store_true",')
        code_lines.append('                        help="Enable verbose logging")')
        code_lines.append('    ')
        code_lines.append('    return parser.parse_args()')
        code_lines.append('')
        code_lines.append('')
        
        # Main processing function
        if "async" in features:
            code_lines.append(f'async def {name}(args):')
        else:
            code_lines.append(f'def {name}(args):')
        code_lines.append('    """Main processing function."""')
        code_lines.append('    # TODO: Implement main logic')
        code_lines.append('    print(f"Processing {args.input}")')
        if "async" in features:
            code_lines.append('    # await async_operation()')
        code_lines.append('    ')
        code_lines.append('    if args.output:')
        code_lines.append('        print(f"Writing output to {args.output}")')
        code_lines.append('    ')
        code_lines.append('    return 0')
        code_lines.append('')
        code_lines.append('')
        
        # Main entry point
        if "async" in features:
            code_lines.append('async def main():')
        else:
            code_lines.append('def main():')
        code_lines.append('    """Script entry point."""')
        code_lines.append('    args = parse_args()')
        code_lines.append('    ')
        
        if "logging" in features:
            code_lines.append('    # Setup logging')
            code_lines.append('    logging.basicConfig(')
            code_lines.append('        level=logging.DEBUG if args.verbose else logging.INFO,')
            code_lines.append('        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"')
            code_lines.append('    )')
            code_lines.append('    ')
        
        code_lines.append('    try:')
        if "async" in features:
            code_lines.append(f'        return await {name}(args)')
        else:
            code_lines.append(f'        return {name}(args)')
        code_lines.append('    except Exception as e:')
        code_lines.append('        print(f"Error: {e}", file=sys.stderr)')
        code_lines.append('        return 1')
        code_lines.append('')
        code_lines.append('')
        code_lines.append('if __name__ == "__main__":')
        if "async" in features:
            code_lines.append('    sys.exit(asyncio.run(main()))')
        else:
            code_lines.append('    sys.exit(main())')
        
        return '\n'.join(code_lines)
    
    def _javascript_function_template(self, req: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate JavaScript function code."""
        name = req.get("name", "myFunction")
        params = req.get("parameters", [])
        features = req.get("features", [])
        
        code_lines = []
        
        # Function definition
        if "async" in features:
            code_lines.append(f"async function {name}({', '.join(params)}) {{")
        else:
            code_lines.append(f"function {name}({', '.join(params)}) {{")
        
        # JSDoc
        code_lines.append("  /**")
        code_lines.append(f"   * {req.get('original_description', 'Function implementation')}")
        for param in params:
            code_lines.append(f"   * @param {{any}} {param} - Parameter description")
        code_lines.append("   * @returns {{}} Return value")
        code_lines.append("   */")
        
        # Implementation
        code_lines.append("  ")
        code_lines.append("  // TODO: Implement function logic")
        if "async" in features:
            code_lines.append("  // const result = await asyncOperation();")
        code_lines.append("  const result = null;")
        code_lines.append("  return result;")
        code_lines.append("}")
        
        # Export
        code_lines.append("")
        code_lines.append(f"module.exports = {{ {name} }};")
        
        return '\n'.join(code_lines)
    
    def _javascript_class_template(self, req: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate JavaScript class code."""
        name = req.get("name", "MyClass")
        methods = req.get("specifications", {}).get("methods", [])
        
        code_lines = []
        
        # Class definition
        code_lines.append(f"class {name} {{")
        
        # Constructor
        code_lines.append("  constructor() {")
        code_lines.append(f"    // Initialize {name}")
        
        if "todo" in name.lower():
            code_lines.append("    this.todos = [];")
            code_lines.append("    this.completed = [];")
        else:
            code_lines.append("    // TODO: Initialize properties")
        
        code_lines.append("  }")
        
        # Methods
        if methods:
            for method in methods:
                code_lines.append("")
                code_lines.append(f"  {method}(...args) {{")
                code_lines.append(f"    // TODO: Implement {method}")
                code_lines.append("    return null;")
                code_lines.append("  }")
        
        code_lines.append("}")
        code_lines.append("")
        code_lines.append(f"module.exports = {name};")
        
        return '\n'.join(code_lines)
    
    def _javascript_api_template(self, req: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate JavaScript API endpoint code."""
        name = req.get("name", "apiEndpoint")
        
        code_lines = [
            "const express = require('express');",
            "const router = express.Router();",
            "",
            f"// {req.get('original_description', 'API endpoint')}",
            f"router.post('/{name}', async (req, res) => {{",
            "  try {",
            "    const { data } = req.body;",
            "    ",
            "    // TODO: Implement endpoint logic",
            "    const result = await processData(data);",
            "    ",
            "    res.json({",
            "      status: 'success',",
            "      data: result",
            "    });",
            "  } catch (error) {",
            "    res.status(500).json({",
            "      status: 'error',",
            "      message: error.message",
            "    });",
            "  }",
            "});",
            "",
            "async function processData(data) {",
            "  // TODO: Implement processing",
            "  return data;",
            "}",
            "",
            "module.exports = router;"
        ]
        
        return '\n'.join(code_lines)
    
    def _javascript_component_template(self, req: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate JavaScript React component code."""
        name = req.get("name", "MyComponent")
        
        code_lines = [
            "import React, { useState, useEffect } from 'react';",
            "",
            f"function {name}(props) {{",
            "  // Component state",
            "  const [data, setData] = useState(null);",
            "  const [loading, setLoading] = useState(false);",
            "  ",
            "  useEffect(() => {",
            "    // Component lifecycle",
            "  }, []);",
            "  ",
            "  return (",
            "    <div>",
            f"      <h1>{name}</h1>",
            "      {/* TODO: Implement component UI */}",
            "    </div>",
            "  );",
            "}",
            "",
            f"export default {name};"
        ]
        
        return '\n'.join(code_lines)
    
    def _fibonacci_implementation(self, params: List[str]) -> List[str]:
        """Generate fibonacci implementation."""
        param = params[0] if params else "n"
        return [
            f'    if {param} < 0:',
            f'        raise ValueError("Input must be non-negative")',
            f'    if {param} <= 1:',
            f'        return {param}',
            f'    return {param[0] if param else ""}fibonacci({param} - 1) + {param[0] if param else ""}fibonacci({param} - 2)'
        ]
    
    def _scraper_implementation(self, params: List[str], features: List[str]) -> List[str]:
        """Generate web scraper implementation."""
        lines = [
            '    import requests',
            '    from bs4 import BeautifulSoup',
            '    ',
            f'    # Fetch the webpage',
            f'    response = requests.get({params[0] if params else "url"})',
            '    response.raise_for_status()',
            '    ',
            '    # Parse HTML',
            '    soup = BeautifulSoup(response.text, "html.parser")',
            '    ',
            '    # Extract data',
            '    titles = []',
            '    for article in soup.find_all("article"):',
            '        title = article.find("h2")',
            '        if title:',
            '            titles.append(title.text.strip())',
            '    ',
            '    return titles'
        ]
        
        if "async" in features:
            # Convert to async version
            lines[1] = '    import aiohttp'
            lines[2] = '    from bs4 import BeautifulSoup'
            lines[4] = '    # Fetch the webpage asynchronously'
            lines[5] = f'    async with aiohttp.ClientSession() as session:'
            lines.insert(6, f'        async with session.get({params[0] if params else "url"}) as response:')
            lines[7] = '            html = await response.text()'
            
        return lines
    
    def _generate_method(self, method_name: str, class_name: str, req: Dict[str, Any]) -> List[str]:
        """Generate a class method."""
        lines = ['    ', f'    def {method_name}(self']
        
        # Add parameters based on method name
        if method_name in ["add", "remove", "complete"]:
            lines[1] += ", item"
        elif method_name == "is_allowed":
            lines[1] += ""
        
        lines[1] += "):"
        lines.append(f'        """Handle {method_name} operation."""')
        
        # Method implementation based on class and method
        if "todo" in class_name.lower():
            if method_name == "add":
                lines.extend([
                    '        self.todos.append(item)',
                    '        return len(self.todos) - 1'
                ])
            elif method_name == "remove":
                lines.extend([
                    '        if 0 <= item < len(self.todos):',
                    '            return self.todos.pop(item)',
                    '        return None'
                ])
            elif method_name == "complete":
                lines.extend([
                    '        if 0 <= item < len(self.todos):',
                    '            completed_item = self.todos.pop(item)',
                    '            self.completed.append(completed_item)',
                    '            return True',
                    '        return False'
                ])
            elif method_name == "list_all":
                lines.extend([
                    '        return {',
                    '            "todos": self.todos.copy(),',
                    '            "completed": self.completed.copy()',
                    '        }'
                ])
        elif "rate" in class_name.lower() and "limit" in class_name.lower():
            if method_name == "is_allowed":
                lines.extend([
                    '        current_time = time.time()',
                    '        ',
                    '        # Remove old requests outside time window',
                    '        while self.requests and self.requests[0] < current_time - self.time_window:',
                    '            self.requests.popleft()',
                    '        ',
                    '        # Check if under limit',
                    '        if len(self.requests) < self.max_requests:',
                    '            self.requests.append(current_time)',
                    '            return True',
                    '        return False'
                ])
            elif method_name == "reset":
                lines.extend([
                    '        self.requests.clear()',
                    '        return True'
                ])
            elif method_name == "get_remaining":
                lines.extend([
                    '        current_time = time.time()',
                    '        ',
                    '        # Remove old requests',
                    '        while self.requests and self.requests[0] < current_time - self.time_window:',
                    '            self.requests.popleft()',
                    '        ',
                    '        return max(0, self.max_requests - len(self.requests))'
                ])
        else:
            lines.extend([
                '        # TODO: Implement method logic',
                '        pass'
            ])
        
        return lines
    
    def _generate_auth_decorator(self, framework: str) -> List[str]:
        """Generate authentication decorator."""
        if framework == "fastapi":
            return [
                'def require_auth(func):',
                '    """Require authentication for endpoint."""',
                '    async def wrapper(*args, **kwargs):',
                '        # TODO: Implement auth check',
                '        # token = get_token_from_request()',
                '        # if not verify_token(token):',
                '        #     raise HTTPException(status_code=401, detail="Unauthorized")',
                '        return await func(*args, **kwargs)',
                '    return wrapper',
                ''
            ]
        else:
            return [
                'def require_auth(f):',
                '    """Require authentication for endpoint."""',
                '    @wraps(f)',
                '    def decorated_function(*args, **kwargs):',
                '        # TODO: Implement auth check',
                '        # token = request.headers.get("Authorization")',
                '        # if not verify_token(token):',
                '        #     return jsonify({"error": "Unauthorized"}), 401',
                '        return f(*args, **kwargs)',
                '    return decorated_function',
                ''
            ]
    
    def _get_seconds(self, period: str) -> int:
        """Convert period to seconds."""
        periods = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400
        }
        return periods.get(period.lower(), 60)
    
    def _extract_imports(self, code: str, language: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        
        if language == "python":
            for line in code.split('\n'):
                if line.strip().startswith(('import ', 'from ')):
                    imports.append(line.strip())
        elif language == "javascript":
            for line in code.split('\n'):
                if 'require(' in line or line.strip().startswith('import '):
                    imports.append(line.strip())
        
        return imports
    
    def _fix_for_error(self, code: str, error: str, language: str) -> str:
        """Attempt to fix code based on error."""
        # Simple fixes for common errors
        if "divide by zero" in error.lower():
            # Add zero check
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if '/' in line and not 'if' in lines[i-1] if i > 0 else True:
                    # Add check before division
                    indent = len(line) - len(line.lstrip())
                    lines.insert(i, ' ' * indent + 'if denominator != 0:')
                    lines[i+1] = '    ' + lines[i+1]
                    lines.insert(i+2, ' ' * indent + 'else:')
                    lines.insert(i+3, ' ' * indent + '    raise ValueError("Cannot divide by zero")')
                    break
            code = '\n'.join(lines)
        
        return code


if __name__ == "__main__":
    # Test the generators
    designer = ArchitectureDesigner()
    generator = CodeGenerator()
    
    test_req = {
        "type": "class",
        "name": "TodoList",
        "language": "python",
        "specifications": {
            "methods": ["add", "remove", "complete", "list_all"]
        }
    }
    
    design = designer.design(test_req)
    print("Design:", design)
    
    code = generator.generate(test_req, design)
    print("\nGenerated Code:")
    print(code["code"])