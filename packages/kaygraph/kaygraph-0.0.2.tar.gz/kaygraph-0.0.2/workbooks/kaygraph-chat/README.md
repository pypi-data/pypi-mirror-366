# KayGraph Chat

This workbook demonstrates how to build an interactive chatbot using KayGraph with conversation history management.

## What it does

The chat application:
- Maintains full conversation history
- Provides contextual responses based on chat history
- Supports graceful exit with multiple commands
- Handles errors with retry logic
- Allows custom system prompts for different personalities

## How to run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your LLM (edit `utils/call_llm.py`):
   - Add your API key and preferred LLM service
   - The example includes a mock implementation for testing

3. Run with default assistant:
```bash
python main.py
```

4. Run with custom personality:
```bash
python main.py "You are a helpful pirate who speaks in pirate slang"
```

5. Exit the chat:
   - Type 'exit', 'quit', 'bye', or 'goodbye'
   - Or press Ctrl+C

## How it works

### Graph Structure
```
InputNode → ChatNode → OutputNode
    ↑                      ↓
    └──────────────────────┘
         (continue loop)
```

### Key Components

1. **InputNode**: 
   - Captures user input
   - Displays assistant responses
   - Detects exit commands

2. **ChatNode**: 
   - Maintains conversation history
   - Calls LLM with full context
   - Handles API failures gracefully

3. **OutputNode**: 
   - Manages conversation flow
   - Tracks conversation statistics
   - Decides whether to continue or exit

### Features from KayGraph

- **Node retry mechanism**: Handles LLM failures
- **Graph orchestration**: Clean conversation loop
- **Logging**: Detailed execution traces
- **Error handling**: Graceful fallbacks

## Customization

### Custom System Prompts

Create different chatbot personalities:

```bash
# Helpful tutor
python main.py "You are a patient tutor who explains concepts clearly"

# Creative writer
python main.py "You are a creative writing assistant who helps with storytelling"

# Technical expert
python main.py "You are a technical expert who provides detailed programming help"
```

### Extending the Chat

You can enhance the chatbot by:

1. **Adding memory**: Store conversations across sessions
2. **Tool integration**: Add nodes for web search, calculations, etc.
3. **Multi-turn planning**: Use chain-of-thought for complex queries
4. **Response filtering**: Add content moderation nodes

## Example Conversation

```
Welcome to KayGraph Chat!
Type 'exit', 'quit', or 'bye' to end the conversation.
--------------------------------------------------

You: Hello! What can you help me with?