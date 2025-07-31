# KayGraph Basic Communication Pattern

This example demonstrates fundamental communication patterns between nodes in KayGraph workflows. It shows how nodes can exchange messages, share data, and coordinate through the shared store.

## Features

1. **Direct Communication**: Node-to-node message passing
2. **Event Broadcasting**: One-to-many notifications
3. **Request-Response**: Synchronous communication patterns
4. **Data Channels**: Typed message channels
5. **Message Queues**: Buffered communication

## Quick Start

```bash
# Run basic communication examples
python main.py

# Run specific pattern
python main.py --pattern pubsub
```

## Communication Patterns

### 1. Producer-Consumer

```
┌──────────────┐     Queue      ┌──────────────┐
│   Producer   │────────────────▶│   Consumer   │
│     Node     │                 │     Node     │
└──────────────┘                 └──────────────┘
```

Producer generates data, Consumer processes it:
```python
class ProducerNode(Node):
    def exec(self, prep_res):
        return {"data": generate_data()}
    
    def post(self, shared, prep_res, exec_res):
        shared["queue"].append(exec_res["data"])

class ConsumerNode(Node):
    def prep(self, shared):
        return shared["queue"].pop(0) if shared["queue"] else None
```

### 2. Publish-Subscribe

```
                 ┌──────────────┐
                 │ Subscriber A │
                 └──────────────┘
                         ▲
┌──────────────┐         │         ┌──────────────┐
│  Publisher   │─────────┼────────▶│ Subscriber B │
│     Node     │         │         └──────────────┘
└──────────────┘         ▼
                 ┌──────────────┐
                 │ Subscriber C │
                 └──────────────┘
```

Publisher broadcasts to all subscribers:
```python
class PublisherNode(Node):
    def post(self, shared, prep_res, exec_res):
        event = {"type": "data_update", "data": exec_res}
        for subscriber in shared["subscribers"]:
            subscriber.notify(event)
```

### 3. Request-Response

```
┌──────────────┐  Request   ┌──────────────┐
│   Client     │───────────▶│   Server     │
│    Node      │◀───────────│    Node      │
└──────────────┘  Response  └──────────────┘
```

Client requests service from server:
```python
class ClientNode(Node):
    def exec(self, prep_res):
        request_id = str(uuid.uuid4())
        return {"request_id": request_id, "query": "process this"}
    
    def post(self, shared, prep_res, exec_res):
        shared["pending_requests"][exec_res["request_id"]] = exec_res
        return "wait_response"
```

### 4. Pipeline

```
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ Stage1 │───▶│ Stage2 │───▶│ Stage3 │───▶│ Output │
└────────┘    └────────┘    └────────┘    └────────┘
```

Data flows through processing stages:
```python
stage1 >> stage2 >> stage3 >> output
```

### 5. Fan-Out/Fan-In

```
                ┌──────────┐
           ┌───▶│ Worker 1 │───┐
           │    └──────────┘   │
┌────────┐ │    ┌──────────┐   │ ┌────────┐
│Splitter│─┼───▶│ Worker 2 │───┼▶│ Merger │
└────────┘ │    └──────────┘   │ └────────┘
           │    ┌──────────┐   │
           └───▶│ Worker 3 │───┘
                └──────────┘
```

Split work among workers, then merge results.

## Message Types

### 1. Data Message
```python
{
    "type": "data",
    "payload": {...},
    "timestamp": "2024-01-15T10:30:00Z",
    "source": "node_id"
}
```

### 2. Control Message
```python
{
    "type": "control",
    "command": "pause|resume|stop",
    "target": "node_id"
}
```

### 3. Event Message
```python
{
    "type": "event",
    "event_name": "data_ready",
    "data": {...},
    "subscribers": ["node1", "node2"]
}
```

### 4. Error Message
```python
{
    "type": "error",
    "error_code": "E001",
    "message": "Processing failed",
    "source": "node_id",
    "stacktrace": "..."
}
```

## Implementation Examples

### 1. Message Queue
```python
class MessageQueue:
    def __init__(self, max_size=1000):
        self.queue = deque(maxlen=max_size)
        self.subscribers = []
    
    def publish(self, message):
        self.queue.append(message)
        for sub in self.subscribers:
            sub.on_message(message)
    
    def subscribe(self, callback):
        self.subscribers.append(callback)
```

### 2. Event Bus
```python
class EventBus:
    def __init__(self):
        self.handlers = defaultdict(list)
    
    def on(self, event_type, handler):
        self.handlers[event_type].append(handler)
    
    def emit(self, event_type, data):
        for handler in self.handlers[event_type]:
            handler(data)
```

### 3. Channel
```python
class Channel:
    def __init__(self, name):
        self.name = name
        self.messages = asyncio.Queue()
    
    async def send(self, message):
        await self.messages.put(message)
    
    async def receive(self):
        return await self.messages.get()
```

## Shared Store Patterns

### 1. Message Buffer
```python
shared = {
    "messages": {
        "inbox": [],      # Incoming messages
        "outbox": [],     # Outgoing messages
        "processed": []   # Completed messages
    }
}
```

### 2. Channel Registry
```python
shared = {
    "channels": {
        "data": Channel("data"),
        "control": Channel("control"),
        "events": Channel("events")
    }
}
```

### 3. Subscription Map
```python
shared = {
    "subscriptions": {
        "topic1": ["node1", "node2"],
        "topic2": ["node3"],
        "broadcast": ["*"]  # All nodes
    }
}
```

## Advanced Patterns

### 1. Reliable Delivery
```python
class ReliableMessageNode(Node):
    def post(self, shared, prep_res, exec_res):
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "data": exec_res,
            "attempts": 0,
            "max_attempts": 3
        }
        
        shared["pending_messages"][message_id] = message
        return "send_message"
```

### 2. Message Filtering
```python
class FilterNode(Node):
    def __init__(self, filter_func, node_id=None):
        super().__init__(node_id)
        self.filter_func = filter_func
    
    def exec(self, messages):
        return [msg for msg in messages if self.filter_func(msg)]
```

### 3. Message Transformation
```python
class TransformNode(Node):
    def exec(self, message):
        return {
            **message,
            "transformed": True,
            "processed_at": datetime.now()
        }
```

### 4. Message Routing
```python
class RouterNode(Node):
    def post(self, shared, prep_res, exec_res):
        message_type = exec_res.get("type")
        
        if message_type == "urgent":
            return "priority_queue"
        elif message_type == "bulk":
            return "batch_processor"
        else:
            return "normal_queue"
```

## Configuration

```python
COMMUNICATION_CONFIG = {
    "message_queue": {
        "max_size": 10000,
        "overflow_policy": "drop_oldest"  # or "reject_new"
    },
    "channels": {
        "buffer_size": 1000,
        "timeout": 30
    },
    "retry": {
        "max_attempts": 3,
        "backoff": "exponential",
        "base_delay": 1.0
    }
}
```

## Best Practices

1. **Message Size**: Keep messages small and focused
2. **Async First**: Use async patterns for I/O-bound communication
3. **Error Handling**: Always handle communication failures
4. **Buffering**: Use appropriate buffer sizes
5. **Timeouts**: Set reasonable timeouts for all operations
6. **Monitoring**: Track message flow and queue depths
7. **Testing**: Test with message loss and delays

## Use Cases

1. **Data Processing Pipeline**: Stream processing with multiple stages
2. **Event-Driven Architecture**: Loosely coupled components
3. **Task Distribution**: Distribute work among multiple workers
4. **Real-time Updates**: Push notifications to subscribers
5. **Command and Control**: Coordinate distributed components