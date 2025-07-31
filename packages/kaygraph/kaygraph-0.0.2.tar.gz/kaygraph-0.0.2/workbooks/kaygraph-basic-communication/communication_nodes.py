#!/usr/bin/env python3
"""
Basic communication nodes for KayGraph.
"""

import asyncio
import json
import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime
from collections import defaultdict, deque
from pathlib import Path
from abc import ABC, abstractmethod

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, BatchNode, ValidatedNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Message:
    """Basic message structure."""
    
    def __init__(self, sender: str, content: Any, msg_type: str = "data",
                 priority: int = 5):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.content = content
        self.type = msg_type
        self.priority = priority
        self.timestamp = datetime.now()
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "content": self.content,
            "type": self.type,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class MessageQueue:
    """Thread-safe message queue."""
    
    def __init__(self, max_size: int = 1000):
        self._queue = deque(maxlen=max_size)
        self._subscribers: List[Callable] = []
    
    def put(self, message: Message):
        """Add message to queue."""
        self._queue.append(message)
        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(message)
            except Exception as e:
                logger.error(f"Subscriber error: {e}")
    
    def get(self) -> Optional[Message]:
        """Get message from queue."""
        return self._queue.popleft() if self._queue else None
    
    def peek(self) -> Optional[Message]:
        """Peek at next message without removing."""
        return self._queue[0] if self._queue else None
    
    def size(self) -> int:
        """Get queue size."""
        return len(self._queue)
    
    def subscribe(self, callback: Callable):
        """Subscribe to new messages."""
        self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from messages."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)


class EventBus:
    """Simple event bus for pub/sub."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history = deque(maxlen=100)
    
    def on(self, event_type: str, handler: Callable):
        """Register event handler."""
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler registered for {event_type}")
    
    def off(self, event_type: str, handler: Callable):
        """Unregister event handler."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
    
    def emit(self, event_type: str, data: Any = None):
        """Emit an event."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self._event_history.append(event)
        
        # Call all handlers
        for handler in self._handlers[event_type]:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
        
        # Call wildcard handlers
        for handler in self._handlers.get("*", []):
            try:
                handler(event_type, data)
            except Exception as e:
                logger.error(f"Wildcard handler error: {e}")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get event history."""
        return list(self._event_history)


class Channel:
    """Communication channel between nodes."""
    
    def __init__(self, name: str, buffer_size: int = 100):
        self.name = name
        self._buffer = deque(maxlen=buffer_size)
        self._receivers: Set[str] = set()
    
    def send(self, sender: str, data: Any):
        """Send data through channel."""
        message = Message(sender, data)
        self._buffer.append(message)
        logger.debug(f"Channel {self.name}: {sender} sent message")
    
    def receive(self, receiver: str) -> Optional[Message]:
        """Receive data from channel."""
        if receiver not in self._receivers:
            self._receivers.add(receiver)
        
        # Simple round-robin for demo
        if self._buffer:
            return self._buffer.popleft()
        return None
    
    def broadcast(self, sender: str, data: Any):
        """Broadcast to all receivers."""
        message = Message(sender, data, msg_type="broadcast")
        # In real implementation, would send to all receivers
        self._buffer.append(message)


