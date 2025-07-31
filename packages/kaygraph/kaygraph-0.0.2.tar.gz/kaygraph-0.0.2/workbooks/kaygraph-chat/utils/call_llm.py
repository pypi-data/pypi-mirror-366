"""
Utility function to call LLM API for chat responses.
This is a placeholder implementation - replace with your actual LLM integration.
"""

import os
from typing import List, Dict, Any, Optional


def call_llm(
    messages: List[Dict[str, str]],
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 1024,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None
) -> str:
    """
    Call the LLM API with conversation history.
    
    Args:
        messages: Conversation history in format [{"role": "user/assistant", "content": "..."}]
        model: The model to use
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature for creativity
        system_prompt: Optional system prompt
        
    Returns:
        The assistant's response text
    """
    # Placeholder implementation
    # Replace this with your actual LLM API call
    # For example, using Anthropic's Claude API:
    #
    # from anthropic import Anthropic
    # client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    # 
    # response = client.messages.create(
    #     model=model,
    #     max_tokens=max_tokens,
    #     temperature=temperature,
    #     system=system_prompt or "You are a helpful assistant.",
    #     messages=messages
    # )
    # return response.content[0].text
    
    # For demo purposes, return contextual mock responses
    if not messages:
        return "Hello! How can I help you today?"
    
    last_message = messages[-1]["content"].lower()
    
    # Simple pattern matching for demo
    if "how are you" in last_message:
        return "I'm doing well, thank you for asking! How can I assist you today?"
    elif "weather" in last_message:
        return "I don't have access to real-time weather data, but I'd be happy to help you with other questions!"
    elif "hello" in last_message or "hi" in last_message:
        return "Hello! It's nice to meet you. What would you like to talk about?"
    elif "thank" in last_message:
        return "You're very welcome! Is there anything else I can help you with?"
    else:
        return f"I understand you said: '{messages[-1]['content']}'. How can I help you further?"


if __name__ == "__main__":
    # Test the function
    test_messages = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hello! How can I help you?"},
        {"role": "user", "content": "What's the weather like?"}
    ]
    
    response = call_llm(test_messages)
    print(f"Response: {response}")