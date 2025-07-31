#!/usr/bin/env python3
"""
Background task nodes for FastAPI integration.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, ValidatedNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInfo:
    """Task information container."""
    
    def __init__(self, task_id: str, workflow: str, params: Dict[str, Any]):
        self.task_id = task_id
        self.workflow = workflow
        self.params = params
        self.status = TaskStatus.PENDING
        self.progress = 0.0
        self.message = "Task created"
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.progress_history = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "workflow": self.workflow,
            "params": self.params,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self._calculate_duration(),
            "progress_history": self.progress_history
        }
    
    def _calculate_duration(self) -> Optional[float]:
        """Calculate task duration in seconds."""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()


class TaskStore:
    """In-memory task storage."""
    
    def __init__(self):
        self.tasks: Dict[str, TaskInfo] = {}
        self._lock = asyncio.Lock()
    
    async def create_task(self, workflow: str, params: Dict[str, Any]) -> str:
        """Create a new task."""
        async with self._lock:
            task_id = str(uuid.uuid4())
            self.tasks[task_id] = TaskInfo(task_id, workflow, params)
            return task_id
    
    async def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task by ID."""
        async with self._lock:
            return self.tasks.get(task_id)
    
    async def update_task(self, task_id: str, **kwargs):
        """Update task information."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if task:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                
                # Track progress history
                if "progress" in kwargs:
                    task.progress_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "progress": kwargs["progress"],
                        "message": kwargs.get("message", "")
                    })
    
    async def list_tasks(self, status: Optional[TaskStatus] = None) -> List[TaskInfo]:
        """List all tasks, optionally filtered by status."""
        async with self._lock:
            tasks = list(self.tasks.values())
            if status:
                tasks = [t for t in tasks if t.status == status]
            return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        async with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
            return False
    
    async def cleanup_old_tasks(self, max_age_seconds: int = 86400):
        """Clean up tasks older than max_age_seconds."""
        async with self._lock:
            now = datetime.now()
            to_delete = []
            
            for task_id, task in self.tasks.items():
                if task.completed_at:
                    age = (now - task.completed_at).total_seconds()
                    if age > max_age_seconds:
                        to_delete.append(task_id)
            
            for task_id in to_delete:
                del self.tasks[task_id]
            
            return len(to_delete)


class BackgroundTaskNode(AsyncNode):
    """Base node for background task execution."""
    
    def __init__(self, task_store: TaskStore, node_id: str = None):
        super().__init__(node_id or "background_task")
        self.task_store = task_store
    
    async def update_progress(self, task_id: str, progress: float, message: str = ""):
        """Update task progress."""
        await self.task_store.update_task(
            task_id,
            progress=progress,
            message=message
        )
        logger.info(f"Task {task_id}: {progress}% - {message}")
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare background task."""
        task_id = shared.get("task_id")
        if not task_id:
            raise ValueError("task_id required in shared store")
        
        task = await self.task_store.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Mark as running
        await self.task_store.update_task(
            task_id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now(),
            message="Task started"
        )
        
        return {
            "task_id": task_id,
            "task": task
        }
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute background task (override in subclasses)."""
        task_id = prep_res["task_id"]
        
        # Simulate work with progress updates
        for i in range(5):
            await asyncio.sleep(1)
            progress = (i + 1) * 20
            await self.update_progress(
                task_id,
                progress,
                f"Processing step {i + 1}/5"
            )
        
        return {"result": "Task completed successfully"}
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
                        exec_res: Dict[str, Any]) -> Optional[str]:
        """Update task status after execution."""
        task_id = prep_res["task_id"]
        
        if "error" in exec_res:
            # Task failed
            await self.task_store.update_task(
                task_id,
                status=TaskStatus.FAILED,
                error=str(exec_res["error"]),
                completed_at=datetime.now(),
                message="Task failed"
            )
        else:
            # Task completed
            await self.task_store.update_task(
                task_id,
                status=TaskStatus.COMPLETED,
                result=exec_res.get("result"),
                completed_at=datetime.now(),
                progress=100.0,
                message="Task completed"
            )
        
        shared["task_result"] = exec_res
        return None
    
    async def on_error(self, error: Exception, shared: Dict[str, Any], 
                      prep_res: Optional[Dict[str, Any]] = None):
        """Handle errors during task execution."""
        if prep_res and "task_id" in prep_res:
            await self.task_store.update_task(
                prep_res["task_id"],
                status=TaskStatus.FAILED,
                error=str(error),
                completed_at=datetime.now(),
                message=f"Task failed: {str(error)}"
            )


class DataProcessingTaskNode(BackgroundTaskNode):
    """Background task for data processing."""
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Process data in background."""
        task_id = prep_res["task_id"]
        task = prep_res["task"]
        
        # Get processing parameters
        data = task.params.get("data", [])
        chunk_size = task.params.get("chunk_size", 10)
        
        if not data:
            return {"result": "No data to process"}
        
        # Process data in chunks
        results = []
        total_chunks = (len(data) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            chunk_num = i // chunk_size + 1
            
            # Process chunk
            await self.update_progress(
                task_id,
                (chunk_num / total_chunks) * 100,
                f"Processing chunk {chunk_num}/{total_chunks}"
            )
            
            # Simulate processing
            await asyncio.sleep(0.5)
            chunk_result = [item.upper() if isinstance(item, str) else item 
                          for item in chunk]
            results.extend(chunk_result)
        
        return {
            "result": {
                "processed_items": len(results),
                "chunks_processed": total_chunks,
                "sample": results[:5] if results else []
            }
        }


class ModelTrainingTaskNode(BackgroundTaskNode):
    """Background task for model training."""
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Train model in background."""
        task_id = prep_res["task_id"]
        task = prep_res["task"]
        
        # Get training parameters
        epochs = task.params.get("epochs", 10)
        batch_size = task.params.get("batch_size", 32)
        learning_rate = task.params.get("learning_rate", 0.001)
        
        # Simulate training epochs
        metrics_history = []
        
        for epoch in range(epochs):
            # Update progress
            progress = ((epoch + 1) / epochs) * 100
            await self.update_progress(
                task_id,
                progress,
                f"Training epoch {epoch + 1}/{epochs}"
            )
            
            # Simulate epoch training
            await asyncio.sleep(1)
            
            # Generate mock metrics
            loss = 1.0 / (epoch + 1) + 0.1 * (0.5 - asyncio.get_event_loop().time() % 1)
            accuracy = min(0.99, 0.5 + (epoch + 1) * 0.05)
            
            metrics = {
                "epoch": epoch + 1,
                "loss": round(loss, 4),
                "accuracy": round(accuracy, 4),
                "learning_rate": learning_rate
            }
            metrics_history.append(metrics)
        
        return {
            "result": {
                "final_loss": metrics_history[-1]["loss"],
                "final_accuracy": metrics_history[-1]["accuracy"],
                "epochs_completed": epochs,
                "metrics_history": metrics_history,
                "model_path": f"/models/model_{task_id}.pkl"
            }
        }


class DocumentIndexingTaskNode(BackgroundTaskNode):
    """Background task for document indexing."""
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Index documents in background."""
        task_id = prep_res["task_id"]
        task = prep_res["task"]
        
        # Get indexing parameters
        documents = task.params.get("documents", [])
        chunk_size = task.params.get("chunk_size", 500)
        
        if not documents:
            return {"result": "No documents to index"}
        
        # Process each document
        indexed_docs = []
        total_chunks = 0
        
        for i, doc_path in enumerate(documents):
            # Update progress
            doc_progress = ((i + 1) / len(documents)) * 100
            await self.update_progress(
                task_id,
                doc_progress,
                f"Indexing document {i + 1}/{len(documents)}: {doc_path}"
            )
            
            # Simulate document processing
            await asyncio.sleep(0.5)
            
            # Mock chunking and indexing
            doc_size = 5000  # Mock document size
            chunks = (doc_size + chunk_size - 1) // chunk_size
            total_chunks += chunks
            
            indexed_docs.append({
                "path": doc_path,
                "chunks": chunks,
                "embeddings_created": chunks,
                "index_id": f"idx_{task_id}_{i}"
            })
        
        return {
            "result": {
                "documents_indexed": len(indexed_docs),
                "total_chunks": total_chunks,
                "index_location": f"/indexes/index_{task_id}",
                "documents": indexed_docs
            }
        }


class TaskQueueNode(AsyncNode):
    """Node for managing task queue."""
    
    def __init__(self, task_store: TaskStore, max_workers: int = 4,
                 node_id: str = None):
        super().__init__(node_id or "task_queue")
        self.task_store = task_store
        self.max_workers = max_workers
        self._queue = asyncio.Queue()
        self._workers = []
        self._shutdown = False
    
    async def start_workers(self):
        """Start queue workers."""
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)
        logger.info(f"Started {self.max_workers} queue workers")
    
    async def stop_workers(self):
        """Stop queue workers."""
        self._shutdown = True
        
        # Add sentinel values to wake up workers
        for _ in self._workers:
            await self._queue.put(None)
        
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        logger.info("All queue workers stopped")
    
    async def _worker(self, worker_id: int):
        """Queue worker coroutine."""
        logger.info(f"Worker {worker_id} started")
        
        while not self._shutdown:
            try:
                # Get task from queue
                task_info = await self._queue.get()
                if task_info is None:
                    break
                
                # Process task based on workflow type
                await self._process_task(task_info)
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
            finally:
                self._queue.task_done()
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _process_task(self, task_info: dict):
        """Process a queued task."""
        task_id = task_info["task_id"]
        workflow = task_info["workflow"]
        
        try:
            # Select appropriate node based on workflow
            if workflow == "data_processing":
                node = DataProcessingTaskNode(self.task_store)
            elif workflow == "model_training":
                node = ModelTrainingTaskNode(self.task_store)
            elif workflow == "document_indexing":
                node = DocumentIndexingTaskNode(self.task_store)
            else:
                node = BackgroundTaskNode(self.task_store)
            
            # Run the node
            shared = {"task_id": task_id}
            await node.run_async(shared)
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            await self.task_store.update_task(
                task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                completed_at=datetime.now()
            )
    
    async def submit_task(self, workflow: str, params: Dict[str, Any]) -> str:
        """Submit a task to the queue."""
        # Create task in store
        task_id = await self.task_store.create_task(workflow, params)
        
        # Add to queue
        await self._queue.put({
            "task_id": task_id,
            "workflow": workflow
        })
        
        logger.info(f"Task {task_id} submitted to queue")
        return task_id
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare queue management."""
        action = shared.get("queue_action", "status")
        return {"action": action}
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue management action."""
        action = prep_res["action"]
        
        if action == "status":
            return {
                "queue_size": self._queue.qsize(),
                "max_workers": self.max_workers,
                "active_workers": len([w for w in self._workers if not w.done()]),
                "shutdown": self._shutdown
            }
        
        return {"status": "ok"}
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
                        exec_res: Dict[str, Any]) -> Optional[str]:
        """Update shared store with queue status."""
        shared["queue_status"] = exec_res
        return None


