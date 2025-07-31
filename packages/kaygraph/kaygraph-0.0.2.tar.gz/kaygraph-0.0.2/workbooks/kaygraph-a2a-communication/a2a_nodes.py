#!/usr/bin/env python3
"""
Agent-to-Agent (A2A) communication nodes for KayGraph.
"""

import asyncio
import json
import logging
import uuid
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set, Callable, Tuple
from datetime import datetime
from enum import Enum
from collections import defaultdict, deque
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import AsyncNode, Node, ValidatedNode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Standard message types."""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    PUBLISH = "publish"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    HEARTBEAT = "heartbeat"
    REGISTER = "register"
    DEREGISTER = "deregister"
    DISCOVER = "discover"
    TASK = "task"
    RESULT = "result"
    ERROR = "error"


class Message:
    """A2A message structure."""
    
    def __init__(self, sender: str, recipient: str, msg_type: MessageType,
                 payload: Dict[str, Any], correlation_id: Optional[str] = None,
                 priority: int = 5, ttl: int = 300):
        self.message_id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.type = msg_type
        self.payload = payload
        self.correlation_id = correlation_id
        self.timestamp = datetime.now()
        self.priority = priority  # 0-10, higher is more important
        self.ttl = ttl  # Time to live in seconds
        self.hops = []  # Track message path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "type": self.type.value,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "ttl": self.ttl,
            "hops": self.hops
        }
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl


class MessageBus:
    """Central message bus for agent communication."""
    
    def __init__(self, max_queue_size: int = 10000):
        self.queues: Dict[str, asyncio.Queue] = {}  # agent_id -> queue
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)  # topic -> subscribers
        self.message_history: deque = deque(maxlen=1000)  # Recent messages
        self.max_queue_size = max_queue_size
        self._lock = asyncio.Lock()
    
    async def register_agent(self, agent_id: str):
        """Register an agent with the message bus."""
        async with self._lock:
            if agent_id not in self.queues:
                self.queues[agent_id] = asyncio.Queue(maxsize=self.max_queue_size)
                logger.info(f"Agent {agent_id} registered with message bus")
    
    async def deregister_agent(self, agent_id: str):
        """Remove an agent from the message bus."""
        async with self._lock:
            if agent_id in self.queues:
                del self.queues[agent_id]
                # Remove from all subscriptions
                for subscribers in self.subscriptions.values():
                    subscribers.discard(agent_id)
                logger.info(f"Agent {agent_id} deregistered from message bus")
    
    async def send_message(self, message: Message):
        """Send a message to recipient(s)."""
        # Add to history
        self.message_history.append(message.to_dict())
        
        # Check if expired
        if message.is_expired():
            logger.warning(f"Message {message.message_id} expired, not sending")
            return
        
        # Handle different recipient types
        if message.recipient == "broadcast":
            # Send to all agents except sender
            for agent_id, queue in self.queues.items():
                if agent_id != message.sender:
                    try:
                        await queue.put(message)
                    except asyncio.QueueFull:
                        logger.error(f"Queue full for agent {agent_id}")
        
        elif message.recipient.startswith("topic:"):
            # Publish to topic subscribers
            topic = message.recipient[6:]  # Remove "topic:" prefix
            subscribers = self.subscriptions.get(topic, set())
            for agent_id in subscribers:
                if agent_id != message.sender and agent_id in self.queues:
                    try:
                        await self.queues[agent_id].put(message)
                    except asyncio.QueueFull:
                        logger.error(f"Queue full for agent {agent_id}")
        
        else:
            # Direct message
            if message.recipient in self.queues:
                try:
                    await self.queues[message.recipient].put(message)
                except asyncio.QueueFull:
                    logger.error(f"Queue full for agent {message.recipient}")
            else:
                logger.warning(f"Agent {message.recipient} not found")
    
    async def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Receive a message for an agent."""
        if agent_id not in self.queues:
            return None
        
        try:
            if timeout:
                message = await asyncio.wait_for(
                    self.queues[agent_id].get(),
                    timeout=timeout
                )
            else:
                message = await self.queues[agent_id].get()
            
            # Add hop
            message.hops.append(agent_id)
            return message
            
        except asyncio.TimeoutError:
            return None
    
    async def subscribe(self, agent_id: str, topic: str):
        """Subscribe an agent to a topic."""
        async with self._lock:
            self.subscriptions[topic].add(agent_id)
            logger.info(f"Agent {agent_id} subscribed to topic {topic}")
    
    async def unsubscribe(self, agent_id: str, topic: str):
        """Unsubscribe an agent from a topic."""
        async with self._lock:
            self.subscriptions[topic].discard(agent_id)
            logger.info(f"Agent {agent_id} unsubscribed from topic {topic}")
    
    def get_queue_size(self, agent_id: str) -> int:
        """Get queue size for an agent."""
        if agent_id in self.queues:
            return self.queues[agent_id].qsize()
        return 0


