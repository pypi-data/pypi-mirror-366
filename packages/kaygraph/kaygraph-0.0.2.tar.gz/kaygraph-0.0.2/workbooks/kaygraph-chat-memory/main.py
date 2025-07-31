"""
Chat with memory example using KayGraph.

Demonstrates a chatbot with both short-term (conversation) and 
long-term (user profile) memory capabilities.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from kaygraph import Node, Graph, ValidatedNode
from utils.memory_store import MemoryStore, UserProfile
from utils.chat_utils import (
    summarize_conversation, 
    extract_user_preferences,
    format_chat_history
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class UserIdentificationNode(Node):
    """Identify or create user profile."""
    
    def __init__(self, memory_store: MemoryStore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_store = memory_store
    
    def prep(self, shared):
        """Get user ID from shared state."""
        return shared.get("user_id", "default_user")
    
    def exec(self, user_id):
        """Load or create user profile."""
        profile = self.memory_store.get_user_profile(user_id)
        
        if profile is None:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                created_at=datetime.now(),
                preferences={},
                conversation_count=0,
                topics_discussed=[],
                personality_traits=[]
            )
            self.memory_store.save_user_profile(profile)
            self.logger.info(f"Created new profile for user: {user_id}")
        else:
            self.logger.info(f"Loaded existing profile for user: {user_id}")
        
        return profile
    
    def post(self, shared, prep_res, exec_res):
        """Store user profile in shared state."""
        shared["user_profile"] = exec_res
        shared["is_new_user"] = exec_res.conversation_count == 0
        return "default"


class ConversationMemoryNode(Node):
    """Manage conversation memory (short-term)."""
    
    def __init__(self, memory_store: MemoryStore, max_history: int = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_store = memory_store
        self.max_history = max_history
    
    def prep(self, shared):
        """Get conversation context."""
        return {
            "user_id": shared.get("user_id", "default_user"),
            "session_id": shared.get("session_id", ""),
            "new_message": shared.get("user_input", "")
        }
    
    def exec(self, context):
        """Load and update conversation history."""
        # Load existing conversation
        conversation = self.memory_store.get_conversation(
            context["user_id"], 
            context["session_id"]
        )
        
        if conversation is None:
            conversation = {
                "session_id": context["session_id"],
                "messages": [],
                "started_at": datetime.now().isoformat(),
                "context": {}
            }
        
        # Add new user message if present
        if context["new_message"]:
            conversation["messages"].append({
                "role": "user",
                "content": context["new_message"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Trim history if too long
        if len(conversation["messages"]) > self.max_history * 2:
            # Keep recent messages and create summary of older ones
            old_messages = conversation["messages"][:-self.max_history]
            summary = summarize_conversation(old_messages)
            
            conversation["context"]["previous_summary"] = summary
            conversation["messages"] = conversation["messages"][-self.max_history:]
        
        return conversation
    
    def post(self, shared, prep_res, exec_res):
        """Store updated conversation."""
        shared["conversation"] = exec_res
        shared["message_count"] = len(exec_res["messages"])
        
        # Save to memory store
        self.memory_store.save_conversation(
            prep_res["user_id"],
            exec_res
        )
        
        return "default"


class PersonalizationNode(Node):
    """Apply personalization based on user memory."""
    
    def prep(self, shared):
        """Get user profile and conversation."""
        return {
            "profile": shared.get("user_profile"),
            "conversation": shared.get("conversation", {}),
            "is_new_user": shared.get("is_new_user", False)
        }
    
    def exec(self, context):
        """Generate personalization context."""
        profile = context["profile"]
        conversation = context["conversation"]
        
        personalization = {
            "greeting_style": "formal" if context["is_new_user"] else "casual",
            "use_name": profile.attributes.get("name") is not None,
            "interests": profile.topics_discussed[-5:] if profile.topics_discussed else [],
            "preferences": profile.preferences,
            "conversation_style": profile.attributes.get("preferred_style", "balanced")
        }
        
        # Analyze recent conversation for context
        if conversation.get("messages"):
            recent_topics = extract_user_preferences(conversation["messages"][-6:])
            personalization["recent_context"] = recent_topics
        
        # Add personality insights
        if profile.personality_traits:
            personalization["personality"] = profile.personality_traits
        
        return personalization
    
    def post(self, shared, prep_res, exec_res):
        """Store personalization context."""
        shared["personalization"] = exec_res
        self.logger.info(f"Applied personalization: {exec_res}")
        return "default"


class MemoryAwareChatNode(Node):
    """Generate responses using memory context."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(max_retries=2, wait=1, *args, **kwargs)
    
    def prep(self, shared):
        """Prepare chat context with memory."""
        return {
            "user_input": shared.get("user_input", ""),
            "conversation": shared.get("conversation", {}),
            "personalization": shared.get("personalization", {}),
            "profile": shared.get("user_profile")
        }
    
    def exec(self, context):
        """Generate memory-aware response."""
        if not context["user_input"]:
            # Generate greeting based on history
            if context["profile"].conversation_count == 0:
                response = "Hello! I'm your AI assistant. I'll remember our conversations to provide better help over time. What can I assist you with today?"
            else:
                name = context["profile"].attributes.get("name", "there")
                last_topic = context["profile"].topics_discussed[-1] if context["profile"].topics_discussed else None
                
                if last_topic:
                    response = f"Welcome back, {name}! Last time we discussed {last_topic}. What would you like to talk about today?"
                else:
                    response = f"Welcome back, {name}! How can I help you today?"
        else:
            # Generate contextual response
            response = self._generate_contextual_response(context)
        
        return response
    
    def post(self, shared, prep_res, exec_res):
        """Store assistant response."""
        # Add to conversation
        if "conversation" in shared:
            shared["conversation"]["messages"].append({
                "role": "assistant",
                "content": exec_res,
                "timestamp": datetime.now().isoformat()
            })
        
        shared["assistant_response"] = exec_res
        return "default"
    
    def _generate_contextual_response(self, context):
        """Generate response with context awareness."""
        user_input = context["user_input"].lower()
        personalization = context["personalization"]
        
        # Check for memory-related queries
        if "remember" in user_input or "forgot" in user_input:
            return self._handle_memory_query(context)
        
        # Check for preference updates
        if "call me" in user_input or "my name is" in user_input:
            return self._handle_name_update(user_input, context)
        
        # Generate personalized response
        response = f"I understand you're asking about '{context['user_input']}'. "
        
        # Add context from previous conversations
        if personalization.get("interests"):
            related_interest = None
            for interest in personalization["interests"]:
                if interest.lower() in user_input:
                    related_interest = interest
                    break
            
            if related_interest:
                response += f"I see this relates to {related_interest}, which we've discussed before. "
        
        # Add personalized touch
        if personalization.get("use_name") and context["profile"].attributes.get("name"):
            response += f"Let me help you with that, {context['profile'].attributes['name']}."
        else:
            response += "Let me help you with that."
        
        return response
    
    def _handle_memory_query(self, context):
        """Handle queries about memory."""
        profile = context["profile"]
        
        if profile.topics_discussed:
            topics = ", ".join(profile.topics_discussed[-3:])
            return f"I remember we've discussed: {topics}. I also know that you've had {profile.conversation_count} conversations with me."
        else:
            return "This is our first conversation, so I'm just getting to know you. I'll remember our discussions for future conversations."
    
    def _handle_name_update(self, user_input, context):
        """Handle name updates."""
        # Simple name extraction (in production, use NER)
        if "call me " in user_input:
            name = user_input.split("call me ")[-1].strip().capitalize()
        elif "my name is " in user_input:
            name = user_input.split("my name is ")[-1].strip().capitalize()
        else:
            name = None
        
        if name:
            return f"Nice to meet you, {name}! I'll remember that for our future conversations."
        
        return "I'd be happy to remember your name. Just tell me what you'd like to be called."


