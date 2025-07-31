import json
import random
import tempfile
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from kaygraph import Node
import logging

logging.basicConfig(level=logging.INFO)


class DatabasePool:
    """Simulated database connection pool"""
    
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self.active_connections = []
        self.connection_count = 0
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup"""
        if len(self.active_connections) >= self.max_connections:
            raise RuntimeError(f"Connection pool exhausted (max: {self.max_connections})")
        
        # Create mock connection
        connection_id = f"conn_{self.connection_count}"
        self.connection_count += 1
        
        # Simulate connection setup
        mock_connection = MockDatabaseConnection(connection_id)
        self.active_connections.append(mock_connection)
        
        self.logger.info(f"Acquired database connection: {connection_id}")
        
        try:
            yield mock_connection
        finally:
            # Cleanup connection
            self.active_connections.remove(mock_connection)
            mock_connection.close()
            self.logger.info(f"Released database connection: {connection_id}")
    
    def close_all(self):
        """Close all connections in the pool"""
        for conn in self.active_connections[:]:
            conn.close()
            self.active_connections.remove(conn)
        self.logger.info("Closed all database connections")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "max_connections": self.max_connections,
            "active_connections": len(self.active_connections),
            "total_created": self.connection_count
        }


class MockDatabaseConnection:
    """Mock database connection"""
    
    def __init__(self, connection_id: str):
        self.connection_id = connection_id
        self.is_open = True
        self.queries_executed = 0
    
    def execute(self, query: str) -> List[Dict[str, Any]]:
        """Execute a mock database query"""
        if not self.is_open:
            raise RuntimeError("Connection is closed")
        
        self.queries_executed += 1
        
        # Simulate query execution time
        time.sleep(random.uniform(0.1, 0.3))
        
        # Generate mock results
        if "SELECT" in query.upper():
            return [
                {
                    "id": i,
                    "name": f"record_{i}",
                    "value": random.randint(1, 100),
                    "category": random.choice(["A", "B", "C"])
                }
                for i in range(random.randint(5, 15))
            ]
        else:
            return [{"affected_rows": random.randint(1, 5)}]
    
    def close(self):
        """Close the connection"""
        self.is_open = False


class HttpClientPool:
    """HTTP client session pool"""
    
    def __init__(self, max_sessions: int = 3):
        self.max_sessions = max_sessions
        self.active_sessions = []
        self.session_count = 0
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @contextmanager
    def get_session(self):
        """Get an HTTP session with automatic cleanup"""
        if len(self.active_sessions) >= self.max_sessions:
            # Reuse existing session
            session = random.choice(self.active_sessions)
            self.logger.info(f"Reusing HTTP session: {session.session_id}")
            yield session
            return
        
        # Create new session
        session_id = f"session_{self.session_count}"
        self.session_count += 1
        
        session = MockHttpSession(session_id)
        self.active_sessions.append(session)
        
        self.logger.info(f"Created HTTP session: {session_id}")
        
        try:
            yield session
        finally:
            # Keep session alive for reuse
            pass
    
    def close_all(self):
        """Close all HTTP sessions"""
        for session in self.active_sessions[:]:
            session.close()
            self.active_sessions.remove(session)
        self.logger.info("Closed all HTTP sessions")
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "max_sessions": self.max_sessions,
            "active_sessions": len(self.active_sessions),
            "total_created": self.session_count
        }


class MockHttpSession:
    """Mock HTTP session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.is_open = True
        self.requests_made = 0
    
    def post(self, url: str, data: Any) -> Dict[str, Any]:
        """Make a mock HTTP POST request"""
        if not self.is_open:
            raise RuntimeError("Session is closed")
        
        self.requests_made += 1
        
        # Simulate network latency
        time.sleep(random.uniform(0.2, 0.6))
        
        # Simulate occasional failures
        if random.random() < 0.05:
            raise ConnectionError("Network timeout")
        
        return {
            "status_code": 200,
            "response": f"Successfully uploaded {len(str(data))} bytes",
            "request_id": f"req_{self.requests_made}"
        }
    
    def close(self):
        """Close the session"""
        self.is_open = False


