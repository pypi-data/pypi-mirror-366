# KayGraph Text to SQL

Demonstrates natural language to SQL query generation using KayGraph for building database query interfaces.

## What it does

This example shows how to:
- **Natural Language Understanding**: Parse user queries
- **Schema Awareness**: Understand database structure
- **SQL Generation**: Create valid SQL from text
- **Query Validation**: Ensure SQL safety and correctness
- **Error Correction**: Fix and retry invalid queries
- **Result Formatting**: Present data in readable format

## Features

- Mock SQL parser with intent recognition
- Database schema introspection
- SQL generation with multiple dialects
- Query validation and sanitization
- Automatic error correction
- Pretty result formatting

## How to run

```bash
python main.py
```

## Architecture

```
ParseQueryNode → SchemaAnalysisNode → SQLGenerationNode → SQLValidationNode → ExecuteQueryNode → FormatResultsNode
                                                                ↓ (invalid)
                                                          SQLCorrectionNode ←┘
```

### Node Descriptions

1. **ParseQueryNode**: Extracts intent, entities, and filters from natural language
2. **SchemaAnalysisNode**: Identifies relevant tables and columns
3. **SQLGenerationNode**: Constructs SQL query from components
4. **SQLValidationNode**: Checks syntax and prevents SQL injection
5. **ExecuteQueryNode**: Runs query against mock database
6. **SQLCorrectionNode**: Fixes common SQL errors
7. **FormatResultsNode**: Formats results as tables or JSON

## Example Queries

### Basic Queries
```
"Show all customers"
→ SELECT * FROM customers

"Find products under $50"
→ SELECT * FROM products WHERE price < 50

"Count orders by status"
→ SELECT status, COUNT(*) FROM orders GROUP BY status
```

### Complex Queries
```
"Top 5 customers by total spending"
→ SELECT c.name, SUM(o.total) as total_spent 
  FROM customers c 
  JOIN orders o ON c.id = o.customer_id 
  GROUP BY c.id, c.name 
  ORDER BY total_spent DESC 
  LIMIT 5

"Products that have never been ordered"
→ SELECT p.* FROM products p 
  LEFT JOIN order_items oi ON p.id = oi.product_id 
  WHERE oi.id IS NULL
```

## Mock Database Schema

### Customers Table
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR)
- email (VARCHAR)
- created_at (TIMESTAMP)

### Products Table
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR)
- price (DECIMAL)
- category (VARCHAR)
- stock (INTEGER)

### Orders Table
- id (INTEGER, PRIMARY KEY)
- customer_id (INTEGER, FOREIGN KEY)
- status (VARCHAR)
- total (DECIMAL)
- created_at (TIMESTAMP)

### Order_Items Table
- id (INTEGER, PRIMARY KEY)
- order_id (INTEGER, FOREIGN KEY)
- product_id (INTEGER, FOREIGN KEY)
- quantity (INTEGER)
- price (DECIMAL)

## Query Patterns

### 1. Selection Patterns
- Simple: "show/list/find [entities]"
- Filtered: "find [entities] where/with [condition]"
- Limited: "top/first [n] [entities]"

### 2. Aggregation Patterns
- Count: "count/how many [entities]"
- Sum: "total [field] for [entities]"
- Average: "average [field] of [entities]"
- Group: "[aggregate] by [field]"

### 3. Join Patterns
- Inner: "[entities] with/and their [related]"
- Left: "[entities] including those without [related]"
- Multiple: "[entity1] and [entity2] and [entity3]"

## Security Features

1. **SQL Injection Prevention**
   - Parameterized queries
   - Input sanitization
   - Whitelist of allowed operations

2. **Access Control**
   - Read-only queries by default
   - No DDL operations allowed
   - Limited to specific tables

3. **Resource Limits**
   - Query timeout
   - Result size limits
   - Complexity restrictions

## Integration Examples

### With Real Databases

```python
# PostgreSQL
import psycopg2
conn = psycopg2.connect("postgresql://user:pass@localhost/db")

# MySQL
import pymysql
conn = pymysql.connect(host='localhost', user='user', password='pass', db='db')

# SQLite
import sqlite3
conn = sqlite3.connect('database.db')
```

### With ORMs

```python
# SQLAlchemy
from sqlalchemy import create_engine
engine = create_engine('sqlite:///database.db')

# Django ORM
from myapp.models import Customer
customers = Customer.objects.filter(created_at__gte='2024-01-01')
```

## Advanced Features

### 1. Query Explanation
```python
def explain_query(sql):
    """Explain what a SQL query does in plain English."""
    # Parse SQL and generate explanation
    return "This query finds all customers who placed orders in the last 30 days"
```

### 2. Query Optimization
```python
def optimize_query(sql):
    """Suggest query optimizations."""
    suggestions = []
    if "SELECT *" in sql:
        suggestions.append("Select only needed columns")
    if not "LIMIT" in sql:
        suggestions.append("Add LIMIT clause for large tables")
    return suggestions
```

### 3. Multi-dialect Support
```python
def translate_sql(sql, from_dialect="postgresql", to_dialect="mysql"):
    """Translate SQL between dialects."""
    # Handle dialect-specific syntax
    return translated_sql
```

## Use Cases

- **Business Intelligence**: Natural language reporting
- **Data Exploration**: Interactive data analysis
- **Customer Support**: Query customer data
- **Analytics Dashboards**: Dynamic queries
- **Chatbots**: Database-backed Q&A

## Performance Tips

1. **Query Caching**: Cache frequent queries
2. **Index Hints**: Suggest useful indexes
3. **Query Plans**: Analyze execution plans
4. **Batch Operations**: Group similar queries
5. **Connection Pooling**: Reuse connections

## Best Practices

1. **Always validate user input**
2. **Use read-only connections**
3. **Log all queries for audit**
4. **Set query timeouts**
5. **Limit result sizes**
6. **Provide query explanations**

## Dependencies

This example uses mock implementations. For production:
- `sqlglot`: SQL parsing and generation
- `sqlalchemy`: Database abstraction
- `sqlparse`: SQL formatting
- Database drivers for your specific database