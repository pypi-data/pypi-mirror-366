# KayGraph Chat with Memory

An advanced chatbot implementation featuring both short-term (conversation) and long-term (user profile) memory using KayGraph.

## What it does

This chatbot remembers:
- **User Information**: Names, preferences, personality traits
- **Conversation History**: Current and past conversations
- **Topics Discussed**: Tracks interests over time
- **Interaction Patterns**: Learns communication style preferences

## Features

### Memory Types

1. **Short-term Memory** (Conversation)
   - Current session messages
   - Recent context
   - Conversation summaries

2. **Long-term Memory** (User Profile)
   - User attributes (name, preferences)
   - Topics discussed across sessions
   - Conversation count and history
   - Personality insights

### Key Capabilities

- **Personalized Greetings**: Different for new vs returning users
- **Context Awareness**: References previous conversations
- **Preference Learning**: Remembers user preferences
- **Multi-user Support**: Switch between different users
- **Session Management**: Multiple conversations per user
- **Memory Queries**: Users can ask what the bot remembers

## How to run

```bash
python main.py
```

### Commands

- `exit` - End the chat
- `new` - Start a new session (keeps user)
- `switch <username>` - Switch to different user
- Ask "what do you remember?" to query memory

## Architecture

```
UserIdentificationNode → ConversationMemoryNode → PersonalizationNode
                                                          ↓
                        MemoryUpdateNode ← MemoryAwareChatNode
```

### Node Descriptions

1. **UserIdentificationNode**: Loads or creates user profile
2. **ConversationMemoryNode**: Manages conversation history
3. **PersonalizationNode**: Applies user-specific personalization
4. **MemoryAwareChatNode**: Generates memory-aware responses
5. **MemoryUpdateNode**: Extracts and saves new information

## Memory Storage

The system uses a JSON-based storage system (`chat_memory.json`) with:

```json
{
  "users": {
    "user1": {
      "user_id": "user1",
      "created_at": "2023-...",
      "conversation_count": 5,
      "topics_discussed": ["python", "weather"],
      "preferences": {"style": "casual"},
      "attributes": {"name": "Alice"}
    }
  },
  "conversations": {
    "user1": {
      "session_123": {
        "messages": [...],
        "started_at": "2023-..."
      }
    }
  }
}
```

## Example Interactions

### First Time User
```
Assistant: Hello! I'm your AI assistant. I'll remember our conversations to provide better help over time. What can I assist you with today?

You: Hi! Call me Bob. I'm interested in learning Python.