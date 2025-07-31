"""
Parallel batch processing nodes using KayGraph.
"""

import time
import logging
from typing import Dict, Any, List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from kaygraph import Node, BatchNode, ParallelBatchNode, MetricsNode
from utils.processing import (
    simulate_io_operation, process_text_item, process_number_item,
    calculate_optimal_batch_size, BatchProcessor, create_progress_callback
)


class LoadDataNode(Node):
    """Load data for batch processing."""
    
    def __init__(self, data_type: str = "numbers", count: int = 100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = data_type
        self.count = count
    
    def exec(self, prep_res: Any) -> List[Any]:
        """Generate or load data items."""
        if self.data_type == "numbers":
            # Generate numeric data
            items = list(range(1, self.count + 1))
            self.logger.info(f"Generated {len(items)} numbers")
            
        elif self.data_type == "text":
            # Generate text data
            items = [
                f"This is text item number {i}. " * (i % 10 + 1)
                for i in range(1, self.count + 1)
            ]
            self.logger.info(f"Generated {len(items)} text items")
            
        elif self.data_type == "mixed":
            # Generate mixed data
            items = []
            for i in range(1, self.count + 1):
                if i % 2 == 0:
                    items.append(i)
                else:
                    items.append(f"Text item {i}")
            self.logger.info(f"Generated {len(items)} mixed items")
            
        else:
            items = list(range(1, self.count + 1))
        
        return items
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: List[Any]) -> str:
        """Store loaded data."""
        shared["items"] = exec_res
        shared["total_items"] = len(exec_res)
        shared["data_type"] = self.data_type
        return "default"


