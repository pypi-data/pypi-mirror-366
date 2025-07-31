"""
Chat nodes implementation using KayGraph.
"""

import logging
from typing import Dict, Any, List, Optional
from kaygraph import Node
from utils.call_llm import call_llm


class InputNode(Node):
    """Captures user input and manages conversation flow."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(max_retries=1, *args, **kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Check if this is the first interaction."""
        return {
            "is_first": len(shared.get("messages", [])) == 0,
            "last_response": shared.get("assistant_response", "")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Get user input."""
        # Display last assistant response if any
        if prep_res["last_response"]:
            print(f"\nAssistant: {prep_res['last_response']}")
        
        # Show welcome message on first interaction
        if prep_res["is_first"]:
            print("\nWelcome to KayGraph Chat!")
            print("Type 'exit', 'quit', or 'bye' to end the conversation.")
            print("-" * 50)
        
        # Get user input
        user_input = input("\nYou: ").strip()
        return user_input
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Update shared state with user input."""
        shared["user_input"] = exec_res
        
        # Check for exit commands
        if exec_res.lower() in ["exit", "quit", "bye", "goodbye"]:
            shared["should_exit"] = True
            shared["assistant_response"] = "Goodbye! It was nice chatting with you."
            return "exit"
        
        self.logger.info(f"User input: {exec_res}")
        return "default"


class ChatNode(Node):
    """Processes user input and generates responses using conversation history."""
    
    def __init__(self, system_prompt: Optional[str] = None, *args, **kwargs):
        super().__init__(max_retries=2, wait=1, *args, **kwargs)
        self.system_prompt = system_prompt or "You are a helpful, friendly assistant."
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare conversation context."""
        return {
            "messages": shared.get("messages", []).copy(),
            "user_input": shared["user_input"]
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Generate assistant response."""
        # Add user message to history
        messages = prep_res["messages"]
        messages.append({
            "role": "user",
            "content": prep_res["user_input"]
        })
        
        # Call LLM for response
        response = call_llm(
            messages=messages,
            system_prompt=self.system_prompt,
            temperature=0.7
        )
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Update conversation history."""
        # Initialize messages if needed
        if "messages" not in shared:
            shared["messages"] = []
        
        # Add user message
        shared["messages"].append({
            "role": "user",
            "content": prep_res["user_input"]
        })
        
        # Add assistant response
        shared["messages"].append({
            "role": "assistant",
            "content": exec_res
        })
        
        # Store response for display
        shared["assistant_response"] = exec_res
        
        self.logger.info(f"Generated response: {exec_res[:50]}...")
        return "default"
    
    def exec_fallback(self, prep_res: Dict[str, Any], exc: Exception) -> str:
        """Fallback response when LLM fails."""
        self.logger.warning(f"LLM call failed: {exc}")
        return "I apologize, but I'm having trouble processing your request right now. Could you please try again?"


class OutputNode(Node):
    """Handles conversation continuation logic."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare output state."""
        return {
            "should_exit": shared.get("should_exit", False),
            "message_count": len(shared.get("messages", []))
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Determine next action."""
        return {
            "continue": not prep_res["should_exit"],
            "stats": {
                "total_messages": prep_res["message_count"],
                "total_turns": prep_res["message_count"] // 2
            }
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Decide whether to continue or exit."""
        if exec_res["continue"]:
            return "continue"
        else:
            # Print farewell and stats
            print(f"\nAssistant: {shared.get('assistant_response', 'Goodbye!')}")
            print("\n" + "=" * 50)
            print(f"Conversation ended. Total turns: {exec_res['stats']['total_turns']}")
            return "end"