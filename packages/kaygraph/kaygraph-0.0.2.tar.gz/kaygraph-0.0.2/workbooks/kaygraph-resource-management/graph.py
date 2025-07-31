from kaygraph import Graph
from nodes import (
    DatabaseReaderNode,
    FileProcessorNode,
    ApiUploaderNode,
    NotificationNode,
    ResourceMonitorNode,
    ResourcePool
)


class ResourceManagedGraph(Graph):
    """A graph with automatic resource management"""
    
    def setup_resources(self):
        """Setup shared resources for the entire graph"""
        self.resource_pool = ResourcePool()
        self.logger.info("Graph-level resources setup")
    
    def cleanup_resources(self):
        """Cleanup all graph resources"""
        if hasattr(self, 'resource_pool'):
            self.resource_pool.cleanup_all()
        self.logger.info("Graph-level resources cleaned up")
    
    def prep(self, shared):
        """Prepare shared context with resource pool"""
        shared["_resource_pool"] = getattr(self, 'resource_pool', None)
        return super().prep(shared)
    
    def _run(self, shared):
        """Run the graph with resource management"""
        # Setup resources
        self.setup_resources()
        
        try:
            # Inject resource pool into each node's context
            current_node = self.start_node
            while current_node:
                if hasattr(self, 'resource_pool'):
                    current_node.set_context("resource_pool", self.resource_pool)
                # Move to next node (simplified traversal)
                if current_node.successors:
                    current_node = list(current_node.successors.values())[0]
                else:
                    break
            
            # Run the normal graph execution
            return super()._run(shared)
            
        finally:
            # Always cleanup resources
            self.cleanup_resources()


def create_resource_managed_workflow() -> ResourceManagedGraph:
    """Creates a workflow with comprehensive resource management"""
    
    # Create the graph
    graph = ResourceManagedGraph()
    
    # Create nodes
    db_reader = DatabaseReaderNode()
    file_processor = FileProcessorNode()
    api_uploader = ApiUploaderNode()
    notifier = NotificationNode()
    
    # Connect the main workflow
    graph.start(db_reader)
    db_reader >> file_processor
    file_processor >> api_uploader
    api_uploader >> notifier
    
    return graph


def create_monitored_workflow() -> Graph:
    """Creates a workflow with resource monitoring"""
    
    # Create main workflow
    main_graph = create_resource_managed_workflow()
    
    # Create monitoring graph
    monitor_graph = Graph()
    resource_monitor = ResourceMonitorNode()
    monitor_graph.start(resource_monitor)
    
    return main_graph, monitor_graph