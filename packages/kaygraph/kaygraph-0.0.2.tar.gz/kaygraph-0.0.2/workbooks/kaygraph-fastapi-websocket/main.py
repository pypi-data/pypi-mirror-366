#!/usr/bin/env python3
"""
FastAPI WebSocket integration with KayGraph workflows.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from contextlib import asynccontextmanager

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, AsyncGraph
from websocket_nodes import (
    ConnectionManager, ChatWebSocketNode, ProgressWebSocketNode,
    InteractiveWebSocketNode, BroadcastWebSocketNode, CollaborativeWebSocketNode
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection manager
manager = ConnectionManager()


# Mock FastAPI (in production, use real FastAPI)
class MockFastAPI:
    """Mock FastAPI for demonstration."""
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.routes = []
    
    def websocket(self, path: str):
        def decorator(func):
            self.routes.append(("WS", path, func))
            logger.info(f"WebSocket route registered: {path}")
            return func
        return decorator
    
    def get(self, path: str, **kwargs):
        def decorator(func):
            self.routes.append(("GET", path, func))
            return func
        return decorator


class MockWebSocket:
    """Mock WebSocket for demonstration."""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.accepted = False
        self.closed = False
    
    async def accept(self):
        self.accepted = True
        logger.info(f"WebSocket {self.client_id} accepted")
    
    async def send_text(self, data: str):
        if not self.closed:
            logger.info(f"WS {self.client_id} << {data[:100]}...")
    
    async def send_json(self, data: dict):
        if not self.closed:
            await self.send_text(json.dumps(data))
    
    async def receive_text(self) -> str:
        # Simulate receiving text
        await asyncio.sleep(1)
        return '{"type": "ping"}'
    
    async def receive_json(self) -> dict:
        text = await self.receive_text()
        return json.loads(text)
    
    async def close(self, code: int = 1000, reason: str = ""):
        self.closed = True
        logger.info(f"WebSocket {self.client_id} closed: {code} - {reason}")


# Create FastAPI app
app = MockFastAPI()


# WebSocket endpoints

@app.websocket("/ws/chat")
async def chat_websocket_endpoint(websocket: MockWebSocket):
    """Chat WebSocket endpoint."""
    client_id = f"chat_{id(websocket)}"
    
    try:
        await websocket.accept()
        await manager.connect(client_id, websocket, {"type": "chat"})
        
        # Create chat node
        chat_node = ChatWebSocketNode(
            manager,
            system_prompt="I'm KayGraph Chat Assistant. How can I help you?"
        )
        
        # Create graph
        graph = AsyncGraph(start=chat_node)
        
        # Handle incoming messages
        async def message_handler():
            while True:
                try:
                    data = await websocket.receive_json()
                    
                    if data.get("type") == "message":
                        # Add message to node's input queue
                        await chat_node.input_queue.put(data)
                    elif data.get("type") == "end_chat":
                        await chat_node.input_queue.put(data)
                        break
                    
                except Exception as e:
                    logger.error(f"Message handler error: {e}")
                    break
        
        # Start message handler
        handler_task = asyncio.create_task(message_handler())
        
        # Run the chat workflow
        shared = {"client_id": client_id}
        await graph.run_async(shared)
        
        # Cancel handler
        handler_task.cancel()
        
    except Exception as e:
        logger.error(f"Chat WebSocket error: {e}")
    
    finally:
        await manager.disconnect(client_id)


@app.websocket("/ws/progress/{task_id}")
async def progress_websocket_endpoint(websocket: MockWebSocket, task_id: str):
    """Progress tracking WebSocket endpoint."""
    client_id = f"progress_{task_id}"
    
    try:
        await websocket.accept()
        await manager.connect(client_id, websocket, {"task_id": task_id})
        
        # Create progress node
        progress_node = ProgressWebSocketNode(manager)
        
        # Create graph
        graph = AsyncGraph(start=progress_node)
        
        # Run progress workflow
        shared = {
            "client_id": client_id,
            "task_data": {
                "items": [f"item_{i}" for i in range(10)]
            }
        }
        
        await graph.run_async(shared)
        
    except Exception as e:
        logger.error(f"Progress WebSocket error: {e}")
    
    finally:
        await manager.disconnect(client_id)


@app.websocket("/ws/interactive")
async def interactive_websocket_endpoint(websocket: MockWebSocket):
    """Interactive workflow WebSocket endpoint."""
    client_id = f"interactive_{id(websocket)}"
    
    try:
        await websocket.accept()
        await manager.connect(client_id, websocket, {"type": "interactive"})
        
        # Create interactive node
        interactive_node = InteractiveWebSocketNode(manager)
        
        # Create graph
        graph = AsyncGraph(start=interactive_node)
        
        # Handle incoming responses
        async def response_handler():
            while True:
                try:
                    data = await websocket.receive_json()
                    await interactive_node.input_queue.put(data)
                    
                    if data.get("type") == "complete":
                        break
                        
                except Exception as e:
                    logger.error(f"Response handler error: {e}")
                    break
        
        # Start response handler
        handler_task = asyncio.create_task(response_handler())
        
        # Run interactive workflow
        shared = {
            "client_id": client_id,
            "workflow_data": {
                "project": "Example Project",
                "budget": 10000,
                "timeline": "3 months"
            }
        }
        
        await graph.run_async(shared)
        
        # Cancel handler
        handler_task.cancel()
        
    except Exception as e:
        logger.error(f"Interactive WebSocket error: {e}")
    
    finally:
        await manager.disconnect(client_id)


@app.websocket("/ws/broadcast")
async def broadcast_websocket_endpoint(websocket: MockWebSocket):
    """Broadcast WebSocket endpoint for receiving updates."""
    client_id = f"broadcast_{id(websocket)}"
    
    try:
        await websocket.accept()
        await manager.connect(client_id, websocket, {"type": "broadcast_receiver"})
        
        # Handle subscription requests
        while True:
            try:
                data = await websocket.receive_json()
                
                if data.get("type") == "subscribe":
                    topics = data.get("topics", [])
                    for topic in topics:
                        await manager.subscribe(client_id, topic)
                    
                    await websocket.send_json({
                        "type": "subscribed",
                        "topics": topics
                    })
                
                elif data.get("type") == "unsubscribe":
                    topics = data.get("topics", [])
                    for topic in topics:
                        await manager.unsubscribe(client_id, topic)
                    
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "topics": topics
                    })
                
                elif data.get("type") == "join_group":
                    group = data.get("group")
                    if group:
                        await manager.add_to_group(client_id, group)
                        await websocket.send_json({
                            "type": "joined_group",
                            "group": group
                        })
                
                elif data.get("type") == "disconnect":
                    break
                    
            except Exception as e:
                logger.error(f"Broadcast receiver error: {e}")
                break
        
    except Exception as e:
        logger.error(f"Broadcast WebSocket error: {e}")
    
    finally:
        await manager.disconnect(client_id)


@app.websocket("/ws/collaborate/{session_id}")
async def collaborative_websocket_endpoint(websocket: MockWebSocket, session_id: str):
    """Collaborative workflow WebSocket endpoint."""
    client_id = f"collab_{id(websocket)}_{session_id}"
    
    try:
        await websocket.accept()
        await manager.connect(client_id, websocket, {
            "type": "collaborative",
            "session_id": session_id
        })
        
        # Add to session group
        await manager.add_to_group(client_id, f"session_{session_id}")
        
        # For demo, just keep connection open and relay messages
        while True:
            try:
                data = await websocket.receive_json()
                
                # Broadcast to session group
                await manager.broadcast_to_group(
                    f"session_{session_id}",
                    {
                        "type": "collaborative_update",
                        "from": client_id,
                        "data": data
                    }
                )
                
                if data.get("type") == "leave_session":
                    break
                    
            except Exception as e:
                logger.error(f"Collaborative handler error: {e}")
                break
        
    except Exception as e:
        logger.error(f"Collaborative WebSocket error: {e}")
    
    finally:
        await manager.remove_from_group(client_id, f"session_{session_id}")
        await manager.disconnect(client_id)


# HTTP endpoints for management

@app.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket statistics."""
    return {
        "active_connections": manager.connection_count(),
        "total_messages": manager.message_count(),
        "uptime_seconds": manager.uptime(),
        "clients": manager.list_clients()
    }


