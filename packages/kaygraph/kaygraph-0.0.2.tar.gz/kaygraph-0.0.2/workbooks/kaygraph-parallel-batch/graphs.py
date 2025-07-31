"""
Parallel batch processing graphs using KayGraph.
"""

from kaygraph import Graph
from nodes import (
    LoadDataNode, SplitBatchNode, SequentialProcessNode,
    ParallelProcessNode, AggregateNode, ReportNode
)


def create_comparison_graph(
    data_type: str = "numbers",
    count: int = 100,
    process_type: str = "io",
    max_workers: int = None
) -> Graph:
    """
    Create a graph that compares sequential vs parallel processing.
    
    Args:
        data_type: Type of data to generate ("numbers", "text", "mixed")
        count: Number of items to process
        process_type: Type of processing ("io", "text", "number")
        max_workers: Maximum parallel workers
        
    Returns:
        Configured comparison graph
    """
    # Create nodes
    load_node = LoadDataNode(
        data_type=data_type,
        count=count,
        node_id="load"
    )
    
    split_node = SplitBatchNode(
        max_workers=max_workers,
        node_id="split"
    )
    
    sequential_node = SequentialProcessNode(
        process_type=process_type,
        node_id="sequential"
    )
    
    parallel_node = ParallelProcessNode(
        process_type=process_type,
        max_workers=max_workers,
        node_id="parallel"
    )
    
    aggregate_node = AggregateNode(node_id="aggregate")
    report_node = ReportNode(node_id="report")
    
    # Connect nodes
    # Load and split data
    load_node >> split_node
    
    # Process both ways
    split_node >> sequential_node >> parallel_node
    
    # Aggregate and report
    parallel_node >> aggregate_node >> report_node
    
    # Pass max_workers to aggregate for efficiency calculation
    aggregate_node.set_params({"max_workers": max_workers or 4})
    
    # Create graph
    graph = Graph(start=load_node)
    graph.logger.info(f"Comparison graph created for {count} {data_type} items")
    
    return graph


def create_parallel_only_graph(
    data_type: str = "numbers",
    count: int = 1000,
    process_type: str = "io",
    max_workers: int = None
) -> Graph:
    """
    Create a graph for parallel processing only (no comparison).
    
    Args:
        data_type: Type of data to generate
        count: Number of items to process
        process_type: Type of processing
        max_workers: Maximum parallel workers
        
    Returns:
        Configured parallel processing graph
    """
    # Create nodes
    load_node = LoadDataNode(
        data_type=data_type,
        count=count,
        node_id="load"
    )
    
    split_node = SplitBatchNode(
        max_workers=max_workers,
        node_id="split"
    )
    
    parallel_node = ParallelProcessNode(
        process_type=process_type,
        max_workers=max_workers,
        node_id="parallel"
    )
    
    # Simple report node
    class SimpleReportNode(Node):
        def prep(self, shared):
            return shared.get("parallel_metrics", {})
        
        def exec(self, metrics):
            return f"""
Parallel Processing Complete
===========================
Total items: {metrics.get('total_processed', 0)}
Time: {metrics.get('total_duration', 0):.2f}s
Throughput: {metrics.get('throughput', 0):.1f} items/sec
Success rate: {metrics.get('success_rate', 0):.1%}
"""
        
        def post(self, shared, prep_res, exec_res):
            print(exec_res)
            return "default"
    
    report_node = SimpleReportNode(node_id="simple_report")
    
    # Connect nodes
    load_node >> split_node >> parallel_node >> report_node
    
    # Create graph
    graph = Graph(start=load_node)
    graph.logger.info(f"Parallel-only graph created for {count} items")
    
    return graph


if __name__ == "__main__":
    # Test graph creation
    print("Creating parallel batch processing graphs...")
    
    # Comparison graph
    comp_graph = create_comparison_graph(
        data_type="numbers",
        count=100,
        process_type="io"
    )
    print(f"Comparison graph created: {comp_graph.start_node.node_id}")
    
    # Parallel-only graph
    par_graph = create_parallel_only_graph(
        data_type="text",
        count=1000,
        process_type="text"
    )
    print(f"Parallel-only graph created: {par_graph.start_node.node_id}")