class AgentRegistry:
    """Registry for agent discovery and metadata."""
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> metadata
        self.capabilities: Dict[str, Set[str]] = defaultdict(set)  # capability -> agents
        self.last_heartbeat: Dict[str, datetime] = {}  # agent_id -> timestamp
        self._lock = asyncio.Lock()
    
    async def register(self, agent_id: str, metadata: Dict[str, Any]):
        """Register an agent."""
        async with self._lock:
            self.agents[agent_id] = metadata
            self.last_heartbeat[agent_id] = datetime.now()
            
            # Index capabilities
            capabilities = metadata.get("capabilities", [])
            for cap in capabilities:
                self.capabilities[cap].add(agent_id)
            
            logger.info(f"Agent {agent_id} registered: {metadata}")
    
    async def deregister(self, agent_id: str):
        """Remove an agent."""
        async with self._lock:
            if agent_id in self.agents:
                # Remove from capabilities
                metadata = self.agents[agent_id]
                for cap in metadata.get("capabilities", []):
                    self.capabilities[cap].discard(agent_id)
                
                del self.agents[agent_id]
                del self.last_heartbeat[agent_id]
                logger.info(f"Agent {agent_id} deregistered")
    
    async def heartbeat(self, agent_id: str):
        """Update agent heartbeat."""
        async with self._lock:
            if agent_id in self.agents:
                self.last_heartbeat[agent_id] = datetime.now()
    
    async def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents with a specific capability."""
        async with self._lock:
            return list(self.capabilities.get(capability, []))
    
    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent metadata."""
        async with self._lock:
            return self.agents.get(agent_id)
    
    async def get_all_agents(self) -> List[str]:
        """Get all registered agents."""
        async with self._lock:
            return list(self.agents.keys())
    
    async def check_health(self, timeout_seconds: int = 120) -> Dict[str, bool]:
        """Check agent health based on heartbeats."""
        now = datetime.now()
        health = {}
        
        async with self._lock:
            for agent_id, last_hb in self.last_heartbeat.items():
                age = (now - last_hb).total_seconds()
                health[agent_id] = age < timeout_seconds
        
        return health


