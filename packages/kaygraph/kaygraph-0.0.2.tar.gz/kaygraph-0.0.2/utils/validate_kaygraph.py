#!/usr/bin/env python3
"""
KayGraph Code Validator - Check if code follows KayGraph patterns

Usage:
    python validate_kaygraph.py <file_or_directory> [--fix] [--verbose]
    
Examples:
    python validate_kaygraph.py nodes.py
    python validate_kaygraph.py ./my_project --verbose
    python validate_kaygraph.py ./my_project --fix
"""

import ast
import os
import sys
from pathlib import Path
import argparse
from typing import List, Tuple, Dict, Any


class KayGraphValidator(ast.NodeVisitor):
    """AST visitor to validate KayGraph patterns"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.errors = []
        self.warnings = []
        self.info = []
        self.current_class = None
        self.current_method = None
        self.node_classes = set()
        self.imports = {}
        
    def add_error(self, line: int, message: str):
        self.errors.append((line, f"ERROR: {message}"))
        
    def add_warning(self, line: int, message: str):
        self.warnings.append((line, f"WARNING: {message}"))
        
    def add_info(self, line: int, message: str):
        self.info.append((line, f"INFO: {message}"))
    
    def visit_Import(self, node):
        """Track imports"""
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Track from imports"""
        if node.module == "kaygraph":
            for alias in node.names:
                name = alias.asname or alias.name
                self.imports[name] = f"kaygraph.{alias.name}"
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Validate class definitions"""
        self.current_class = node.name
        
        # Check if it's a Node class
        is_node_class = False
        for base in node.bases:
            base_name = self._get_name(base)
            if base_name and "Node" in base_name:
                is_node_class = True
                self.node_classes.add(node.name)
                self._validate_node_class(node)
                break
        
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        """Validate method definitions"""
        old_method = self.current_method
        self.current_method = node.name
        
        if self.current_class in self.node_classes:
            self._validate_node_method(node)
        
        self.generic_visit(node)
        self.current_method = old_method
    
    def _get_name(self, node):
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None
    
    def _validate_node_class(self, node):
        """Validate Node class structure"""
        # Check naming convention
        if not node.name.endswith("Node"):
            self.add_warning(
                node.lineno,
                f"Node class '{node.name}' should end with 'Node'"
            )
        
        # Check for required methods
        methods = {m.name for m in node.body if isinstance(m, ast.FunctionDef)}
        required_methods = {"prep", "exec", "post"}
        missing = required_methods - methods
        
        if missing:
            self.add_error(
                node.lineno,
                f"Node class '{node.name}' missing required methods: {missing}"
            )
        
        # Check for docstring
        if not ast.get_docstring(node):
            self.add_warning(
                node.lineno,
                f"Node class '{node.name}' should have a docstring"
            )
    
    def _validate_node_method(self, node):
        """Validate methods within Node classes"""
        if node.name == "exec":
            self._validate_exec_method(node)
        elif node.name == "prep":
            self._validate_prep_method(node)
        elif node.name == "post":
            self._validate_post_method(node)
    
    def _validate_exec_method(self, node):
        """Validate exec method doesn't access shared"""
        # Check parameters
        if len(node.args.args) != 2:  # self, prep_res
            self.add_error(
                node.lineno,
                f"exec() should have exactly 2 parameters (self, prep_res)"
            )
        
        # Check for shared access
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id == "shared":
                self.add_error(
                    child.lineno,
                    "exec() method must NOT access 'shared' store"
                )
            elif isinstance(child, ast.Attribute):
                if isinstance(child.value, ast.Name) and child.value.id == "shared":
                    self.add_error(
                        child.lineno,
                        "exec() method must NOT access 'shared' store"
                    )
    
    def _validate_prep_method(self, node):
        """Validate prep method"""
        # Check parameters
        if len(node.args.args) != 2:  # self, shared
            self.add_error(
                node.lineno,
                "prep() should have exactly 2 parameters (self, shared)"
            )
        
        # Check if it returns something
        has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
        if not has_return:
            self.add_warning(
                node.lineno,
                "prep() should return data for exec()"
            )
    
    def _validate_post_method(self, node):
        """Validate post method"""
        # Check parameters
        expected_params = 4  # self, shared, prep_res, exec_res
        if len(node.args.args) != expected_params:
            self.add_error(
                node.lineno,
                f"post() should have exactly {expected_params} parameters "
                "(self, shared, prep_res, exec_res)"
            )
        
        # Check if it returns action
        has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
        if not has_return:
            self.add_warning(
                node.lineno,
                "post() should return an action string or None"
            )


