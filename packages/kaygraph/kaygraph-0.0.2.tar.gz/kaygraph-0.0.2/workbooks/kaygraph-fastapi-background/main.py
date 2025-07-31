#!/usr/bin/env python3
"""
FastAPI application with KayGraph background tasks.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from contextlib import asynccontextmanager

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from background_nodes import (
    TaskStore, TaskQueueNode, TaskStatus, TaskCleanupNode
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global task store and queue
task_store = TaskStore()
task_queue = None


# Mock FastAPI imports (in production, use real FastAPI)
class MockFastAPI:
    """Mock FastAPI for demonstration."""
    
    def __init__(self, lifespan=None, **kwargs):
        self.lifespan = lifespan
        self.kwargs = kwargs
        self.routes = []
    
    def get(self, path: str, **kwargs):
        def decorator(func):
            self.routes.append(("GET", path, func))
            return func
        return decorator
    
    def post(self, path: str, **kwargs):
        def decorator(func):
            self.routes.append(("POST", path, func))
            return func
        return decorator
    
    def delete(self, path: str, **kwargs):
        def decorator(func):
            self.routes.append(("DELETE", path, func))
            return func
        return decorator
    
    def websocket(self, path: str):
        def decorator(func):
            self.routes.append(("WS", path, func))
            return func
        return decorator


class MockWebSocket:
    """Mock WebSocket for demonstration."""
    
    async def accept(self):
        logger.info("WebSocket connection accepted")
    
    async def send_json(self, data: dict):
        logger.info(f"WebSocket send: {data}")
    
    async def receive_json(self) -> dict:
        await asyncio.sleep(1)
        return {"type": "ping"}
    
    async def close(self):
        logger.info("WebSocket connection closed")


class MockBackgroundTasks:
    """Mock background tasks for demonstration."""
    
    def add_task(self, func, *args, **kwargs):
        asyncio.create_task(func(*args, **kwargs))


class MockStreamingResponse:
    """Mock streaming response."""
    
    def __init__(self, generator, media_type="text/event-stream"):
        self.generator = generator
        self.media_type = media_type


# Application lifespan
@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager."""
    global task_queue
    
    # Startup
    logger.info("Starting FastAPI application...")
    task_queue = TaskQueueNode(task_store, max_workers=4)
    await task_queue.start_workers()
    
    # Start periodic cleanup
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    cleanup_task.cancel()
    await task_queue.stop_workers()


async def periodic_cleanup():
    """Periodically clean up old tasks."""
    cleanup_node = TaskCleanupNode(task_store, max_age_hours=24)
    
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            shared = {}
            await cleanup_node.run_async(shared)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Create FastAPI app
app = MockFastAPI(lifespan=lifespan)


# API Models (in production, use Pydantic)
class TaskSubmission:
    def __init__(self, workflow: str, params: Dict[str, Any]):
        self.workflow = workflow
        self.params = params


class TaskResponse:
    def __init__(self, task_id: str, status: str, message: str):
        self.task_id = task_id
        self.status = status
        self.message = message


# API Endpoints

@app.post("/tasks/")
async def submit_task(submission: TaskSubmission) -> TaskResponse:
    """Submit a new background task."""
    try:
        task_id = await task_queue.submit_task(
            submission.workflow,
            submission.params
        )
        
        return TaskResponse(
            task_id=task_id,
            status="accepted",
            message=f"Task {task_id} submitted successfully"
        )
    
    except Exception as e:
        logger.error(f"Task submission error: {e}")
        return TaskResponse(
            task_id="",
            status="error",
            message=str(e)
        )