class TaskCleanupNode(AsyncNode):
    """Node for cleaning up old tasks."""
    
    def __init__(self, task_store: TaskStore, max_age_hours: int = 24,
                 node_id: str = None):
        super().__init__(node_id or "task_cleanup")
        self.task_store = task_store
        self.max_age_seconds = max_age_hours * 3600
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up old tasks."""
        deleted_count = await self.task_store.cleanup_old_tasks(
            self.max_age_seconds
        )
        
        logger.info(f"Cleaned up {deleted_count} old tasks")
        
        return {
            "deleted_count": deleted_count,
            "max_age_hours": self.max_age_seconds // 3600
        }


# Example usage
if __name__ == "__main__":
    async def main():
        # Create task store
        task_store = TaskStore()
        
        # Create and start queue
        queue_node = TaskQueueNode(task_store, max_workers=2)
        await queue_node.start_workers()
        
        try:
            # Submit some tasks
            task1_id = await queue_node.submit_task(
                "data_processing",
                {"data": ["hello", "world", "test"], "chunk_size": 2}
            )
            print(f"Submitted data processing task: {task1_id}")
            
            task2_id = await queue_node.submit_task(
                "model_training",
                {"epochs": 5, "batch_size": 32}
            )
            print(f"Submitted model training task: {task2_id}")
            
            task3_id = await queue_node.submit_task(
                "document_indexing",
                {"documents": ["doc1.pdf", "doc2.pdf"], "chunk_size": 500}
            )
            print(f"Submitted document indexing task: {task3_id}")
            
            # Wait a bit and check status
            await asyncio.sleep(2)
            
            # Get task status
            for task_id in [task1_id, task2_id, task3_id]:
                task = await task_store.get_task(task_id)
                if task:
                    print(f"\nTask {task_id}:")
                    print(f"  Status: {task.status.value}")
                    print(f"  Progress: {task.progress}%")
                    print(f"  Message: {task.message}")
            
            # Wait for completion
            await asyncio.sleep(10)
            
            # Final status
            print("\n=== Final Status ===")
            tasks = await task_store.list_tasks()
            for task in tasks:
                print(f"\nTask {task.task_id}:")
                print(f"  Workflow: {task.workflow}")
                print(f"  Status: {task.status.value}")
                print(f"  Duration: {task._calculate_duration():.2f}s")
                if task.result:
                    print(f"  Result: {task.result}")
            
        finally:
            # Stop workers
            await queue_node.stop_workers()
    
    # Run example
    asyncio.run(main())