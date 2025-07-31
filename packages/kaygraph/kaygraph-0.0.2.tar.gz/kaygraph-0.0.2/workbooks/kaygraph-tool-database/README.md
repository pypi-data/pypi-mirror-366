# KayGraph Tool Integration - SQLite Database

Demonstrates integrating SQLite database operations with KayGraph for building task management workflows with persistent storage.

## What it does

This example shows how to:
- **Database Operations**: Create, read, update, delete (CRUD)
- **Schema Management**: Initialize and manage database schema
- **Batch Processing**: Update multiple records efficiently
- **Search & Query**: Full-text search and filtering
- **Reporting**: Generate insights from stored data

## Features

- Complete task management system
- SQLite database integration
- Batch update operations
- Search functionality
- Statistical reporting
- Transaction history tracking

## How to run

```bash
python main.py
```

## Architecture

```
InitDatabaseNode → CreateTaskNode → ListTasksNode → UpdateTaskBatchNode → SearchTasksNode → GenerateReportNode
```

### Node Descriptions

1. **InitDatabaseNode**: Creates database and schema
2. **CreateTaskNode**: Adds new tasks to database
3. **ListTasksNode**: Queries and displays tasks
4. **UpdateTaskBatchNode**: Updates multiple tasks in batch
5. **SearchTasksNode**: Full-text search across tasks
6. **GenerateReportNode**: Creates summary report

## Database Schema

```sql
-- Main tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 3,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    due_date TIMESTAMP,
    tags TEXT,           -- JSON array
    metadata TEXT        -- JSON object
);

-- History tracking
CREATE TABLE task_history (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    action TEXT,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks (id)
);
```

## Tool Integration Pattern

```python
# Database manager as context manager
with DatabaseManager(db_path) as db:
    # Automatic connection management
    task_id = db.create_task(task_data)
    tasks = db.list_tasks(status="pending")
```

## Example Output

```
🗄️  KayGraph Database Tool Integration
============================================================
This example demonstrates SQLite database integration
for task management workflows.

Creating 5 sample tasks...

--- Processing Task 1/5 ---
[INFO] Initialized database: task_management.db

✅ Created task #1: Implement database integration

📋 Tasks (1 found):
------------------------------------------------------------
⏳ [  1] Implement database integration            P5
        Add SQLite support to KayGraph examples
        Tags: development, kaygraph

📊 Statistics:
  Total tasks: 1
  By status: {'pending': 1}
  Overdue: 0

--- Processing Task 3/5 ---
✅ Created task #3: Code review

📋 Tasks (3 found):
------------------------------------------------------------
⏳ [  1] Implement database integration            P5
⏳ [  2] Write documentation                       P4
⏳ [  3] Code review                               P3

📝 Batch Update Results:
  ✅ Successful: 2
  ❌ Failed: 0
  - Updated #1: Implement database integration -> in_progress
  - Updated #2: Write documentation -> in_progress

🔍 Search Results for 'project':
Found 2 matching tasks
------------------------------------------------------------
[  1] Implement database integration
      Add SQLite support to KayGraph examples
[  4] Update dependencies
      Check and update project dependencies

============================================================
📊 TASK MANAGEMENT REPORT
============================================================
Generated: 2024-03-15T10:30:45
Database: task_management.db

📈 Summary:
  Total tasks: 5
  - Pending: 3
  - In_progress: 2

💡 Insights:
  • Completion rate: 0.0% (0/5 tasks)
  • High priority tasks (P4-P5): 3
  • ⚠️ 1 tasks are overdue!

📄 Full report saved to: task_report.json

✨ Database integration example complete!
Database file: task_management.db
```

## Use Cases

- **Task Management**: Track todos, projects, issues
- **Inventory Systems**: Product catalog management
- **Event Logging**: Store and query application events
- **Configuration Storage**: Persistent settings
- **Data Pipeline**: ETL with persistent checkpoints

## Advanced Features

### 1. Transaction Support
```python
def transfer_task(from_user: int, to_user: int, task_id: int):
    with db.connection:  # Transaction context
        # All operations succeed or rollback
        db.update_task(task_id, assigned_to=to_user)
        db.log_transfer(from_user, to_user, task_id)
```

### 2. Custom Queries
```python
class AnalyticsNode(Node):
    def exec(self, data):
        with DatabaseManager() as db:
            # Custom SQL query
            cursor = db.execute("""
                SELECT 
                    DATE(created_at) as day,
                    COUNT(*) as tasks_created
                FROM tasks
                GROUP BY DATE(created_at)
                ORDER BY day DESC
                LIMIT 30
            """)
            return cursor.fetchall()
```

### 3. Migration Support
```python
class MigrationNode(Node):
    def exec(self, data):
        migrations = [
            "ALTER TABLE tasks ADD COLUMN assignee TEXT",
            "CREATE INDEX idx_assignee ON tasks(assignee)",
        ]
        
        with DatabaseManager() as db:
            for migration in migrations:
                db.execute(migration)
```

## Best Practices

1. **Use Context Managers**: Automatic connection handling
2. **Parameterized Queries**: Prevent SQL injection
3. **Index Key Columns**: Improve query performance
4. **Transaction Batching**: Group related operations
5. **Schema Versioning**: Track database changes

## Performance Tips

- Use indexes for frequently queried columns
- Batch operations when possible
- Use PRAGMA settings for SQLite optimization
- Consider connection pooling for high load
- Regular VACUUM for database maintenance

## Security Considerations

- Always use parameterized queries
- Validate input data before storage
- Implement proper access controls
- Encrypt sensitive data
- Regular backups

## Dependencies

This example uses Python's built-in `sqlite3` module - no external dependencies required!