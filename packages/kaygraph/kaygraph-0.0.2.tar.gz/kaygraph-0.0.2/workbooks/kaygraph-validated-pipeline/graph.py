from kaygraph import Graph
from nodes import (
    DataLoaderNode,
    DataCleanerNode,
    DataTransformerNode,
    DataAggregatorNode,
    DataExporterNode,
    ValidationErrorHandler
)


def create_validated_pipeline() -> Graph:
    """Creates a data pipeline with validation at each stage"""
    
    # Create the graph
    graph = Graph()
    
    # Create nodes
    loader = DataLoaderNode()
    cleaner = DataCleanerNode()
    transformer = DataTransformerNode()
    aggregator = DataAggregatorNode()
    exporter = DataExporterNode()
    error_handler = ValidationErrorHandler()
    
    # Connect nodes in sequence
    graph.start(loader)
    loader >> cleaner
    cleaner >> transformer
    transformer >> aggregator
    aggregator >> exporter
    
    # Note: In a real implementation, you might add error transitions:
    # loader - "validation_error" >> error_handler
    # cleaner - "validation_error" >> error_handler
    # etc.
    
    return graph


def create_error_handling_pipeline() -> Graph:
    """Creates a pipeline with explicit error handling paths"""
    
    graph = Graph()
    
    # Create nodes
    loader = DataLoaderNode()
    cleaner = DataCleanerNode()
    transformer = DataTransformerNode()
    aggregator = DataAggregatorNode()
    exporter = DataExporterNode()
    error_handler = ValidationErrorHandler()
    
    # Main flow
    graph.start(loader)
    loader - "cleaned" >> cleaner
    cleaner - "transformed" >> transformer
    transformer - "aggregated" >> aggregator
    aggregator - "exported" >> exporter
    
    # Error handling paths
    loader - "error" >> error_handler
    cleaner - "error" >> error_handler
    transformer - "error" >> error_handler
    aggregator - "error" >> error_handler
    exporter - "error" >> error_handler
    
    return graph