class A2AAgent(ABC):
    """Base class for A2A agents."""
    
    def __init__(self, agent_id: str, message_bus: MessageBus,
                 registry: AgentRegistry, capabilities: List[str] = None):
        self.agent_id = agent_id
        self.message_bus = message_bus
        self.registry = registry
        self.capabilities = capabilities or []
        self.running = False
        self._response_futures: Dict[str, asyncio.Future] = {}  # correlation_id -> future
        self._heartbeat_task = None
        self._message_handler_task = None
    
    async def start(self):
        """Start the agent."""
        # Register with message bus
        await self.message_bus.register_agent(self.agent_id)
        
        # Register with registry
        metadata = {
            "type": self.__class__.__name__,
            "capabilities": self.capabilities,
            "started_at": datetime.now().isoformat()
        }
        await self.registry.register(self.agent_id, metadata)
        
        # Start background tasks
        self.running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._message_handler_task = asyncio.create_task(self._message_handler_loop())
        
        logger.info(f"Agent {self.agent_id} started")
    
    async def stop(self):
        """Stop the agent."""
        self.running = False
        
        # Cancel background tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._message_handler_task:
            self._message_handler_task.cancel()
        
        # Deregister
        await self.registry.deregister(self.agent_id)
        await self.message_bus.deregister_agent(self.agent_id)
        
        logger.info(f"Agent {self.agent_id} stopped")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats."""
        while self.running:
            try:
                await self.registry.heartbeat(self.agent_id)
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def _message_handler_loop(self):
        """Handle incoming messages."""
        while self.running:
            try:
                message = await self.message_bus.receive_message(
                    self.agent_id,
                    timeout=1.0
                )
                
                if message:
                    await self._handle_message(message)
                    
            except Exception as e:
                logger.error(f"Message handler error: {e}")
    
    async def _handle_message(self, message: Message):
        """Route message to appropriate handler."""
        # Handle response messages
        if message.type == MessageType.RESPONSE and message.correlation_id:
            if message.correlation_id in self._response_futures:
                future = self._response_futures.pop(message.correlation_id)
                if not future.done():
                    future.set_result(message)
                return
        
        # Delegate to subclass handler
        await self.handle_message(message)
    
    @abstractmethod
    async def handle_message(self, message: Message):
        """Handle an incoming message (implement in subclass)."""
        pass
    
    async def send_message(self, recipient: str, msg_type: MessageType,
                          payload: Dict[str, Any], **kwargs) -> None:
        """Send a message."""
        message = Message(
            sender=self.agent_id,
            recipient=recipient,
            msg_type=msg_type,
            payload=payload,
            **kwargs
        )
        await self.message_bus.send_message(message)
    
    async def request(self, recipient: str, payload: Dict[str, Any],
                     timeout: float = 30.0) -> Optional[Message]:
        """Send request and wait for response."""
        correlation_id = str(uuid.uuid4())
        
        # Create future for response
        future = asyncio.Future()
        self._response_futures[correlation_id] = future
        
        # Send request
        await self.send_message(
            recipient,
            MessageType.REQUEST,
            payload,
            correlation_id=correlation_id
        )
        
        try:
            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            self._response_futures.pop(correlation_id, None)
            return None
    
    async def reply(self, original_message: Message, payload: Dict[str, Any]):
        """Reply to a message."""
        await self.send_message(
            original_message.sender,
            MessageType.RESPONSE,
            payload,
            correlation_id=original_message.correlation_id
        )
    
    async def broadcast(self, payload: Dict[str, Any], **kwargs):
        """Broadcast message to all agents."""
        await self.send_message("broadcast", MessageType.BROADCAST, payload, **kwargs)
    
    async def publish(self, topic: str, payload: Dict[str, Any], **kwargs):
        """Publish message to a topic."""
        await self.send_message(f"topic:{topic}", MessageType.PUBLISH, payload, **kwargs)
    
    async def subscribe(self, topic: str):
        """Subscribe to a topic."""
        await self.message_bus.subscribe(self.agent_id, topic)
    
    async def unsubscribe(self, topic: str):
        """Unsubscribe from a topic."""
        await self.message_bus.unsubscribe(self.agent_id, topic)


class CoordinatorAgent(A2AAgent):
    """Agent that coordinates work among other agents."""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, registry: AgentRegistry):
        super().__init__(agent_id, message_bus, registry, 
                        capabilities=["coordination", "task_distribution"])
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}  # task_id -> task_info
    
    async def handle_message(self, message: Message):
        """Handle coordination messages."""
        if message.type == MessageType.TASK:
            await self._handle_task_request(message)
        elif message.type == MessageType.RESULT:
            await self._handle_task_result(message)
    
    async def _handle_task_request(self, message: Message):
        """Handle incoming task request."""
        task = message.payload
        task_id = str(uuid.uuid4())
        task_type = task.get("type", "unknown")
        
        # Find capable agent
        capable_agents = await self.registry.find_agents_by_capability(task_type)
        
        if not capable_agents:
            # No capable agent found
            await self.reply(message, {
                "status": "error",
                "error": f"No agent found for task type: {task_type}"
            })
            return
        
        # Select agent (simple round-robin for demo)
        selected_agent = capable_agents[0]
        
        # Store task info
        self.pending_tasks[task_id] = {
            "original_message": message,
            "assigned_to": selected_agent,
            "task": task,
            "assigned_at": datetime.now()
        }
        
        # Delegate task
        await self.send_message(
            selected_agent,
            MessageType.TASK,
            {
                "task_id": task_id,
                "task": task
            }
        )
        
        logger.info(f"Task {task_id} assigned to {selected_agent}")
    
    async def _handle_task_result(self, message: Message):
        """Handle task completion result."""
        task_id = message.payload.get("task_id")
        
        if task_id not in self.pending_tasks:
            logger.warning(f"Unknown task result: {task_id}")
            return
        
        task_info = self.pending_tasks.pop(task_id)
        original_message = task_info["original_message"]
        
        # Forward result to original requester
        await self.reply(original_message, message.payload)
        
        logger.info(f"Task {task_id} completed")


class SpecialistAgent(A2AAgent):
    """Agent specialized in specific tasks."""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, registry: AgentRegistry,
                 specialties: List[str]):
        super().__init__(agent_id, message_bus, registry, capabilities=specialties)
        self.specialties = specialties
    
    async def handle_message(self, message: Message):
        """Handle specialist messages."""
        if message.type == MessageType.TASK:
            await self._handle_task(message)
    
    async def _handle_task(self, message: Message):
        """Process assigned task."""
        task_id = message.payload.get("task_id")
        task = message.payload.get("task", {})
        task_type = task.get("type")
        
        if task_type not in self.specialties:
            # Can't handle this task
            await self.reply(message, {
                "task_id": task_id,
                "status": "error",
                "error": f"Task type {task_type} not in specialties"
            })
            return
        
        # Process task (simulate work)
        logger.info(f"Processing task {task_id} of type {task_type}")
        await asyncio.sleep(2)  # Simulate processing
        
        # Send result
        result = {
            "task_id": task_id,
            "status": "completed",
            "result": f"Processed {task_type} task successfully",
            "processed_by": self.agent_id
        }
        
        await self.send_message(
            message.sender,
            MessageType.RESULT,
            result
        )


class MonitorAgent(A2AAgent):
    """Agent that monitors system health."""
    
    def __init__(self, agent_id: str, message_bus: MessageBus, registry: AgentRegistry):
        super().__init__(agent_id, message_bus, registry, 
                        capabilities=["monitoring", "alerting"])
        self._monitor_task = None
    
    async def start(self):
        """Start monitoring."""
        await super().start()
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        """Stop monitoring."""
        if self._monitor_task:
            self._monitor_task.cancel()
        await super().stop()
    
    async def _monitor_loop(self):
        """Periodic monitoring loop."""
        while self.running:
            try:
                # Check agent health
                health = await self.registry.check_health()
                unhealthy = [agent for agent, is_healthy in health.items() 
                           if not is_healthy]
                
                if unhealthy:
                    # Broadcast alert
                    await self.broadcast({
                        "alert": "unhealthy_agents",
                        "agents": unhealthy,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Check message queues
                all_agents = await self.registry.get_all_agents()
                for agent in all_agents:
                    queue_size = self.message_bus.get_queue_size(agent)
                    if queue_size > 100:  # Threshold
                        await self.publish("alerts", {
                            "alert": "queue_backlog",
                            "agent": agent,
                            "queue_size": queue_size
                        })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
    
    async def handle_message(self, message: Message):
        """Handle monitoring messages."""
        if message.type == MessageType.REQUEST:
            request_type = message.payload.get("type")
            
            if request_type == "system_status":
                # Provide system status
                all_agents = await self.registry.get_all_agents()
                health = await self.registry.check_health()
                
                status = {
                    "total_agents": len(all_agents),
                    "healthy_agents": sum(1 for h in health.values() if h),
                    "agents": all_agents,
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.reply(message, status)


# Example usage
if __name__ == "__main__":
    async def main():
        # Create infrastructure
        message_bus = MessageBus()
        registry = AgentRegistry()
        
        # Create agents
        coordinator = CoordinatorAgent("coordinator", message_bus, registry)
        specialist1 = SpecialistAgent("specialist1", message_bus, registry,
                                    ["data_analysis", "reporting"])
        specialist2 = SpecialistAgent("specialist2", message_bus, registry,
                                    ["nlp_processing", "translation"])
        monitor = MonitorAgent("monitor", message_bus, registry)
        
        # Start all agents
        agents = [coordinator, specialist1, specialist2, monitor]
        for agent in agents:
            await agent.start()
        
        # Subscribe monitor to alerts
        await monitor.subscribe("alerts")
        
        # Simulate task requests
        print("=== Sending task requests ===")
        
        # Request data analysis
        response = await coordinator.request({
            "type": "data_analysis",
            "data": [1, 2, 3, 4, 5]
        }, timeout=10)
        
        if response:
            print(f"Data analysis result: {response.payload}")
        
        # Request NLP processing
        response = await coordinator.request({
            "type": "nlp_processing",
            "text": "Hello world"
        }, timeout=10)
        
        if response:
            print(f"NLP result: {response.payload}")
        
        # Get system status
        response = await monitor.request({
            "type": "system_status"
        }, timeout=5)
        
        if response:
            print(f"System status: {response.payload}")
        
        # Wait a bit for monitoring
        await asyncio.sleep(5)
        
        # Stop all agents
        print("\n=== Stopping agents ===")
        for agent in agents:
            await agent.stop()
    
    # Run example
    asyncio.run(main())