"""
Database utility functions for SQLite operations.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage SQLite database operations."""
    
    def __init__(self, db_path: str = "tasks.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from database")
    
    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cursor object
        """
        self.connect()
        cursor = self.connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        self.connection.commit()
        return cursor
    
    def init_schema(self):
        """Initialize database schema."""
        schema = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            tags TEXT,
            metadata TEXT
        );
        
        CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            action TEXT,
            old_value TEXT,
            new_value TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            changed_by TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
        """
        
        for statement in schema.split(';'):
            if statement.strip():
                self.execute(statement)
        
        logger.info("Database schema initialized")
    
    def create_task(self, task_data: Dict[str, Any]) -> int:
        """
        Create a new task.
        
        Args:
            task_data: Task information
            
        Returns:
            ID of created task
        """
        # Extract fields
        title = task_data.get('title')
        description = task_data.get('description', '')
        status = task_data.get('status', 'pending')
        priority = task_data.get('priority', 3)
        due_date = task_data.get('due_date')
        tags = json.dumps(task_data.get('tags', []))
        metadata = json.dumps(task_data.get('metadata', {}))
        
        query = """
        INSERT INTO tasks (title, description, status, priority, due_date, tags, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = self.execute(query, (title, description, status, priority, due_date, tags, metadata))
        task_id = cursor.lastrowid
        
        # Log history
        self._log_history(task_id, 'created', None, json.dumps(task_data))
        
        logger.info(f"Created task {task_id}: {title}")
        return task_id
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task data or None
        """
        query = "SELECT * FROM tasks WHERE id = ?"
        cursor = self.execute(query, (task_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def list_tasks(self, 
                   status: str = None,
                   priority: int = None,
                   limit: int = 100,
                   offset: int = 0) -> List[Dict[str, Any]]:
        """
        List tasks with optional filters.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            limit: Maximum number of results
            offset: Skip first N results
            
        Returns:
            List of tasks
        """
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if priority is not None:
            query += " AND priority = ?"
            params.append(priority)
        
        query += " ORDER BY priority DESC, due_date ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = self.execute(query, tuple(params))
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def update_task(self, task_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a task.
        
        Args:
            task_id: Task ID
            updates: Fields to update
            
        Returns:
            True if updated
        """
        # Get current task
        current = self.get_task(task_id)
        if not current:
            return False
        
        # Build update query
        fields = []
        params = []
        
        for field, value in updates.items():
            if field in ['title', 'description', 'status', 'priority', 'due_date']:
                fields.append(f"{field} = ?")
                params.append(value)
            elif field == 'tags':
                fields.append("tags = ?")
                params.append(json.dumps(value))
            elif field == 'metadata':
                fields.append("metadata = ?")
                params.append(json.dumps(value))
        
        if not fields:
            return False
        
        # Add updated_at
        fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        params.append(task_id)
        
        self.execute(query, tuple(params))
        
        # Log history
        for field, new_value in updates.items():
            old_value = current.get(field)
            if old_value != new_value:
                self._log_history(task_id, f'updated_{field}', 
                                str(old_value), str(new_value))
        
        logger.info(f"Updated task {task_id}")
        return True
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted
        """
        # Check if exists
        task = self.get_task(task_id)
        if not task:
            return False
        
        # Delete history first
        self.execute("DELETE FROM task_history WHERE task_id = ?", (task_id,))
        
        # Delete task
        self.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        logger.info(f"Deleted task {task_id}")
        return True
    
    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search tasks by title or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tasks
        """
        sql = """
        SELECT * FROM tasks 
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY priority DESC, due_date ASC
        """
        
        search_param = f"%{query}%"
        cursor = self.execute(sql, (search_param, search_param))
        
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics."""
        stats = {
            'total_tasks': 0,
            'by_status': {},
            'by_priority': {},
            'overdue': 0
        }
        
        # Total tasks
        cursor = self.execute("SELECT COUNT(*) as count FROM tasks")
        stats['total_tasks'] = cursor.fetchone()['count']
        
        # By status
        cursor = self.execute("""
            SELECT status, COUNT(*) as count 
            FROM tasks 
            GROUP BY status
        """)
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # By priority
        cursor = self.execute("""
            SELECT priority, COUNT(*) as count 
            FROM tasks 
            GROUP BY priority
            ORDER BY priority DESC
        """)
        stats['by_priority'] = {row['priority']: row['count'] for row in cursor.fetchall()}
        
        # Overdue tasks
        cursor = self.execute("""
            SELECT COUNT(*) as count 
            FROM tasks 
            WHERE due_date < datetime('now') AND status != 'completed'
        """)
        stats['overdue'] = cursor.fetchone()['count']
        
        return stats
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        task = dict(row)
        
        # Parse JSON fields
        if task.get('tags'):
            task['tags'] = json.loads(task['tags'])
        else:
            task['tags'] = []
        
        if task.get('metadata'):
            task['metadata'] = json.loads(task['metadata'])
        else:
            task['metadata'] = {}
        
        return task
    
    def _log_history(self, task_id: int, action: str, 
                     old_value: str = None, new_value: str = None):
        """Log task history."""
        query = """
        INSERT INTO task_history (task_id, action, old_value, new_value, changed_by)
        VALUES (?, ?, ?, ?, ?)
        """
        
        self.execute(query, (task_id, action, old_value, new_value, 'system'))
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Convenience functions

def init_database(db_path: str = "tasks.db") -> DatabaseManager:
    """Initialize database with schema."""
    db = DatabaseManager(db_path)
    db.init_schema()
    return db


def create_task(title: str, description: str = "", **kwargs) -> int:
    """Create a new task."""
    with DatabaseManager() as db:
        task_data = {
            'title': title,
            'description': description,
            **kwargs
        }
        return db.create_task(task_data)


def list_tasks(status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
    """List tasks with optional status filter."""
    with DatabaseManager() as db:
        return db.list_tasks(status=status, limit=limit)


def update_task(task_id: int, **updates) -> bool:
    """Update a task."""
    with DatabaseManager() as db:
        return db.update_task(task_id, updates)


def delete_task(task_id: int) -> bool:
    """Delete a task."""
    with DatabaseManager() as db:
        return db.delete_task(task_id)


if __name__ == "__main__":
    # Test database operations
    print("Testing Database Manager")
    print("=" * 50)
    
    # Initialize database
    db = init_database("test_tasks.db")
    
    # Create some tasks
    task1_id = create_task(
        "Complete project proposal",
        "Write and submit the Q1 project proposal",
        priority=5,
        tags=["work", "urgent"]
    )
    print(f"Created task {task1_id}")
    
    task2_id = create_task(
        "Buy groceries",
        "Milk, eggs, bread",
        priority=2,
        tags=["personal", "shopping"]
    )
    print(f"Created task {task2_id}")
    
    # List tasks
    print("\nAll tasks:")
    tasks = list_tasks()
    for task in tasks:
        print(f"  [{task['id']}] {task['title']} - {task['status']} (P{task['priority']})")
    
    # Update task
    update_task(task1_id, status="in_progress")
    print(f"\nUpdated task {task1_id} status")
    
    # Get statistics
    with DatabaseManager("test_tasks.db") as db:
        stats = db.get_statistics()
        print(f"\nStatistics:")
        print(f"  Total tasks: {stats['total_tasks']}")
        print(f"  By status: {stats['by_status']}")
        print(f"  By priority: {stats['by_priority']}")