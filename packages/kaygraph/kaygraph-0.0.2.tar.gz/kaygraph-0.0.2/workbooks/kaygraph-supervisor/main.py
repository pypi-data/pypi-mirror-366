"""
Supervisor pattern example using KayGraph.

Demonstrates a supervisor that manages unreliable worker agents,
with retry logic and result validation.
"""

import random
import logging
from typing import Dict, Any, List, Optional
from kaygraph import Node, Graph, MetricsNode
from utils.tasks import generate_research_task, validate_research_result

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class SupervisorNode(MetricsNode):
    """Supervisor that assigns and monitors tasks."""
    
    def __init__(self, max_attempts: int = 3, *args, **kwargs):
        super().__init__(collect_metrics=True, *args, **kwargs)
        self.max_attempts = max_attempts
    
    def prep(self, shared):
        """Prepare supervision context."""
        return {
            "topic": shared.get("topic", ""),
            "workers": shared.get("workers", ["worker1", "worker2", "worker3"]),
            "attempt": shared.get("current_attempt", 0),
            "previous_results": shared.get("task_results", {})
        }
    
    def exec(self, context):
        """Determine supervision action."""
        topic = context["topic"]
        attempt = context["attempt"]
        previous_results = context["previous_results"]
        
        # Check if we have successful results
        successful_results = [
            r for r in previous_results.values() 
            if r.get("status") == "success"
        ]
        
        if successful_results:
            # We have at least one successful result
            return {
                "action": "complete",
                "final_result": self._consolidate_results(successful_results)
            }
        
        if attempt >= self.max_attempts:
            # Max attempts reached
            return {
                "action": "failed",
                "reason": "Max attempts reached without successful results"
            }
        
        # Assign new task
        task = generate_research_task(topic, attempt)
        
        # Select worker (round-robin or based on performance)
        worker_id = self._select_worker(context["workers"], previous_results)
        
        return {
            "action": "assign",
            "task": task,
            "worker": worker_id,
            "attempt": attempt + 1
        }
    
    def post(self, shared, prep_res, exec_res):
        """Update shared state based on supervision decision."""
        action = exec_res["action"]
        
        if action == "assign":
            shared["current_task"] = exec_res["task"]
            shared["assigned_worker"] = exec_res["worker"]
            shared["current_attempt"] = exec_res["attempt"]
            self.logger.info(f"Assigned task to {exec_res['worker']} (attempt {exec_res['attempt']})")
            return "assign"
        
        elif action == "complete":
            shared["final_result"] = exec_res["final_result"]
            shared["supervision_complete"] = True
            self.logger.info("Supervision complete - successful results obtained")
            return "complete"
        
        else:  # failed
            shared["supervision_failed"] = True
            shared["failure_reason"] = exec_res["reason"]
            self.logger.warning(f"Supervision failed: {exec_res['reason']}")
            return "failed"
    
    def _select_worker(self, workers: List[str], previous_results: Dict[str, Any]) -> str:
        """Select best worker based on history."""
        # Calculate worker performance
        worker_stats = {}
        for worker in workers:
            worker_stats[worker] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0
            }
        
        for worker_id, result in previous_results.items():
            if worker_id in worker_stats:
                worker_stats[worker_id]["attempts"] += 1
                if result.get("status") == "success":
                    worker_stats[worker_id]["successes"] += 1
                else:
                    worker_stats[worker_id]["failures"] += 1
        
        # Select worker with best success rate (or least attempts)
        best_worker = min(workers, key=lambda w: (
            -worker_stats[w]["successes"],  # Prefer more successes
            worker_stats[w]["attempts"]      # Then fewer attempts
        ))
        
        return best_worker
    
    def _consolidate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate multiple successful results."""
        # For now, just return the first one
        # Could implement voting, merging, or quality scoring
        return results[0]


class WorkerNode(Node):
    """Worker agent that executes research tasks."""
    
    def __init__(self, reliability: float = 0.7, *args, **kwargs):
        """
        Initialize worker with configurable reliability.
        
        Args:
            reliability: Probability of successful task completion (0-1)
        """
        super().__init__(*args, **kwargs)
        self.reliability = reliability
    
    def prep(self, shared):
        """Check if this worker is assigned."""
        assigned_worker = shared.get("assigned_worker", "")
        if assigned_worker == self.node_id:
            return shared.get("current_task", {})
        return None
    
    def exec(self, task):
        """Execute the research task."""
        if task is None:
            return None
        
        self.logger.info(f"{self.node_id} executing task: {task.get('description', '')}")
        
        # Simulate unreliable execution
        if random.random() < self.reliability:
            # Success
            result = {
                "status": "success",
                "worker": self.node_id,
                "task_id": task.get("id"),
                "findings": f"Research findings for: {task.get('topic', '')}",
                "confidence": random.uniform(0.7, 0.95),
                "data": {
                    "facts": [
                        f"Fact 1 about {task.get('topic', '')}",
                        f"Fact 2 about {task.get('topic', '')}",
                        f"Important insight about {task.get('topic', '')}"
                    ],
                    "sources": ["source1.com", "source2.org"],
                    "timestamp": time.time()
                }
            }
        else:
            # Failure
            failure_reasons = [
                "Network timeout",
                "Invalid data format",
                "Insufficient information",
                "API rate limit exceeded"
            ]
            result = {
                "status": "failed",
                "worker": self.node_id,
                "task_id": task.get("id"),
                "error": random.choice(failure_reasons)
            }
        
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Report results back to supervisor."""
        if exec_res is None:
            return "not_assigned"
        
        # Store result
        if "task_results" not in shared:
            shared["task_results"] = {}
        
        shared["task_results"][self.node_id] = exec_res
        
        if exec_res["status"] == "success":
            self.logger.info(f"{self.node_id} completed task successfully")
        else:
            self.logger.warning(f"{self.node_id} failed: {exec_res.get('error', 'Unknown error')}")
        
        return "reported"


