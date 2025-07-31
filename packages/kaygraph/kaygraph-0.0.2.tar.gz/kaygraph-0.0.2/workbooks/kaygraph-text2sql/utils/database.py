"""
Mock database implementation for SQL execution.

This module provides a mock database with sample data
for demonstrating text-to-SQL functionality.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


def get_mock_schema() -> Dict[str, Any]:
    """Get the mock database schema."""
    return {
        "tables": {
            "customers": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "name", "type": "VARCHAR"},
                    {"name": "email", "type": "VARCHAR"},
                    {"name": "created_at", "type": "TIMESTAMP"}
                ],
                "primary_key": "id"
            },
            "products": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "name", "type": "VARCHAR"},
                    {"name": "price", "type": "DECIMAL"},
                    {"name": "category", "type": "VARCHAR"},
                    {"name": "stock", "type": "INTEGER"}
                ],
                "primary_key": "id"
            },
            "orders": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "customer_id", "type": "INTEGER", "foreign_key": "customers.id"},
                    {"name": "status", "type": "VARCHAR"},
                    {"name": "total", "type": "DECIMAL"},
                    {"name": "created_at", "type": "TIMESTAMP"}
                ],
                "primary_key": "id"
            },
            "order_items": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "order_id", "type": "INTEGER", "foreign_key": "orders.id"},
                    {"name": "product_id", "type": "INTEGER", "foreign_key": "products.id"},
                    {"name": "quantity", "type": "INTEGER"},
                    {"name": "price", "type": "DECIMAL"}
                ],
                "primary_key": "id"
            }
        },
        "relationships": [
            {
                "from_table": "orders",
                "from_column": "customer_id",
                "to_table": "customers",
                "to_column": "id"
            },
            {
                "from_table": "order_items",
                "from_column": "order_id",
                "to_table": "orders",
                "to_column": "id"
            },
            {
                "from_table": "order_items",
                "from_column": "product_id",
                "to_table": "products",
                "to_column": "id"
            }
        ]
    }


class MockDatabase:
    """Mock database for SQL execution."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize mock database with sample data.
        
        Args:
            schema: Database schema (optional)
        """
        self.schema = schema or get_mock_schema()
        self.data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate sample data for all tables."""
        data = {}
        
        # Customers
        data["customers"] = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", 
             "created_at": datetime.now() - timedelta(days=180)},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com",
             "created_at": datetime.now() - timedelta(days=150)},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com",
             "created_at": datetime.now() - timedelta(days=120)},
            {"id": 4, "name": "Alice Brown", "email": "alice@example.com",
             "created_at": datetime.now() - timedelta(days=90)},
            {"id": 5, "name": "Charlie Wilson", "email": "charlie@example.com",
             "created_at": datetime.now() - timedelta(days=60)}
        ]
        
        # Products
        data["products"] = [
            {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics", "stock": 50},
            {"id": 2, "name": "Mouse", "price": 29.99, "category": "Electronics", "stock": 200},
            {"id": 3, "name": "Keyboard", "price": 79.99, "category": "Electronics", "stock": 150},
            {"id": 4, "name": "Monitor", "price": 299.99, "category": "Electronics", "stock": 75},
            {"id": 5, "name": "Desk Chair", "price": 199.99, "category": "Furniture", "stock": 30},
            {"id": 6, "name": "Notebook", "price": 4.99, "category": "Stationery", "stock": 500},
            {"id": 7, "name": "Pen Set", "price": 12.99, "category": "Stationery", "stock": 300},
            {"id": 8, "name": "USB Cable", "price": 9.99, "category": "Electronics", "stock": 400},
            {"id": 9, "name": "Webcam", "price": 89.99, "category": "Electronics", "stock": 60},
            {"id": 10, "name": "Headphones", "price": 149.99, "category": "Electronics", "stock": 100}
        ]
        
        # Orders
        data["orders"] = [
            {"id": 1, "customer_id": 1, "status": "completed", "total": 1079.97,
             "created_at": datetime.now() - timedelta(days=30)},
            {"id": 2, "customer_id": 2, "status": "completed", "total": 299.99,
             "created_at": datetime.now() - timedelta(days=25)},
            {"id": 3, "customer_id": 1, "status": "completed", "total": 149.99,
             "created_at": datetime.now() - timedelta(days=20)},
            {"id": 4, "customer_id": 3, "status": "pending", "total": 89.99,
             "created_at": datetime.now() - timedelta(days=15)},
            {"id": 5, "customer_id": 4, "status": "completed", "total": 1299.98,
             "created_at": datetime.now() - timedelta(days=10)},
            {"id": 6, "customer_id": 2, "status": "cancelled", "total": 199.99,
             "created_at": datetime.now() - timedelta(days=5)},
            {"id": 7, "customer_id": 5, "status": "completed", "total": 42.97,
             "created_at": datetime.now() - timedelta(days=3)},
            {"id": 8, "customer_id": 1, "status": "pending", "total": 379.98,
             "created_at": datetime.now() - timedelta(days=1)}
        ]
        
        # Order Items
        data["order_items"] = [
            # Order 1
            {"id": 1, "order_id": 1, "product_id": 1, "quantity": 1, "price": 999.99},
            {"id": 2, "order_id": 1, "product_id": 3, "quantity": 1, "price": 79.99},
            
            # Order 2
            {"id": 3, "order_id": 2, "product_id": 4, "quantity": 1, "price": 299.99},
            
            # Order 3
            {"id": 4, "order_id": 3, "product_id": 10, "quantity": 1, "price": 149.99},
            
            # Order 4
            {"id": 5, "order_id": 4, "product_id": 9, "quantity": 1, "price": 89.99},
            
            # Order 5
            {"id": 6, "order_id": 5, "product_id": 1, "quantity": 1, "price": 999.99},
            {"id": 7, "order_id": 5, "product_id": 4, "quantity": 1, "price": 299.99},
            
            # Order 6
            {"id": 8, "order_id": 6, "product_id": 5, "quantity": 1, "price": 199.99},
            
            # Order 7
            {"id": 9, "order_id": 7, "product_id": 2, "quantity": 1, "price": 29.99},
            {"id": 10, "order_id": 7, "product_id": 7, "quantity": 1, "price": 12.99},
            
            # Order 8
            {"id": 11, "order_id": 8, "product_id": 3, "quantity": 1, "price": 79.99},
            {"id": 12, "order_id": 8, "product_id": 4, "quantity": 1, "price": 299.99}
        ]
        
        return data
    
    def execute(self, sql: str) -> Dict[str, Any]:
        """
        Execute SQL query against mock data.
        
        Args:
            sql: SQL query string
            
        Returns:
            Query results
        """
        logger.info(f"Executing mock SQL: {sql}")
        
        # Parse SQL (simplified)
        sql_upper = sql.upper()
        
        # Extract main components
        if "SELECT" not in sql_upper:
            raise ValueError("Only SELECT queries are supported")
        
        # Simple parser for demonstration
        result = self._execute_select(sql)
        
        return result
    
    def _execute_select(self, sql: str) -> Dict[str, Any]:
        """Execute SELECT query."""
        # This is a simplified mock implementation
        # In production, use a real SQL parser
        
        sql_upper = sql.upper()
        
        # Handle specific queries
        if "SELECT * FROM customers" in sql:
            return {
                "columns": ["id", "name", "email", "created_at"],
                "rows": self.data["customers"][:10],  # Limit results
                "execution_time": 0.001
            }
        
        elif "SELECT * FROM products WHERE price < 50" in sql:
            filtered = [p for p in self.data["products"] if p["price"] < 50]
            return {
                "columns": ["id", "name", "price", "category", "stock"],
                "rows": filtered,
                "execution_time": 0.002
            }
        
        elif "SELECT status, COUNT(*)" in sql and "GROUP BY status" in sql:
            # Count orders by status
            status_counts = {}
            for order in self.data["orders"]:
                status = order["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            rows = [{"status": status, "COUNT(*)": count} 
                   for status, count in status_counts.items()]
            
            return {
                "columns": ["status", "COUNT(*)"],
                "rows": rows,
                "execution_time": 0.003
            }
        
        elif "SUM(o.total) as total_spent" in sql:
            # Top customers by spending
            customer_totals = {}
            for order in self.data["orders"]:
                if order["status"] == "completed":
                    cid = order["customer_id"]
                    customer_totals[cid] = customer_totals.get(cid, 0) + order["total"]
            
            # Join with customer names
            rows = []
            for cid, total in customer_totals.items():
                customer = next((c for c in self.data["customers"] if c["id"] == cid), None)
                if customer:
                    rows.append({
                        "id": cid,
                        "name": customer["name"],
                        "total_spent": round(total, 2)
                    })
            
            # Sort by total spent
            rows.sort(key=lambda x: x["total_spent"], reverse=True)
            
            # Apply limit if present
            limit_match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
            if limit_match:
                limit = int(limit_match.group(1))
                rows = rows[:limit]
            
            return {
                "columns": ["id", "name", "total_spent"],
                "rows": rows,
                "execution_time": 0.005
            }
        
        elif "products" in sql.lower() and "LEFT JOIN order_items" in sql:
            # Products that have never been ordered
            ordered_product_ids = {item["product_id"] for item in self.data["order_items"]}
            unordered = [p for p in self.data["products"] if p["id"] not in ordered_product_ids]
            
            # Note: In this mock data, all products have been ordered
            # So we'll return product with ID 6 (Notebook) as an example
            unordered = [p for p in self.data["products"] if p["id"] == 6][:1]
            
            return {
                "columns": ["id", "name", "price", "category", "stock"],
                "rows": unordered,
                "execution_time": 0.004
            }
        
        else:
            # Generic fallback
            return {
                "columns": ["message"],
                "rows": [{"message": "Query executed successfully (mock)"}],
                "execution_time": 0.001
            }


if __name__ == "__main__":
    # Test the mock database
    db = MockDatabase()
    
    test_queries = [
        "SELECT * FROM customers",
        "SELECT * FROM products WHERE price < 50",
        "SELECT status, COUNT(*) FROM orders GROUP BY status",
        """SELECT c.id, c.name, SUM(o.total) as total_spent
           FROM customers c
           INNER JOIN orders o ON c.id = o.customer_id
           GROUP BY c.id, c.name
           ORDER BY total_spent DESC
           LIMIT 5"""
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = db.execute(query)
            print(f"Columns: {result['columns']}")
            print(f"Rows returned: {len(result['rows'])}")
            if result['rows']:
                print(f"First row: {result['rows'][0]}")
        except Exception as e:
            print(f"Error: {e}")