class ProducerNode(Node):
    """Node that produces messages."""
    
    def __init__(self, produce_func: Optional[Callable] = None, 
                 node_id: str = None):
        super().__init__(node_id or "producer")
        self.produce_func = produce_func or self._default_produce
        self.message_count = 0
    
    def _default_produce(self) -> Any:
        """Default production function."""
        self.message_count += 1
        return {
            "item_id": self.message_count,
            "data": f"Item {self.message_count}",
            "timestamp": datetime.now().isoformat()
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Produce data."""
        data = self.produce_func()
        return {"produced_data": data}
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
            exec_res: Dict[str, Any]) -> Optional[str]:
        """Send produced data."""
        # Add to queue
        queue = shared.get("message_queue")
        if queue:
            message = Message(self.node_id, exec_res["produced_data"])
            queue.put(message)
        
        # Emit event
        event_bus = shared.get("event_bus")
        if event_bus:
            event_bus.emit("data_produced", exec_res["produced_data"])
        
        # Send to channel
        channel = shared.get("data_channel")
        if channel:
            channel.send(self.node_id, exec_res["produced_data"])
        
        return None


class ConsumerNode(Node):
    """Node that consumes messages."""
    
    def __init__(self, process_func: Optional[Callable] = None,
                 node_id: str = None):
        super().__init__(node_id or "consumer")
        self.process_func = process_func or self._default_process
        self.processed_count = 0
    
    def _default_process(self, data: Any) -> Any:
        """Default processing function."""
        self.processed_count += 1
        return {
            "processed": True,
            "result": f"Processed: {data}",
            "count": self.processed_count
        }
    
    def prep(self, shared: Dict[str, Any]) -> Optional[Message]:
        """Get message to process."""
        # Try queue first
        queue = shared.get("message_queue")
        if queue:
            return queue.get()
        
        # Try channel
        channel = shared.get("data_channel")
        if channel:
            return channel.receive(self.node_id)
        
        return None
    
    def exec(self, message: Optional[Message]) -> Dict[str, Any]:
        """Process message."""
        if not message:
            return {"processed": False, "reason": "No message"}
        
        result = self.process_func(message.content)
        return {
            "message_id": message.id,
            "result": result,
            "processing_time": (datetime.now() - message.timestamp).total_seconds()
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Optional[Message], 
            exec_res: Dict[str, Any]) -> Optional[str]:
        """Store result."""
        if exec_res.get("processed", True):
            # Emit completion event
            event_bus = shared.get("event_bus")
            if event_bus:
                event_bus.emit("data_consumed", exec_res)
        
        # Continue processing if more messages
        queue = shared.get("message_queue")
        if queue and queue.size() > 0:
            return "default"  # Process next message
        
        return None


class PublisherNode(Node):
    """Node that publishes to subscribers."""
    
    def __init__(self, topic: str, node_id: str = None):
        super().__init__(node_id or f"publisher_{topic}")
        self.topic = topic
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Generate publication data."""
        return {
            "topic": self.topic,
            "data": {
                "update_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "content": f"Update for {self.topic}"
            }
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
            exec_res: Dict[str, Any]) -> Optional[str]:
        """Publish to subscribers."""
        # Use event bus for pub/sub
        event_bus = shared.get("event_bus")
        if event_bus:
            event_bus.emit(self.topic, exec_res["data"])
            logger.info(f"Published to topic {self.topic}")
        
        # Also store in shared for pull-based subscribers
        publications = shared.setdefault("publications", {})
        topic_pubs = publications.setdefault(self.topic, [])
        topic_pubs.append(exec_res["data"])
        
        return None


class SubscriberNode(Node):
    """Node that subscribes to topics."""
    
    def __init__(self, topics: List[str], handler: Optional[Callable] = None,
                 node_id: str = None):
        super().__init__(node_id or f"subscriber_{topics[0]}")
        self.topics = topics
        self.handler = handler or self._default_handler
        self.received_messages = []
    
    def _default_handler(self, topic: str, data: Any):
        """Default message handler."""
        logger.info(f"Received on {topic}: {data}")
        self.received_messages.append({
            "topic": topic,
            "data": data,
            "received_at": datetime.now().isoformat()
        })
    
    def before_prep(self):
        """Subscribe to topics."""
        shared = self._shared_ref
        if shared:
            event_bus = shared.get("event_bus")
            if event_bus:
                for topic in self.topics:
                    event_bus.on(topic, lambda data: self.handler(topic, data))
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Check for new publications."""
        new_pubs = {}
        publications = shared.get("publications", {})
        
        for topic in self.topics:
            if topic in publications:
                new_pubs[topic] = publications[topic]
        
        # Store reference for event handler
        self._shared_ref = shared
        
        return {"new_publications": new_pubs}
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Process publications."""
        processed = 0
        
        for topic, pubs in prep_res["new_publications"].items():
            for pub in pubs:
                self.handler(topic, pub)
                processed += 1
        
        return {
            "processed_count": processed,
            "total_received": len(self.received_messages)
        }


class RequestNode(Node):
    """Node that makes requests."""
    
    def __init__(self, service_id: str, node_id: str = None):
        super().__init__(node_id or "request_node")
        self.service_id = service_id
        self.pending_requests = {}
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Create request."""
        request_id = str(uuid.uuid4())
        request = {
            "id": request_id,
            "service": self.service_id,
            "payload": {
                "action": "process",
                "data": "test data"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.pending_requests[request_id] = request
        return {"request": request}
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
            exec_res: Dict[str, Any]) -> Optional[str]:
        """Send request."""
        request = exec_res["request"]
        
        # Add to service queue
        service_queues = shared.setdefault("service_queues", {})
        service_queue = service_queues.setdefault(self.service_id, deque())
        service_queue.append(request)
        
        # Store pending request
        pending = shared.setdefault("pending_requests", {})
        pending[request["id"]] = {
            "request": request,
            "requester": self.node_id,
            "status": "pending"
        }
        
        return "wait_response"


class ResponseNode(Node):
    """Node that handles responses."""
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id or "response_handler")
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Check for responses."""
        responses = shared.get("responses", {})
        pending = shared.get("pending_requests", {})
        
        my_responses = []
        for req_id, response in responses.items():
            if req_id in pending and pending[req_id]["requester"] == self.node_id:
                my_responses.append(response)
        
        return {"responses": my_responses}
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Process responses."""
        results = []
        
        for response in prep_res["responses"]:
            results.append({
                "request_id": response["request_id"],
                "result": response["result"],
                "duration": response.get("processing_time", 0)
            })
        
        return {"processed_responses": results}


class ServiceNode(Node):
    """Node that provides a service."""
    
    def __init__(self, service_id: str, process_func: Optional[Callable] = None,
                 node_id: str = None):
        super().__init__(node_id or f"service_{service_id}")
        self.service_id = service_id
        self.process_func = process_func or self._default_process
    
    def _default_process(self, request: Dict[str, Any]) -> Any:
        """Default service processing."""
        return {
            "status": "success",
            "result": f"Processed: {request['payload']}"
        }
    
    def prep(self, shared: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get next request."""
        service_queues = shared.get("service_queues", {})
        
        if self.service_id in service_queues:
            queue = service_queues[self.service_id]
            if queue:
                return queue.popleft()
        
        return None
    
    def exec(self, request: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Process request."""
        if not request:
            return {"processed": False}
        
        start_time = time.time()
        result = self.process_func(request)
        
        return {
            "request_id": request["id"],
            "result": result,
            "processing_time": time.time() - start_time,
            "processed_by": self.node_id
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Optional[Dict[str, Any]], 
            exec_res: Dict[str, Any]) -> Optional[str]:
        """Send response."""
        if exec_res.get("processed", True) and prep_res:
            # Store response
            responses = shared.setdefault("responses", {})
            responses[exec_res["request_id"]] = exec_res
            
            # Update request status
            pending = shared.get("pending_requests", {})
            if exec_res["request_id"] in pending:
                pending[exec_res["request_id"]]["status"] = "completed"
        
        # Check for more requests
        service_queues = shared.get("service_queues", {})
        if self.service_id in service_queues and service_queues[self.service_id]:
            return "default"  # Process next request
        
        return None


class BroadcastNode(Node):
    """Node that broadcasts to all listeners."""
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id or "broadcaster")
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Create broadcast message."""
        return {
            "broadcast": {
                "id": str(uuid.uuid4()),
                "type": "system_update",
                "message": "Important announcement",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
            exec_res: Dict[str, Any]) -> Optional[str]:
        """Broadcast message."""
        broadcast = exec_res["broadcast"]
        
        # Add to broadcast queue
        broadcasts = shared.setdefault("broadcasts", deque(maxlen=100))
        broadcasts.append(broadcast)
        
        # Emit event
        event_bus = shared.get("event_bus")
        if event_bus:
            event_bus.emit("broadcast", broadcast)
        
        logger.info(f"Broadcast sent: {broadcast['type']}")
        return None


class PipelineStageNode(Node):
    """Node representing a pipeline stage."""
    
    def __init__(self, stage_name: str, transform_func: Optional[Callable] = None,
                 node_id: str = None):
        super().__init__(node_id or f"stage_{stage_name}")
        self.stage_name = stage_name
        self.transform_func = transform_func or self._default_transform
    
    def _default_transform(self, data: Any) -> Any:
        """Default transformation."""
        return {
            **data,
            f"{self.stage_name}_processed": True,
            f"{self.stage_name}_timestamp": datetime.now().isoformat()
        }
    
    def prep(self, shared: Dict[str, Any]) -> Any:
        """Get input data."""
        return shared.get("pipeline_data")
    
    def exec(self, data: Any) -> Any:
        """Transform data."""
        if data is None:
            return None
        
        return self.transform_func(data)
    
    def post(self, shared: Dict[str, Any], prep_res: Any, 
            exec_res: Any) -> Optional[str]:
        """Pass data to next stage."""
        shared["pipeline_data"] = exec_res
        
        # Log stage completion
        pipeline_log = shared.setdefault("pipeline_log", [])
        pipeline_log.append({
            "stage": self.stage_name,
            "timestamp": datetime.now().isoformat(),
            "data_snapshot": str(exec_res)[:100]
        })
        
        return None


# Example usage
if __name__ == "__main__":
    # Test basic communication
    logger.info("Testing basic communication patterns...")
    
    # Create shared communication infrastructure
    shared = {
        "message_queue": MessageQueue(),
        "event_bus": EventBus(),
        "data_channel": Channel("data"),
        "service_queues": {},
        "broadcasts": deque(maxlen=100)
    }
    
    # Test producer-consumer
    producer = ProducerNode()
    consumer = ConsumerNode()
    
    # Produce some messages
    for _ in range(3):
        producer.run(shared)
    
    # Consume messages
    while shared["message_queue"].size() > 0:
        consumer.run(shared)
    
    logger.info(f"Consumer processed {consumer.processed_count} messages")
    
    # Test pub-sub
    publisher = PublisherNode("news")
    subscriber = SubscriberNode(["news", "updates"])
    
    # Subscribe and publish
    subscriber.run(shared)  # Subscribe
    publisher.run(shared)   # Publish
    subscriber.run(shared)  # Process publications
    
    logger.info(f"Subscriber received {len(subscriber.received_messages)} messages")
    
    # Test request-response
    service = ServiceNode("data_service")
    requester = RequestNode("data_service")
    responder = ResponseNode()
    
    # Make request
    requester.run(shared)
    # Process request
    service.run(shared)
    # Handle response
    responder.run(shared)
    
    logger.info("Basic communication tests completed!")