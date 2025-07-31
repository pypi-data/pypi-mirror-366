from kaygraph import Graph
from nodes import (
    DataCollectorNode,
    ProcessingNode,
    DeliveryNode,
    ErrorHandlerNode
)


def create_fault_tolerant_workflow() -> Graph:
    """Creates a workflow with comprehensive fault tolerance"""
    
    # Create the graph
    graph = Graph()
    
    # Create nodes
    collector = DataCollectorNode()
    processor = ProcessingNode()
    delivery = DeliveryNode()
    error_handler = ErrorHandlerNode()
    
    # Connect main workflow with conditional transitions
    graph.start(collector)
    
    # From collector: normal flow or circuit breaker fallback
    collector - "success" >> processor
    collector - "circuit_open" >> processor  # Still process with fallback data
    
    # From processor: normal flow or handle retry exhaustion
    processor - "success" >> delivery
    processor - "retry_exhausted" >> delivery  # Try delivery even with partial results
    
    # From delivery: success or failure handling
    delivery - "success" >> error_handler
    delivery - "delivery_failed" >> error_handler
    
    return graph


def create_resilient_workflow_with_fallbacks() -> Graph:
    """Creates a more complex workflow with explicit fallback paths"""
    
    graph = Graph()
    
    # Main nodes
    collector = DataCollectorNode()
    processor = ProcessingNode()
    delivery = DeliveryNode()
    error_handler = ErrorHandlerNode()
    
    # Fallback nodes (in a real implementation, these would be separate node classes)
    from nodes import DataCollectorNode, ProcessingNode, DeliveryNode
    
    class FallbackDataNode(DataCollectorNode):
        """Provides cached/default data when primary collection fails"""
        def __init__(self):
            super().__init__()
            self.node_id = "fallback_data"
        
        def exec(self, config):
            # Always return cached/default data
            self.logger.info("Using fallback data source")
            return {
                "data": [{"id": f"fallback_{i}", "value": 100, "source": "fallback"} for i in range(10)],
                "source": "fallback",
                "collected_at": time.time()
            }
    
    class PartialProcessingNode(ProcessingNode):
        """Handles partial processing when main processing fails"""
        def __init__(self):
            super().__init__()
            self.node_id = "partial_processor"
        
        def exec(self, input_data):
            # Simple processing for recovery
            self.logger.info("Using partial processing mode")
            processed = [{**record, "processed": True, "mode": "partial"} for record in input_data[:5]]
            return {
                "processed_data": processed,
                "processing_mode": "partial",
                "success_rate": 1.0
            }
    
    class AlternateDeliveryNode(DeliveryNode):
        """Alternative delivery mechanism"""
        def __init__(self):
            super().__init__()
            self.node_id = "alternate_delivery"
        
        def exec(self, delivery_input):
            # Always use backup delivery method
            self.logger.info("Using alternate delivery channel")
            data = delivery_input.get("data", [])
            return {
                "delivery_results": [{
                    "channel": "alternate",
                    "success": True,
                    "records_delivered": len(data)
                }],
                "total_delivered": len(data)
            }
    
    # Create fallback nodes
    fallback_data = FallbackDataNode()
    partial_processor = PartialProcessingNode()
    alternate_delivery = AlternateDeliveryNode()
    
    # Main flow
    graph.start(collector)
    collector - "success" >> processor
    processor - "success" >> delivery
    delivery - "success" >> error_handler
    
    # Fallback paths
    collector - "circuit_open" >> fallback_data
    fallback_data >> processor
    
    processor - "retry_exhausted" >> partial_processor
    partial_processor >> delivery
    
    delivery - "delivery_failed" >> alternate_delivery
    alternate_delivery >> error_handler
    
    return graph