class ResourcePool:
    """Shared resource pool for the entire graph"""
    
    def __init__(self):
        self.db_pool = DatabasePool(max_connections=5)
        self.http_pool = HttpClientPool(max_sessions=3)
        self.temp_files = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def cleanup_all(self):
        """Cleanup all resources"""
        self.db_pool.close_all()
        self.http_pool.close_all()
        
        # Cleanup temp files
        for temp_file in self.temp_files:
            try:
                temp_file.close()
            except:
                pass
        self.temp_files.clear()
        
        self.logger.info("Cleaned up all resources")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive resource statistics"""
        return {
            "database": self.db_pool.get_stats(),
            "http": self.http_pool.get_stats(),
            "temp_files": len(self.temp_files)
        }


class DatabaseReaderNode(Node):
    """Reads data from database with connection pooling"""
    
    def setup_resources(self):
        """Setup database resources"""
        if "resource_pool" not in self._execution_context:
            self._execution_context["resource_pool"] = ResourcePool()
        self.logger.info("Database reader resources setup")
    
    def cleanup_resources(self):
        """Cleanup database resources"""
        if "resource_pool" in self._execution_context:
            # Don't cleanup shared pool here - let graph handle it
            pass
        self.logger.info("Database reader resources cleaned up")
    
    def prep(self, shared: Dict[str, Any]) -> str:
        query = self.params.get("query", "SELECT * FROM sample_data LIMIT 50")
        return query
    
    def exec(self, query: str) -> List[Dict[str, Any]]:
        """Execute database query with proper connection management"""
        resource_pool = self.get_context("resource_pool")
        
        with resource_pool.db_pool.get_connection() as conn:
            # Simulate multiple queries in same transaction
            results = conn.execute(query)
            
            # Additional query for metadata
            meta_query = "SELECT COUNT(*) as total FROM sample_data"
            metadata = conn.execute(meta_query)
            
            return {
                "data": results,
                "metadata": metadata[0] if metadata else {"total": len(results)},
                "connection_stats": {
                    "connection_id": conn.connection_id,
                    "queries_executed": conn.queries_executed
                }
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["database_results"] = exec_res
        shared["records_read"] = len(exec_res["data"])
        
        self.logger.info(f"Read {len(exec_res['data'])} records from database")
        return "processed"


class FileProcessorNode(Node):
    """Processes files with proper file handle management"""
    
    def setup_resources(self):
        """Setup file processing resources"""
        self.temp_files = []
        self.logger.info("File processor resources setup")
    
    def cleanup_resources(self):
        """Cleanup file resources"""
        for temp_file in self.temp_files:
            try:
                temp_file.close()
            except:
                pass
        self.temp_files.clear()
        self.logger.info("File processor resources cleaned up")
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("database_results", {}).get("data", [])
    
    def exec(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process data with temporary file management"""
        
        # Create temporary file for processing
        temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        self.temp_files.append(temp_file)
        
        try:
            # Write data to temp file
            json.dump(data, temp_file, indent=2)
            temp_file.flush()
            
            # Process the file (simulate heavy processing)
            with open(temp_file.name, 'r') as read_file:
                file_data = json.load(read_file)
                
                # Simulate processing time
                time.sleep(random.uniform(0.3, 0.8))
                
                # Process each record
                processed_data = []
                for record in file_data:
                    processed_record = {
                        **record,
                        "processed_at": time.time(),
                        "file_size": len(json.dumps(record)),
                        "checksum": hash(json.dumps(record, sort_keys=True))
                    }
                    processed_data.append(processed_record)
                
                # Create output file
                output_file = tempfile.NamedTemporaryFile(mode='w+', suffix='_output.json', delete=False)
                self.temp_files.append(output_file)
                
                json.dump(processed_data, output_file, indent=2)
                output_file.flush()
                
                return {
                    "processed_data": processed_data,
                    "input_file": temp_file.name,
                    "output_file": output_file.name,
                    "processing_stats": {
                        "records_processed": len(processed_data),
                        "input_size_bytes": temp_file.tell(),
                        "output_size_bytes": output_file.tell()
                    }
                }
                
        except Exception as e:
            self.logger.error(f"File processing failed: {e}")
            raise
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["file_results"] = exec_res
        shared["processed_records"] = len(exec_res["processed_data"])
        
        self.logger.info(f"Processed {len(exec_res['processed_data'])} records through file system")
        return "uploaded"


