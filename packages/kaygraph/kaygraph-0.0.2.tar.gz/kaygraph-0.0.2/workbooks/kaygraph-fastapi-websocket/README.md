# KayGraph FastAPI WebSocket Integration

This example demonstrates real-time bidirectional communication between KayGraph workflows and web clients using FastAPI WebSockets.

## Features

1. **Real-time Updates**: Push workflow updates to connected clients
2. **Bidirectional Communication**: Clients can send commands to workflows
3. **Multiple Connections**: Support multiple WebSocket clients
4. **Connection Management**: Handle connect/disconnect gracefully
5. **Message Routing**: Route messages between nodes and clients

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn websockets

# Run the server
python main.py

# Or with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   WebSocket     │◀───▶│   Connection    │◀───▶│   KayGraph      │
│   Clients       │     │   Manager       │     │   Workflows     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                       │                        │
         │                       ▼                        │
         │              ┌─────────────────┐              │
         └──────────────│  Message Router │◀─────────────┘
                        └─────────────────┘
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/workflow');

ws.onopen = () => {
    console.log('Connected to workflow');
};
```

### Message Types

#### Client to Server

```javascript
// Start workflow
ws.send(JSON.stringify({
    type: 'start_workflow',
    workflow: 'chat',
    params: { message: 'Hello' }
}));

// Send node input
ws.send(JSON.stringify({
    type: 'node_input',
    node_id: 'input_node',
    data: { value: 42 }
}));

// Subscribe to updates
ws.send(JSON.stringify({
    type: 'subscribe',
    topics: ['progress', 'results']
}));
```

#### Server to Client

```javascript
// Workflow started
{
    "type": "workflow_started",
    "workflow_id": "abc123",
    "timestamp": "2024-01-15T10:30:00Z"
}

// Node update
{
    "type": "node_update",
    "node_id": "process_node",
    "status": "running",
    "progress": 45.5,
    "message": "Processing data..."
}

// Result available
{
    "type": "result",
    "node_id": "output_node",
    "data": { "answer": "The result is 42" }
}
```

## Usage Examples

### 1. Chat Interface

```python
# Real-time chat with streaming responses
class ChatNode(WebSocketNode):
    async def exec_async(self, message):
        # Stream tokens as they're generated
        async for token in generate_response(message):
            await self.send_update("token", token)
```

### 2. Progress Monitoring

```python
# Monitor long-running workflows
class ProcessingNode(WebSocketNode):
    async def exec_async(self, data):
        total = len(data)
        for i, item in enumerate(data):
            progress = (i + 1) / total * 100
            await self.send_update("progress", {
                "percent": progress,
                "current": i + 1,
                "total": total
            })
```

### 3. Interactive Workflows

```python
# Get user input during workflow
class ApprovalNode(WebSocketNode):
    async def exec_async(self, data):
        # Request approval
        await self.send_update("approval_request", {
            "message": "Approve this action?",
            "options": ["yes", "no"]
        })
        
        # Wait for response
        response = await self.wait_for_input(timeout=60)
        return response
```

## Client Examples

### JavaScript/Browser

```html
<!DOCTYPE html>
<html>
<head>
    <title>KayGraph WebSocket Client</title>
</head>
<body>
    <div id="messages"></div>
    <input type="text" id="input" placeholder="Enter message">
    <button onclick="sendMessage()">Send</button>
    
    <script>
        const ws = new WebSocket('ws://localhost:8000/ws/chat');
        const messages = document.getElementById('messages');
        
        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            messages.innerHTML += `<p>${msg.type}: ${JSON.stringify(msg.data)}</p>`;
        };
        
        function sendMessage() {
            const input = document.getElementById('input');
            ws.send(JSON.stringify({
                type: 'message',
                content: input.value
            }));
            input.value = '';
        }
    </script>
</body>
</html>
```

### Python Client

```python
import asyncio
import websockets
import json

async def client():
    async with websockets.connect('ws://localhost:8000/ws/workflow') as ws:
        # Start workflow
        await ws.send(json.dumps({
            'type': 'start_workflow',
            'workflow': 'data_processing',
            'params': {'data': [1, 2, 3, 4, 5]}
        }))
        
        # Listen for updates
        async for message in ws:
            data = json.loads(message)
            print(f"Received: {data['type']} - {data.get('data')}")
            
            if data['type'] == 'workflow_completed':
                break

asyncio.run(client())
```

## Advanced Features

### 1. Connection Groups

```python
# Broadcast to multiple clients
manager.broadcast_to_group("admins", {
    "type": "system_alert",
    "message": "High CPU usage detected"
})
```

### 2. Authentication

```python
@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Verify token
    user = await verify_token(token)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
```

### 3. Rate Limiting

```python
# Limit message frequency
rate_limiter = RateLimiter(max_messages=100, window=60)

if not await rate_limiter.check(client_id):
    await websocket.send_json({
        "type": "error",
        "message": "Rate limit exceeded"
    })
```

### 4. Message Queuing

```python
# Queue messages for offline clients
offline_queue = MessageQueue()

if not client.is_connected:
    await offline_queue.add(client_id, message)
else:
    await client.send(message)
```

## Configuration

```python
# config.py
WEBSOCKET_CONFIG = {
    "max_connections": 1000,
    "ping_interval": 30,
    "ping_timeout": 10,
    "max_message_size": 1024 * 1024,  # 1MB
    "compression": "deflate",
    "origins": ["http://localhost:3000"],  # CORS
}
```

## Error Handling

```python
try:
    await websocket.accept()
    await handle_connection(websocket)
except WebSocketDisconnect:
    logger.info(f"Client {client_id} disconnected")
except Exception as e:
    logger.error(f"WebSocket error: {e}")
    await websocket.close(code=1011, reason="Internal error")
```

## Monitoring

### Connection Metrics

```python
@app.get("/ws/metrics")
async def websocket_metrics():
    return {
        "active_connections": manager.connection_count(),
        "total_messages": manager.message_count(),
        "uptime": manager.uptime(),
        "clients": manager.list_clients()
    }
```

### Health Check

```python
@app.get("/ws/health")
async def websocket_health():
    return {
        "status": "healthy",
        "connections": manager.connection_count(),
        "max_connections": WEBSOCKET_CONFIG["max_connections"]
    }
```

## Deployment Considerations

### 1. Load Balancing

Use sticky sessions or Redis pub/sub for multi-server deployments:

```python
# Use Redis for cross-server communication
redis_client = redis.Redis()
pubsub = redis_client.pubsub()
```

### 2. SSL/TLS

```nginx
# Nginx configuration
location /ws {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_ssl_verify off;
}
```

### 3. Scaling

- Use connection pooling
- Implement backpressure handling
- Monitor memory usage
- Set appropriate timeouts

## Best Practices

1. **Message Format**: Use consistent JSON schema
2. **Error Recovery**: Implement reconnection logic
3. **State Management**: Keep client state minimal
4. **Security**: Always validate and sanitize inputs
5. **Performance**: Batch updates when possible