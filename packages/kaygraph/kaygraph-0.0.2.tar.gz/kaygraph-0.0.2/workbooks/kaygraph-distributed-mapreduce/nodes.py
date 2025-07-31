import asyncio
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from kaygraph import ValidatedNode, MetricsNode, Node
import logging

logging.basicConfig(level=logging.INFO)


class Worker:
    """Simulated distributed worker"""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.is_healthy = True
        self.tasks_completed = 0
        self.total_processing_time = 0
        self.last_heartbeat = time.time()
        self.logger = logging.getLogger(f"Worker_{worker_id}")
    
    def process_map_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a map task"""
        start_time = time.time()
        
        try:
            # Simulate worker failure
            if random.random() < 0.02:  # 2% failure rate
                raise RuntimeError(f"Worker {self.worker_id} simulated failure")
            
            # Simulate map processing
            partition_data = task_data.get("data", [])
            map_function = task_data.get("map_function", "word_count")
            
            if map_function == "word_count":
                result = self._word_count_map(partition_data)
            elif map_function == "sum_values":
                result = self._sum_values_map(partition_data)
            else:
                result = self._generic_map(partition_data)
            
            processing_time = time.time() - start_time
            self.tasks_completed += 1
            self.total_processing_time += processing_time
            self.last_heartbeat = time.time()
            
            return {
                "worker_id": self.worker_id,
                "task_id": task_data.get("task_id", "unknown"),
                "result": result,
                "processing_time": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            self.is_healthy = False
            self.logger.error(f"Map task failed: {e}")
            return {
                "worker_id": self.worker_id,
                "task_id": task_data.get("task_id", "unknown"),
                "error": str(e),
                "status": "failed"
            }
    
    def process_reduce_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a reduce task"""
        start_time = time.time()
        
        try:
            # Simulate worker failure
            if random.random() < 0.01:  # 1% failure rate for reduce
                raise RuntimeError(f"Worker {self.worker_id} reduce failure")
            
            # Simulate reduce processing
            intermediate_data = task_data.get("data", {})
            reduce_function = task_data.get("reduce_function", "sum_reduce")
            
            if reduce_function == "sum_reduce":
                result = self._sum_reduce(intermediate_data)
            elif reduce_function == "count_reduce":
                result = self._count_reduce(intermediate_data)
            else:
                result = self._generic_reduce(intermediate_data)
            
            processing_time = time.time() - start_time
            self.tasks_completed += 1
            self.total_processing_time += processing_time
            self.last_heartbeat = time.time()
            
            return {
                "worker_id": self.worker_id,
                "task_id": task_data.get("task_id", "unknown"),
                "result": result,
                "processing_time": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            self.is_healthy = False
            self.logger.error(f"Reduce task failed: {e}")
            return {
                "worker_id": self.worker_id,
                "task_id": task_data.get("task_id", "unknown"),
                "error": str(e),
                "status": "failed"
            }
    
    def _word_count_map(self, data: List[str]) -> List[Tuple[str, int]]:
        """Map function for word counting"""
        word_counts = defaultdict(int)
        for line in data:
            words = line.lower().split()
            for word in words:
                # Clean word
                word = ''.join(c for c in word if c.isalnum())
                if word:
                    word_counts[word] += 1
        
        return list(word_counts.items())
    
    def _sum_values_map(self, data: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """Map function for summing values by category"""
        results = []
        for record in data:
            category = record.get("category", "unknown")
            value = record.get("value", 0)
            results.append((category, value))
        return results
    
    def _generic_map(self, data: List[Any]) -> List[Tuple[str, Any]]:
        """Generic map function"""
        return [(f"key_{i}", item) for i, item in enumerate(data)]
    
    def _sum_reduce(self, data: Dict[str, List[float]]) -> Dict[str, float]:
        """Reduce function for summing values"""
        return {key: sum(values) for key, values in data.items()}
    
    def _count_reduce(self, data: Dict[str, List[int]]) -> Dict[str, int]:
        """Reduce function for counting occurrences"""
        return {key: sum(values) for key, values in data.items()}
    
    def _generic_reduce(self, data: Dict[str, List[Any]]) -> Dict[str, int]:
        """Generic reduce function"""
        return {key: len(values) for key, values in data.items()}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        return {
            "worker_id": self.worker_id,
            "is_healthy": self.is_healthy,
            "tasks_completed": self.tasks_completed,
            "total_processing_time": self.total_processing_time,
            "avg_task_time": self.total_processing_time / self.tasks_completed if self.tasks_completed > 0 else 0,
            "last_heartbeat": self.last_heartbeat
        }


class WorkerPool:
    """Manages a pool of distributed workers"""
    
    def __init__(self, num_workers: int = 4):
        self.workers = [Worker(i) for i in range(num_workers)]
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.logger = logging.getLogger("WorkerPool")
    
    def get_healthy_workers(self) -> List[Worker]:
        """Get list of healthy workers"""
        return [w for w in self.workers if w.is_healthy]
    
    def execute_map_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute map tasks across workers"""
        healthy_workers = self.get_healthy_workers()
        
        if not healthy_workers:
            raise RuntimeError("No healthy workers available")
        
        # Submit tasks to workers
        future_to_task = {}
        for i, task in enumerate(tasks):
            worker = healthy_workers[i % len(healthy_workers)]
            future = self.executor.submit(worker.process_map_task, task)
            future_to_task[future] = task
        
        # Collect results
        results = []
        failed_tasks = []
        
        for future in as_completed(future_to_task):
            try:
                result = future.result(timeout=30)  # 30 second timeout
                if result["status"] == "success":
                    results.append(result)
                else:
                    failed_tasks.append(future_to_task[future])
            except Exception as e:
                self.logger.error(f"Task execution failed: {e}")
                failed_tasks.append(future_to_task[future])
        
        # Retry failed tasks on different workers
        if failed_tasks:
            self.logger.info(f"Retrying {len(failed_tasks)} failed tasks")
            for task in failed_tasks:
                healthy_workers = self.get_healthy_workers()
                if healthy_workers:
                    worker = random.choice(healthy_workers)
                    try:
                        result = worker.process_map_task(task)
                        if result["status"] == "success":
                            results.append(result)
                    except Exception as e:
                        self.logger.error(f"Retry also failed: {e}")
        
        return results
    
    def execute_reduce_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute reduce tasks across workers"""
        healthy_workers = self.get_healthy_workers()
        
        if not healthy_workers:
            raise RuntimeError("No healthy workers available")
        
        # Submit tasks to workers
        future_to_task = {}
        for i, task in enumerate(tasks):
            worker = healthy_workers[i % len(healthy_workers)]
            future = self.executor.submit(worker.process_reduce_task, task)
            future_to_task[future] = task
        
        # Collect results
        results = []
        for future in as_completed(future_to_task):
            try:
                result = future.result(timeout=30)
                if result["status"] == "success":
                    results.append(result)
            except Exception as e:
                self.logger.error(f"Reduce task failed: {e}")
        
        return results
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get statistics for the entire worker pool"""
        worker_stats = [w.get_stats() for w in self.workers]
        healthy_count = len(self.get_healthy_workers())
        total_tasks = sum(w.tasks_completed for w in self.workers)
        total_time = sum(w.total_processing_time for w in self.workers)
        
        return {
            "total_workers": len(self.workers),
            "healthy_workers": healthy_count,
            "total_tasks_completed": total_tasks,
            "total_processing_time": total_time,
            "worker_details": worker_stats
        }
    
    def cleanup(self):
        """Cleanup worker pool"""
        self.executor.shutdown(wait=True)


class DataPartitionerNode(ValidatedNode):
    """Partitions input data for distributed processing"""
    
    def __init__(self):
        super().__init__(node_id="data_partitioner")
    
    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data for partitioning"""
        if not input_data:
            raise ValueError("No input data provided")
        
        data = input_data.get("data", [])
        if not data:
            raise ValueError("Empty data provided")
        
        if len(data) < 1:
            raise ValueError("Insufficient data for processing")
        
        return input_data
    
    def validate_output(self, partitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate partitioned data"""
        if not partitions:
            raise ValueError("No partitions created")
        
        # Verify all partitions have data
        for i, partition in enumerate(partitions):
            if not partition.get("data"):
                raise ValueError(f"Partition {i} is empty")
        
        # Verify total data is preserved
        total_items = sum(len(p["data"]) for p in partitions)
        if total_items == 0:
            raise ValueError("All partitions are empty")
        
        return partitions
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return self.params.copy()
    
    def exec(self, input_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Partition data for distributed processing"""
        data = input_config.get("data", [])
        num_workers = input_config.get("num_workers", 4)
        map_function = input_config.get("map_function", "word_count")
        
        # Calculate optimal partition size
        total_items = len(data)
        items_per_partition = max(1, total_items // num_workers)
        
        partitions = []
        for i in range(num_workers):
            start_idx = i * items_per_partition
            
            if i == num_workers - 1:
                # Last partition gets remaining items
                end_idx = total_items
            else:
                end_idx = start_idx + items_per_partition
            
            if start_idx < total_items:
                partition_data = data[start_idx:end_idx]
                partitions.append({
                    "task_id": f"map_task_{i}",
                    "partition_id": i,
                    "data": partition_data,
                    "map_function": map_function,
                    "start_idx": start_idx,
                    "end_idx": end_idx
                })
        
        return partitions
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["partitions"] = exec_res
        shared["num_partitions"] = len(exec_res)
        
        total_items = sum(len(p["data"]) for p in exec_res)
        self.logger.info(f"Created {len(exec_res)} partitions with {total_items} total items")
        
        return "partitioned"


class MapCoordinatorNode(MetricsNode):
    """Coordinates map tasks across distributed workers"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, node_id="map_coordinator")
        self.worker_pool = None
    
    def setup_resources(self):
        """Setup worker pool"""
        num_workers = self.params.get("num_workers", 4)
        self.worker_pool = WorkerPool(num_workers)
        self.logger.info(f"Initialized worker pool with {num_workers} workers")
    
    def cleanup_resources(self):
        """Cleanup worker pool"""
        if self.worker_pool:
            self.worker_pool.cleanup()
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("partitions", [])
    
    def exec(self, partitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute map tasks across workers"""
        if not self.worker_pool:
            raise RuntimeError("Worker pool not initialized")
        
        start_time = time.time()
        
        # Execute map tasks
        map_results = self.worker_pool.execute_map_tasks(partitions)
        
        # Collect intermediate results
        intermediate_data = defaultdict(list)
        successful_tasks = 0
        
        for result in map_results:
            if result["status"] == "success":
                successful_tasks += 1
                # Group results by key for shuffle phase
                for key, value in result["result"]:
                    intermediate_data[key].append(value)
        
        execution_time = time.time() - start_time
        
        # Get worker pool statistics
        pool_stats = self.worker_pool.get_pool_stats()
        
        return {
            "intermediate_data": dict(intermediate_data),
            "successful_tasks": successful_tasks,
            "total_tasks": len(partitions),
            "execution_time": execution_time,
            "unique_keys": len(intermediate_data),
            "pool_stats": pool_stats
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["map_results"] = exec_res
        
        successful = exec_res["successful_tasks"]
        total = exec_res["total_tasks"]
        self.logger.info(f"Map phase completed: {successful}/{total} tasks successful")
        
        return "mapped"


class ShuffleNode(Node):
    """Shuffles and sorts intermediate results for reduce phase"""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return shared.get("map_results", {})
    
    def exec(self, map_results: Dict[str, Any]) -> Dict[str, Any]:
        """Shuffle intermediate data for reduce phase"""
        intermediate_data = map_results.get("intermediate_data", {})
        num_reducers = self.params.get("num_reducers", 4)
        
        # Sort keys for consistent partitioning
        sorted_keys = sorted(intermediate_data.keys())
        
        # Partition keys across reducers
        keys_per_reducer = max(1, len(sorted_keys) // num_reducers)
        
        reduce_partitions = []
        for i in range(num_reducers):
            start_idx = i * keys_per_reducer
            
            if i == num_reducers - 1:
                # Last reducer gets remaining keys
                end_idx = len(sorted_keys)
            else:
                end_idx = start_idx + keys_per_reducer
            
            if start_idx < len(sorted_keys):
                partition_keys = sorted_keys[start_idx:end_idx]
                partition_data = {key: intermediate_data[key] for key in partition_keys}
                
                reduce_partitions.append({
                    "task_id": f"reduce_task_{i}",
                    "partition_id": i,
                    "data": partition_data,
                    "reduce_function": self.params.get("reduce_function", "sum_reduce"),
                    "key_count": len(partition_keys)
                })
        
        return {
            "reduce_partitions": reduce_partitions,
            "total_keys": len(sorted_keys),
            "num_reducers": len(reduce_partitions)
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["shuffle_results"] = exec_res
        
        num_partitions = exec_res["num_reducers"]
        total_keys = exec_res["total_keys"]
        self.logger.info(f"Shuffle phase completed: {total_keys} keys partitioned into {num_partitions} reducers")
        
        return "shuffled"


class ReduceCoordinatorNode(MetricsNode):
    """Coordinates reduce tasks across distributed workers"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, node_id="reduce_coordinator")
        self.worker_pool = None
    
    def setup_resources(self):
        """Setup worker pool (reuse from map phase if available)"""
        num_workers = self.params.get("num_workers", 4)
        self.worker_pool = WorkerPool(num_workers)
    
    def cleanup_resources(self):
        """Cleanup worker pool"""
        if self.worker_pool:
            self.worker_pool.cleanup()
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        shuffle_results = shared.get("shuffle_results", {})
        return shuffle_results.get("reduce_partitions", [])
    
    def exec(self, reduce_partitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute reduce tasks across workers"""
        if not self.worker_pool:
            raise RuntimeError("Worker pool not initialized")
        
        start_time = time.time()
        
        # Execute reduce tasks
        reduce_results = self.worker_pool.execute_reduce_tasks(reduce_partitions)
        
        # Combine results from all reducers
        final_results = {}
        successful_tasks = 0
        
        for result in reduce_results:
            if result["status"] == "success":
                successful_tasks += 1
                final_results.update(result["result"])
        
        execution_time = time.time() - start_time
        
        # Get worker pool statistics
        pool_stats = self.worker_pool.get_pool_stats()
        
        return {
            "final_results": final_results,
            "successful_tasks": successful_tasks,
            "total_tasks": len(reduce_partitions),
            "execution_time": execution_time,
            "result_count": len(final_results),
            "pool_stats": pool_stats
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["reduce_results"] = exec_res
        
        successful = exec_res["successful_tasks"]
        total = exec_res["total_tasks"]
        result_count = exec_res["result_count"]
        
        self.logger.info(f"Reduce phase completed: {successful}/{total} tasks successful, {result_count} final results")
        
        return "reduced"


class ResultAggregatorNode(ValidatedNode):
    """Aggregates and validates final MapReduce results"""
    
    def __init__(self):
        super().__init__(node_id="result_aggregator")
    
    def validate_input(self, reduce_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate reduce results"""
        if not reduce_results:
            raise ValueError("No reduce results provided")
        
        if reduce_results.get("successful_tasks", 0) == 0:
            raise ValueError("No successful reduce tasks")
        
        final_results = reduce_results.get("final_results", {})
        if not final_results:
            raise ValueError("No final results produced")
        
        return reduce_results
    
    def validate_output(self, aggregated_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate aggregated results"""
        if not aggregated_results.get("results"):
            raise ValueError("No aggregated results")
        
        summary = aggregated_results.get("summary", {})
        if summary.get("total_execution_time", 0) <= 0:
            raise ValueError("Invalid execution time")
        
        return aggregated_results
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "map_results": shared.get("map_results", {}),
            "reduce_results": shared.get("reduce_results", {}),
            "num_partitions": shared.get("num_partitions", 0)
        }
    
    def exec(self, aggregation_input: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate final results with comprehensive metrics"""
        map_results = aggregation_input.get("map_results", {})
        reduce_results = aggregation_input.get("reduce_results", {})
        
        # Calculate total execution time
        map_time = map_results.get("execution_time", 0)
        reduce_time = reduce_results.get("execution_time", 0)
        total_time = map_time + reduce_time
        
        # Get final results
        final_results = reduce_results.get("final_results", {})
        
        # Calculate performance metrics
        map_pool_stats = map_results.get("pool_stats", {})
        reduce_pool_stats = reduce_results.get("pool_stats", {})
        
        # Sort results by value for better presentation
        if final_results:
            sorted_results = dict(sorted(final_results.items(), key=lambda x: x[1], reverse=True))
        else:
            sorted_results = {}
        
        # Create comprehensive summary
        summary = {
            "total_execution_time": total_time,
            "map_execution_time": map_time,
            "reduce_execution_time": reduce_time,
            "map_tasks_successful": map_results.get("successful_tasks", 0),
            "reduce_tasks_successful": reduce_results.get("successful_tasks", 0),
            "total_workers_used": max(
                map_pool_stats.get("total_workers", 0),
                reduce_pool_stats.get("total_workers", 0)
            ),
            "total_tasks_completed": (
                map_pool_stats.get("total_tasks_completed", 0) +
                reduce_pool_stats.get("total_tasks_completed", 0)
            ),
            "result_count": len(final_results),
            "partitions_processed": aggregation_input.get("num_partitions", 0),
            "avg_map_task_time": map_time / map_results.get("successful_tasks", 1),
            "avg_reduce_task_time": reduce_time / reduce_results.get("successful_tasks", 1)
        }
        
        return {
            "results": sorted_results,
            "summary": summary,
            "map_metrics": map_results,
            "reduce_metrics": reduce_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["final_aggregated_results"] = exec_res
        
        summary = exec_res["summary"]
        result_count = summary["result_count"]
        total_time = summary["total_execution_time"]
        
        self.logger.info(f"MapReduce completed: {result_count} results in {total_time:.2f}s")
        
        return None  # End of workflow