@app.get("/ws/broadcast/send")
async def send_broadcast(message: str, topic: Optional[str] = None):
    """Send a broadcast message."""
    broadcast_node = BroadcastWebSocketNode(manager)
    
    shared = {
        "broadcast_data": {
            "type": "announcement",
            "content": message,
            "topics": [topic] if topic else []
        }
    }
    
    graph = AsyncGraph(start=broadcast_node)
    await graph.run_async(shared)
    
    return {
        "status": "broadcast_sent",
        "recipients": manager.connection_count()
    }


# Example client HTML
CLIENT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>KayGraph WebSocket Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .chat-box { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin: 10px 0; }
        .input-group { display: flex; gap: 10px; margin: 10px 0; }
        input { flex: 1; padding: 5px; }
        button { padding: 5px 15px; cursor: pointer; }
        .message { margin: 5px 0; }
        .user { color: blue; }
        .assistant { color: green; }
        .system { color: gray; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>KayGraph WebSocket Demo</h1>
        
        <h2>Chat Interface</h2>
        <div id="chatBox" class="chat-box"></div>
        <div class="input-group">
            <input type="text" id="chatInput" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
            <button onclick="connectChat()">Connect</button>
            <button onclick="disconnectChat()">Disconnect</button>
        </div>
        
        <h2>Progress Tracking</h2>
        <div id="progressBox" class="chat-box"></div>
        <div class="input-group">
            <button onclick="startProgress()">Start Task</button>
        </div>
    </div>
    
    <script>
        let chatWs = null;
        let progressWs = null;
        
        function connectChat() {
            if (chatWs) return;
            
            chatWs = new WebSocket('ws://localhost:8000/ws/chat');
            
            chatWs.onopen = () => {
                addChatMessage('Connected to chat', 'system');
            };
            
            chatWs.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'message') {
                    addChatMessage(data.data.content, data.data.role);
                } else if (data.type === 'token') {
                    // Handle streaming tokens
                    appendToLastMessage(data.data.token);
                } else if (data.type === 'chat_ready') {
                    addChatMessage(data.data.message, 'system');
                }
            };
            
            chatWs.onerror = (error) => {
                addChatMessage('Connection error', 'system');
            };
            
            chatWs.onclose = () => {
                addChatMessage('Disconnected from chat', 'system');
                chatWs = null;
            };
        }
        
        function disconnectChat() {
            if (chatWs) {
                chatWs.send(JSON.stringify({type: 'end_chat'}));
                chatWs.close();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (message && chatWs && chatWs.readyState === WebSocket.OPEN) {
                chatWs.send(JSON.stringify({
                    type: 'message',
                    content: message
                }));
                addChatMessage(message, 'user');
                input.value = '';
            }
        }
        
        function addChatMessage(message, role) {
            const chatBox = document.getElementById('chatBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            messageDiv.textContent = `${role}: ${message}`;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function appendToLastMessage(token) {
            const chatBox = document.getElementById('chatBox');
            const messages = chatBox.getElementsByClassName('message');
            if (messages.length > 0) {
                const lastMessage = messages[messages.length - 1];
                if (lastMessage.classList.contains('assistant')) {
                    lastMessage.textContent += token;
                } else {
                    addChatMessage(token, 'assistant');
                }
            }
        }
        
        function startProgress() {
            if (progressWs) progressWs.close();
            
            const taskId = 'task_' + Date.now();
            progressWs = new WebSocket(`ws://localhost:8000/ws/progress/${taskId}`);
            
            progressWs.onopen = () => {
                addProgressMessage('Connected to progress tracker', 'system');
            };
            
            progressWs.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'progress') {
                    addProgressMessage(
                        `Progress: ${data.data.percent.toFixed(1)}% - ${data.data.message}`,
                        'info'
                    );
                } else if (data.type === 'workflow_completed') {
                    addProgressMessage('Task completed!', 'success');
                }
            };
            
            progressWs.onerror = (error) => {
                addProgressMessage('Connection error', 'error');
            };
            
            progressWs.onclose = () => {
                addProgressMessage('Disconnected', 'system');
                progressWs = null;
            };
        }
        
        function addProgressMessage(message, type) {
            const progressBox = document.getElementById('progressBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            progressBox.appendChild(messageDiv);
            progressBox.scrollTop = progressBox.scrollHeight;
        }
        
        // Auto-connect chat on load
        window.onload = () => {
            connectChat();
        };
    </script>
</body>
</html>
"""


@app.get("/")
async def serve_client():
    """Serve the demo client."""
    return {"html": CLIENT_HTML, "message": "Copy the HTML to a file and open in browser"}


# Main entry point
if __name__ == "__main__":
    async def run_server():
        """Run the mock WebSocket server."""
        logger.info("Starting KayGraph WebSocket server...")
        logger.info("Demo client available at http://localhost:8000/")
        
        # Log registered routes
        for method, path, handler in app.routes:
            logger.info(f"  {method} {path} -> {handler.__name__}")
        
        # Simulate some WebSocket connections
        logger.info("\nSimulating WebSocket connections...")
        
        # Chat connection
        chat_ws = MockWebSocket("chat_demo")
        await chat_websocket_endpoint(chat_ws)
        
        # Progress connection
        progress_ws = MockWebSocket("progress_demo")
        await progress_websocket_endpoint(progress_ws, "task_123")
        
        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
    
    # Run the server
    asyncio.run(run_server())