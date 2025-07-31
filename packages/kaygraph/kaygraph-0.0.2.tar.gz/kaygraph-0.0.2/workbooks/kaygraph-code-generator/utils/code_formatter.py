"""
Code formatting and documentation utilities.

This module provides code refactoring and documentation generation
capabilities.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CodeRefactorer:
    """Refactor code for better quality and performance."""
    
    def __init__(self, language: str = "python"):
        """
        Initialize refactorer for specific language.
        
        Args:
            language: Programming language
        """
        self.language = language
        self.refactorers = {
            "python": self._refactor_python,
            "javascript": self._refactor_javascript
        }
    
    def refactor(self, code: str, style_guide: str = "default") -> Dict[str, Any]:
        """
        Refactor code for improvements.
        
        Args:
            code: Source code to refactor
            style_guide: Style guide to follow
            
        Returns:
            Refactored code with improvements list
        """
        refactorer = self.refactorers.get(self.language, self._refactor_generic)
        return refactorer(code, style_guide)
    
    def _refactor_python(self, code: str, style_guide: str) -> Dict[str, Any]:
        """Refactor Python code."""
        improvements = []
        lines = code.split('\n')
        refactored_lines = []
        
        # Track improvements
        imports_organized = False
        constants_extracted = False
        
        # Process imports first
        imports = []
        other_lines = []
        
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line)
            else:
                other_lines.append(line)
        
        # Organize imports
        if imports:
            # Standard library imports
            stdlib = []
            third_party = []
            local = []
            
            for imp in imports:
                if imp.strip().startswith('from .'):
                    local.append(imp)
                elif any(mod in imp for mod in ['asyncio', 'logging', 'time', 'sys', 'os', 'json']):
                    stdlib.append(imp)
                else:
                    third_party.append(imp)
            
            # Sort each group
            stdlib.sort()
            third_party.sort()
            local.sort()
            
            # Rebuild with groups
            organized_imports = []
            if stdlib:
                organized_imports.extend(stdlib)
            if third_party:
                if stdlib:
                    organized_imports.append('')
                organized_imports.extend(third_party)
            if local:
                if stdlib or third_party:
                    organized_imports.append('')
                organized_imports.extend(local)
            
            if organized_imports != imports:
                improvements.append("Organized imports by category")
                imports_organized = True
            
            refactored_lines.extend(organized_imports)
            if organized_imports:
                refactored_lines.append('')
        
        # Process rest of code
        for i, line in enumerate(other_lines):
            # Extract magic numbers as constants
            if re.search(r'\b\d{2,}\b', line) and not line.strip().startswith('#'):
                # Found magic number
                match = re.search(r'\b(\d{2,})\b', line)
                if match:
                    number = match.group(1)
                    const_name = f"DEFAULT_VALUE_{number}"
                    
                    # Add constant definition at module level
                    if not constants_extracted:
                        refactored_lines.insert(len(organized_imports) + 1, f"{const_name} = {number}")
                        refactored_lines.insert(len(organized_imports) + 2, '')
                        improvements.append("Extracted magic numbers as constants")
                        constants_extracted = True
                    
                    # Replace in line
                    line = line.replace(number, const_name)
            
            # Improve string formatting
            if '".format(' in line or "'.format(" in line:
                # Convert to f-strings (Python 3.6+)
                line = self._convert_to_fstring(line)
                if '".format(' not in line and "'.format(" not in line:
                    improvements.append("Converted .format() to f-strings")
            
            # Add type hints for function definitions
            if line.strip().startswith('def ') and ':' in line and '->' not in line:
                # Simple type hint addition
                if '(self)' in line:
                    line = line.replace('):', ') -> None:')
                elif '()' in line:
                    line = line.replace('):', ') -> None:')
                improvements.append("Added return type hints")
            
            refactored_lines.append(line)
        
        # Calculate metrics
        metrics = {
            "lines_of_code": len([l for l in refactored_lines if l.strip() and not l.strip().startswith('#')]),
            "comment_lines": len([l for l in refactored_lines if l.strip().startswith('#')]),
            "blank_lines": len([l for l in refactored_lines if not l.strip()]),
            "functions": len([l for l in refactored_lines if l.strip().startswith('def ')]),
            "classes": len([l for l in refactored_lines if l.strip().startswith('class ')])
        }
        
        # Remove duplicate improvements
        improvements = list(dict.fromkeys(improvements))
        
        return {
            "code": '\n'.join(refactored_lines),
            "improvements": improvements,
            "metrics": metrics
        }
    
    def _refactor_javascript(self, code: str, style_guide: str) -> Dict[str, Any]:
        """Refactor JavaScript code."""
        improvements = []
        lines = code.split('\n')
        refactored_lines = []
        
        for line in lines:
            # Convert var to let/const
            if line.strip().startswith('var '):
                # Determine if it's reassigned
                var_name = re.search(r'var\s+(\w+)', line)
                if var_name:
                    name = var_name.group(1)
                    # Check if reassigned in rest of code
                    reassigned = any(
                        re.search(rf'{name}\s*=', l) 
                        for l in lines[lines.index(line)+1:]
                    )
                    
                    if reassigned:
                        line = line.replace('var ', 'let ', 1)
                    else:
                        line = line.replace('var ', 'const ', 1)
                    improvements.append("Replaced var with let/const")
            
            # Use arrow functions for callbacks
            if 'function(' in line and 'callback' in line.lower():
                # Convert to arrow function
                line = re.sub(r'function\s*\((.*?)\)\s*{', r'(\1) => {', line)
                improvements.append("Converted callbacks to arrow functions")
            
            # Use template literals
            if "' + " in line or '" + ' in line:
                line = self._convert_to_template_literal(line)
                improvements.append("Used template literals")
            
            refactored_lines.append(line)
        
        # Remove duplicate improvements
        improvements = list(dict.fromkeys(improvements))
        
        metrics = {
            "lines_of_code": len([l for l in refactored_lines if l.strip() and not l.strip().startswith('//')]),
            "functions": len([l for l in refactored_lines if 'function' in l or '=>' in l]),
            "async_functions": len([l for l in refactored_lines if 'async' in l])
        }
        
        return {
            "code": '\n'.join(refactored_lines),
            "improvements": improvements,
            "metrics": metrics
        }
    
    def _refactor_generic(self, code: str, style_guide: str) -> Dict[str, Any]:
        """Generic refactoring."""
        improvements = []
        lines = code.split('\n')
        
        # Basic improvements
        # Remove trailing whitespace
        refactored_lines = [line.rstrip() for line in lines]
        if any(line != refactored for line, refactored in zip(lines, refactored_lines)):
            improvements.append("Removed trailing whitespace")
        
        # Ensure file ends with newline
        if refactored_lines and refactored_lines[-1]:
            refactored_lines.append('')
            improvements.append("Added newline at end of file")
        
        return {
            "code": '\n'.join(refactored_lines),
            "improvements": improvements,
            "metrics": {}
        }
    
    def _convert_to_fstring(self, line: str) -> str:
        """Convert .format() to f-string."""
        # Simple conversion for basic cases
        pattern = r'(["\'])([^"\']*)\1\.format\((.*?)\)'
        
        def replace_format(match):
            quote = match.group(1)
            template = match.group(2)
            args = match.group(3).split(',')
            
            # Replace {} with {arg}
            for i, arg in enumerate(args):
                arg = arg.strip()
                template = template.replace('{}', f'{{{arg}}}', 1)
            
            return f'f{quote}{template}{quote}'
        
        return re.sub(pattern, replace_format, line)
    
    def _convert_to_template_literal(self, line: str) -> str:
        """Convert string concatenation to template literals."""
        # Pattern for string concatenation
        pattern = r'(["\'])([^"\']*)\1\s*\+\s*(\w+)\s*\+\s*(["\'])([^"\']*)\4'
        
        def replace_concat(match):
            str1 = match.group(2)
            var = match.group(3)
            str2 = match.group(5)
            return f'`{str1}${{{var}}}{str2}`'
        
        return re.sub(pattern, replace_concat, line)


class CodeDocumenter:
    """Add documentation to code."""
    
    def __init__(self, language: str = "python"):
        """
        Initialize documenter for specific language.
        
        Args:
            language: Programming language
        """
        self.language = language
        self.documenters = {
            "python": self._document_python,
            "javascript": self._document_javascript
        }
    
    def document(self, code: str, requirements: Dict[str, Any], 
                 design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add documentation to code.
        
        Args:
            code: Source code to document
            requirements: Original requirements
            design: Architecture design
            
        Returns:
            Documented code with additional docs
        """
        documenter = self.documenters.get(self.language, self._document_generic)
        return documenter(code, requirements, design)
    
    def _document_python(self, code: str, requirements: Dict[str, Any], 
                        design: Dict[str, Any]) -> Dict[str, Any]:
        """Document Python code."""
        lines = code.split('\n')
        documented_lines = []
        
        # Add module docstring if missing
        if not lines[0].startswith('"""') and not lines[0].startswith('#!'):
            module_doc = [
                '"""',
                f'{requirements.get("original_description", "Module implementation")}',
                '',
                f'Generated on: {datetime.now().strftime("%Y-%m-%d")}',
                '"""',
                ''
            ]
            documented_lines.extend(module_doc)
        
        # Process code
        in_class = False
        in_function = False
        class_name = None
        
        for i, line in enumerate(lines):
            # Add class documentation
            if line.strip().startswith('class '):
                in_class = True
                class_name = re.search(r'class\s+(\w+)', line).group(1)
                documented_lines.append(line)
                
                # Check if next line is already a docstring
                if i + 1 < len(lines) and not lines[i + 1].strip().startswith('"""'):
                    indent = '    '
                    doc = [
                        f'{indent}"""',
                        f'{indent}{class_name} implementation.',
                        f'{indent}',
                        f'{indent}This class {self._get_class_description(class_name, requirements)}',
                        f'{indent}"""'
                    ]
                    documented_lines.extend(doc)
                continue
            
            # Add function documentation
            if line.strip().startswith('def '):
                in_function = True
                func_match = re.search(r'def\s+(\w+)\((.*?)\)', line)
                if func_match:
                    func_name = func_match.group(1)
                    params = [p.strip() for p in func_match.group(2).split(',') if p.strip() and p.strip() != 'self']
                    
                    documented_lines.append(line)
                    
                    # Check if next line is already a docstring
                    if i + 1 < len(lines) and not lines[i + 1].strip().startswith('"""'):
                        indent = '    ' if not in_class else '        '
                        doc = [f'{indent}"""']
                        
                        # Add description
                        desc = self._get_function_description(func_name, class_name, requirements)
                        doc.append(f'{indent}{desc}')
                        
                        # Add parameters
                        if params:
                            doc.append(f'{indent}')
                            doc.append(f'{indent}Args:')
                            for param in params:
                                param_desc = self._get_param_description(param, func_name)
                                doc.append(f'{indent}    {param}: {param_desc}')
                        
                        # Add return documentation
                        if '->' in line:
                            return_type = line.split('->')[1].strip().rstrip(':')
                            doc.append(f'{indent}')
                            doc.append(f'{indent}Returns:')
                            doc.append(f'{indent}    {return_type}: {self._get_return_description(func_name)}')
                        
                        # Add raises if error handling present
                        if i + 10 < len(lines):
                            next_lines = '\n'.join(lines[i+1:i+10])
                            if 'raise' in next_lines:
                                doc.append(f'{indent}')
                                doc.append(f'{indent}Raises:')
                                doc.append(f'{indent}    Exception: If an error occurs')
                        
                        doc.append(f'{indent}"""')
                        documented_lines.extend(doc)
                    continue
            
            documented_lines.append(line)
        
        # Generate README
        readme = self._generate_readme(requirements, design)
        
        # Generate API docs
        api_docs = self._generate_api_docs(documented_lines, requirements)
        
        return {
            "code": '\n'.join(documented_lines),
            "readme": readme,
            "api_docs": api_docs
        }
    
    def _document_javascript(self, code: str, requirements: Dict[str, Any], 
                           design: Dict[str, Any]) -> Dict[str, Any]:
        """Document JavaScript code."""
        lines = code.split('\n')
        documented_lines = []
        
        # Add file header
        if not lines[0].startswith('/**'):
            header = [
                '/**',
                f' * {requirements.get("original_description", "Module implementation")}',
                f' * @module {requirements.get("name", "module")}',
                f' * @generated {datetime.now().strftime("%Y-%m-%d")}',
                ' */',
                ''
            ]
            documented_lines.extend(header)
        
        # Process code
        for i, line in enumerate(lines):
            # Document functions
            if 'function' in line or '=>' in line:
                func_match = re.search(r'function\s+(\w+)\((.*?)\)', line)
                if not func_match:
                    # Arrow function
                    func_match = re.search(r'const\s+(\w+)\s*=.*?\((.*?)\)\s*=>', line)
                
                if func_match:
                    func_name = func_match.group(1)
                    params = [p.strip() for p in func_match.group(2).split(',') if p.strip()]
                    
                    # Add JSDoc
                    if i == 0 or not lines[i-1].strip().startswith('/**'):
                        jsdoc = ['/**']
                        jsdoc.append(f' * {self._get_function_description(func_name, None, requirements)}')
                        
                        for param in params:
                            jsdoc.append(f' * @param {{any}} {param} - {self._get_param_description(param, func_name)}')
                        
                        jsdoc.append(f' * @returns {{}} {self._get_return_description(func_name)}')
                        jsdoc.append(' */')
                        
                        documented_lines.extend(jsdoc)
            
            documented_lines.append(line)
        
        # Generate README
        readme = self._generate_readme(requirements, design)
        
        return {
            "code": '\n'.join(documented_lines),
            "readme": readme,
            "api_docs": ""
        }
    
    def _document_generic(self, code: str, requirements: Dict[str, Any], 
                         design: Dict[str, Any]) -> Dict[str, Any]:
        """Generic documentation."""
        # Just add a header comment
        header = f"# {requirements.get('original_description', 'Code implementation')}\n# Generated on: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        return {
            "code": header + code,
            "readme": self._generate_readme(requirements, design),
            "api_docs": ""
        }
    
    def _get_class_description(self, class_name: str, requirements: Dict[str, Any]) -> str:
        """Generate class description."""
        desc = requirements.get("original_description", "").lower()
        
        if "todo" in class_name.lower():
            return "manages a todo list with add, remove, and complete functionality."
        elif "rate" in class_name.lower() and "limit" in class_name.lower():
            return "implements rate limiting to control API request frequency."
        else:
            return f"implements {desc}."
    
    def _get_function_description(self, func_name: str, class_name: Optional[str], 
                                 requirements: Dict[str, Any]) -> str:
        """Generate function description."""
        func_lower = func_name.lower()
        
        # Common function descriptions
        descriptions = {
            "add": "Add an item to the collection.",
            "remove": "Remove an item from the collection.",
            "complete": "Mark an item as completed.",
            "list_all": "List all items in the collection.",
            "is_allowed": "Check if an action is allowed under current limits.",
            "reset": "Reset the state to initial values.",
            "get_remaining": "Get the remaining allowed count.",
            "fibonacci": "Calculate the nth Fibonacci number.",
            "process": "Process the input data.",
            "validate": "Validate the input parameters.",
            "main": "Main entry point of the program."
        }
        
        return descriptions.get(func_lower, f"Handle {func_name} operation.")
    
    def _get_param_description(self, param: str, func_name: str) -> str:
        """Generate parameter description."""
        param_lower = param.lower()
        
        # Common parameter descriptions
        descriptions = {
            "n": "The position in the sequence",
            "item": "The item to process",
            "data": "Input data to process",
            "url": "The URL to fetch",
            "args": "Command line arguments",
            "request": "The HTTP request object",
            "response": "The HTTP response object"
        }
        
        return descriptions.get(param_lower, f"The {param} parameter")
    
    def _get_return_description(self, func_name: str) -> str:
        """Generate return value description."""
        func_lower = func_name.lower()
        
        # Common return descriptions
        descriptions = {
            "add": "The index of the added item",
            "remove": "The removed item or None",
            "complete": "True if successful, False otherwise",
            "is_allowed": "True if allowed, False otherwise",
            "fibonacci": "The Fibonacci number at position n",
            "validate": "Validation result",
            "process": "Processed data"
        }
        
        return descriptions.get(func_lower, "The operation result")
    
    def _generate_readme(self, requirements: Dict[str, Any], design: Dict[str, Any]) -> str:
        """Generate README documentation."""
        readme = [
            f"# {requirements.get('name', 'Project')}",
            "",
            f"{requirements.get('original_description', 'Project implementation')}",
            "",
            "## Overview",
            "",
            f"This {requirements.get('type', 'project')} implements {requirements.get('original_description', 'the requested functionality')}.",
            "",
            "## Features",
            ""
        ]
        
        # Add features
        features = requirements.get("features", [])
        if features:
            for feature in features:
                readme.append(f"- {feature.replace('_', ' ').title()} support")
        else:
            readme.append("- Core functionality implementation")
        
        # Add usage
        readme.extend([
            "",
            "## Usage",
            "",
            "```" + requirements.get("language", "python"),
            f"# Example usage",
            f"from {requirements.get('name', 'module')} import {requirements.get('name', 'main')}",
            "",
            "# Use the functionality",
            f"result = {requirements.get('name', 'main')}()",
            "```",
            "",
            "## Requirements",
            "",
            f"- {requirements.get('language', 'Python').title()} 3.6+",
            "- No external dependencies",
            "",
            "## License",
            "",
            "MIT License",
            "",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d')}"
        ])
        
        return '\n'.join(readme)
    
    def _generate_api_docs(self, code_lines: List[str], requirements: Dict[str, Any]) -> str:
        """Generate API documentation."""
        api_docs = [
            f"# API Documentation for {requirements.get('name', 'Module')}",
            "",
            "## Classes",
            ""
        ]
        
        # Extract classes and functions
        current_class = None
        
        for line in code_lines:
            if line.strip().startswith('class '):
                match = re.search(r'class\s+(\w+)', line)
                if match:
                    current_class = match.group(1)
                    api_docs.append(f"### {current_class}")
                    api_docs.append("")
            
            elif line.strip().startswith('def ') and current_class:
                match = re.search(r'def\s+(\w+)\((.*?)\)', line)
                if match:
                    method = match.group(1)
                    params = match.group(2)
                    api_docs.append(f"#### {method}({params})")
                    api_docs.append("")
        
        return '\n'.join(api_docs)


if __name__ == "__main__":
    # Test refactoring
    refactorer = CodeRefactorer("python")
    
    test_code = '''
import json
import os
import sys

def calculate(x, y):
    result = x * 100 + y * 200
    return result
'''
    
    result = refactorer.refactor(test_code, "pep8")
    print("Refactored code:")
    print(result["code"])
    print("\nImprovements:", result["improvements"])
    
    # Test documentation
    documenter = CodeDocumenter("python")
    doc_result = documenter.document(
        result["code"],
        {"name": "calculator", "original_description": "Calculate values"},
        {}
    )
    print("\nDocumented code:")
    print(doc_result["code"])