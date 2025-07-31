import argparse
import logging
import random
from typing import Dict, Any, List
from graph import create_distributed_mapreduce_workflow, create_fault_tolerant_mapreduce_workflow

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_sample_data(dataset_type: str, size: int) -> List[Any]:
    """Generate sample data for MapReduce processing"""
    
    if dataset_type == "word_count":
        # Generate text data for word counting
        words = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "hello", "world", 
                "python", "programming", "distributed", "computing", "mapreduce", "framework"]
        
        data = []
        for _ in range(size):
            # Generate sentences with random words
            sentence_length = random.randint(5, 15)
            sentence = " ".join(random.choices(words, k=sentence_length))
            data.append(sentence)
        
        return data
    
    elif dataset_type == "sum_values":
        # Generate numerical data for aggregation
        categories = ["A", "B", "C", "D", "E"]
        
        data = []
        for _ in range(size):
            record = {
                "category": random.choice(categories),
                "value": random.uniform(1.0, 100.0),
                "timestamp": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            }
            data.append(record)
        
        return data
    
    else:  # generic data
        return [f"item_{i}_{random.randint(1, 1000)}" for i in range(size)]


def run_mapreduce_demo(
    dataset_type: str = "word_count",
    dataset_size: int = 1000,
    num_workers: int = 4,
    simulate_failures: bool = False,
    monitor_workers: bool = False,
    use_fault_tolerant: bool = False
):
    """Run the distributed MapReduce demo"""
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║        KayGraph Distributed MapReduce Demo               ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This demo shows:                                         ║
    ║  • Distributed work coordination across workers          ║
    ║  • Fault tolerance with worker failure recovery          ║
    ║  • Real-time metrics from distributed execution          ║
    ║  • Load balancing and work distribution                   ║
    ║  • Validation across distributed results                 ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Configuration:
    • Dataset: {dataset_type} ({dataset_size:,} items)
    • Workers: {num_workers}
    • Failure simulation: {'Yes' if simulate_failures else 'No'}
    • Worker monitoring: {'Yes' if monitor_workers else 'No'}
    • Fault tolerance: {'Enhanced' if use_fault_tolerant else 'Standard'}
    """)
    
    # Generate sample data
    logger.info(f"Generating {dataset_size} {dataset_type} items...")
    sample_data = generate_sample_data(dataset_type, dataset_size)
    
    # Initialize shared context
    shared: Dict[str, Any] = {
        "config": {
            "dataset_type": dataset_type,
            "dataset_size": dataset_size,
            "num_workers": num_workers,
            "simulate_failures": simulate_failures,
            "monitor_workers": monitor_workers
        }
    }
    
    # Create appropriate workflow
    if use_fault_tolerant:
        workflow = create_fault_tolerant_mapreduce_workflow()
        print("Using fault-tolerant MapReduce workflow...")
    else:
        workflow = create_distributed_mapreduce_workflow()
        print("Using standard distributed MapReduce workflow...")
    
    # Configure workflow parameters
    map_function, reduce_function = get_functions_for_dataset(dataset_type)
    
    workflow.set_params({
        "data": sample_data,
        "num_workers": num_workers,
        "map_function": map_function,
        "reduce_function": reduce_function,
        "simulate_failure": simulate_failures
    })
    
    try:
        logger.info("Starting distributed MapReduce execution...")
        
        # Run the workflow using context manager for resource cleanup
        with workflow:
            result = workflow.run(shared)
        
        # Display comprehensive results
        display_mapreduce_results(shared, dataset_type)
        
        if monitor_workers:
            display_worker_monitoring(shared)
        
        display_distribution_analysis(shared)
        
        logger.info("Distributed MapReduce completed successfully!")
        
    except Exception as e:
        logger.error(f"MapReduce workflow failed: {e}")
        print(f"\n❌ MapReduce failed: {e}")
        print("KayGraph's distributed error handling contained the failure!")
        
        # Show partial results
        if shared:
            print(f"\n📊 Partial results before failure:")
            display_partial_mapreduce_results(shared)


def get_functions_for_dataset(dataset_type: str) -> tuple:
    """Get appropriate map and reduce functions for dataset type"""
    
    if dataset_type == "word_count":
        return "word_count", "count_reduce"
    elif dataset_type == "sum_values":
        return "sum_values", "sum_reduce"
    else:
        return "generic_map", "generic_reduce"


def display_mapreduce_results(shared: Dict[str, Any], dataset_type: str):
    """Display comprehensive MapReduce results"""
    
    print(f"\n📊 MapReduce Execution Results:")
    print("=" * 60)
    
    # Data partitioning results
    num_partitions = shared.get("num_partitions", 0)
    print(f"📋 Data Partitioning:")
    print(f"  Partitions created: {num_partitions}")
    
    # Map phase results
    map_results = shared.get("map_results", {})
    print(f"\n🗺️ Map Phase:")
    print(f"  Tasks successful: {map_results.get('successful_tasks', 0)}/{map_results.get('total_tasks', 0)}")
    print(f"  Execution time: {map_results.get('execution_time', 0):.2f}s")
    print(f"  Unique keys generated: {map_results.get('unique_keys', 0):,}")
    
    # Shuffle phase results
    shuffle_results = shared.get("shuffle_results", {})
    print(f"\n🔀 Shuffle Phase:")
    print(f"  Keys partitioned: {shuffle_results.get('total_keys', 0):,}")
    print(f"  Reduce partitions: {shuffle_results.get('num_reducers', 0)}")
    
    # Reduce phase results
    reduce_results = shared.get("reduce_results", {})
    print(f"\n📉 Reduce Phase:")
    print(f"  Tasks successful: {reduce_results.get('successful_tasks', 0)}/{reduce_results.get('total_tasks', 0)}")
    print(f"  Execution time: {reduce_results.get('execution_time', 0):.2f}s")
    print(f"  Final results: {reduce_results.get('result_count', 0):,}")
    
    # Final aggregated results
    final_results = shared.get("final_aggregated_results", {})
    if final_results:
        summary = final_results.get("summary", {})
        results = final_results.get("results", {})
        
        print(f"\n🎯 Final Results:")
        print(f"  Total execution time: {summary.get('total_execution_time', 0):.2f}s")
        print(f"  Total results: {summary.get('result_count', 0):,}")
        print(f"  Workers used: {summary.get('total_workers_used', 0)}")
        print(f"  Tasks completed: {summary.get('total_tasks_completed', 0)}")
        
        # Show top results based on dataset type
        if results:
            print(f"\n🏆 Top Results:")
            top_items = list(results.items())[:10]  # Top 10
            
            for key, value in top_items:
                if dataset_type == "word_count":
                    print(f"  '{key}': {value} occurrences")
                elif dataset_type == "sum_values":
                    print(f"  Category '{key}': {value:.2f}")
                else:
                    print(f"  '{key}': {value}")
        
        # Performance metrics
        avg_map_time = summary.get("avg_map_task_time", 0)
        avg_reduce_time = summary.get("avg_reduce_task_time", 0)
        
        print(f"\n⚡ Performance Metrics:")
        print(f"  Avg map task time: {avg_map_time:.3f}s")
        print(f"  Avg reduce task time: {avg_reduce_time:.3f}s")
        print(f"  Parallelization efficiency: {calculate_efficiency(summary):.1%}")


def display_worker_monitoring(shared: Dict[str, Any]):
    """Display worker monitoring information"""
    
    print(f"\n👥 Worker Monitoring:")
    print("=" * 60)
    
    # Map phase worker stats
    map_results = shared.get("map_results", {})
    map_pool_stats = map_results.get("pool_stats", {})
    
    if map_pool_stats:
        print(f"📊 Map Phase Workers:")
        print(f"  Total workers: {map_pool_stats.get('total_workers', 0)}")
        print(f"  Healthy workers: {map_pool_stats.get('healthy_workers', 0)}")
        print(f"  Tasks completed: {map_pool_stats.get('total_tasks_completed', 0)}")
        print(f"  Total processing time: {map_pool_stats.get('total_processing_time', 0):.2f}s")
        
        # Individual worker details
        worker_details = map_pool_stats.get("worker_details", [])
        if worker_details:
            print(f"\n  Individual Worker Performance:")
            for worker in worker_details:
                status = "✅ Healthy" if worker.get("is_healthy", False) else "❌ Failed"
                print(f"    Worker {worker.get('worker_id', 'unknown')}: {status} "
                      f"({worker.get('tasks_completed', 0)} tasks, "
                      f"{worker.get('avg_task_time', 0):.3f}s avg)")
    
    # Reduce phase worker stats
    reduce_results = shared.get("reduce_results", {})
    reduce_pool_stats = reduce_results.get("pool_stats", {})
    
    if reduce_pool_stats:
        print(f"\n📊 Reduce Phase Workers:")
        print(f"  Total workers: {reduce_pool_stats.get('total_workers', 0)}")
        print(f"  Healthy workers: {reduce_pool_stats.get('healthy_workers', 0)}")
        print(f"  Tasks completed: {reduce_pool_stats.get('total_tasks_completed', 0)}")


def display_distribution_analysis(shared: Dict[str, Any]):
    """Display analysis of distributed execution patterns"""
    
    print(f"\n🔍 Distribution Analysis:")
    print("=" * 60)
    
    final_results = shared.get("final_aggregated_results", {})
    if not final_results:
        return
    
    summary = final_results.get("summary", {})
    map_results = shared.get("map_results", {})
    reduce_results = shared.get("reduce_results", {})
    
    # Execution efficiency
    total_time = summary.get("total_execution_time", 0)
    map_time = summary.get("map_execution_time", 0)
    reduce_time = summary.get("reduce_execution_time", 0)
    
    print(f"⚡ Execution Efficiency:")
    print(f"  Map phase: {map_time:.2f}s ({map_time/total_time*100:.1f}% of total)")
    print(f"  Reduce phase: {reduce_time:.2f}s ({reduce_time/total_time*100:.1f}% of total)")
    
    # Task distribution
    map_tasks = map_results.get("total_tasks", 0)
    reduce_tasks = reduce_results.get("total_tasks", 0)
    total_workers = summary.get("total_workers_used", 1)
    
    print(f"\n📋 Task Distribution:")
    print(f"  Map tasks per worker: {map_tasks / total_workers:.1f}")
    print(f"  Reduce tasks per worker: {reduce_tasks / total_workers:.1f}")
    
    # Success rates
    map_success_rate = map_results.get("successful_tasks", 0) / max(1, map_results.get("total_tasks", 1))
    reduce_success_rate = reduce_results.get("successful_tasks", 0) / max(1, reduce_results.get("total_tasks", 1))
    
    print(f"\n✅ Success Rates:")
    print(f"  Map phase: {map_success_rate:.1%}")
    print(f"  Reduce phase: {reduce_success_rate:.1%}")
    print(f"  Overall: {(map_success_rate + reduce_success_rate) / 2:.1%}")
    
    # KayGraph advantages
    print(f"\n🚀 KayGraph Distribution Advantages:")
    print(f"  ✅ Automatic work partitioning and load balancing")
    print(f"  ✅ Real-time worker health monitoring")
    print(f"  ✅ Fault tolerance with task redistribution")
    print(f"  ✅ Comprehensive metrics from all workers")
    print(f"  ✅ Validation across distributed results")
    print(f"  ✅ Resource management with automatic cleanup")


def calculate_efficiency(summary: Dict[str, Any]) -> float:
    """Calculate parallelization efficiency"""
    total_time = summary.get("total_execution_time", 0)
    total_workers = summary.get("total_workers_used", 1)
    total_tasks = summary.get("total_tasks_completed", 0)
    
    if total_time == 0 or total_tasks == 0:
        return 0.0
    
    # Estimate serial execution time (very rough)
    avg_task_time = (summary.get("avg_map_task_time", 0) + summary.get("avg_reduce_task_time", 0)) / 2
    estimated_serial_time = total_tasks * avg_task_time
    
    # Calculate efficiency
    theoretical_parallel_time = estimated_serial_time / total_workers
    efficiency = theoretical_parallel_time / total_time if total_time > 0 else 0
    
    return min(efficiency, 1.0)  # Cap at 100%


def display_partial_mapreduce_results(shared: Dict[str, Any]):
    """Display partial results when MapReduce fails"""
    
    stages_completed = []
    
    if "partitions" in shared:
        stages_completed.append("Data Partitioning")
    if "map_results" in shared:
        stages_completed.append("Map Phase")
    if "shuffle_results" in shared:
        stages_completed.append("Shuffle Phase")
    if "reduce_results" in shared:
        stages_completed.append("Reduce Phase")
    if "final_aggregated_results" in shared:
        stages_completed.append("Result Aggregation")
    
    print(f"  Completed stages: {', '.join(stages_completed)}")
    
    # Show worker statistics if available
    map_results = shared.get("map_results", {})
    if map_results.get("pool_stats"):
        pool_stats = map_results["pool_stats"]
        print(f"  Workers: {pool_stats.get('healthy_workers', 0)}/{pool_stats.get('total_workers', 0)} healthy")
        print(f"  Tasks completed: {pool_stats.get('total_tasks_completed', 0)}")


def main():
    """Main entry point with command line options"""
    
    parser = argparse.ArgumentParser(description="KayGraph Distributed MapReduce Demo")
    parser.add_argument(
        "--dataset-type",
        choices=["word_count", "sum_values", "generic"],
        default="word_count",
        help="Type of dataset to process"
    )
    parser.add_argument(
        "--dataset-size",
        type=int,
        default=1000,
        help="Size of dataset to generate"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of workers to use"
    )
    parser.add_argument(
        "--simulate-failures",
        action="store_true",
        help="Simulate worker failures during execution"
    )
    parser.add_argument(
        "--monitor-workers",
        action="store_true",
        help="Enable detailed worker monitoring"
    )
    parser.add_argument(
        "--use-fault-tolerant",
        action="store_true",
        help="Use fault-tolerant workflow with enhanced error handling"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the demo
    run_mapreduce_demo(
        dataset_type=args.dataset_type,
        dataset_size=args.dataset_size,
        num_workers=args.workers,
        simulate_failures=args.simulate_failures,
        monitor_workers=args.monitor_workers,
        use_fault_tolerant=args.use_fault_tolerant
    )


if __name__ == "__main__":
    main()