from kaygraph import Graph
from nodes import (
    DataSourceNode,
    DataValidationNode,
    DataProcessingNode,
    DataAggregationNode,
    DataStorageNode,
    ErrorHandlerNode
)


def create_monitoring_workflow() -> Graph:
    """Creates a workflow with comprehensive monitoring"""
    
    # Create the graph
    graph = Graph()
    
    # Create nodes
    data_source = DataSourceNode()
    validator = DataValidationNode()
    processor = DataProcessingNode()
    aggregator = DataAggregationNode()
    storage = DataStorageNode()
    error_handler = ErrorHandlerNode()
    
    # Build the workflow
    graph.start(data_source)
    
    # Main flow
    data_source >> ("validate", validator)
    validator >> ("process", processor)
    validator >> ("no_valid_data", error_handler)
    processor >> ("aggregate", aggregator)
    aggregator >> ("store", storage)
    
    # Error handling paths
    processor >> ("error", error_handler)
    storage >> ("error", error_handler)
    
    return graph


def create_parallel_monitoring_workflow() -> Graph:
    """Creates a workflow with parallel processing branches"""
    
    from kaygraph import ParallelBatchNode
    
    class ParallelProcessor(ParallelBatchNode):
        """Process items in parallel with monitoring"""
        def __init__(self):
            super().__init__(max_workers=4, node_id="parallel_processor")
            # Inherit monitoring from MonitoringNode
            from monitoring_nodes import MonitoringNode
            MonitoringNode.__init__(self, node_id="parallel_processor")
        
        def prep(self, shared):
            # Split data into chunks for parallel processing
            data = shared.get("valid_data", [])
            chunk_size = 5
            return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        
        def exec(self, chunk):
            # Process each chunk
            import time
            import random
            
            processed = []
            for item in chunk:
                time.sleep(random.uniform(0.01, 0.05))
                processed.append({
                    **item,
                    "processed": True,
                    "chunk_id": id(chunk)
                })
            return processed
        
        def post(self, shared, prep_res, exec_res):
            # Flatten results
            all_processed = []
            for chunk_result in exec_res:
                all_processed.extend(chunk_result)
            
            shared["processed_data"] = all_processed
            return "aggregate"
    
    # Create graph with parallel processing
    graph = Graph()
    
    # Create nodes
    data_source = DataSourceNode()
    validator = DataValidationNode()
    parallel_processor = ParallelProcessor()
    aggregator = DataAggregationNode()
    storage = DataStorageNode()
    
    # Build workflow
    graph.start(data_source)
    data_source >> ("validate", validator)
    validator >> ("process", parallel_processor)
    parallel_processor >> ("aggregate", aggregator)
    aggregator >> ("store", storage)
    
    return graph