"""
Message queue and communication utilities for multi-agent system.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Message structure for agent communication."""
    from_agent: str
    to_agent: str
    message_type: str
    content: Any
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return asdict(self)


class MessageQueue:
    """Simple async message queue for agent communication."""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def send_message(self, message: Message):
        """Add message to queue."""
        async with self.lock:
            self.messages.append(message)
            self.logger.info(f"Message sent: {message.from_agent} -> {message.to_agent} "
                           f"(type: {message.message_type})")
    
    async def get_messages_for_agent(self, agent_id: str) -> List[Message]:
        """Get all pending messages for an agent."""
        async with self.lock:
            agent_messages = [
                msg for msg in self.messages 
                if msg.to_agent == agent_id or msg.to_agent == "all"
            ]
            
            # Remove retrieved messages from queue
            self.messages = [
                msg for msg in self.messages 
                if msg not in agent_messages
            ]
            
            if agent_messages:
                self.logger.info(f"Retrieved {len(agent_messages)} messages for {agent_id}")
            
            return agent_messages
    
    async def broadcast_message(self, from_agent: str, message_type: str, content: Any):
        """Send message to all agents."""
        message = Message(
            from_agent=from_agent,
            to_agent="all",
            message_type=message_type,
            content=content
        )
        await self.send_message(message)
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self.messages)
    
    def clear(self):
        """Clear all messages."""
        self.messages.clear()
        self.logger.info("Message queue cleared")


class SharedWorkspace:
    """Shared workspace for agent collaboration."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def write(self, key: str, value: Any, agent_id: str):
        """Write data to shared workspace."""
        async with self.lock:
            self.data[key] = {
                "value": value,
                "written_by": agent_id,
                "timestamp": time.time()
            }
            self.logger.info(f"{agent_id} wrote to workspace: {key}")
    
    async def read(self, key: str) -> Optional[Any]:
        """Read data from shared workspace."""
        async with self.lock:
            if key in self.data:
                return self.data[key]["value"]
            return None
    
    async def read_with_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Read data with metadata."""
        async with self.lock:
            return self.data.get(key)
    
    async def list_keys(self) -> List[str]:
        """List all keys in workspace."""
        async with self.lock:
            return list(self.data.keys())
    
    def clear(self):
        """Clear workspace."""
        self.data.clear()
        self.logger.info("Workspace cleared")


def create_task_assignment(task_type: str, task_data: Dict[str, Any]) -> Message:
    """Create a task assignment message."""
    return Message(
        from_agent="supervisor",
        to_agent=f"{task_type}_agent",
        message_type=f"assign_{task_type}",
        content=task_data
    )


def create_completion_message(agent_id: str, result: Any) -> Message:
    """Create a task completion message."""
    return Message(
        from_agent=agent_id,
        to_agent="supervisor",
        message_type="task_complete",
        content={
            "agent": agent_id,
            "result": result,
            "completion_time": time.time()
        }
    )


if __name__ == "__main__":
    # Test messaging system
    import asyncio
    
    async def test_messaging():
        # Create message queue
        queue = MessageQueue()
        workspace = SharedWorkspace()
        
        # Test message sending
        msg1 = Message("agent1", "agent2", "test", {"data": "hello"})
        await queue.send_message(msg1)
        
        # Test broadcast
        await queue.broadcast_message("supervisor", "status_update", "Starting task")
        
        # Test retrieval
        messages = await queue.get_messages_for_agent("agent2")
        print(f"Agent2 received {len(messages)} messages")
        
        # Test workspace
        await workspace.write("research_notes", ["fact1", "fact2"], "researcher")
        notes = await workspace.read("research_notes")
        print(f"Research notes: {notes}")
        
        # Show workspace keys
        keys = await workspace.list_keys()
        print(f"Workspace keys: {keys}")
    
    # Run test
    asyncio.run(test_messaging())