class MemoryUpdateNode(Node):
    """Update long-term memory based on conversation."""
    
    def __init__(self, memory_store: MemoryStore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_store = memory_store
    
    def prep(self, shared):
        """Get data for memory update."""
        return {
            "profile": shared.get("user_profile"),
            "conversation": shared.get("conversation", {}),
            "user_input": shared.get("user_input", ""),
            "assistant_response": shared.get("assistant_response", "")
        }
    
    def exec(self, context):
        """Extract information to update memory."""
        updates = {
            "topics": [],
            "preferences": {},
            "attributes": {}
        }
        
        if not context["user_input"]:
            return updates
        
        # Extract topics discussed
        user_input = context["user_input"].lower()
        
        # Simple topic extraction (in production, use NLP)
        topic_keywords = ["python", "weather", "news", "sports", "cooking", "travel", "health", "technology"]
        for keyword in topic_keywords:
            if keyword in user_input:
                updates["topics"].append(keyword)
        
        # Extract name if mentioned
        if "call me " in user_input:
            name = user_input.split("call me ")[-1].strip().capitalize()
            updates["attributes"]["name"] = name
        elif "my name is " in user_input:
            name = user_input.split("my name is ")[-1].strip().capitalize()
            updates["attributes"]["name"] = name
        
        # Extract preferences
        if "prefer" in user_input or "like" in user_input:
            updates["preferences"]["detected_preference"] = context["user_input"]
        
        return updates
    
    def post(self, shared, prep_res, exec_res):
        """Update user profile with new information."""
        profile = prep_res["profile"]
        
        # Update topics
        for topic in exec_res["topics"]:
            if topic not in profile.topics_discussed:
                profile.topics_discussed.append(topic)
        
        # Update attributes
        profile.attributes.update(exec_res["attributes"])
        
        # Update preferences
        profile.preferences.update(exec_res["preferences"])
        
        # Increment conversation count
        profile.conversation_count += 1
        profile.last_interaction = datetime.now()
        
        # Save updated profile
        self.memory_store.save_user_profile(profile)
        
        self.logger.info(f"Updated user profile: {len(exec_res['topics'])} new topics")
        return "default"


def create_memory_chat_graph(memory_store: MemoryStore):
    """Create a chat graph with memory capabilities."""
    # Create nodes
    user_id_node = UserIdentificationNode(memory_store, node_id="user_id")
    conv_memory_node = ConversationMemoryNode(memory_store, node_id="conv_memory")
    personalization_node = PersonalizationNode(node_id="personalization")
    chat_node = MemoryAwareChatNode(node_id="chat")
    memory_update_node = MemoryUpdateNode(memory_store, node_id="memory_update")
    
    # Connect nodes
    user_id_node >> conv_memory_node >> personalization_node >> chat_node >> memory_update_node
    
    # Create graph
    return Graph(start=user_id_node)


def main():
    """Run the chat with memory example."""
    print("KayGraph Chat with Memory")
    print("=" * 40)
    print("Commands: 'exit' to quit, 'new' for new session, 'switch <user>' to change user")
    print("=" * 40)
    
    # Initialize memory store
    memory_store = MemoryStore("./chat_memory.json")
    
    # Create graph
    graph = create_memory_chat_graph(memory_store)
    
    # Session management
    current_user = "user1"
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\nStarting session for user: {current_user}")
    print(f"Session ID: {session_id}\n")
    
    # Initial greeting
    shared = {
        "user_id": current_user,
        "session_id": session_id,
        "user_input": ""
    }
    graph.run(shared)
    print(f"Assistant: {shared.get('assistant_response', '')}")
    
    # Chat loop
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'exit':
            print("Goodbye! I'll remember our conversation for next time.")
            break
        
        elif user_input.lower() == 'new':
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"Started new session: {session_id}")
            continue
        
        elif user_input.lower().startswith('switch '):
            current_user = user_input.split(' ', 1)[1]
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"Switched to user: {current_user}")
            
            # Greet new/returning user
            shared = {
                "user_id": current_user,
                "session_id": session_id,
                "user_input": ""
            }
            graph.run(shared)
            print(f"Assistant: {shared.get('assistant_response', '')}")
            continue
        
        # Process user input
        shared = {
            "user_id": current_user,
            "session_id": session_id,
            "user_input": user_input
        }
        
        try:
            graph.run(shared)
            print(f"Assistant: {shared.get('assistant_response', '')}")
            
            # Show memory stats
            profile = shared.get("user_profile")
            if profile:
                print(f"\n[Memory: {profile.conversation_count} conversations, "
                      f"{len(profile.topics_discussed)} topics discussed]")
        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()