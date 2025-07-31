from kaygraph import Graph
from nodes import (
    DataIngestionNode,
    DataValidationNode,
    DataProcessingNode,
    DataEnrichmentNode,
    DataStorageNode,
    MetricsAggregatorNode
)

def create_metrics_graph() -> Graph:
    """Creates the main data processing graph with metrics collection"""
    
    # Create the graph
    graph = Graph()
    
    # Create nodes
    ingestion = DataIngestionNode()
    validation = DataValidationNode()
    processing = DataProcessingNode()
    enrichment = DataEnrichmentNode()
    storage = DataStorageNode()
    
    # Connect nodes with named actions
    graph.start(ingestion)
    ingestion >> validation
    validation >> processing
    processing >> enrichment
    enrichment >> storage
    
    return graph


def create_metrics_aggregation_graph() -> Graph:
    """Creates a separate graph for metrics aggregation"""
    
    graph = Graph()
    aggregator = MetricsAggregatorNode()
    
    graph.start(aggregator)
    
    return graph