from kaygraph import Graph
from api_nodes import (
    RequestValidatorNode,
    ProcessorNode,
    ResponseBuilderNode
)


def create_api_processing_workflow() -> Graph:
    """Creates the main API processing workflow"""
    
    # Create the graph
    graph = Graph()
    
    # Create nodes
    validator = RequestValidatorNode()
    processor = ProcessorNode()
    response_builder = ResponseBuilderNode()
    
    # Connect the workflow
    graph.start(validator)
    validator - "validated" >> processor
    processor - "processed" >> response_builder
    processor - "process_failed" >> response_builder  # Handle failures
    
    return graph


def create_resilient_api_workflow() -> Graph:
    """Creates an API workflow with enhanced error handling"""
    
    graph = Graph()
    
    # Main nodes
    validator = RequestValidatorNode()
    processor = ProcessorNode()
    response_builder = ResponseBuilderNode()
    
    # Error handling nodes
    class FallbackProcessor(ProcessorNode):
        """Simplified processor for when main processing fails"""
        def __init__(self):
            super().__init__()
            self.node_id = "fallback_processor"
        
        def exec(self, validated_request):
            # Simple fallback processing
            return {
                "result": {
                    "message": "Processing temporarily unavailable",
                    "fallback": True,
                    "original_request": validated_request.get("type", "unknown")
                },
                "success": True,
                "processing_type": "fallback",
                "processing_time": 0.001,
                "correlation_id": validated_request.get("correlation_id", "unknown"),
                "source": "fallback"
            }
    
    class ErrorResponseBuilder(ResponseBuilderNode):
        """Specialized response builder for errors"""
        def __init__(self):
            super().__init__()
            self.node_id = "error_response_builder"
        
        def exec(self, response_input):
            # Build error-specific response
            validated_request = response_input.get("validated_request", {})
            
            return {
                "request_id": validated_request.get("request_id", "unknown"),
                "status": "error",
                "data": {},
                "error": {
                    "type": "service_error",
                    "message": "Service temporarily unavailable",
                    "code": "SVC_001"
                },
                "metadata": {
                    "request_id": validated_request.get("request_id", "unknown"),
                    "correlation_id": validated_request.get("correlation_id", "unknown"),
                    "processed_at": "datetime.now().isoformat()",
                    "api_version": "1.0",
                    "error_handling": "automatic"
                }
            }
    
    fallback_processor = FallbackProcessor()
    error_response_builder = ErrorResponseBuilder()
    
    # Main flow
    graph.start(validator)
    validator - "validated" >> processor
    processor - "processed" >> response_builder
    
    # Error handling paths
    processor - "process_failed" >> fallback_processor
    fallback_processor >> response_builder
    
    # Validation failure path
    validator - "validation_failed" >> error_response_builder
    
    return graph