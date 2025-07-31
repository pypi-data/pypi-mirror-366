"""
SQL-specific nodes for KayGraph with connection pooling and transaction support.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager
from datetime import datetime

# Import the base KayGraph nodes
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, ValidatedNode, MetricsNode

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Simple connection pool implementation."""
    def __init__(self, create_connection_func, max_size=10):
        self.create_connection = create_connection_func
        self.max_size = max_size
        self.pool = []
        self.in_use = set()
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        conn = None
        try:
            # Try to get from pool
            if self.pool:
                conn = self.pool.pop()
            elif len(self.in_use) < self.max_size:
                conn = self.create_connection()
            else:
                # Wait for a connection to be returned
                while not self.pool:
                    time.sleep(0.1)
                conn = self.pool.pop()
            
            self.in_use.add(conn)
            yield conn
        finally:
            if conn:
                self.in_use.discard(conn)
                if len(self.pool) < self.max_size:
                    self.pool.append(conn)
                else:
                    conn.close()


class SQLNode(ValidatedNode, MetricsNode):
    """
    Base node for SQL execution with connection pooling and monitoring.
    """
    
    # Class-level connection pool
    _connection_pool = None
    
    def __init__(self, 
                 query: Optional[str] = None,
                 params: Optional[Dict] = None,
                 transaction: bool = True,
                 timeout: Optional[int] = None,
                 max_retries: int = 3,
                 node_id: Optional[str] = None):
        """
        Initialize SQL node.
        
        Args:
            query: SQL query to execute (can also come from shared/params)
            params: Query parameters for safe parameterized queries
            transaction: Whether to wrap execution in a transaction
            timeout: Query timeout in seconds
            max_retries: Number of retries on failure
            node_id: Node identifier
        """
        super().__init__(max_retries=max_retries, node_id=node_id)
        self.query = query
        self.query_params = params or {}
        self.use_transaction = transaction
        self.timeout = timeout
    
    @classmethod
    def configure_pool(cls, db_config: Dict[str, Any], pool_size: int = 10):
        """Configure the connection pool for all SQLNode instances."""
        def create_connection():
            # Example using psycopg2, adjust for your database
            import psycopg2
            conn = psycopg2.connect(**db_config)
            conn.autocommit = False  # We'll manage transactions
            return conn
        
        cls._connection_pool = ConnectionPool(create_connection, pool_size)
        logger.info(f"Configured connection pool with size {pool_size}")
    
    def validate_input(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SQL query and parameters."""
        query = prep_res.get("query")
        if not query:
            raise ValueError("No SQL query provided")
        
        # Basic SQL injection prevention
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
        query_upper = query.upper()
        if any(kw in query_upper for kw in dangerous_keywords) and "WHERE" not in query_upper:
            raise ValueError(f"Dangerous SQL operation without WHERE clause")
        
        return prep_res
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare SQL execution context."""
        # Get query from multiple sources (priority order)
        query = self.query or shared.get("sql_query") or self.params.get("query")
        
        # Get parameters
        params = {
            **self.query_params,
            **shared.get("sql_params", {}),
            **self.params.get("params", {})
        }
        
        # Add execution metadata
        return {
            "query": query,
            "params": params,
            "start_time": datetime.utcnow(),
            "timeout": self.timeout,
            "use_transaction": self.use_transaction
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query with connection from pool."""
        if not self._connection_pool:
            raise RuntimeError("Connection pool not configured. Call SQLNode.configure_pool() first.")
        
        query = prep_res["query"]
        params = prep_res["params"]
        
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Set query timeout if specified
                if prep_res["timeout"]:
                    cursor.execute(f"SET statement_timeout = {prep_res['timeout'] * 1000}")
                
                # Execute query
                start = time.time()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                execution_time = time.time() - start
                
                # Get results based on query type
                if query.strip().upper().startswith(("SELECT", "WITH")):
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    result = {
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows)
                    }
                else:
                    # For INSERT/UPDATE/DELETE
                    result = {
                        "row_count": cursor.rowcount
                    }
                
                # Commit if using transaction
                if prep_res["use_transaction"]:
                    conn.commit()
                
                return {
                    "success": True,
                    "result": result,
                    "execution_time": execution_time,
                    "query": query
                }
                
            except Exception as e:
                # Rollback on error
                if prep_res["use_transaction"]:
                    conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def validate_output(self, exec_res: Dict[str, Any]) -> Dict[str, Any]:
        """Validate execution results."""
        if not exec_res.get("success"):
            raise ValueError("SQL execution failed")
        
        # Log slow queries
        if exec_res["execution_time"] > 5.0:
            logger.warning(f"Slow query detected: {exec_res['execution_time']:.2f}s")
        
        return exec_res
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store results and determine next action."""
        # Store results in shared
        shared["sql_result"] = exec_res["result"]
        shared["last_execution"] = {
            "query": exec_res["query"],
            "execution_time": exec_res["execution_time"],
            "timestamp": prep_res["start_time"],
            "row_count": exec_res["result"].get("row_count", 0)
        }
        
        # Log execution
        logger.info(f"SQL executed in {exec_res['execution_time']:.2f}s, "
                   f"rows: {exec_res['result'].get('row_count', 0)}")
        
        return None  # Default transition
    
    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Handle SQL errors with logging and alerting."""
        logger.error(f"SQL execution failed: {error}")
        
        # Store error information
        shared["sql_error"] = {
            "error": str(error),
            "timestamp": datetime.utcnow(),
            "query": self.query or shared.get("sql_query", "Unknown")
        }
        
        # Could send alerts here (email, Slack, etc.)
        # alert_ops_team(f"SQL failure in {self.node_id}: {error}")
        
        return False  # Don't suppress, let retry logic handle it


class TransactionalSQLNode(SQLNode):
    """
    SQL node that ensures all operations within a graph run in a single transaction.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_transaction = True
        self._transaction_conn = None
    
    def setup_resources(self):
        """Get a dedicated connection for the transaction."""
        if not self._connection_pool:
            raise RuntimeError("Connection pool not configured")
        
        # This would need enhancement to ConnectionPool to support 
        # checking out connections for longer periods
        self._transaction_conn = self._connection_pool.create_connection()
        self._transaction_conn.autocommit = False
        logger.info("Started transaction")
    
    def cleanup_resources(self):
        """Commit or rollback the transaction."""
        if self._transaction_conn:
            try:
                if self.get_context("has_error"):
                    self._transaction_conn.rollback()
                    logger.info("Transaction rolled back due to error")
                else:
                    self._transaction_conn.commit()
                    logger.info("Transaction committed successfully")
            finally:
                self._transaction_conn.close()
                self._transaction_conn = None
    
    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Mark transaction for rollback on error."""
        self.set_context("has_error", True)
        return super().on_error(shared, error)


class BulkInsertNode(SQLNode):
    """
    Optimized node for bulk insert operations.
    """
    
    def __init__(self, table_name: str, columns: List[str], 
                 batch_size: int = 1000, *args, **kwargs):
        self.table_name = table_name
        self.columns = columns
        self.batch_size = batch_size
        super().__init__(*args, **kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare bulk insert data."""
        data = shared.get("bulk_data", [])
        
        if not data:
            raise ValueError("No bulk data provided")
        
        # Split into batches
        batches = [data[i:i + self.batch_size] 
                   for i in range(0, len(data), self.batch_size)]
        
        return {
            "batches": batches,
            "total_rows": len(data),
            "use_transaction": True,
            "timeout": self.timeout
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bulk insert in batches."""
        if not self._connection_pool:
            raise RuntimeError("Connection pool not configured")
        
        total_inserted = 0
        start_time = time.time()
        
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                for batch in prep_res["batches"]:
                    # Build VALUES clause
                    placeholders = ",".join(
                        f"({','.join(['%s'] * len(self.columns))})" 
                        for _ in batch
                    )
                    
                    query = f"""
                        INSERT INTO {self.table_name} ({','.join(self.columns)})
                        VALUES {placeholders}
                    """
                    
                    # Flatten batch data
                    values = []
                    for row in batch:
                        values.extend(row[col] for col in self.columns)
                    
                    cursor.execute(query, values)
                    total_inserted += cursor.rowcount
                
                conn.commit()
                
                return {
                    "success": True,
                    "result": {
                        "row_count": total_inserted,
                        "batch_count": len(prep_res["batches"])
                    },
                    "execution_time": time.time() - start_time,
                    "query": f"BULK INSERT INTO {self.table_name}"
                }
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()


if __name__ == "__main__":
    # Test the SQL nodes
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example configuration
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "test",
        "user": "test_user",
        "password": "test_password"
    }
    
    # Configure pool (would fail without actual DB)
    try:
        SQLNode.configure_pool(db_config)
        
        # Example usage
        shared = {
            "sql_query": "SELECT * FROM users WHERE created_at > %s",
            "sql_params": {"created_at": "2024-01-01"}
        }
        
        node = SQLNode(max_retries=3)
        # node.run(shared)  # Would execute if DB was available
        
        print("SQL nodes configured successfully")
    except Exception as e:
        print(f"Configuration example (would work with real DB): {e}")