class SplitBatchNode(Node):
    """Split data into optimal batches."""
    
    def __init__(self, max_workers: Optional[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_workers = max_workers
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get items and calculate batch size."""
        items = shared.get("items", [])
        batch_size = calculate_optimal_batch_size(
            len(items),
            max_workers=self.max_workers
        )
        
        return {
            "items": items,
            "batch_size": batch_size
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> List[List[Any]]:
        """Split items into batches."""
        items = prep_res["items"]
        batch_size = prep_res["batch_size"]
        
        # Create batches
        batches = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batches.append(batch)
        
        self.logger.info(f"Split {len(items)} items into {len(batches)} batches "
                        f"(size: {batch_size})")
        
        return batches
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: List[List]) -> str:
        """Store batches."""
        shared["batches"] = exec_res
        shared["batch_size"] = prep_res["batch_size"]
        shared["num_batches"] = len(exec_res)
        return "default"


class SequentialProcessNode(BatchNode, MetricsNode):
    """Process batches sequentially (for comparison)."""
    
    def __init__(self, process_type: str = "io", *args, **kwargs):
        super().__init__(collect_metrics=True, *args, **kwargs)
        self.process_type = process_type
        self.processor = BatchProcessor(self._get_process_func())
    
    def _get_process_func(self) -> Callable:
        """Get appropriate processing function."""
        if self.process_type == "io":
            return simulate_io_operation
        elif self.process_type == "text":
            return process_text_item
        elif self.process_type == "number":
            return process_number_item
        else:
            return lambda x: {"item": x, "processed": True}
    
    def prep(self, shared: Dict[str, Any]) -> List[Any]:
        """Get all items for sequential processing."""
        self.processor.start_time = time.time()
        return shared.get("items", [])
    
    def exec(self, item: Any) -> Dict[str, Any]:
        """Process single item."""
        return self.processor.process_item_with_error_handling(item)
    
    def post(self, shared: Dict[str, Any], prep_res: List, exec_res: List[Dict]) -> str:
        """Store sequential results."""
        self.processor.end_time = time.time()
        self.processor.results = exec_res
        
        metrics = self.processor.get_metrics()
        shared["sequential_results"] = exec_res
        shared["sequential_metrics"] = metrics
        
        self.logger.info(f"Sequential processing complete: {metrics}")
        return "default"


class ParallelProcessNode(ParallelBatchNode, MetricsNode):
    """Process batches in parallel."""
    
    def __init__(self, process_type: str = "io", max_workers: Optional[int] = None, 
                 *args, **kwargs):
        super().__init__(max_workers=max_workers, collect_metrics=True, *args, **kwargs)
        self.process_type = process_type
        self.processor = BatchProcessor(self._get_process_func())
    
    def _get_process_func(self) -> Callable:
        """Get appropriate processing function."""
        if self.process_type == "io":
            return simulate_io_operation
        elif self.process_type == "text":
            return process_text_item
        elif self.process_type == "number":
            return process_number_item
        else:
            return lambda x: {"item": x, "processed": True}
    
    def prep(self, shared: Dict[str, Any]) -> List[Any]:
        """Get all items for parallel processing."""
        self.processor.start_time = time.time()
        
        # Create progress callback
        total_items = shared.get("total_items", 0)
        self.progress_callback = create_progress_callback(total_items)
        
        return shared.get("items", [])
    
    def exec(self, item: Any) -> Dict[str, Any]:
        """Process single item."""
        result = self.processor.process_item_with_error_handling(item)
        
        # Update progress (in real implementation, batch this)
        if hasattr(self, '_processed_count'):
            self._processed_count += 1
            if self._processed_count % 10 == 0:
                self.progress_callback(10)
        else:
            self._processed_count = 1
        
        return result
    
    def post(self, shared: Dict[str, Any], prep_res: List, exec_res: List[Dict]) -> str:
        """Store parallel results."""
        self.processor.end_time = time.time()
        self.processor.results = exec_res
        
        metrics = self.processor.get_metrics()
        shared["parallel_results"] = exec_res
        shared["parallel_metrics"] = metrics
        
        self.logger.info(f"Parallel processing complete: {metrics}")
        return "default"


class AggregateNode(Node):
    """Aggregate and analyze results."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all results."""
        return {
            "sequential_results": shared.get("sequential_results", []),
            "parallel_results": shared.get("parallel_results", []),
            "sequential_metrics": shared.get("sequential_metrics", {}),
            "parallel_metrics": shared.get("parallel_metrics", {}),
            "data_type": shared.get("data_type", "unknown")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and compare results."""
        seq_metrics = prep_res["sequential_metrics"]
        par_metrics = prep_res["parallel_metrics"]
        
        # Calculate speedup
        speedup = 1.0
        if seq_metrics.get("total_duration") and par_metrics.get("total_duration"):
            speedup = seq_metrics["total_duration"] / par_metrics["total_duration"]
        
        # Verify results match (for correctness)
        results_match = self._verify_results(
            prep_res["sequential_results"],
            prep_res["parallel_results"]
        )
        
        analysis = {
            "total_items": len(prep_res["sequential_results"]),
            "data_type": prep_res["data_type"],
            "sequential_time": seq_metrics.get("total_duration", 0),
            "parallel_time": par_metrics.get("total_duration", 0),
            "speedup": speedup,
            "efficiency": speedup / (self.params.get("max_workers", 4)),
            "results_match": results_match,
            "sequential_throughput": seq_metrics.get("throughput", 0),
            "parallel_throughput": par_metrics.get("throughput", 0),
            "errors": {
                "sequential": seq_metrics.get("failed", 0),
                "parallel": par_metrics.get("failed", 0)
            }
        }
        
        return analysis
    
    def _verify_results(self, seq_results: List[Dict], par_results: List[Dict]) -> bool:
        """Verify that results match between sequential and parallel."""
        if len(seq_results) != len(par_results):
            return False
        
        # Sort results by item for comparison
        seq_sorted = sorted(seq_results, key=lambda x: str(x.get("item", "")))
        par_sorted = sorted(par_results, key=lambda x: str(x.get("item", "")))
        
        # Compare relevant fields (excluding timing)
        for s, p in zip(seq_sorted, par_sorted):
            if s.get("item") != p.get("item"):
                return False
            if s.get("status") != p.get("status"):
                return False
        
        return True
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> str:
        """Store analysis results."""
        shared["analysis"] = exec_res
        self.logger.info(f"Analysis complete: {exec_res['speedup']:.2f}x speedup")
        return "default"


class ReportNode(Node):
    """Generate performance report."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare report data."""
        return {
            "analysis": shared.get("analysis", {}),
            "batch_size": shared.get("batch_size", 0),
            "num_batches": shared.get("num_batches", 0)
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Generate report."""
        analysis = prep_res["analysis"]
        
        report = f"""
Parallel Batch Processing Performance Report
===========================================

Data Summary:
- Total items: {analysis.get('total_items', 0)}
- Data type: {analysis.get('data_type', 'unknown')}
- Batch size: {prep_res['batch_size']}
- Number of batches: {prep_res['num_batches']}

Performance Results:
- Sequential processing time: {analysis.get('sequential_time', 0):.2f}s
- Parallel processing time: {analysis.get('parallel_time', 0):.2f}s
- Speedup: {analysis.get('speedup', 1.0):.2f}x
- Efficiency: {analysis.get('efficiency', 0):.1%}

Throughput:
- Sequential: {analysis.get('sequential_throughput', 0):.1f} items/sec
- Parallel: {analysis.get('parallel_throughput', 0):.1f} items/sec

Correctness:
- Results match: {'✓' if analysis.get('results_match') else '✗'}
- Sequential errors: {analysis.get('errors', {}).get('sequential', 0)}
- Parallel errors: {analysis.get('errors', {}).get('parallel', 0)}

Conclusion:
"""
        
        if analysis.get('speedup', 1.0) > 1.5:
            report += f"Parallel processing provided significant speedup ({analysis['speedup']:.1f}x faster)!"
        elif analysis.get('speedup', 1.0) > 1.1:
            report += f"Parallel processing provided moderate speedup ({analysis['speedup']:.1f}x faster)."
        else:
            report += "Parallel processing provided minimal benefit for this workload."
        
        return report
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> str:
        """Display report."""
        print(exec_res)
        shared["report"] = exec_res
        return "default"