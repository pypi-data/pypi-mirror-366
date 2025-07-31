#!/usr/bin/env python3
"""
WebSocket nodes for real-time communication in KayGraph.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import AsyncNode, ValidatedNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, Any] = {}  # client_id -> websocket
        self.client_metadata: Dict[str, Dict[str, Any]] = {}  # client_id -> metadata
        self.groups: Dict[str, Set[str]] = defaultdict(set)  # group -> client_ids
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # topic -> client_ids
        self._lock = asyncio.Lock()
        self._message_count = 0
        self._start_time = datetime.now()
    
    async def connect(self, client_id: str, websocket: Any, 
                     metadata: Optional[Dict[str, Any]] = None):
        """Register a new connection."""
        async with self._lock:
            self.active_connections[client_id] = websocket
            self.client_metadata[client_id] = metadata or {}
            self.client_metadata[client_id]["connected_at"] = datetime.now()
            
        logger.info(f"Client {client_id} connected")
    
    async def disconnect(self, client_id: str):
        """Remove a connection."""
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                del self.client_metadata[client_id]
                
                # Remove from all groups
                for group in list(self.groups.values()):
                    group.discard(client_id)
                
                # Remove from all subscriptions
                for subscribers in list(self.subscriptions.values()):
                    subscribers.discard(client_id)
        
        logger.info(f"Client {client_id} disconnected")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client."""
        async with self._lock:
            websocket = self.active_connections.get(client_id)
        
        if websocket:
            try:
                await websocket.send_json(message)
                self._message_count += 1
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[str] = None):
        """Broadcast message to all connected clients."""
        disconnected = []
        
        async with self._lock:
            clients = list(self.active_connections.items())
        
        for client_id, websocket in clients:
            if client_id != exclude:
                try:
                    await websocket.send_json(message)
                    self._message_count += 1
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)
    
    async def add_to_group(self, client_id: str, group: str):
        """Add client to a group."""
        async with self._lock:
            self.groups[group].add(client_id)
        logger.info(f"Client {client_id} added to group {group}")
    
    async def remove_from_group(self, client_id: str, group: str):
        """Remove client from a group."""
        async with self._lock:
            self.groups[group].discard(client_id)
    
    async def broadcast_to_group(self, group: str, message: Dict[str, Any]):
        """Broadcast message to all clients in a group."""
        async with self._lock:
            client_ids = list(self.groups.get(group, []))
        
        for client_id in client_ids:
            await self.send_personal_message(message, client_id)
    
    async def subscribe(self, client_id: str, topic: str):
        """Subscribe client to a topic."""
        async with self._lock:
            self.subscriptions[topic].add(client_id)
        logger.info(f"Client {client_id} subscribed to {topic}")
    
    async def unsubscribe(self, client_id: str, topic: str):
        """Unsubscribe client from a topic."""
        async with self._lock:
            self.subscriptions[topic].discard(client_id)
    
    async def publish(self, topic: str, message: Dict[str, Any]):
        """Publish message to all subscribers of a topic."""
        async with self._lock:
            client_ids = list(self.subscriptions.get(topic, []))
        
        message["topic"] = topic
        for client_id in client_ids:
            await self.send_personal_message(message, client_id)
    
    def connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)
    
    def message_count(self) -> int:
        """Get total messages sent."""
        return self._message_count
    
    def uptime(self) -> float:
        """Get uptime in seconds."""
        return (datetime.now() - self._start_time).total_seconds()
    
    def list_clients(self) -> List[Dict[str, Any]]:
        """List all connected clients."""
        clients = []
        for client_id, metadata in self.client_metadata.items():
            clients.append({
                "client_id": client_id,
                "connected_at": metadata.get("connected_at", "").isoformat() if metadata.get("connected_at") else None,
                "groups": [g for g, members in self.groups.items() if client_id in members],
                "subscriptions": [t for t, subs in self.subscriptions.items() if client_id in subs]
            })
        return clients