@app.get("/tasks/")
async def list_tasks(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all tasks."""
    try:
        task_status = TaskStatus(status) if status else None
        tasks = await task_store.list_tasks(task_status)
        return [task.to_dict() for task in tasks]
    
    except Exception as e:
        logger.error(f"Task listing error: {e}")
        return []


@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> Dict[str, Any]:
    """Get task details."""
    task = await task_store.get_task(task_id)
    
    if not task:
        return {"error": f"Task {task_id} not found"}
    
    return task.to_dict()


@app.get("/tasks/{task_id}/result")
async def get_task_result(task_id: str) -> Dict[str, Any]:
    """Get task result."""
    task = await task_store.get_task(task_id)
    
    if not task:
        return {"error": f"Task {task_id} not found"}
    
    if task.status != TaskStatus.COMPLETED:
        return {
            "error": f"Task not completed. Current status: {task.status.value}"
        }
    
    return {
        "task_id": task_id,
        "result": task.result,
        "duration": task._calculate_duration()
    }


@app.get("/tasks/{task_id}/progress")
async def get_task_progress(task_id: str) -> Dict[str, Any]:
    """Get task progress."""
    task = await task_store.get_task(task_id)
    
    if not task:
        return {"error": f"Task {task_id} not found"}
    
    return {
        "task_id": task_id,
        "status": task.status.value,
        "progress": task.progress,
        "message": task.message,
        "duration": task._calculate_duration()
    }


@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """Cancel a task."""
    task = await task_store.get_task(task_id)
    
    if not task:
        return {"error": f"Task {task_id} not found"}
    
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        return {"error": f"Cannot cancel {task.status.value} task"}
    
    # Update task status
    await task_store.update_task(
        task_id,
        status=TaskStatus.CANCELLED,
        message="Task cancelled by user"
    )
    
    return {
        "task_id": task_id,
        "status": "cancelled",
        "message": "Task cancelled successfully"
    }


@app.get("/tasks/{task_id}/stream")
async def stream_task_progress(task_id: str):
    """Stream task progress updates using Server-Sent Events."""
    
    async def event_generator():
        """Generate SSE events."""
        last_progress = -1
        
        while True:
            task = await task_store.get_task(task_id)
            
            if not task:
                yield f"data: {{\"error\": \"Task {task_id} not found\"}}\n\n"
                break
            
            # Send update if progress changed
            if task.progress != last_progress:
                last_progress = task.progress
                
                data = {
                    "task_id": task_id,
                    "status": task.status.value,
                    "progress": task.progress,
                    "message": task.message
                }
                
                yield f"data: {data}\n\n"
            
            # Check if task is done
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, 
                             TaskStatus.CANCELLED]:
                yield f"data: {{\"done\": true}}\n\n"
                break
            
            # Wait before next check
            await asyncio.sleep(0.5)
    
    return MockStreamingResponse(event_generator())


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: MockWebSocket, task_id: str):
    """WebSocket endpoint for real-time task updates."""
    await websocket.accept()
    
    try:
        last_progress = -1
        
        while True:
            task = await task_store.get_task(task_id)
            
            if not task:
                await websocket.send_json({
                    "error": f"Task {task_id} not found"
                })
                break
            
            # Send update if progress changed
            if task.progress != last_progress:
                last_progress = task.progress
                
                await websocket.send_json({
                    "task_id": task_id,
                    "status": task.status.value,
                    "progress": task.progress,
                    "message": task.message,
                    "duration": task._calculate_duration()
                })
            
            # Check if task is done
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED,
                             TaskStatus.CANCELLED]:
                await websocket.send_json({
                    "task_id": task_id,
                    "done": True,
                    "final_status": task.status.value,
                    "result": task.result if task.status == TaskStatus.COMPLETED else None,
                    "error": task.error if task.status == TaskStatus.FAILED else None
                })
                break
            
            # Check for client messages
            try:
                msg = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=0.5
                )
                
                if msg.get("type") == "cancel":
                    await task_store.update_task(
                        task_id,
                        status=TaskStatus.CANCELLED,
                        message="Cancelled via WebSocket"
                    )
            
            except asyncio.TimeoutError:
                pass
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        await websocket.close()


@app.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get system metrics."""
    all_tasks = await task_store.list_tasks()
    
    # Count by status
    status_counts = {}
    for status in TaskStatus:
        status_counts[status.value] = sum(
            1 for t in all_tasks if t.status == status
        )
    
    # Calculate average duration
    completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
    avg_duration = 0
    if completed_tasks:
        durations = [t._calculate_duration() for t in completed_tasks]
        avg_duration = sum(durations) / len(durations)
    
    # Queue status
    queue_status = {}
    if task_queue:
        shared = {"queue_action": "status"}
        await task_queue.run_async(shared)
        queue_status = shared.get("queue_status", {})
    
    return {
        "total_tasks": len(all_tasks),
        "status_counts": status_counts,
        "average_duration": round(avg_duration, 2),
        "queue_status": queue_status
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "kaygraph-background-tasks"
    }


# Dashboard endpoint (in production, serve actual HTML)
@app.get("/dashboard")
async def dashboard():
    """Task dashboard."""
    return {
        "message": "Dashboard would be served here",
        "endpoints": [
            "GET /tasks/ - List all tasks",
            "POST /tasks/ - Submit new task",
            "GET /tasks/{id} - Get task details",
            "GET /tasks/{id}/result - Get task result",
            "GET /tasks/{id}/progress - Get task progress",
            "DELETE /tasks/{id} - Cancel task",
            "GET /tasks/{id}/stream - SSE progress stream",
            "WS /ws/{id} - WebSocket updates",
            "GET /metrics - System metrics",
            "GET /health - Health check"
        ]
    }


# Main entry point
if __name__ == "__main__":
    async def run_server():
        """Run the mock server."""
        logger.info("Starting KayGraph FastAPI Background Tasks server...")
        
        # Initialize app
        async with lifespan(app):
            logger.info("Server started on http://localhost:8000")
            logger.info("API documentation at http://localhost:8000/docs")
            
            # Submit a test task
            test_task = TaskSubmission(
                workflow="data_processing",
                params={"data": ["test", "data", "items"], "chunk_size": 2}
            )
            
            response = await submit_task(test_task)
            logger.info(f"Test task submitted: {response.task_id}")
            
            # Keep server running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
    
    # Run the server
    asyncio.run(run_server())