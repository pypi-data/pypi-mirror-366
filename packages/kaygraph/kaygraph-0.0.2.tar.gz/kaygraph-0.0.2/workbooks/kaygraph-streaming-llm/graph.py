from kaygraph import Graph
from nodes import (
    PromptProcessorNode,
    StreamingLLMNode,
    ResponseHandlerNode,
    TokenAggregatorNode
)


def create_streaming_llm_workflow() -> Graph:
    """Creates an enhanced streaming LLM workflow with production features"""
    
    # Create the graph
    graph = Graph()
    
    # Create nodes
    prompt_processor = PromptProcessorNode()
    streaming_llm = StreamingLLMNode()
    response_handler = ResponseHandlerNode()
    token_aggregator = TokenAggregatorNode()
    
    # Connect the main workflow
    graph.start(prompt_processor)
    prompt_processor - "validated" >> streaming_llm
    streaming_llm - "streamed" >> response_handler
    streaming_llm - "stream_failed" >> token_aggregator  # Handle failures
    response_handler - "processed" >> token_aggregator
    response_handler - "high_filter_rate" >> token_aggregator  # Handle high filtering
    
    return graph


def create_resilient_streaming_workflow() -> Graph:
    """Creates a more resilient streaming workflow with error handling"""
    
    graph = Graph()
    
    # Main nodes
    prompt_processor = PromptProcessorNode()
    streaming_llm = StreamingLLMNode()
    response_handler = ResponseHandlerNode()
    token_aggregator = TokenAggregatorNode()
    
    # Error handling nodes
    class FallbackResponseNode(ResponseHandlerNode):
        """Provides fallback responses when streaming fails"""
        def __init__(self):
            super().__init__()
            self.node_id = "fallback_response"
        
        def exec(self, streaming_result):
            # Provide fallback response
            fallback_tokens = ["I", " apologize", ",", " but", " I", " encountered", " an", " issue", ".", " Please", " try", " again", "."]
            
            return {
                "validated_tokens": fallback_tokens,
                "validated_response": " ".join(fallback_tokens),
                "filtered_tokens": [],
                "safety_summary": {"total_violations": 0, "violation_rate": 0},
                "quality_metrics": {
                    "avg_safety_score": 1.0,
                    "filter_rate": 0.0,
                    "total_tokens": len(fallback_tokens),
                    "validated_tokens": len(fallback_tokens)
                },
                "source": "fallback"
            }
    
    class StreamingRetryNode(StreamingLLMNode):
        """Retry streaming with simpler parameters"""
        def __init__(self):
            super().__init__()
            self.node_id = "streaming_retry"
        
        def prep(self, shared):
            # Use simpler parameters for retry
            prompt_config = shared.get("processed_prompt", {}).copy()
            prompt_config["max_tokens"] = min(prompt_config.get("max_tokens", 100), 50)
            prompt_config["temperature"] = 0.3  # Lower temperature for more reliable output
            return prompt_config
    
    fallback_response = FallbackResponseNode()
    streaming_retry = StreamingRetryNode()
    
    # Main flow
    graph.start(prompt_processor)
    prompt_processor - "validated" >> streaming_llm
    streaming_llm - "streamed" >> response_handler
    response_handler - "processed" >> token_aggregator
    
    # Error handling paths
    streaming_llm - "stream_failed" >> streaming_retry
    streaming_retry - "streamed" >> response_handler
    streaming_retry - "stream_failed" >> fallback_response
    
    # High filter rate handling
    response_handler - "high_filter_rate" >> fallback_response
    fallback_response >> token_aggregator
    
    return graph