class WebSocketNode(AsyncNode):
    """Base node for WebSocket communication."""
    
    def __init__(self, manager: ConnectionManager, node_id: str = None):
        super().__init__(node_id or "websocket_node")
        self.manager = manager
        self.client_id = None
        self.input_queue = asyncio.Queue()
    
    async def send_update(self, update_type: str, data: Any, 
                         client_id: Optional[str] = None):
        """Send update to client(s)."""
        message = {
            "type": update_type,
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        if client_id:
            await self.manager.send_personal_message(message, client_id)
        elif self.client_id:
            await self.manager.send_personal_message(message, self.client_id)
        else:
            await self.manager.broadcast(message)
    
    async def wait_for_input(self, timeout: Optional[float] = None) -> Any:
        """Wait for input from client."""
        try:
            if timeout:
                return await asyncio.wait_for(
                    self.input_queue.get(),
                    timeout=timeout
                )
            else:
                return await self.input_queue.get()
        except asyncio.TimeoutError:
            return None
    
    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare WebSocket communication."""
        self.client_id = shared.get("client_id")
        return {
            "client_id": self.client_id,
            "workflow_id": shared.get("workflow_id", str(uuid.uuid4()))
        }
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WebSocket communication (override in subclasses)."""
        # Send workflow started message
        await self.send_update("workflow_started", {
            "workflow_id": prep_res["workflow_id"]
        })
        
        # Default implementation
        await asyncio.sleep(1)
        
        return {"status": "completed"}
    
    async def post_async(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
                        exec_res: Dict[str, Any]) -> Optional[str]:
        """Complete WebSocket communication."""
        # Send completion message
        await self.send_update("workflow_completed", {
            "workflow_id": prep_res["workflow_id"],
            "result": exec_res
        })
        
        shared["websocket_result"] = exec_res
        return None


class ChatWebSocketNode(WebSocketNode):
    """WebSocket node for chat interactions."""
    
    def __init__(self, manager: ConnectionManager, system_prompt: str = None,
                 node_id: str = None):
        super().__init__(manager, node_id or "chat_websocket")
        self.system_prompt = system_prompt or "I'm a helpful assistant."
        self.conversation_history = []
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat conversation via WebSocket."""
        client_id = prep_res["client_id"]
        
        # Send welcome message
        await self.send_update("chat_ready", {
            "message": "Chat session started. Send your messages!",
            "system": self.system_prompt
        })
        
        # Chat loop
        while True:
            # Wait for user message
            user_input = await self.wait_for_input(timeout=300)  # 5 min timeout
            
            if not user_input:
                await self.send_update("timeout", {
                    "message": "Session timed out due to inactivity"
                })
                break
            
            if user_input.get("type") == "end_chat":
                break
            
            if user_input.get("type") == "message":
                user_message = user_input.get("content", "")
                
                # Add to history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_message
                })
                
                # Simulate streaming response
                await self.send_update("typing", {"status": True})
                
                # Generate response (mock)
                response = f"You said: '{user_message}'. This is a mock response."
                
                # Stream tokens
                words = response.split()
                for i, word in enumerate(words):
                    await self.send_update("token", {
                        "token": word + " ",
                        "position": i
                    })
                    await asyncio.sleep(0.1)  # Simulate typing delay
                
                # Send complete message
                await self.send_update("message", {
                    "role": "assistant",
                    "content": response
                })
                
                await self.send_update("typing", {"status": False})
                
                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
        
        return {
            "messages_exchanged": len(self.conversation_history),
            "conversation": self.conversation_history
        }


class ProgressWebSocketNode(WebSocketNode):
    """WebSocket node for progress tracking."""
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with progress updates."""
        client_id = prep_res["client_id"]
        
        # Get task parameters
        task_data = prep_res.get("task_data", {})
        items = task_data.get("items", list(range(10)))
        
        # Process items with progress
        results = []
        total = len(items)
        
        for i, item in enumerate(items):
            # Send progress update
            progress = ((i + 1) / total) * 100
            await self.send_update("progress", {
                "percent": progress,
                "current": i + 1,
                "total": total,
                "message": f"Processing item {i + 1} of {total}"
            })
            
            # Simulate processing
            await asyncio.sleep(0.5)
            results.append(f"Processed: {item}")
            
            # Send item completed
            await self.send_update("item_completed", {
                "item": item,
                "result": results[-1]
            })
        
        return {
            "items_processed": len(results),
            "results": results
        }


class InteractiveWebSocketNode(WebSocketNode):
    """WebSocket node for interactive workflows."""
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute interactive workflow."""
        client_id = prep_res["client_id"]
        workflow_data = prep_res.get("workflow_data", {})
        
        # Step 1: Initial data
        await self.send_update("step", {
            "number": 1,
            "title": "Review Data",
            "description": "Please review the following data",
            "data": workflow_data
        })
        
        # Request confirmation
        await self.send_update("input_request", {
            "type": "confirmation",
            "message": "Do you approve this data?",
            "options": ["approve", "reject", "modify"]
        })
        
        # Wait for response
        response = await self.wait_for_input(timeout=60)
        
        if not response:
            return {"status": "timeout", "step": 1}
        
        action = response.get("action", "reject")
        
        if action == "modify":
            # Request modifications
            await self.send_update("input_request", {
                "type": "form",
                "message": "Please provide modifications",
                "fields": [
                    {"name": "field1", "type": "text", "label": "Field 1"},
                    {"name": "field2", "type": "number", "label": "Field 2"}
                ]
            })
            
            modifications = await self.wait_for_input(timeout=120)
            if modifications:
                workflow_data.update(modifications.get("data", {}))
        
        elif action == "reject":
            return {"status": "rejected", "step": 1}
        
        # Step 2: Processing
        await self.send_update("step", {
            "number": 2,
            "title": "Processing",
            "description": "Processing approved data"
        })
        
        # Simulate processing with updates
        for i in range(5):
            await self.send_update("processing", {
                "stage": f"Stage {i + 1}/5",
                "progress": (i + 1) * 20
            })
            await asyncio.sleep(0.5)
        
        # Step 3: Results
        results = {
            "processed_data": workflow_data,
            "metrics": {
                "items_processed": 10,
                "success_rate": 0.95,
                "duration": 2.5
            }
        }
        
        await self.send_update("step", {
            "number": 3,
            "title": "Results",
            "description": "Processing complete",
            "data": results
        })
        
        return {
            "status": "completed",
            "action": action,
            "results": results
        }


class BroadcastWebSocketNode(WebSocketNode):
    """WebSocket node for broadcasting to multiple clients."""
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast updates to all connected clients."""
        broadcast_data = prep_res.get("broadcast_data", {})
        message_type = broadcast_data.get("type", "announcement")
        content = broadcast_data.get("content", "")
        
        # Broadcast to all
        await self.manager.broadcast({
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "source": self.node_id
        })
        
        # Broadcast to specific groups if specified
        groups = broadcast_data.get("groups", [])
        for group in groups:
            await self.manager.broadcast_to_group(group, {
                "type": f"{message_type}_group",
                "content": content,
                "group": group,
                "timestamp": datetime.now().isoformat()
            })
        
        # Publish to topics if specified
        topics = broadcast_data.get("topics", [])
        for topic in topics:
            await self.manager.publish(topic, {
                "type": f"{message_type}_topic",
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "broadcast_sent": True,
            "recipients": {
                "all": self.manager.connection_count(),
                "groups": groups,
                "topics": topics
            }
        }


class CollaborativeWebSocketNode(WebSocketNode):
    """WebSocket node for collaborative workflows."""
    
    def __init__(self, manager: ConnectionManager, min_participants: int = 2,
                 node_id: str = None):
        super().__init__(manager, node_id or "collaborative_websocket")
        self.min_participants = min_participants
        self.participants = {}
        self.votes = {}
        self.shared_state = {}
    
    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute collaborative workflow."""
        session_id = prep_res["workflow_id"]
        
        # Wait for minimum participants
        await self.manager.broadcast({
            "type": "session_created",
            "session_id": session_id,
            "min_participants": self.min_participants,
            "message": f"Waiting for {self.min_participants} participants..."
        })
        
        # Simulate waiting for participants (in real app, would track joins)
        await asyncio.sleep(2)
        
        # Collaborative editing phase
        await self.manager.broadcast({
            "type": "collaboration_start",
            "session_id": session_id,
            "phase": "editing",
            "shared_document": {
                "title": "Collaborative Document",
                "content": "Initial content",
                "version": 1
            }
        })
        
        # Simulate collaborative edits
        edits = []
        for i in range(3):
            edit = {
                "user": f"user_{i}",
                "operation": "insert",
                "position": i * 10,
                "text": f" Edit {i}"
            }
            edits.append(edit)
            
            # Broadcast edit to all participants
            await self.manager.broadcast({
                "type": "edit",
                "session_id": session_id,
                "edit": edit
            })
            
            await asyncio.sleep(0.5)
        
        # Voting phase
        await self.manager.broadcast({
            "type": "phase_change",
            "session_id": session_id,
            "phase": "voting",
            "message": "Please vote to approve the changes"
        })
        
        # Simulate vote collection (in real app, would wait for actual votes)
        await asyncio.sleep(2)
        
        votes = {
            "approve": 2,
            "reject": 0,
            "abstain": 1
        }
        
        # Broadcast results
        await self.manager.broadcast({
            "type": "voting_complete",
            "session_id": session_id,
            "results": votes,
            "outcome": "approved" if votes["approve"] > votes["reject"] else "rejected"
        })
        
        return {
            "session_id": session_id,
            "participants": 3,
            "edits_made": len(edits),
            "voting_results": votes,
            "final_outcome": "approved"
        }


# Example usage
if __name__ == "__main__":
    async def main():
        # Create connection manager
        manager = ConnectionManager()
        
        # Simulate WebSocket connections
        class MockWebSocket:
            async def send_json(self, data):
                print(f"Sending: {json.dumps(data, indent=2)}")
        
        # Connect some clients
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        
        await manager.connect("client1", ws1, {"user": "alice"})
        await manager.connect("client2", ws2, {"user": "bob"})
        
        # Test chat node
        print("=== Testing Chat WebSocket Node ===")
        chat_node = ChatWebSocketNode(manager)
        shared = {"client_id": "client1"}
        
        # Simulate chat (would normally get real input)
        chat_node.input_queue.put_nowait({"type": "message", "content": "Hello!"})
        chat_node.input_queue.put_nowait({"type": "end_chat"})
        
        result = await chat_node.run_async(shared)
        print(f"Chat result: {result}")
        
        # Test progress node
        print("\n=== Testing Progress WebSocket Node ===")
        progress_node = ProgressWebSocketNode(manager)
        shared = {
            "client_id": "client2",
            "task_data": {"items": ["A", "B", "C"]}
        }
        
        result = await progress_node.run_async(shared)
        print(f"Progress result: {result}")
        
        # Test broadcast node
        print("\n=== Testing Broadcast WebSocket Node ===")
        broadcast_node = BroadcastWebSocketNode(manager)
        shared = {
            "broadcast_data": {
                "type": "announcement",
                "content": "System maintenance in 10 minutes"
            }
        }
        
        result = await broadcast_node.run_async(shared)
        print(f"Broadcast result: {result}")
        
        # Show manager stats
        print(f"\nManager stats:")
        print(f"  Connections: {manager.connection_count()}")
        print(f"  Messages sent: {manager.message_count()}")
        print(f"  Clients: {manager.list_clients()}")
    
    # Run example
    asyncio.run(main())