class ApiUploaderNode(Node):
    """Uploads data using HTTP client sessions"""
    
    def setup_resources(self):
        """Setup HTTP client resources"""
        # Use shared resource pool
        self.logger.info("API uploader resources setup")
    
    def cleanup_resources(self):
        """Cleanup HTTP resources"""
        # Shared pool will handle cleanup
        self.logger.info("API uploader resources cleaned up")
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("file_results", {}).get("processed_data", [])
    
    def exec(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload data using HTTP session management"""
        resource_pool = self.get_context("resource_pool") or ResourcePool()
        
        upload_results = []
        
        # Upload in batches using session reuse
        batch_size = 5
        for i in range(0, len(processed_data), batch_size):
            batch = processed_data[i:i + batch_size]
            
            with resource_pool.http_pool.get_session() as session:
                try:
                    # Upload batch
                    upload_data = {
                        "batch_id": f"batch_{i // batch_size}",
                        "records": batch,
                        "timestamp": time.time()
                    }
                    
                    response = session.post("https://api.example.com/upload", upload_data)
                    
                    upload_results.append({
                        "batch_id": upload_data["batch_id"],
                        "records_count": len(batch),
                        "response": response,
                        "session_id": session.session_id
                    })
                    
                except Exception as e:
                    self.logger.error(f"Upload failed for batch {i // batch_size}: {e}")
                    # Continue with next batch
                    upload_results.append({
                        "batch_id": f"batch_{i // batch_size}",
                        "records_count": len(batch),
                        "error": str(e),
                        "session_id": session.session_id
                    })
        
        return {
            "upload_results": upload_results,
            "total_batches": len(upload_results),
            "successful_uploads": sum(1 for r in upload_results if "error" not in r),
            "failed_uploads": sum(1 for r in upload_results if "error" in r)
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["upload_results"] = exec_res
        
        success_count = exec_res["successful_uploads"]
        total_count = exec_res["total_batches"]
        
        self.logger.info(f"Uploaded {success_count}/{total_count} batches successfully")
        return "notified"


class NotificationNode(Node):
    """Sends notifications with resource cleanup"""
    
    def setup_resources(self):
        """Setup notification resources"""
        self.notification_clients = []
        self.logger.info("Notification resources setup")
    
    def cleanup_resources(self):
        """Cleanup notification resources"""
        for client in self.notification_clients:
            try:
                client.close()
            except:
                pass
        self.notification_clients.clear()
        self.logger.info("Notification resources cleaned up")
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "records_read": shared.get("records_read", 0),
            "processed_records": shared.get("processed_records", 0),
            "upload_results": shared.get("upload_results", {}),
            "resource_stats": shared.get("resource_stats", {})
        }
    
    def exec(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notifications about processing completion"""
        
        # Create mock notification client
        notification_client = MockNotificationClient()
        self.notification_clients.append(notification_client)
        
        try:
            # Prepare notification message
            upload_results = summary_data.get("upload_results", {})
            
            message = {
                "type": "processing_complete",
                "summary": {
                    "records_read": summary_data.get("records_read", 0),
                    "records_processed": summary_data.get("processed_records", 0),
                    "successful_uploads": upload_results.get("successful_uploads", 0),
                    "failed_uploads": upload_results.get("failed_uploads", 0)
                },
                "resource_usage": summary_data.get("resource_stats", {}),
                "timestamp": time.time()
            }
            
            # Send notification
            result = notification_client.send_notification("processing_team", message)
            
            return {
                "notification_sent": True,
                "notification_result": result,
                "message_size": len(json.dumps(message))
            }
            
        except Exception as e:
            self.logger.error(f"Notification failed: {e}")
            return {
                "notification_sent": False,
                "error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["notification_result"] = exec_res
        
        if exec_res.get("notification_sent", False):
            self.logger.info("Processing completion notification sent successfully")
        else:
            self.logger.warning("Failed to send notification")
        
        return None  # End of workflow


class MockNotificationClient:
    """Mock notification client"""
    
    def __init__(self):
        self.client_id = f"notif_{random.randint(1000, 9999)}"
        self.is_open = True
    
    def send_notification(self, recipient: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a mock notification"""
        if not self.is_open:
            raise RuntimeError("Notification client is closed")
        
        # Simulate sending time
        time.sleep(random.uniform(0.1, 0.3))
        
        return {
            "message_id": f"msg_{random.randint(10000, 99999)}",
            "recipient": recipient,
            "status": "delivered",
            "delivery_time": time.time()
        }
    
    def close(self):
        """Close the notification client"""
        self.is_open = False


class ResourceMonitorNode(Node):
    """Monitors resource usage across the workflow"""
    
    def prep(self, shared: Dict[str, Any]) -> Optional[ResourcePool]:
        # Get the shared resource pool
        return shared.get("_resource_pool")
    
    def exec(self, resource_pool: Optional[ResourcePool]) -> Dict[str, Any]:
        """Collect resource usage statistics"""
        if not resource_pool:
            return {"error": "No resource pool available"}
        
        stats = resource_pool.get_stats()
        
        # Add monitoring timestamp
        stats["monitoring_time"] = time.time()
        stats["status"] = "healthy"
        
        # Check for resource issues
        warnings = []
        
        db_stats = stats.get("database", {})
        if db_stats.get("active_connections", 0) > db_stats.get("max_connections", 0) * 0.8:
            warnings.append("Database connection pool near capacity")
        
        http_stats = stats.get("http", {})
        if http_stats.get("active_sessions", 0) > http_stats.get("max_sessions", 0) * 0.8:
            warnings.append("HTTP session pool near capacity")
        
        if warnings:
            stats["warnings"] = warnings
            stats["status"] = "warning"
        
        return stats
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["resource_stats"] = exec_res
        
        if exec_res.get("warnings"):
            for warning in exec_res["warnings"]:
                self.logger.warning(f"Resource warning: {warning}")
        
        return None