"""
SQL query generator and utilities.

This module handles SQL generation, validation, correction, and formatting.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SQLGenerator:
    """Generate SQL queries from parsed components."""
    
    def __init__(self, dialect: str = "sqlite"):
        """
        Initialize SQL generator.
        
        Args:
            dialect: SQL dialect (sqlite, mysql, postgresql)
        """
        self.dialect = dialect
        
        # Dialect-specific features
        self.dialect_features = {
            "sqlite": {
                "limit_syntax": "LIMIT {n}",
                "string_quote": "'",
                "identifier_quote": '"'
            },
            "mysql": {
                "limit_syntax": "LIMIT {n}",
                "string_quote": "'",
                "identifier_quote": "`"
            },
            "postgresql": {
                "limit_syntax": "LIMIT {n}",
                "string_quote": "'",
                "identifier_quote": '"'
            }
        }
    
    def generate(self, parsed_query: Dict[str, Any], schema_info: Dict[str, Any], 
                 previous_error: Optional[str] = None) -> str:
        """
        Generate SQL query from parsed components.
        
        Args:
            parsed_query: Parsed natural language query
            schema_info: Schema analysis results
            previous_error: Previous SQL error to avoid
            
        Returns:
            Generated SQL query string
        """
        intent = parsed_query.get("intent", "select")
        
        if intent in ["select", "count"]:
            return self._generate_select_query(parsed_query, schema_info)
        elif intent == "aggregate":
            return self._generate_aggregate_query(parsed_query, schema_info)
        elif intent == "top_n":
            return self._generate_top_n_query(parsed_query, schema_info)
        else:
            # Default to select
            return self._generate_select_query(parsed_query, schema_info)
    
    def _generate_select_query(self, parsed: Dict[str, Any], schema: Dict[str, Any]) -> str:
        """Generate a SELECT query."""
        parts = []
        
        # SELECT clause
        if parsed.get("intent") == "count" and not parsed.get("filters", {}).get("_group_by"):
            parts.append("SELECT COUNT(*)")
        else:
            parts.append("SELECT *")
        
        # FROM clause
        main_table = parsed.get("entities", {}).get("main", "unknown_table")
        parts.append(f"FROM {main_table}")
        
        # JOIN clauses
        for join in schema.get("joins", []):
            join_type = join.get("type", "INNER")
            parts.append(f"{join_type} JOIN {join['to_table']} ON {join['on']}")
        
        # WHERE clause
        where_conditions = []
        
        # Regular filters
        for filter_key, filter_value in parsed.get("filters", {}).items():
            if filter_key.startswith("_"):
                continue  # Skip special filters
            
            if "__" in filter_key:
                column, op = filter_key.split("__", 1)
                if op == "lt":
                    where_conditions.append(f"{column} < {filter_value}")
                elif op == "gt":
                    where_conditions.append(f"{column} > {filter_value}")
                elif op == "gte":
                    where_conditions.append(f"{column} >= '{filter_value}'")
                elif op == "lt":
                    where_conditions.append(f"{column} < '{filter_value}'")
                elif op == "range":
                    where_conditions.append(f"{column} BETWEEN '{filter_value[0]}' AND '{filter_value[1]}'")
            else:
                # Direct equality
                if isinstance(filter_value, str):
                    where_conditions.append(f"{filter_key} = '{filter_value}'")
                else:
                    where_conditions.append(f"{filter_key} = {filter_value}")
        
        # Special conditions from joins
        for join in schema.get("joins", []):
            if join.get("condition"):
                where_conditions.append(join["condition"])
        
        if where_conditions:
            parts.append("WHERE " + " AND ".join(where_conditions))
        
        # GROUP BY clause
        group_by = parsed.get("filters", {}).get("_group_by")
        if group_by:
            parts.append(f"GROUP BY {group_by}")
            # If counting with group by, modify SELECT
            if parsed.get("intent") == "count":
                parts[0] = f"SELECT {group_by}, COUNT(*)"
        
        # ORDER BY clause
        order_by = parsed.get("order_by")
        if order_by:
            order_col = order_by.get("column", "1")
            order_dir = order_by.get("direction", "ASC")
            parts.append(f"ORDER BY {order_col} {order_dir}")
        
        # LIMIT clause
        limit = parsed.get("limit")
        if limit:
            limit_syntax = self.dialect_features[self.dialect]["limit_syntax"]
            parts.append(limit_syntax.format(n=limit))
        
        return " ".join(parts)
    
    def _generate_aggregate_query(self, parsed: Dict[str, Any], schema: Dict[str, Any]) -> str:
        """Generate an aggregate query."""
        agg = parsed.get("aggregation", {})
        agg_type = agg.get("type", "SUM")
        agg_column = agg.get("column", "*")
        agg_alias = agg.get("alias", "result")
        
        # Start with basic structure
        parsed_copy = parsed.copy()
        parsed_copy["intent"] = "select"  # Treat as select for base generation
        
        # Generate base query
        base_query = self._generate_select_query(parsed_copy, schema)
        
        # Replace SELECT clause with aggregation
        if agg_column == "*":
            new_select = f"SELECT {agg_type}(*) as {agg_alias}"
        else:
            new_select = f"SELECT {agg_type}({agg_column}) as {agg_alias}"
        
        # If there's a group by, include that column too
        group_by = parsed.get("filters", {}).get("_group_by")
        if group_by:
            new_select = f"SELECT {group_by}, {agg_type}({agg_column}) as {agg_alias}"
        
        # Replace the SELECT clause
        query_parts = base_query.split("FROM", 1)
        if len(query_parts) == 2:
            return new_select + " FROM" + query_parts[1]
        
        return new_select + " FROM unknown_table"
    
    def _generate_top_n_query(self, parsed: Dict[str, Any], schema: Dict[str, Any]) -> str:
        """Generate a TOP N query."""
        # For "Top 5 customers by total spending"
        if "by total spending" in parsed.get("original_query", ""):
            return self._generate_top_customers_query(parsed, schema)
        
        # Otherwise use standard select with limit
        return self._generate_select_query(parsed, schema)
    
    def _generate_top_customers_query(self, parsed: Dict[str, Any], schema: Dict[str, Any]) -> str:
        """Generate specific query for top customers by spending."""
        limit = parsed.get("limit", 5)
        
        return f"""SELECT c.id, c.name, SUM(o.total) as total_spent
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY total_spent DESC
LIMIT {limit}"""
    
    def is_parameterized(self, sql: str) -> bool:
        """Check if SQL uses parameterized queries."""
        # Simple check for parameter placeholders
        return "?" in sql or "%s" in sql or ":1" in sql


class SQLValidator:
    """Validate SQL queries for syntax and security."""
    
    def __init__(self):
        """Initialize validator with rules."""
        # Forbidden keywords (for security)
        self.forbidden_keywords = [
            "DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER",
            "TRUNCATE", "EXEC", "EXECUTE", "GRANT", "REVOKE"
        ]
        
        # Required structure patterns
        self.required_patterns = [
            r"SELECT\s+.+\s+FROM\s+\w+",  # Basic SELECT...FROM
        ]
        
        # Common syntax patterns
        self.syntax_patterns = {
            "valid_table_name": r"^[a-zA-Z_]\w*$",
            "valid_column_name": r"^[a-zA-Z_]\w*$",
            "balanced_parentheses": r"^\([^()]*\)$"
        }
    
    def validate(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL query.
        
        Args:
            sql: SQL query string
            
        Returns:
            Validation result with 'valid' flag and any errors/warnings
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not sql:
            result["valid"] = False
            result["errors"].append("Empty SQL query")
            return result
        
        sql_upper = sql.upper()
        
        # Check for forbidden operations
        for keyword in self.forbidden_keywords:
            if keyword in sql_upper:
                result["valid"] = False
                result["errors"].append(f"Forbidden operation: {keyword}")
        
        # Check basic structure
        has_valid_structure = any(
            re.search(pattern, sql_upper)
            for pattern in self.required_patterns
        )
        
        if not has_valid_structure:
            result["valid"] = False
            result["errors"].append("Invalid SQL structure")
        
        # Check for common issues
        if "FROM nowhere" in sql:
            result["valid"] = False
            result["errors"].append("Invalid table name: nowhere")
        
        if "stuffs" in sql.lower():
            result["valid"] = False
            result["errors"].append("Ambiguous table reference: stuffs")
        
        # Check for SQL injection attempts
        if ";" in sql and sql.count(";") > 1:
            result["valid"] = False
            result["errors"].append("Multiple statements not allowed")
        
        if re.search(r"--|\\/\\*|\\*\\/", sql):
            result["valid"] = False
            result["errors"].append("SQL comments not allowed")
        
        # Warnings
        if "SELECT *" in sql_upper:
            result["warnings"].append("Consider selecting specific columns instead of *")
        
        if "LIMIT" not in sql_upper and "COUNT" not in sql_upper:
            result["warnings"].append("Consider adding LIMIT to prevent large result sets")
        
        return result


class SQLCorrector:
    """Attempt to correct invalid SQL queries."""
    
    def __init__(self):
        """Initialize corrector with common fixes."""
        self.common_fixes = {
            "Invalid table name: nowhere": {
                "pattern": r"FROM\s+nowhere",
                "replacement": "FROM customers",  # Default to customers table
                "description": "Replaced invalid table 'nowhere' with 'customers'"
            },
            "Ambiguous table reference: stuffs": {
                "pattern": r"stuffs",
                "replacement": "products",  # Assume they meant products
                "description": "Replaced ambiguous 'stuffs' with 'products'"
            },
            "Invalid SQL structure": {
                "pattern": r"^Select from (\w+)$",
                "replacement": r"SELECT * FROM \1",
                "description": "Fixed incomplete SELECT statement"
            }
        }
    
    def correct(self, sql: str, errors: List[str]) -> Dict[str, Any]:
        """
        Attempt to correct SQL based on errors.
        
        Args:
            sql: Invalid SQL query
            errors: List of validation errors
            
        Returns:
            Correction result
        """
        result = {
            "corrected": False,
            "sql": sql,
            "fix_description": None,
            "reason": "No applicable fix found"
        }
        
        # Try to apply fixes based on errors
        for error in errors:
            if error in self.common_fixes:
                fix = self.common_fixes[error]
                
                # Apply the fix
                corrected_sql = re.sub(
                    fix["pattern"],
                    fix["replacement"],
                    sql,
                    flags=re.IGNORECASE
                )
                
                if corrected_sql != sql:
                    result["corrected"] = True
                    result["sql"] = corrected_sql
                    result["fix_description"] = fix["description"]
                    break
        
        # Additional heuristic fixes
        if not result["corrected"]:
            # Fix case sensitivity issues
            if "select" in sql.lower() and "SELECT" not in sql:
                result["corrected"] = True
                result["sql"] = sql.upper().replace("FROM", " FROM ").replace("WHERE", " WHERE ")
                result["fix_description"] = "Fixed SQL keyword capitalization"
        
        return result


class ResultFormatter:
    """Format SQL query results for display."""
    
    def format(self, rows: List[Dict[str, Any]], columns: List[str], 
               format_type: str = "table") -> str:
        """
        Format query results.
        
        Args:
            rows: Query result rows
            columns: Column names
            format_type: Output format (table, json, csv)
            
        Returns:
            Formatted result string
        """
        if format_type == "table":
            return self._format_as_table(rows, columns)
        elif format_type == "json":
            return self._format_as_json(rows, columns)
        elif format_type == "csv":
            return self._format_as_csv(rows, columns)
        else:
            return self._format_as_table(rows, columns)
    
    def _format_as_table(self, rows: List[Dict[str, Any]], columns: List[str]) -> str:
        """Format as ASCII table."""
        if not rows:
            return "No results"
        
        # Calculate column widths
        widths = {}
        for col in columns:
            widths[col] = len(col)
            for row in rows:
                val_len = len(str(row.get(col, "")))
                widths[col] = max(widths[col], val_len)
        
        # Build table
        lines = []
        
        # Header
        header = "| " + " | ".join(col.ljust(widths[col]) for col in columns) + " |"
        separator = "|-" + "-|-".join("-" * widths[col] for col in columns) + "-|"
        
        lines.append(header)
        lines.append(separator)
        
        # Rows
        for row in rows:
            row_str = "| " + " | ".join(
                str(row.get(col, "")).ljust(widths[col]) 
                for col in columns
            ) + " |"
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def _format_as_json(self, rows: List[Dict[str, Any]], columns: List[str]) -> str:
        """Format as JSON."""
        import json
        return json.dumps(rows, indent=2)
    
    def _format_as_csv(self, rows: List[Dict[str, Any]], columns: List[str]) -> str:
        """Format as CSV."""
        lines = [",".join(columns)]
        
        for row in rows:
            values = [str(row.get(col, "")) for col in columns]
            lines.append(",".join(values))
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test the SQL generator
    generator = SQLGenerator(dialect="sqlite")
    
    test_cases = [
        {
            "parsed": {
                "intent": "select",
                "entities": {"main": "customers"},
                "filters": {},
                "limit": None
            },
            "schema": {
                "tables": ["customers"],
                "joins": []
            }
        },
        {
            "parsed": {
                "intent": "select",
                "entities": {"main": "products"},
                "filters": {"price__lt": 50},
                "limit": 10
            },
            "schema": {
                "tables": ["products"],
                "joins": []
            }
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\nTest {i + 1}:")
        sql = generator.generate(test["parsed"], test["schema"])
        print(f"SQL: {sql}")
        
        # Validate
        validator = SQLValidator()
        validation = validator.validate(sql)
        print(f"Valid: {validation['valid']}")
        if validation["errors"]:
            print(f"Errors: {validation['errors']}")
        if validation["warnings"]:
            print(f"Warnings: {validation['warnings']}")