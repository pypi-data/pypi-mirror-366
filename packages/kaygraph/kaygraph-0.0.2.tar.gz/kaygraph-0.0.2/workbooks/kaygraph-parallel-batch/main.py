"""
Parallel batch processing example using KayGraph.

This example demonstrates:
- Parallel vs sequential processing comparison
- Automatic batch sizing
- Performance metrics and speedup calculation
- Different processing workloads (I/O-bound, CPU-bound)
"""

import sys
import time
import logging
from graphs import create_comparison_graph, create_parallel_only_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def run_comparison(data_type: str = "numbers", count: int = 100, 
                   process_type: str = "io", max_workers: int = None):
    """Run sequential vs parallel comparison."""
    print(f"\n🔄 Parallel Batch Processing Comparison")
    print(f"📊 Processing {count} {data_type} items with {process_type} operations")
    print("=" * 60)
    
    # Create comparison graph
    graph = create_comparison_graph(
        data_type=data_type,
        count=count,
        process_type=process_type,
        max_workers=max_workers
    )
    
    # Initialize shared state
    shared = {}
    
    try:
        # Run comparison
        print("\n⏱️  Running sequential processing...")
        start_time = time.time()
        
        final_action = graph.run(shared)
        
        total_time = time.time() - start_time
        print(f"\n✅ Comparison complete in {total_time:.2f}s")
        
        return True
        
    except Exception as e:
        logging.error(f"Error during comparison: {e}")
        print(f"\n❌ Comparison failed: {e}")
        return False


def run_parallel_only(data_type: str = "numbers", count: int = 1000,
                     process_type: str = "io", max_workers: int = None):
    """Run parallel processing only."""
    print(f"\n⚡ Parallel Batch Processing")
    print(f"📊 Processing {count} {data_type} items")
    print("=" * 60)
    
    # Create parallel-only graph
    graph = create_parallel_only_graph(
        data_type=data_type,
        count=count,
        process_type=process_type,
        max_workers=max_workers
    )
    
    # Initialize shared state
    shared = {}
    
    try:
        # Run parallel processing
        final_action = graph.run(shared)
        
        print("\n✅ Parallel processing complete")
        return True
        
    except Exception as e:
        logging.error(f"Error during parallel processing: {e}")
        print(f"\n❌ Processing failed: {e}")
        return False


def run_benchmarks():
    """Run various benchmark scenarios."""
    print("KayGraph Parallel Batch Processing Benchmarks")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "I/O-Bound Operations (Small)",
            "data_type": "numbers",
            "count": 50,
            "process_type": "io",
            "max_workers": 8
        },
        {
            "name": "I/O-Bound Operations (Large)",
            "data_type": "numbers",
            "count": 200,
            "process_type": "io",
            "max_workers": 16
        },
        {
            "name": "Text Processing",
            "data_type": "text",
            "count": 100,
            "process_type": "text",
            "max_workers": 4
        },
        {
            "name": "Numeric Calculations",
            "data_type": "numbers",
            "count": 100,
            "process_type": "number",
            "max_workers": 4
        }
    ]
    
    for scenario in scenarios:
        print(f"\n\n🔬 Benchmark: {scenario['name']}")
        print("-" * 40)
        
        run_comparison(
            data_type=scenario["data_type"],
            count=scenario["count"],
            process_type=scenario["process_type"],
            max_workers=scenario["max_workers"]
        )
        
        # Small delay between benchmarks
        time.sleep(1)


def main():
    """Run the parallel batch processing example."""
    if len(sys.argv) < 2:
        print("KayGraph Parallel Batch Processing")
        print("-" * 30)
        print("\nUsage:")
        print("  Compare:    python main.py compare [count] [workers]")
        print("  Parallel:   python main.py parallel [count] [workers]")
        print("  Benchmark:  python main.py benchmark")
        print("\nExamples:")
        print("  python main.py compare 100 8")
        print("  python main.py parallel 1000 16")
        print("  python main.py benchmark")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "compare":
        # Run comparison
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else None
        
        success = run_comparison(
            data_type="numbers",
            count=count,
            process_type="io",
            max_workers=workers
        )
        return 0 if success else 1
    
    elif command == "parallel":
        # Run parallel only
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else None
        
        success = run_parallel_only(
            data_type="mixed",
            count=count,
            process_type="io",
            max_workers=workers
        )
        return 0 if success else 1
    
    elif command == "benchmark":
        # Run benchmarks
        run_benchmarks()
        return 0
    
    else:
        print(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())