def validate_file(filepath: Path, verbose: bool = False) -> Tuple[List, List, List]:
    """Validate a single Python file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        validator = KayGraphValidator(str(filepath))
        validator.visit(tree)
        
        return validator.errors, validator.warnings, validator.info
        
    except SyntaxError as e:
        return [(e.lineno, f"SYNTAX ERROR: {e.msg}")], [], []
    except Exception as e:
        return [(0, f"ERROR: Failed to parse file: {e}")], [], []


def validate_graph_structure(filepath: Path) -> List[str]:
    """Additional validation for graph structure"""
    issues = []
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for graph creation
        if "Graph()" in content and ">>" in content:
            # Basic graph flow checks
            if content.count(">>") > 0:
                issues.append("✓ Graph uses connection operator (>>)")
            
            # Check for add_node calls
            if "add_node" not in content:
                issues.append("⚠️  Graph creation found but no add_node() calls")
        
    except Exception:
        pass
    
    return issues


def format_results(filepath: Path, errors: List, warnings: List, info: List, verbose: bool):
    """Format and print validation results"""
    total_issues = len(errors) + len(warnings)
    
    if total_issues == 0 and not verbose:
        return
    
    print(f"\n{'='*60}")
    print(f"📄 {filepath}")
    print(f"{'='*60}")
    
    if errors:
        print("\n❌ Errors:")
        for line, msg in sorted(errors):
            print(f"  Line {line}: {msg}")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for line, msg in sorted(warnings):
            print(f"  Line {line}: {msg}")
    
    if verbose and info:
        print("\nℹ️  Info:")
        for line, msg in sorted(info):
            print(f"  Line {line}: {msg}")
    
    # Additional graph structure validation
    if filepath.name in ["graph.py", "main.py"]:
        graph_issues = validate_graph_structure(filepath)
        if graph_issues:
            print("\n🔗 Graph Structure:")
            for issue in graph_issues:
                print(f"  {issue}")


def generate_fixes(filepath: Path, errors: List) -> List[str]:
    """Generate fix suggestions for common errors"""
    fixes = []
    
    for line, error in errors:
        if "exec() method must NOT access 'shared'" in error:
            fixes.append(
                f"Line {line}: Move 'shared' access to prep() method and pass via prep_res"
            )
        elif "missing required methods" in error:
            fixes.append(
                f"Line {line}: Add missing methods with proper signatures"
            )
    
    return fixes


def validate_directory(directory: Path, verbose: bool = False, fix: bool = False):
    """Validate all Python files in a directory"""
    py_files = list(directory.rglob("*.py"))
    
    if not py_files:
        print(f"No Python files found in {directory}")
        return
    
    print(f"🔍 Validating {len(py_files)} Python files in {directory}")
    
    total_errors = 0
    total_warnings = 0
    
    for filepath in py_files:
        # Skip __pycache__ and other generated files
        if "__pycache__" in str(filepath):
            continue
        
        errors, warnings, info = validate_file(filepath, verbose)
        total_errors += len(errors)
        total_warnings += len(warnings)
        
        if errors or warnings or verbose:
            format_results(filepath, errors, warnings, info, verbose)
            
            if fix and errors:
                fixes = generate_fixes(filepath, errors)
                if fixes:
                    print("\n🔧 Suggested fixes:")
                    for fix_msg in fixes:
                        print(f"  {fix_msg}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Validation Summary")
    print(f"{'='*60}")
    print(f"  Total files checked: {len(py_files)}")
    print(f"  ❌ Total errors: {total_errors}")
    print(f"  ⚠️  Total warnings: {total_warnings}")
    
    if total_errors == 0:
        print("\n✅ All files pass KayGraph pattern validation!")
    else:
        print("\n❌ Validation failed. Please fix errors before proceeding.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Validate KayGraph code patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pattern checks:
  - Node classes end with 'Node'
  - Required methods: prep(), exec(), post()
  - exec() doesn't access shared store
  - Proper method signatures
  - Graph structure validation
  - Docstring presence

Examples:
  python validate_kaygraph.py nodes.py
  python validate_kaygraph.py ./my_project
  python validate_kaygraph.py ./my_project --verbose
  python validate_kaygraph.py ./my_project --fix
"""
    )
    
    parser.add_argument("path",
                       help="File or directory to validate")
    parser.add_argument("--verbose", "-v",
                       action="store_true",
                       help="Show all information including passed checks")
    parser.add_argument("--fix",
                       action="store_true",
                       help="Suggest fixes for common errors")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        sys.exit(1)
    
    if path.is_file():
        if not path.suffix == '.py':
            print(f"Error: '{path}' is not a Python file")
            sys.exit(1)
        
        errors, warnings, info = validate_file(path, args.verbose)
        format_results(path, errors, warnings, info, args.verbose)
        
        if args.fix and errors:
            fixes = generate_fixes(path, errors)
            if fixes:
                print("\n🔧 Suggested fixes:")
                for fix_msg in fixes:
                    print(f"  {fix_msg}")
        
        if errors:
            sys.exit(1)
    else:
        validate_directory(path, args.verbose, args.fix)


if __name__ == "__main__":
    main()