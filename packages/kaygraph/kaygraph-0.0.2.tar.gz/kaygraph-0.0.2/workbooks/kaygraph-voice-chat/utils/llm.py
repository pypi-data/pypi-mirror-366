"""
LLM utilities for voice chat.
"""

import time
from typing import List, Dict, Any


def process_voice_query(user_input: str, 
                       conversation_history: List[Dict[str, Any]], 
                       personality: str) -> str:
    """
    Process voice query with LLM.
    In production, this would call OpenAI, Anthropic, etc.
    """
    
    # Mock LLM processing
    time.sleep(0.5)  # Simulate API call
    
    # Simple response generation based on input
    user_input_lower = user_input.lower()
    
    # Greetings
    if any(greeting in user_input_lower for greeting in ["hello", "hi", "hey"]):
        return "Hello! How can I help you today?"
    
    # Questions about weather
    elif "weather" in user_input_lower:
        return "I'm sorry, I don't have access to real-time weather data. You might want to check a weather app or website for current conditions."
    
    # Questions about time
    elif any(word in user_input_lower for word in ["time", "clock", "hour"]):
        current_time = time.strftime("%I:%M %p")
        return f"The current time is {current_time}."
    
    # Questions about the assistant
    elif any(word in user_input_lower for word in ["who are you", "what are you", "your name"]):
        return "I'm a voice assistant powered by KayGraph. I can help you with various tasks through natural conversation."
    
    # Math questions
    elif any(op in user_input_lower for op in ["plus", "minus", "times", "divided"]):
        return "I can help with math! For complex calculations, please be specific with the numbers."
    
    # Farewell
    elif any(bye in user_input_lower for bye in ["goodbye", "bye", "see you"]):
        return "Goodbye! It was nice talking with you. Have a great day!"
    
    # Help
    elif "help" in user_input_lower:
        return "I can help you with various tasks like answering questions, having conversations, or providing information. Just ask me anything!"
    
    # Default response with personality
    else:
        if "friendly" in personality.lower():
            return f"That's interesting! You said: '{user_input}'. I'm here to help with any questions you might have."
        else:
            return f"I heard: '{user_input}'. How can I assist you with that?"


def generate_voice_response(text: str, emotion: str = "neutral") -> str:
    """
    Generate voice-optimized response.
    Adjusts text for better TTS output.
    """
    
    # Add pauses for better speech rhythm
    text = text.replace(". ", ". <break time='500ms'/> ")
    text = text.replace(", ", ", <break time='200ms'/> ")
    
    # Add emphasis based on emotion
    if emotion == "excited":
        text = f"<prosody rate='110%' pitch='+5%'>{text}</prosody>"
    elif emotion == "calm":
        text = f"<prosody rate='90%' pitch='-5%'>{text}</prosody>"
    
    return text