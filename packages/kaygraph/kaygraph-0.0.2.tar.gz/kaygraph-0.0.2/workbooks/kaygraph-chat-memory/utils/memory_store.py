"""
Memory storage utilities for chat with memory.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile with long-term memory."""
    user_id: str
    created_at: datetime
    last_interaction: Optional[datetime] = None
    conversation_count: int = 0
    topics_discussed: List[str] = None
    preferences: Dict[str, Any] = None
    attributes: Dict[str, Any] = None
    personality_traits: List[str] = None
    
    def __post_init__(self):
        if self.topics_discussed is None:
            self.topics_discussed = []
        if self.preferences is None:
            self.preferences = {}
        if self.attributes is None:
            self.attributes = {}
        if self.personality_traits is None:
            self.personality_traits = []
    
    def to_dict(self):
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Convert datetime objects to strings
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['last_interaction'] = self.last_interaction.isoformat() if self.last_interaction else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        # Convert string dates back to datetime
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_interaction'):
            data['last_interaction'] = datetime.fromisoformat(data['last_interaction'])
        return cls(**data)


class MemoryStore:
    """Persistent memory storage for chat system."""
    
    def __init__(self, storage_path: str = "./chat_memory.json"):
        """
        Initialize memory store.
        
        Args:
            storage_path: Path to JSON file for persistence
        """
        self.storage_path = storage_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load memory store: {e}")
                return {"users": {}, "conversations": {}}
        return {"users": {}, "conversations": {}}
    
    def _save_data(self):
        """Save data to disk."""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory store: {e}")
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID."""
        user_data = self.data["users"].get(user_id)
        if user_data:
            return UserProfile.from_dict(user_data)
        return None
    
    def save_user_profile(self, profile: UserProfile):
        """Save or update user profile."""
        self.data["users"][profile.user_id] = profile.to_dict()
        self._save_data()
        logger.info(f"Saved profile for user: {profile.user_id}")
    
    def get_conversation(self, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by user and session ID."""
        user_conversations = self.data["conversations"].get(user_id, {})
        return user_conversations.get(session_id)
    
    def save_conversation(self, user_id: str, conversation: Dict[str, Any]):
        """Save or update conversation."""
        if user_id not in self.data["conversations"]:
            self.data["conversations"][user_id] = {}
        
        session_id = conversation["session_id"]
        self.data["conversations"][user_id][session_id] = conversation
        self._save_data()
        logger.debug(f"Saved conversation: {user_id}/{session_id}")
    
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for a user."""
        user_conversations = self.data["conversations"].get(user_id, {})
        
        # Sort by started_at timestamp
        sorted_convs = sorted(
            user_conversations.values(),
            key=lambda x: x.get("started_at", ""),
            reverse=True
        )
        
        return sorted_convs[:limit]
    
    def get_all_users(self) -> List[str]:
        """Get list of all user IDs."""
        return list(self.data["users"].keys())
    
    def delete_user(self, user_id: str):
        """Delete user and all their data."""
        if user_id in self.data["users"]:
            del self.data["users"][user_id]
        if user_id in self.data["conversations"]:
            del self.data["conversations"][user_id]
        self._save_data()
        logger.info(f"Deleted all data for user: {user_id}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage."""
        total_users = len(self.data["users"])
        total_conversations = sum(
            len(convs) for convs in self.data["conversations"].values()
        )
        
        # Calculate average stats
        avg_conversations_per_user = 0
        avg_topics_per_user = 0
        
        if total_users > 0:
            avg_conversations_per_user = total_conversations / total_users
            
            total_topics = sum(
                len(user.get("topics_discussed", []))
                for user in self.data["users"].values()
            )
            avg_topics_per_user = total_topics / total_users
        
        return {
            "total_users": total_users,
            "total_conversations": total_conversations,
            "avg_conversations_per_user": avg_conversations_per_user,
            "avg_topics_per_user": avg_topics_per_user,
            "storage_size_kb": os.path.getsize(self.storage_path) / 1024 if os.path.exists(self.storage_path) else 0
        }


class ConversationSummarizer:
    """Utilities for summarizing conversations."""
    
    @staticmethod
    def summarize_messages(messages: List[Dict[str, str]], max_length: int = 200) -> str:
        """
        Create a summary of messages.
        
        Args:
            messages: List of message dictionaries
            max_length: Maximum summary length
            
        Returns:
            Summary string
        """
        if not messages:
            return "No previous conversation."
        
        # Extract key points (simple implementation)
        topics = []
        for msg in messages:
            if msg["role"] == "user":
                # Extract potential topics (words > 4 chars)
                words = msg["content"].split()
                topics.extend([w.lower() for w in words if len(w) > 4 and w.isalpha()])
        
        # Get unique topics
        unique_topics = list(dict.fromkeys(topics))[:5]
        
        summary = f"Previous conversation covered: {', '.join(unique_topics)}. "
        summary += f"Total {len(messages)} messages exchanged."
        
        return summary[:max_length]
    
    @staticmethod
    def extract_key_information(conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key information from a conversation.
        
        Args:
            conversation: Conversation dictionary
            
        Returns:
            Dictionary of extracted information
        """
        messages = conversation.get("messages", [])
        
        extracted = {
            "message_count": len(messages),
            "user_messages": len([m for m in messages if m["role"] == "user"]),
            "topics": [],
            "questions_asked": 0,
            "preferences_mentioned": []
        }
        
        for msg in messages:
            if msg["role"] == "user":
                content = msg["content"].lower()
                
                # Count questions
                if "?" in content:
                    extracted["questions_asked"] += 1
                
                # Extract preferences
                if "prefer" in content or "like" in content:
                    extracted["preferences_mentioned"].append(msg["content"])
        
        return extracted


if __name__ == "__main__":
    # Test memory store
    store = MemoryStore("test_memory.json")
    
    # Create test profile
    profile = UserProfile(
        user_id="test_user",
        created_at=datetime.now(),
        topics_discussed=["python", "weather"],
        preferences={"style": "casual"}
    )
    
    store.save_user_profile(profile)
    
    # Retrieve profile
    loaded_profile = store.get_user_profile("test_user")
    print(f"Loaded profile: {loaded_profile}")
    
    # Get stats
    stats = store.get_memory_stats()
    print(f"Memory stats: {stats}")
    
    # Clean up
    os.remove("test_memory.json")