#!/usr/bin/env python3
"""
Async queue-based Human-in-the-Loop example.
Demonstrates non-blocking approval workflows for scale.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import uuid
from enum import Enum

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import AsyncGraph, AsyncNode, Node
from hitl_nodes import ApprovalStatus

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ApprovalTask:
    """Represents an approval task in the queue."""
    
    def __init__(self,
                 task_id: str,
                 task_type: str,
                 data: dict,
                 priority: TaskPriority = TaskPriority.NORMAL,
                 timeout_seconds: int = 3600,
                 requester: str = "system"):
        self.task_id = task_id
        self.task_type = task_type
        self.data = data
        self.priority = priority
        self.timeout_seconds = timeout_seconds
        self.requester = requester
        self.created_at = datetime.utcnow()
        self.status = ApprovalStatus.PENDING
        self.assigned_to: Optional[str] = None
        self.result: Optional[dict] = None
    
    def is_expired(self) -> bool:
        """Check if task has expired."""
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.timeout_seconds)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "data": self.data,
            "priority": self.priority.name,
            "timeout_seconds": self.timeout_seconds,
            "requester": self.requester,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "result": self.result
        }


class ApprovalQueue:
    """
    Async priority queue for approval tasks.
    In production, use Redis or RabbitMQ.
    """
    
    def __init__(self):
        self.pending_tasks: List[ApprovalTask] = []
        self.processing_tasks: Dict[str, ApprovalTask] = {}
        self.completed_tasks: Dict[str, ApprovalTask] = {}
        self._lock = asyncio.Lock()
        self._new_task_event = asyncio.Event()
    
    async def submit_task(self, task: ApprovalTask) -> str:
        """Submit a task to the queue."""
        async with self._lock:
            self.pending_tasks.append(task)
            # Sort by priority (higher first) and creation time
            self.pending_tasks.sort(
                key=lambda t: (-t.priority.value, t.created_at)
            )
            logger.info(f"Task {task.task_id} submitted to queue")
        
        # Signal that new task is available
        self._new_task_event.set()
        return task.task_id
    
    async def get_next_task(self, worker_id: str) -> Optional[ApprovalTask]:
        """Get the next task for a worker."""
        while True:
            async with self._lock:
                # Remove expired tasks
                self.pending_tasks = [
                    t for t in self.pending_tasks if not t.is_expired()
                ]
                
                # Get next available task
                if self.pending_tasks:
                    task = self.pending_tasks.pop(0)
                    task.assigned_to = worker_id
                    task.status = ApprovalStatus.PENDING
                    self.processing_tasks[task.task_id] = task
                    return task
            
            # Wait for new tasks
            self._new_task_event.clear()
            await self._new_task_event.wait()
    
    async def complete_task(self, task_id: str, result: dict):
        """Mark a task as completed."""
        async with self._lock:
            if task_id in self.processing_tasks:
                task = self.processing_tasks.pop(task_id)
                task.result = result
                task.status = ApprovalStatus(result["status"])
                self.completed_tasks[task_id] = task
                logger.info(f"Task {task_id} completed with status: {task.status}")
    
    async def get_task_status(self, task_id: str) -> Optional[ApprovalTask]:
        """Get the status of a task."""
        async with self._lock:
            # Check all queues
            for task_list in [self.pending_tasks, 
                            list(self.processing_tasks.values()),
                            list(self.completed_tasks.values())]:
                for task in task_list:
                    if task.task_id == task_id:
                        return task
        return None
    
    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "pending": len(self.pending_tasks),
            "processing": len(self.processing_tasks),
            "completed": len(self.completed_tasks),
            "by_priority": {
                priority.name: sum(1 for t in self.pending_tasks if t.priority == priority)
                for priority in TaskPriority
            }
        }


class AsyncQueueApprovalNode(AsyncNode):
    """
    Async node that submits tasks to approval queue.
    """
    
    def __init__(self,
                 queue: ApprovalQueue,
                 task_type: str,
                 priority: TaskPriority = TaskPriority.NORMAL,
                 timeout_seconds: int = 3600,
                 poll_interval: int = 5,
                 node_id: Optional[str] = None):
        super().__init__(node_id=node_id or f"async_approval_{task_type}")
        self.queue = queue
        self.task_type = task_type
        self.priority = priority
        self.timeout_seconds = timeout_seconds
        self.poll_interval = poll_interval
    
    async def prep_async(self, shared: Dict) -> Dict:
        """Prepare approval task data."""
        return {
            "title": shared.get("approval_title", f"{self.task_type} Approval"),
            "data": shared.get("approval_data", {}),
            "context": shared.get("approval_context", {})
        }
    
    async def exec_async(self, prep_res: Dict) -> Dict:
        """Submit task and wait for approval."""
        # Create approval task
        task = ApprovalTask(
            task_id=str(uuid.uuid4()),
            task_type=self.task_type,
            data=prep_res,
            priority=self.priority,
            timeout_seconds=self.timeout_seconds,
            requester=prep_res.get("context", {}).get("requester", "system")
        )
        
        # Submit to queue
        task_id = await self.queue.submit_task(task)
        logger.info(f"Submitted approval task: {task_id}")
        
        # Poll for completion
        start_time = datetime.utcnow()
        while True:
            # Check timeout
            if (datetime.utcnow() - start_time).total_seconds() > self.timeout_seconds:
                return {
                    "task_id": task_id,
                    "status": "timeout",
                    "message": "Approval request timed out"
                }
            
            # Check task status
            task_status = await self.queue.get_task_status(task_id)
            if task_status and task_status.status != ApprovalStatus.PENDING:
                return {
                    "task_id": task_id,
                    "status": task_status.status.value,
                    "result": task_status.result
                }
            
            # Wait before next poll
            await asyncio.sleep(self.poll_interval)
    
    async def post_async(self, shared: Dict, prep_res: Dict, exec_res: Dict) -> str:
        """Process approval result."""
        shared[f"{self.task_type}_approval_result"] = exec_res
        
        status = exec_res["status"]
        if status == "approved":
            return "approved"
        elif status == "rejected":
            return "rejected"
        elif status == "timeout":
            return "timeout"
        else:
            return "error"


class ApprovalWorker:
    """
    Worker that processes approval tasks from queue.
    Simulates human reviewers.
    """
    
    def __init__(self, worker_id: str, queue: ApprovalQueue, auto_approve_rate: float = 0.7):
        self.worker_id = worker_id
        self.queue = queue
        self.auto_approve_rate = auto_approve_rate
        self.tasks_processed = 0
    
    async def start(self):
        """Start processing tasks."""
        logger.info(f"Worker {self.worker_id} started")
        
        while True:
            try:
                # Get next task
                task = await self.queue.get_next_task(self.worker_id)
                
                # Process task
                await self.process_task(task)
                
                self.tasks_processed += 1
                
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def process_task(self, task: ApprovalTask):
        """Process an approval task."""
        logger.info(f"Worker {self.worker_id} processing task {task.task_id}")
        
        # Simulate review time based on priority
        review_time = {
            TaskPriority.CRITICAL: 2,
            TaskPriority.HIGH: 5,
            TaskPriority.NORMAL: 10,
            TaskPriority.LOW: 15
        }[task.priority]
        
        await asyncio.sleep(review_time)
        
        # Simulate decision (in production, this would be actual human input)
        import random
        approved = random.random() < self.auto_approve_rate
        
        result = {
            "status": "approved" if approved else "rejected",
            "reviewer": self.worker_id,
            "timestamp": datetime.utcnow().isoformat(),
            "comments": "Automated review for demo" if approved else "Does not meet criteria",
            "review_time_seconds": review_time
        }
        
        await self.queue.complete_task(task.task_id, result)


class BudgetRequestNode(Node):
    """Generate budget requests for approval."""
    
    def exec(self, prep_res):
        """Generate budget request."""
        import random
        
        amount = random.randint(1000, 50000)
        department = random.choice(["Engineering", "Marketing", "Sales", "Operations"])
        
        return {
            "request_id": str(uuid.uuid4())[:8],
            "department": department,
            "amount": amount,
            "purpose": f"{department} Q1 2025 initiatives",
            "breakdown": {
                "personnel": amount * 0.6,
                "equipment": amount * 0.2,
                "training": amount * 0.1,
                "misc": amount * 0.1
            }
        }
    
    def post(self, shared, prep_res, exec_res):
        """Prepare for approval."""
        shared["approval_title"] = f"Budget Request: ${exec_res['amount']:,}"
        shared["approval_data"] = exec_res
        
        # Set priority based on amount
        if exec_res["amount"] > 25000:
            shared["priority"] = TaskPriority.HIGH
        elif exec_res["amount"] > 10000:
            shared["priority"] = TaskPriority.NORMAL
        else:
            shared["priority"] = TaskPriority.LOW
        
        logger.info(f"Generated budget request for ${exec_res['amount']:,}")
        return None


class ProcessApprovedBudgetNode(Node):
    """Process approved budget requests."""
    
    def exec(self, budget_data):
        """Process the approved budget."""
        logger.info(f"Processing approved budget: ${budget_data['amount']:,} for {budget_data['department']}")
        
        # In production: update financial systems, send notifications, etc.
        return {
            "processed": True,
            "budget_code": f"BUD-{datetime.utcnow().strftime('%Y%m%d')}-{budget_data['request_id']}",
            "effective_date": (datetime.utcnow() + timedelta(days=7)).date().isoformat()
        }
    
    def prep(self, shared):
        """Get approved budget data."""
        return shared["approval_data"]
    
    def post(self, shared, prep_res, exec_res):
        """Store processing result."""
        shared["budget_processing_result"] = exec_res
        return None


async def create_budget_approval_workflow(queue: ApprovalQueue):
    """Create async budget approval workflow."""
    # Create nodes
    generator = BudgetRequestNode()
    approver = AsyncQueueApprovalNode(
        queue=queue,
        task_type="budget_approval",
        timeout_seconds=1800  # 30 minutes
    )
    processor = ProcessApprovedBudgetNode()
    
    # Build graph
    graph = AsyncGraph(start=generator)
    generator >> approver
    approver - "approved" >> processor
    
    # Handle rejections (just log for demo)
    class LogRejectionNode(AsyncNode):
        async def exec_async(self, data):
            logger.info(f"Budget request rejected: {data}")
    
    rejector = LogRejectionNode()
    approver - "rejected" >> rejector
    approver - "timeout" >> rejector
    
    return graph


async def monitor_queue(queue: ApprovalQueue):
    """Monitor and display queue statistics."""
    while True:
        stats = queue.get_queue_stats()
        
        print("\n" + "="*50)
        print(f"📊 Queue Statistics - {datetime.utcnow().strftime('%H:%M:%S')}")
        print("="*50)
        print(f"⏳ Pending: {stats['pending']}")
        print(f"🔄 Processing: {stats['processing']}")
        print(f"✅ Completed: {stats['completed']}")
        print("\nBy Priority:")
        for priority, count in stats['by_priority'].items():
            if count > 0:
                print(f"  {priority}: {count}")
        
        await asyncio.sleep(10)


async def main():
    """Run the async HITL example."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting Async HITL Queue System")
    print("="*50)
    
    # Create approval queue
    queue = ApprovalQueue()
    
    # Start workers (simulating human reviewers)
    workers = []
    for i in range(3):
        worker = ApprovalWorker(f"worker_{i+1}", queue)
        workers.append(asyncio.create_task(worker.start()))
    
    # Start queue monitor
    monitor_task = asyncio.create_task(monitor_queue(queue))
    
    # Create workflow
    workflow = await create_budget_approval_workflow(queue)
    
    # Generate multiple budget requests
    print("\n📝 Generating budget requests...")
    
    tasks = []
    for i in range(10):
        shared = {
            "request_number": i + 1,
            "requester": f"department_head_{i % 4 + 1}"
        }
        
        # Run workflow
        task = asyncio.create_task(workflow.run_async(shared))
        tasks.append(task)
        
        # Stagger submissions
        await asyncio.sleep(2)
    
    # Wait for all workflows to complete
    print("\n⏳ Waiting for all approvals to complete...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Show results
    print("\n" + "="*50)
    print("📊 Final Results")
    print("="*50)
    
    approved_count = 0
    rejected_count = 0
    timeout_count = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Request {i+1}: ❌ Error - {result}")
        else:
            # Check the shared context for results
            # This is a simplified check - in real workflow, check shared context
            print(f"Request {i+1}: ✅ Completed")
    
    # Cancel background tasks
    for worker in workers:
        worker.cancel()
    monitor_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())