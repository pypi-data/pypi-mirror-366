"""
Database schema analyzer for SQL generation.

This module analyzes database schemas to identify relevant tables
and columns for query generation.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SchemaAnalyzer:
    """Analyze database schema for SQL generation."""
    
    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize with database schema.
        
        Args:
            schema: Database schema dictionary
        """
        self.schema = schema
        self.tables = schema.get("tables", {})
        self.relationships = schema.get("relationships", [])
    
    def analyze_for_query(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze schema based on parsed query requirements.
        
        Args:
            parsed_query: Parsed natural language query
            
        Returns:
            Schema analysis results
        """
        result = {
            "tables": [],
            "columns": [],
            "joins": [],
            "primary_keys": {},
            "foreign_keys": {}
        }
        
        # Get main table
        main_entity = parsed_query.get("entities", {}).get("main")
        if main_entity and main_entity in self.tables:
            result["tables"].append(main_entity)
            
            # Get columns for main table
            table_info = self.tables[main_entity]
            result["columns"].extend([
                {"table": main_entity, "column": col["name"], "type": col["type"]}
                for col in table_info["columns"]
            ])
            
            # Get primary key
            if table_info.get("primary_key"):
                result["primary_keys"][main_entity] = table_info["primary_key"]
        
        # Handle joins
        join_entities = parsed_query.get("entities", {}).get("join", [])
        for join_entity in join_entities:
            if join_entity in self.tables:
                result["tables"].append(join_entity)
                
                # Find relationship
                join_info = self._find_join_path(main_entity, join_entity)
                if join_info:
                    result["joins"].append(join_info)
                
                # Add columns from joined table
                table_info = self.tables[join_entity]
                result["columns"].extend([
                    {"table": join_entity, "column": col["name"], "type": col["type"]}
                    for col in table_info["columns"]
                ])
        
        # Handle special cases
        if parsed_query.get("filters", {}).get("_special") == "not_exists":
            # For "products that have never been ordered"
            result["joins"] = [{
                "type": "LEFT",
                "from_table": "products",
                "to_table": "order_items",
                "on": "products.id = order_items.product_id",
                "condition": "order_items.id IS NULL"
            }]
        
        # Handle aggregations
        if parsed_query.get("aggregation"):
            agg = parsed_query["aggregation"]
            column = agg.get("column")
            
            # If aggregating on a specific column, ensure it's included
            if column and column != "*":
                self._ensure_column_included(result, column, main_entity)
        
        # Handle filters
        for filter_key, filter_value in parsed_query.get("filters", {}).items():
            if filter_key.startswith("_"):
                continue  # Skip special filters
            
            # Extract column name from filter
            column = filter_key.split("__")[0]
            self._ensure_column_included(result, column, main_entity)
        
        # Handle ordering
        order_by = parsed_query.get("order_by")
        if order_by and order_by.get("column"):
            column = order_by["column"]
            # Don't add if it's an alias (like total_spent)
            if not column.endswith("_spent") and not column.endswith("_value"):
                self._ensure_column_included(result, column, main_entity)
        
        # Handle group by
        group_by = parsed_query.get("filters", {}).get("_group_by")
        if group_by:
            self._ensure_column_included(result, group_by, main_entity)
        
        return result
    
    def _find_join_path(self, from_table: str, to_table: str) -> Optional[Dict[str, Any]]:
        """Find the join path between two tables."""
        # Direct relationship
        for rel in self.relationships:
            if (rel["from_table"] == from_table and rel["to_table"] == to_table) or \
               (rel["from_table"] == to_table and rel["to_table"] == from_table):
                return {
                    "type": "INNER",
                    "from_table": from_table,
                    "to_table": to_table,
                    "on": f"{rel['from_table']}.{rel['from_column']} = {rel['to_table']}.{rel['to_column']}"
                }
        
        # For customers -> orders relationship
        if from_table == "customers" and to_table == "orders":
            return {
                "type": "INNER",
                "from_table": "customers",
                "to_table": "orders",
                "on": "customers.id = orders.customer_id"
            }
        
        # For products -> order_items relationship
        if from_table == "products" and to_table == "order_items":
            return {
                "type": "LEFT",
                "from_table": "products",
                "to_table": "order_items",
                "on": "products.id = order_items.product_id"
            }
        
        return None
    
    def _ensure_column_included(self, result: Dict[str, Any], column: str, default_table: str) -> None:
        """Ensure a column is included in the results."""
        # Check if column already included
        for col_info in result["columns"]:
            if col_info["column"] == column:
                return
        
        # Find which table has this column
        table_found = None
        for table_name, table_info in self.tables.items():
            for col in table_info["columns"]:
                if col["name"] == column:
                    table_found = table_name
                    break
        
        if table_found:
            # Add table if not already included
            if table_found not in result["tables"]:
                result["tables"].append(table_found)
                
                # Add join if needed
                if table_found != default_table:
                    join_info = self._find_join_path(default_table, table_found)
                    if join_info and join_info not in result["joins"]:
                        result["joins"].append(join_info)
            
            # Add column
            col_type = next((col["type"] for col in self.tables[table_found]["columns"] 
                           if col["name"] == column), "VARCHAR")
            result["columns"].append({
                "table": table_found,
                "column": column,
                "type": col_type
            })
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, str]]:
        """Get all columns for a specific table."""
        if table_name not in self.tables:
            return []
        
        return [
            {"name": col["name"], "type": col["type"]}
            for col in self.tables[table_name]["columns"]
        ]
    
    def validate_table(self, table_name: str) -> bool:
        """Check if a table exists in the schema."""
        return table_name in self.tables
    
    def validate_column(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        if table_name not in self.tables:
            return False
        
        return any(
            col["name"] == column_name 
            for col in self.tables[table_name]["columns"]
        )


if __name__ == "__main__":
    # Test the schema analyzer
    from database import get_mock_schema
    
    schema = get_mock_schema()
    analyzer = SchemaAnalyzer(schema)
    
    # Test queries
    test_cases = [
        {
            "entities": {"main": "customers"},
            "filters": {},
            "aggregation": None
        },
        {
            "entities": {"main": "products"},
            "filters": {"price__lt": 50},
            "aggregation": None
        },
        {
            "entities": {"main": "customers", "join": ["orders"]},
            "filters": {},
            "aggregation": {"type": "SUM", "column": "total"}
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest case {i + 1}:")
        result = analyzer.analyze_for_query(test_case)
        print(f"Tables: {result['tables']}")
        print(f"Columns: {len(result['columns'])}")
        print(f"Joins: {result['joins']}")