class ValidationNode(Node):
    """Validate research results before finalization."""
    
    def prep(self, shared):
        """Get results to validate."""
        return shared.get("task_results", {})
    
    def exec(self, results):
        """Validate all results."""
        validated_results = {}
        
        for worker_id, result in results.items():
            if result.get("status") == "success":
                # Validate the result
                is_valid, issues = validate_research_result(result)
                
                validated_results[worker_id] = {
                    "original": result,
                    "valid": is_valid,
                    "validation_issues": issues
                }
        
        return validated_results
    
    def post(self, shared, prep_res, exec_res):
        """Store validation results."""
        shared["validated_results"] = exec_res
        
        # Count valid results
        valid_count = sum(1 for r in exec_res.values() if r["valid"])
        self.logger.info(f"Validation complete: {valid_count} valid results out of {len(exec_res)}")
        
        return "default"


class ReportNode(Node):
    """Generate final supervision report."""
    
    def prep(self, shared):
        """Gather all supervision data."""
        return {
            "topic": shared.get("topic", ""),
            "final_result": shared.get("final_result", {}),
            "task_results": shared.get("task_results", {}),
            "validated_results": shared.get("validated_results", {}),
            "attempts": shared.get("current_attempt", 0),
            "success": shared.get("supervision_complete", False)
        }
    
    def exec(self, data):
        """Generate supervision report."""
        report = f"""
Supervision Report
==================

Topic: {data['topic']}
Status: {'SUCCESS' if data['success'] else 'FAILED'}
Total Attempts: {data['attempts']}

Worker Performance:
"""
        
        # Analyze worker performance
        worker_stats = {}
        for worker_id, result in data['task_results'].items():
            status = result.get('status', 'unknown')
            if worker_id not in worker_stats:
                worker_stats[worker_id] = {"success": 0, "failed": 0}
            worker_stats[worker_id][status] = worker_stats[worker_id].get(status, 0) + 1
        
        for worker, stats in worker_stats.items():
            total = stats.get('success', 0) + stats.get('failed', 0)
            success_rate = stats.get('success', 0) / total if total > 0 else 0
            report += f"  - {worker}: {stats.get('success', 0)}/{total} success ({success_rate:.1%})\n"
        
        # Add final result if successful
        if data['success'] and data['final_result']:
            report += f"\nFinal Result:\n"
            report += f"  Worker: {data['final_result'].get('worker', 'Unknown')}\n"
            report += f"  Confidence: {data['final_result'].get('confidence', 0):.2f}\n"
            
            if 'data' in data['final_result']:
                report += f"  Findings:\n"
                for fact in data['final_result']['data'].get('facts', []):
                    report += f"    - {fact}\n"
        
        return report
    
    def post(self, shared, prep_res, exec_res):
        """Display and store report."""
        print(exec_res)
        shared["supervision_report"] = exec_res
        return None


def create_supervisor_graph(num_workers: int = 3, worker_reliability: float = 0.7):
    """Create a supervisor graph with multiple workers."""
    # Create supervisor
    supervisor = SupervisorNode(max_attempts=5, node_id="supervisor")
    
    # Create workers with varying reliability
    workers = []
    for i in range(num_workers):
        # Vary reliability slightly
        reliability = worker_reliability + random.uniform(-0.1, 0.1)
        reliability = max(0.3, min(0.9, reliability))  # Clamp between 0.3 and 0.9
        
        worker = WorkerNode(
            reliability=reliability,
            node_id=f"worker{i+1}"
        )
        workers.append(worker)
    
    # Create validation and report nodes
    validation = ValidationNode(node_id="validation")
    report = ReportNode(node_id="report")
    
    # Connect supervisor to workers
    for worker in workers:
        supervisor >> ("assign", worker)
        worker >> ("reported", supervisor)  # Back to supervisor
    
    # Connect completion paths
    supervisor >> ("complete", validation) >> report
    supervisor >> ("failed", report)
    
    # Create graph
    graph = Graph(start=supervisor)
    
    # Store worker list in graph params
    graph.set_params({"workers": [w.node_id for w in workers]})
    
    return graph


def main():
    """Run the supervisor example."""
    print("KayGraph Supervisor Pattern")
    print("=" * 40)
    
    topics = [
        "Quantum Computing Applications",
        "Climate Change Solutions",
        "Artificial Intelligence Ethics"
    ]
    
    for topic in topics:
        print(f"\n\nSupervising research on: {topic}")
        print("-" * 60)
        
        # Create supervisor graph
        graph = create_supervisor_graph(
            num_workers=3,
            worker_reliability=0.6  # 60% success rate
        )
        
        # Initialize shared state
        shared = {
            "topic": topic,
            "workers": ["worker1", "worker2", "worker3"]
        }
        
        try:
            # Run supervision
            graph.run(shared)
            
            # Show metrics
            if hasattr(graph.start_node, 'get_stats'):
                stats = graph.start_node.get_stats()
                print(f"\nSupervisor Metrics:")
                print(f"  - Total executions: {stats.get('total_executions', 0)}")
                print(f"  - Success rate: {stats.get('success_rate', 0):.1%}")
            
        except Exception as e:
            print(f"Supervision error: {e}")


if __name__ == "__main__":
    import time
    main()