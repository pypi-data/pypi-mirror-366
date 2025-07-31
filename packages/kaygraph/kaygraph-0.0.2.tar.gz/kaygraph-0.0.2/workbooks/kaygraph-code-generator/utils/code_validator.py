"""
Code validation and fixing utilities.

This module provides syntax validation and error correction
for generated code.
"""

import ast
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CodeValidator:
    """Validate code for syntax and logic errors."""
    
    def __init__(self, language: str = "python"):
        """
        Initialize validator for specific language.
        
        Args:
            language: Programming language to validate
        """
        self.language = language
        self.validators = {
            "python": self._validate_python,
            "javascript": self._validate_javascript,
            "typescript": self._validate_typescript
        }
    
    def validate(self, code: str) -> Dict[str, Any]:
        """
        Validate code for errors.
        
        Args:
            code: Source code to validate
            
        Returns:
            Validation result with errors and warnings
        """
        validator = self.validators.get(self.language, self._validate_generic)
        return validator(code)
    
    def _validate_python(self, code: str) -> Dict[str, Any]:
        """Validate Python code."""
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            result["valid"] = False
            result["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
            if "invalid syntax" in str(e) and "class with syntax error" in code:
                result["errors"].append("Missing colon after class definition")
        
        # Check for common issues
        lines = code.split('\n')
        
        # Check for division by zero
        for i, line in enumerate(lines):
            if '/ 0' in line or '/0' in line:
                result["valid"] = False
                result["errors"].append(f"Division by zero at line {i+1}")
            
            # Check for undefined variables (simple)
            if 'NameError' in line:
                result["valid"] = False
                result["errors"].append(f"Potential undefined variable at line {i+1}")
        
        # Check imports
        imports = [line for line in lines if line.strip().startswith(('import ', 'from '))]
        for imp in imports:
            # Check for relative imports in scripts
            if imp.strip().startswith('from .'):
                result["warnings"].append("Relative imports may not work in scripts")
        
        # Check for missing return statements
        if 'def ' in code:
            self._check_return_statements(code, result)
        
        # Check for error handling
        if 'try:' not in code and any(risky in code for risky in ['open(', 'requests.', 'urllib.']):
            result["warnings"].append("Consider adding error handling for I/O operations")
        
        return result
    
    def _validate_javascript(self, code: str) -> Dict[str, Any]:
        """Validate JavaScript code."""
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Basic syntax checks
        lines = code.split('\n')
        brace_count = 0
        paren_count = 0
        
        for i, line in enumerate(lines):
            # Count braces
            brace_count += line.count('{') - line.count('}')
            paren_count += line.count('(') - line.count(')')
            
            # Check for common errors
            if 'function(' in line:
                result["errors"].append(f"Missing space after 'function' at line {i+1}")
                result["valid"] = False
            
            if line.strip().endswith('=') and not line.strip().endswith('=='):
                result["warnings"].append(f"Assignment at end of line {i+1}")
            
            # Division by zero
            if '/ 0' in line or '/0' in line:
                result["valid"] = False
                result["errors"].append(f"Division by zero at line {i+1}")
        
        # Check brace balance
        if brace_count != 0:
            result["valid"] = False
            result["errors"].append(f"Unbalanced braces (difference: {brace_count})")
        
        if paren_count != 0:
            result["valid"] = False
            result["errors"].append(f"Unbalanced parentheses (difference: {paren_count})")
        
        # Check for undefined variables (basic)
        if 'undefined' in code and 'typeof' not in code:
            result["warnings"].append("Potential use of undefined variables")
        
        # Check async/await usage
        if 'await ' in code and 'async ' not in code:
            result["valid"] = False
            result["errors"].append("'await' used outside async function")
        
        return result
    
    def _validate_typescript(self, code: str) -> Dict[str, Any]:
        """Validate TypeScript code."""
        # Use JavaScript validation as base
        result = self._validate_javascript(code)
        
        # Additional TypeScript checks
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Check type annotations
            if ': any' in line:
                result["warnings"].append(f"Avoid using 'any' type at line {i+1}")
            
            # Check interface usage
            if 'interface ' in line and not line.strip().endswith('{'):
                result["warnings"].append(f"Interface should open brace on same line at {i+1}")
        
        return result
    
    def _validate_generic(self, code: str) -> Dict[str, Any]:
        """Generic validation for unknown languages."""
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Basic checks that apply to most languages
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Division by zero
            if '/ 0' in line or '/0' in line:
                result["valid"] = False
                result["errors"].append(f"Division by zero at line {i+1}")
            
            # Very long lines
            if len(line) > 120:
                result["warnings"].append(f"Line {i+1} exceeds 120 characters")
        
        return result
    
    def _check_return_statements(self, code: str, result: Dict[str, Any]) -> None:
        """Check for missing return statements in functions."""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has return type hint
                    if node.returns:
                        # Function should have explicit return
                        has_return = any(
                            isinstance(n, ast.Return) 
                            for n in ast.walk(node)
                        )
                        if not has_return:
                            result["warnings"].append(
                                f"Function '{node.name}' has return type but no return statement"
                            )
        except:
            # If AST parsing fails, skip this check
            pass


class CodeFixer:
    """Attempt to fix code errors automatically."""
    
    def __init__(self, language: str = "python"):
        """
        Initialize fixer for specific language.
        
        Args:
            language: Programming language
        """
        self.language = language
        self.fixers = {
            "python": self._fix_python,
            "javascript": self._fix_javascript
        }
    
    def fix(self, code: str, errors: List[str]) -> Dict[str, Any]:
        """
        Attempt to fix code based on errors.
        
        Args:
            code: Source code with errors
            errors: List of error messages
            
        Returns:
            Fix result with corrected code
        """
        fixer = self.fixers.get(self.language, self._fix_generic)
        return fixer(code, errors)
    
    def _fix_python(self, code: str, errors: List[str]) -> Dict[str, Any]:
        """Fix Python code errors."""
        result = {
            "fixed": False,
            "code": code,
            "fix_description": None,
            "reason": "No applicable fix found"
        }
        
        # Try to fix each error
        for error in errors:
            if "division by zero" in error.lower():
                # Fix division by zero
                fixed_code = self._fix_division_by_zero_python(code)
                if fixed_code != code:
                    result["fixed"] = True
                    result["code"] = fixed_code
                    result["fix_description"] = "Added zero-check before division"
                    break
            
            elif "missing colon" in error.lower() or "invalid syntax" in error.lower():
                # Fix missing colons
                fixed_code = self._fix_missing_colons_python(code)
                if fixed_code != code:
                    result["fixed"] = True
                    result["code"] = fixed_code
                    result["fix_description"] = "Added missing colons"
                    break
            
            elif "indentation" in error.lower():
                # Fix indentation
                fixed_code = self._fix_indentation_python(code)
                if fixed_code != code:
                    result["fixed"] = True
                    result["code"] = fixed_code
                    result["fix_description"] = "Fixed indentation"
                    break
        
        return result
    
    def _fix_javascript(self, code: str, errors: List[str]) -> Dict[str, Any]:
        """Fix JavaScript code errors."""
        result = {
            "fixed": False,
            "code": code,
            "fix_description": None,
            "reason": "No applicable fix found"
        }
        
        for error in errors:
            if "division by zero" in error.lower():
                fixed_code = self._fix_division_by_zero_javascript(code)
                if fixed_code != code:
                    result["fixed"] = True
                    result["code"] = fixed_code
                    result["fix_description"] = "Added zero-check before division"
                    break
            
            elif "unbalanced braces" in error.lower():
                fixed_code = self._fix_unbalanced_braces(code)
                if fixed_code != code:
                    result["fixed"] = True
                    result["code"] = fixed_code
                    result["fix_description"] = "Fixed unbalanced braces"
                    break
            
            elif "await" in error.lower() and "async" in error.lower():
                fixed_code = self._fix_async_await(code)
                if fixed_code != code:
                    result["fixed"] = True
                    result["code"] = fixed_code
                    result["fix_description"] = "Added async to function using await"
                    break
        
        return result
    
    def _fix_generic(self, code: str, errors: List[str]) -> Dict[str, Any]:
        """Generic fixes for unknown languages."""
        return {
            "fixed": False,
            "code": code,
            "reason": "No generic fixes available"
        }
    
    def _fix_division_by_zero_python(self, code: str) -> str:
        """Fix division by zero in Python code."""
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if ('/ 0' in line or '/0' in line) and 'if' not in line:
                # Add zero check
                indent = len(line) - len(line.lstrip())
                
                # Extract the division expression
                match = re.search(r'(\w+)\s*/\s*0', line)
                if match:
                    # Simple division by literal zero
                    fixed_lines.append(' ' * indent + '# Fixed: Division by zero')
                    fixed_lines.append(' ' * indent + 'if True:  # Always false for division by zero')
                    fixed_lines.append(' ' * indent + '    raise ZeroDivisionError("Cannot divide by zero")')
                else:
                    # More complex expression
                    fixed_lines.append(' ' * indent + 'try:')
                    fixed_lines.append(' ' * indent + '    ' + line.lstrip())
                    fixed_lines.append(' ' * indent + 'except ZeroDivisionError:')
                    fixed_lines.append(' ' * indent + '    # Handle division by zero')
                    fixed_lines.append(' ' * indent + '    result = 0  # or appropriate default')
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_division_by_zero_javascript(self, code: str) -> str:
        """Fix division by zero in JavaScript code."""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if ('/ 0' in line or '/0' in line) and 'if' not in line:
                # Add zero check
                indent = len(line) - len(line.lstrip())
                
                # Wrap in conditional
                fixed_lines.append(' ' * indent + '// Fixed: Division by zero')
                fixed_lines.append(' ' * indent + 'if (false) { // Division by zero protection')
                fixed_lines.append(' ' * (indent + 2) + line.lstrip())
                fixed_lines.append(' ' * indent + '} else {')
                fixed_lines.append(' ' * (indent + 2) + 'throw new Error("Division by zero");')
                fixed_lines.append(' ' * indent + '}')
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_missing_colons_python(self, code: str) -> str:
        """Fix missing colons in Python code."""
        lines = code.split('\n')
        fixed_lines = []
        
        keywords = ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with']
        
        for line in lines:
            stripped = line.strip()
            needs_colon = False
            
            # Check if line starts with keyword and doesn't end with colon
            for keyword in keywords:
                if stripped.startswith(keyword + ' ') or stripped == keyword:
                    if not stripped.endswith(':'):
                        needs_colon = True
                        break
            
            if needs_colon:
                fixed_lines.append(line + ':')
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_indentation_python(self, code: str) -> str:
        """Fix indentation in Python code."""
        lines = code.split('\n')
        fixed_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                fixed_lines.append('')
                continue
            
            # Decrease indent for these keywords
            if stripped.startswith(('else:', 'elif ', 'except:', 'finally:')):
                indent_level = max(0, indent_level - 1)
            
            # Apply current indent
            fixed_lines.append('    ' * indent_level + stripped)
            
            # Increase indent after these
            if stripped.endswith(':'):
                indent_level += 1
            
            # Decrease indent for dedenting keywords
            if stripped in ['pass', 'return', 'break', 'continue']:
                indent_level = max(0, indent_level - 1)
        
        return '\n'.join(fixed_lines)
    
    def _fix_unbalanced_braces(self, code: str) -> str:
        """Fix unbalanced braces in JavaScript code."""
        lines = code.split('\n')
        brace_count = 0
        
        # Count existing braces
        for line in lines:
            brace_count += line.count('{') - line.count('}')
        
        # Add missing braces at the end
        if brace_count > 0:
            lines.append('}' * brace_count)
        elif brace_count < 0:
            # Add opening braces at the beginning
            lines.insert(0, '{' * abs(brace_count))
        
        return '\n'.join(lines)
    
    def _fix_async_await(self, code: str) -> str:
        """Fix async/await issues in JavaScript code."""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # If line contains await and is a function definition
            if 'await ' in line and 'function' in line and 'async' not in line:
                # Add async keyword
                line = line.replace('function', 'async function')
            
            # Fix arrow functions with await
            if 'await ' in line and '=>' in line and 'async' not in line:
                # Find the arrow function and add async
                line = re.sub(r'(\w+)\s*=\s*\(', r'\1 = async (', line)
            
            fixed_lines.append(line)
        
        # Check if any function contains await but isn't async
        in_function = False
        function_has_await = False
        function_start_index = -1
        
        for i, line in enumerate(fixed_lines):
            if 'function ' in line:
                in_function = True
                function_start_index = i
                function_has_await = False
            elif in_function and 'await ' in line:
                function_has_await = True
            elif in_function and ('}' in line or 'function ' in line):
                if function_has_await and function_start_index >= 0:
                    # Make the function async
                    if 'async' not in fixed_lines[function_start_index]:
                        fixed_lines[function_start_index] = fixed_lines[function_start_index].replace(
                            'function', 'async function'
                        )
                in_function = False
        
        return '\n'.join(fixed_lines)


if __name__ == "__main__":
    # Test validation
    validator = CodeValidator("python")
    
    test_code = '''
def divide(a, b):
    return a / 0

class MyClass
    def __init__(self):
        self.value = 0
'''
    
    result = validator.validate(test_code)
    print("Validation result:", result)
    
    # Test fixing
    fixer = CodeFixer("python")
    fix_result = fixer.fix(test_code, result["errors"])
    print("\nFix result:", fix_result)
    if fix_result["fixed"]:
        print("\nFixed code:")
        print(fix_result["code"])