from kaygraph import Graph
from nodes import (
    DataPartitionerNode,
    MapCoordinatorNode,
    ShuffleNode,
    ReduceCoordinatorNode,
    ResultAggregatorNode
)


class DistributedMapReduceGraph(Graph):
    """A graph with distributed worker management"""
    
    def setup_resources(self):
        """Setup shared resources for distributed execution"""
        self.logger.info("Setting up distributed MapReduce resources")
    
    def cleanup_resources(self):
        """Cleanup distributed resources"""
        self.logger.info("Cleaning up distributed MapReduce resources")


def create_distributed_mapreduce_workflow() -> DistributedMapReduceGraph:
    """Creates a distributed MapReduce workflow"""
    
    # Create the graph
    graph = DistributedMapReduceGraph()
    
    # Create nodes
    partitioner = DataPartitionerNode()
    map_coordinator = MapCoordinatorNode()
    shuffle = ShuffleNode()
    reduce_coordinator = ReduceCoordinatorNode()
    aggregator = ResultAggregatorNode()
    
    # Connect the workflow
    graph.start(partitioner)
    partitioner - "partitioned" >> map_coordinator
    map_coordinator - "mapped" >> shuffle
    shuffle - "shuffled" >> reduce_coordinator
    reduce_coordinator - "reduced" >> aggregator
    
    return graph


def create_fault_tolerant_mapreduce_workflow() -> Graph:
    """Creates a MapReduce workflow with enhanced fault tolerance"""
    
    graph = DistributedMapReduceGraph()
    
    # Main nodes
    partitioner = DataPartitionerNode()
    map_coordinator = MapCoordinatorNode()
    shuffle = ShuffleNode()
    reduce_coordinator = ReduceCoordinatorNode()
    aggregator = ResultAggregatorNode()
    
    # Error handling nodes
    class PartialResultsAggregator(ResultAggregatorNode):
        """Aggregates partial results when some tasks fail"""
        def __init__(self):
            super().__init__()
            self.node_id = "partial_aggregator"
        
        def validate_input(self, reduce_results):
            # More lenient validation for partial results
            if not reduce_results:
                raise ValueError("No reduce results provided")
            
            final_results = reduce_results.get("final_results", {})
            if not final_results:
                raise ValueError("No partial results available")
            
            return reduce_results
        
        def exec(self, aggregation_input):
            # Similar to parent but with partial result handling
            result = super().exec(aggregation_input)
            result["summary"]["result_type"] = "partial"
            result["summary"]["completeness"] = self._calculate_completeness(aggregation_input)
            return result
        
        def _calculate_completeness(self, input_data):
            map_results = input_data.get("map_results", {})
            reduce_results = input_data.get("reduce_results", {})
            
            map_success_rate = (map_results.get("successful_tasks", 0) / 
                               max(1, map_results.get("total_tasks", 1)))
            reduce_success_rate = (reduce_results.get("successful_tasks", 0) / 
                                  max(1, reduce_results.get("total_tasks", 1)))
            
            return (map_success_rate + reduce_success_rate) / 2
    
    class RetryCoordinator(MapCoordinatorNode):
        """Retry coordinator with different parameters"""
        def __init__(self):
            super().__init__()
            self.node_id = "retry_coordinator"
        
        def setup_resources(self):
            # Use fewer workers for retry
            num_workers = max(1, self.params.get("num_workers", 4) // 2)
            from nodes import WorkerPool
            self.worker_pool = WorkerPool(num_workers)
            self.logger.info(f"Retry coordinator: {num_workers} workers")
    
    partial_aggregator = PartialResultsAggregator()
    retry_coordinator = RetryCoordinator()
    
    # Main flow
    graph.start(partitioner)
    partitioner - "partitioned" >> map_coordinator
    map_coordinator - "mapped" >> shuffle
    shuffle - "shuffled" >> reduce_coordinator
    reduce_coordinator - "reduced" >> aggregator
    
    # Fault tolerance paths
    # If map phase has too many failures, retry with fewer workers
    map_coordinator - "map_failed" >> retry_coordinator
    retry_coordinator - "mapped" >> shuffle
    
    # If reduce phase has failures, use partial results
    reduce_coordinator - "reduce_failed" >> partial_aggregator
    
    return graph