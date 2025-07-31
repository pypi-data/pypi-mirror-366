#!/usr/bin/env python3
"""
Demonstration of basic communication patterns in KayGraph.
"""

import asyncio
import argparse
import logging
import time
from typing import List, Dict, Any
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, AsyncGraph
from communication_nodes import (
    MessageQueue, EventBus, Channel,
    ProducerNode, ConsumerNode,
    PublisherNode, SubscriberNode,
    RequestNode, ResponseNode, ServiceNode,
    BroadcastNode, PipelineStageNode
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_producer_consumer_graph() -> Graph:
    """Create a producer-consumer pattern graph."""
    # Create nodes
    producer1 = ProducerNode(lambda: {"type": "A", "value": time.time()}, "producer1")
    producer2 = ProducerNode(lambda: {"type": "B", "value": time.time()}, "producer2")
    
    consumer1 = ConsumerNode(lambda x: f"C1 processed: {x}", "consumer1")
    consumer2 = ConsumerNode(lambda x: f"C2 processed: {x}", "consumer2")
    
    # Create graph - producers feed into consumers
    graph = Graph()
    
    # Add all nodes
    graph.add_node(producer1)
    graph.add_node(producer2)
    graph.add_node(consumer1)
    graph.add_node(consumer2)
    
    # Producers run in parallel, then consumers
    producer1 >> consumer1
    producer2 >> consumer2
    
    return graph


def create_pubsub_graph() -> Graph:
    """Create a publish-subscribe pattern graph."""
    # Publishers
    news_pub = PublisherNode("news", "news_publisher")
    weather_pub = PublisherNode("weather", "weather_publisher")
    
    # Subscribers
    all_sub = SubscriberNode(["news", "weather"], node_id="all_subscriber")
    news_sub = SubscriberNode(["news"], node_id="news_only_subscriber")
    
    # Create graph
    graph = Graph()
    
    # Publishers can run in parallel
    graph.add_node(news_pub)
    graph.add_node(weather_pub)
    
    # Subscribers run after publishers
    news_pub >> all_sub
    weather_pub >> news_sub
    
    return graph


def create_request_response_graph() -> Graph:
    """Create a request-response pattern graph."""
    # Services
    calc_service = ServiceNode(
        "calculator",
        lambda req: {"result": eval(req["payload"].get("expression", "0"))},
        "calc_service"
    )
    
    echo_service = ServiceNode(
        "echo",
        lambda req: {"echo": req["payload"]},
        "echo_service"
    )
    
    # Clients
    calc_client = RequestNode("calculator", "calc_client")
    echo_client = RequestNode("echo", "echo_client")
    
    # Response handlers
    response_handler = ResponseNode("response_handler")
    
    # Create graph
    graph = Graph()
    
    # Clients make requests
    graph.add_node(calc_client)
    graph.add_node(echo_client)
    
    # Services process requests
    calc_client >> calc_service
    echo_client >> echo_service
    
    # Handle responses
    calc_service >> response_handler
    echo_service >> response_handler
    
    return graph


def create_pipeline_graph() -> Graph:
    """Create a pipeline pattern graph."""
    # Pipeline stages
    stage1 = PipelineStageNode(
        "validation",
        lambda x: {**x, "valid": True} if x else None
    )
    
    stage2 = PipelineStageNode(
        "enrichment",
        lambda x: {**x, "enriched_data": "additional info"} if x else None
    )
    
    stage3 = PipelineStageNode(
        "transformation",
        lambda x: {**x, "transformed": str(x).upper()} if x else None
    )
    
    stage4 = PipelineStageNode(
        "output",
        lambda x: {**x, "final": True} if x else None
    )
    
    # Create pipeline
    graph = Graph()
    
    # Linear pipeline
    stage1 >> stage2 >> stage3 >> stage4
    
    graph.set_start(stage1)
    
    return graph


def create_fanout_fanin_graph() -> Graph:
    """Create a fan-out/fan-in pattern graph."""
    # Splitter node
    class SplitterNode(ProducerNode):
        def exec(self, prep_res):
            # Split data into chunks
            data = list(range(10))
            chunks = [data[i:i+3] for i in range(0, len(data), 3)]
            return {"chunks": chunks}
        
        def post(self, shared, prep_res, exec_res):
            shared["work_chunks"] = exec_res["chunks"]
            shared["completed_chunks"] = []
            return None
    
    # Worker node
    class WorkerNode(ConsumerNode):
        def prep(self, shared):
            chunks = shared.get("work_chunks", [])
            if chunks:
                return chunks.pop(0)
            return None
        
        def exec(self, chunk):
            if chunk is None:
                return {"processed": False}
            
            # Process chunk
            result = [x * 2 for x in chunk]
            return {"result": result, "processed": True}
        
        def post(self, shared, prep_res, exec_res):
            if exec_res.get("processed"):
                shared["completed_chunks"].append(exec_res["result"])
            
            # Continue if more work
            if shared.get("work_chunks"):
                return "default"
            return None
    
    # Merger node
    class MergerNode(Node):
        def prep(self, shared):
            return shared.get("completed_chunks", [])
        
        def exec(self, chunks):
            # Merge all results
            merged = []
            for chunk in chunks:
                merged.extend(chunk)
            return {"merged_result": merged}
        
        def post(self, shared, prep_res, exec_res):
            shared["final_result"] = exec_res["merged_result"]
            logger.info(f"Final merged result: {exec_res['merged_result']}")
            return None
    
    # Create graph
    splitter = SplitterNode(node_id="splitter")
    worker1 = WorkerNode(node_id="worker1")
    worker2 = WorkerNode(node_id="worker2")
    worker3 = WorkerNode(node_id="worker3")
    merger = MergerNode(node_id="merger")
    
    graph = Graph(start=splitter)
    
    # Fan-out
    splitter >> worker1
    splitter >> worker2
    splitter >> worker3
    
    # Fan-in
    worker1 >> merger
    worker2 >> merger
    worker3 >> merger
    
    return graph


def demonstrate_patterns():
    """Demonstrate all communication patterns."""
    print("\n=== Basic Communication Patterns Demo ===\n")
    
    # Create shared communication infrastructure
    shared = {
        "message_queue": MessageQueue(max_size=1000),
        "event_bus": EventBus(),
        "data_channel": Channel("main", buffer_size=100),
        "service_queues": {},
        "broadcasts": [],
        "publications": {},
        "responses": {},
        "pending_requests": {}
    }
    
    # 1. Producer-Consumer Pattern
    print("1. Producer-Consumer Pattern")
    print("-" * 40)
    
    pc_graph = create_producer_consumer_graph()
    
    # Run producers multiple times
    for i in range(3):
        logger.info(f"Production cycle {i+1}")
        pc_graph.run(shared)
        time.sleep(0.1)
    
    print(f"Queue size: {shared['message_queue'].size()}")
    print()
    
    # 2. Publish-Subscribe Pattern
    print("2. Publish-Subscribe Pattern")
    print("-" * 40)
    
    # Setup event handlers
    news_events = []
    weather_events = []
    
    shared["event_bus"].on("news", lambda data: news_events.append(data))
    shared["event_bus"].on("weather", lambda data: weather_events.append(data))
    
    pubsub_graph = create_pubsub_graph()
    pubsub_graph.run(shared)
    
    print(f"News events: {len(news_events)}")
    print(f"Weather events: {len(weather_events)}")
    print(f"Publications stored: {list(shared['publications'].keys())}")
    print()
    
    # 3. Request-Response Pattern
    print("3. Request-Response Pattern")
    print("-" * 40)
    
    # Modify shared to include specific requests
    shared_rr = shared.copy()
    
    # Override request creation for demo
    class DemoCalcRequest(RequestNode):
        def exec(self, prep_res):
            request_id = str(uuid.uuid4())
            return {
                "request": {
                    "id": request_id,
                    "service": self.service_id,
                    "payload": {"expression": "2 + 2 * 3"},
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    # Create custom graph
    calc_client = DemoCalcRequest("calculator", "calc_client")
    calc_service = ServiceNode(
        "calculator",
        lambda req: {"result": eval(req["payload"].get("expression", "0"))},
        "calc_service"
    )
    
    rr_graph = Graph()
    calc_client >> calc_service
    rr_graph.set_start(calc_client)
    
    rr_graph.run(shared_rr)
    
    print(f"Pending requests: {len(shared_rr.get('pending_requests', {}))}")
    print(f"Responses: {len(shared_rr.get('responses', {}))}")
    
    # Show response
    for req_id, response in shared_rr.get('responses', {}).items():
        print(f"Response: {response.get('result')}")
    print()
    
    # 4. Pipeline Pattern
    print("4. Pipeline Pattern")
    print("-" * 40)
    
    shared_pipeline = {
        "pipeline_data": {"input": "test data", "id": 123},
        "pipeline_log": []
    }
    
    pipeline_graph = create_pipeline_graph()
    pipeline_graph.run(shared_pipeline)
    
    print("Pipeline stages executed:")
    for log_entry in shared_pipeline["pipeline_log"]:
        print(f"  - {log_entry['stage']} at {log_entry['timestamp'][:19]}")
    
    print(f"Final data: {shared_pipeline['pipeline_data']}")
    print()
    
    # 5. Fan-out/Fan-in Pattern
    print("5. Fan-out/Fan-in Pattern")
    print("-" * 40)
    
    fanout_graph = create_fanout_fanin_graph()
    fanout_graph.run({})
    print()
    
    # 6. Broadcast Pattern
    print("6. Broadcast Pattern")
    print("-" * 40)
    
    broadcaster = BroadcastNode()
    
    # Register broadcast listeners
    broadcast_received = []
    shared["event_bus"].on("broadcast", 
                          lambda data: broadcast_received.append(data))
    
    broadcaster.run(shared)
    
    print(f"Broadcasts sent: {len(shared.get('broadcasts', []))}")
    print(f"Broadcast listeners notified: {len(broadcast_received)}")
    
    if broadcast_received:
        print(f"Broadcast content: {broadcast_received[0]['message']}")


def demonstrate_advanced_patterns():
    """Demonstrate advanced communication patterns."""
    print("\n=== Advanced Communication Patterns ===\n")
    
    # 1. Reliable Message Delivery
    print("1. Reliable Message Delivery")
    print("-" * 40)
    
    class ReliableProducer(ProducerNode):
        def exec(self, prep_res):
            data = super().exec(prep_res)
            data["delivery_attempts"] = 0
            data["max_attempts"] = 3
            return data
        
        def post(self, shared, prep_res, exec_res):
            # Simulate delivery with retry
            exec_res["delivery_attempts"] += 1
            
            if exec_res["delivery_attempts"] < exec_res["max_attempts"]:
                # Simulate failure
                logger.info(f"Delivery attempt {exec_res['delivery_attempts']} failed")
                return "default"  # Retry
            
            # Success
            super().post(shared, prep_res, exec_res)
            logger.info("Message delivered successfully")
            return None
    
    reliable = ReliableProducer()
    reliable.run({"message_queue": MessageQueue()})
    print()
    
    # 2. Message Aggregation
    print("2. Message Aggregation")
    print("-" * 40)
    
    class AggregatorNode(Node):
        def __init__(self, window_size=5):
            super().__init__("aggregator")
            self.buffer = []
            self.window_size = window_size
        
        def prep(self, shared):
            queue = shared.get("message_queue")
            if queue:
                msg = queue.get()
                if msg:
                    self.buffer.append(msg)
            
            return {"buffer_size": len(self.buffer)}
        
        def exec(self, prep_res):
            if len(self.buffer) >= self.window_size:
                # Aggregate messages
                aggregated = {
                    "count": len(self.buffer),
                    "messages": [m.content for m in self.buffer],
                    "timestamp": datetime.now().isoformat()
                }
                self.buffer.clear()
                return {"aggregated": aggregated}
            
            return {"aggregated": None}
        
        def post(self, shared, prep_res, exec_res):
            if exec_res.get("aggregated"):
                logger.info(f"Aggregated {exec_res['aggregated']['count']} messages")
                shared.setdefault("aggregated_results", []).append(exec_res["aggregated"])
            
            # Continue if more messages
            queue = shared.get("message_queue")
            if queue and queue.size() > 0:
                return "default"
            
            return None
    
    # Test aggregation
    shared = {"message_queue": MessageQueue()}
    
    # Produce messages
    producer = ProducerNode()
    for _ in range(7):
        producer.run(shared)
    
    # Aggregate
    aggregator = AggregatorNode(window_size=3)
    while shared["message_queue"].size() > 0:
        aggregator.run(shared)
    
    print(f"Aggregated batches: {len(shared.get('aggregated_results', []))}")
    print()
    
    # 3. Circuit Breaker Pattern
    print("3. Circuit Breaker Pattern")
    print("-" * 40)
    
    class CircuitBreakerNode(ServiceNode):
        def __init__(self, service_id, failure_threshold=3):
            super().__init__(service_id)
            self.failure_count = 0
            self.failure_threshold = failure_threshold
            self.circuit_open = False
        
        def exec(self, request):
            if self.circuit_open:
                logger.warning("Circuit breaker is OPEN - rejecting request")
                return {
                    "request_id": request["id"] if request else "unknown",
                    "result": {"error": "Circuit breaker open"},
                    "processed": False
                }
            
            # Simulate occasional failures
            import random
            if random.random() < 0.3:  # 30% failure rate
                self.failure_count += 1
                logger.warning(f"Service failure ({self.failure_count}/{self.failure_threshold})")
                
                if self.failure_count >= self.failure_threshold:
                    self.circuit_open = True
                    logger.error("Circuit breaker OPENED due to failures")
                
                return {
                    "request_id": request["id"] if request else "unknown",
                    "result": {"error": "Service failure"},
                    "processed": False
                }
            
            # Success - reset failure count
            self.failure_count = 0
            return super().exec(request)
    
    # Test circuit breaker
    cb_service = CircuitBreakerNode("protected_service")
    
    for i in range(10):
        request = {
            "id": f"req_{i}",
            "payload": {"data": f"test_{i}"}
        }
        result = cb_service.exec(request)
        
        if "error" in result.get("result", {}):
            print(f"Request {i}: {result['result']['error']}")
        else:
            print(f"Request {i}: Success")
    
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KayGraph Basic Communication Patterns Demo"
    )
    
    parser.add_argument(
        "--pattern",
        choices=["all", "basic", "advanced", "producer-consumer", 
                "pubsub", "request-response", "pipeline", "fanout"],
        default="all",
        help="Communication pattern to demonstrate"
    )
    
    args = parser.parse_args()
    
    if args.pattern == "all":
        demonstrate_patterns()
        demonstrate_advanced_patterns()
    elif args.pattern == "basic":
        demonstrate_patterns()
    elif args.pattern == "advanced":
        demonstrate_advanced_patterns()
    else:
        # Run specific pattern
        shared = {
            "message_queue": MessageQueue(),
            "event_bus": EventBus(),
            "data_channel": Channel("main"),
            "service_queues": {},
            "publications": {},
            "responses": {},
            "pending_requests": {}
        }
        
        if args.pattern == "producer-consumer":
            graph = create_producer_consumer_graph()
        elif args.pattern == "pubsub":
            graph = create_pubsub_graph()
        elif args.pattern == "request-response":
            graph = create_request_response_graph()
        elif args.pattern == "pipeline":
            graph = create_pipeline_graph()
            shared = {"pipeline_data": {"test": "data"}, "pipeline_log": []}
        elif args.pattern == "fanout":
            graph = create_fanout_fanin_graph()
            shared = {}
        
        print(f"\n=== Running {args.pattern} pattern ===\n")
        graph.run(shared)
        
        # Show results
        if args.pattern == "producer-consumer":
            print(f"Messages in queue: {shared['message_queue'].size()}")
        elif args.pattern == "pipeline":
            print(f"Pipeline result: {shared.get('pipeline_data')}")


if __name__ == "__main__":
    import uuid
    from datetime import datetime
    main()