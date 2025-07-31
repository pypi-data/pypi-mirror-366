"""
Interactive chat example using KayGraph.

This example demonstrates how to build a conversational chatbot
with conversation history and graceful error handling.
"""

import sys
import logging
from graph import create_chat_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Run the interactive chat example."""
    # Parse command line arguments for custom system prompt
    system_prompt = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python main.py [system_prompt]")
            print("Example: python main.py 'You are a pirate who speaks in pirate slang'")
            return 0
        system_prompt = " ".join(sys.argv[1:])
        print(f"Using custom system prompt: {system_prompt}")
    
    # Create the chat graph
    graph = create_chat_graph(system_prompt=system_prompt)
    
    # Initialize shared state
    shared = {
        "messages": [],
        "should_exit": False
    }
    
    try:
        # Run the chat loop
        final_action = graph.run(shared)
        print(f"\nChat session ended successfully.")
        
    except KeyboardInterrupt:
        print("\n\nChat interrupted by user. Goodbye!")
        return 0
    except Exception as e:
        logging.error(f"Error during chat: {e}")
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())