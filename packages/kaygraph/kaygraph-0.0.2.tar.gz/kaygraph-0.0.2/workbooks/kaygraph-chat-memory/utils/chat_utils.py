"""
Chat utility functions for memory-aware conversations.
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime


def summarize_conversation(messages: List[Dict[str, str]]) -> str:
    """
    Create a summary of a conversation.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        
    Returns:
        Summary string
    """
    if not messages:
        return "No previous conversation."
    
    # Count messages by role
    user_messages = [m for m in messages if m["role"] == "user"]
    assistant_messages = [m for m in messages if m["role"] == "assistant"]
    
    # Extract topics (simple keyword extraction)
    all_text = " ".join(m["content"] for m in messages)
    words = re.findall(r'\b\w{4,}\b', all_text.lower())
    
    # Get most common words (excluding common words)
    common_words = {"that", "this", "with", "from", "have", "been", "what", "when", "where", "which"}
    topic_words = [w for w in words if w not in common_words]
    
    # Count occurrences
    word_counts = {}
    for word in topic_words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Get top topics
    top_topics = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    topic_list = [topic[0] for topic in top_topics]
    
    summary = f"Discussed {len(user_messages)} topics"
    if topic_list:
        summary += f" including: {', '.join(topic_list)}"
    
    return summary


def extract_user_preferences(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Extract user preferences from recent messages.
    
    Args:
        messages: Recent messages to analyze
        
    Returns:
        Dictionary of detected preferences
    """
    preferences = {
        "topics_of_interest": [],
        "communication_style": "neutral",
        "detected_preferences": []
    }
    
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"].lower()
            
            # Detect communication style
            if "please" in content or "thank you" in content:
                preferences["communication_style"] = "polite"
            elif "!" in content or content.isupper():
                preferences["communication_style"] = "enthusiastic"
            elif "?" in content:
                preferences["communication_style"] = "inquisitive"
            
            # Detect preferences
            preference_patterns = [
                (r"i (?:prefer|like|love|enjoy) (\w+)", "positive_preference"),
                (r"i (?:dislike|hate|don't like) (\w+)", "negative_preference"),
                (r"(?:interested|curious) (?:in|about) (\w+)", "interest"),
                (r"call me (\w+)", "preferred_name"),
            ]
            
            for pattern, pref_type in preference_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    preferences["detected_preferences"].append({
                        "type": pref_type,
                        "value": match,
                        "context": msg["content"]
                    })
            
            # Extract topics
            topic_keywords = [
                "programming", "python", "coding", "technology", "ai", "machine learning",
                "weather", "news", "sports", "music", "movies", "books", "travel",
                "food", "cooking", "health", "fitness", "science", "history"
            ]
            
            for keyword in topic_keywords:
                if keyword in content:
                    preferences["topics_of_interest"].append(keyword)
    
    # Remove duplicates
    preferences["topics_of_interest"] = list(set(preferences["topics_of_interest"]))
    
    return preferences


def format_chat_history(messages: List[Dict[str, str]], max_messages: int = 10) -> str:
    """
    Format chat history for display.
    
    Args:
        messages: List of messages
        max_messages: Maximum messages to show
        
    Returns:
        Formatted string
    """
    if not messages:
        return "No chat history."
    
    # Get recent messages
    recent_messages = messages[-max_messages:]
    
    formatted = []
    for msg in recent_messages:
        timestamp = msg.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M")
            except:
                time_str = ""
        else:
            time_str = ""
        
        role = msg["role"].capitalize()
        content = msg["content"]
        
        if time_str:
            formatted.append(f"[{time_str}] {role}: {content}")
        else:
            formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted)


def generate_contextual_prompt(
    user_input: str,
    user_profile: Dict[str, Any],
    recent_context: List[Dict[str, str]],
    personalization: Dict[str, Any]
) -> str:
    """
    Generate a contextual prompt for the LLM based on user memory.
    
    Args:
        user_input: Current user input
        user_profile: User's profile data
        recent_context: Recent conversation messages
        personalization: Personalization settings
        
    Returns:
        Contextual prompt for LLM
    """
    prompt_parts = []
    
    # Add personality instruction
    if personalization.get("communication_style") == "polite":
        prompt_parts.append("Be polite and courteous in your responses.")
    elif personalization.get("communication_style") == "enthusiastic":
        prompt_parts.append("Be enthusiastic and energetic in your responses.")
    
    # Add user context
    if user_profile.get("attributes", {}).get("name"):
        prompt_parts.append(f"The user's name is {user_profile['attributes']['name']}.")
    
    # Add topic context
    if user_profile.get("topics_discussed"):
        recent_topics = user_profile["topics_discussed"][-3:]
        prompt_parts.append(f"Recent topics discussed: {', '.join(recent_topics)}")
    
    # Add preferences
    if user_profile.get("preferences"):
        pref_str = ", ".join(f"{k}: {v}" for k, v in user_profile["preferences"].items())
        prompt_parts.append(f"User preferences: {pref_str}")
    
    # Add conversation context
    if recent_context:
        summary = summarize_conversation(recent_context)
        prompt_parts.append(f"Recent conversation summary: {summary}")
    
    # Combine with user input
    full_prompt = "\n".join(prompt_parts)
    full_prompt += f"\n\nUser says: {user_input}\n\nProvide a helpful, contextual response:"
    
    return full_prompt


def should_update_memory(user_input: str, assistant_response: str) -> bool:
    """
    Determine if the interaction should update long-term memory.
    
    Args:
        user_input: User's message
        assistant_response: Assistant's response
        
    Returns:
        True if memory should be updated
    """
    # Update memory for substantial interactions
    if len(user_input) < 10:
        return False
    
    # Update for preference expressions
    preference_keywords = ["prefer", "like", "love", "hate", "favorite", "always", "never"]
    if any(keyword in user_input.lower() for keyword in preference_keywords):
        return True
    
    # Update for personal information
    personal_keywords = ["my name", "call me", "i am", "i work", "i live", "years old"]
    if any(keyword in user_input.lower() for keyword in personal_keywords):
        return True
    
    # Update for substantial topics
    if len(user_input.split()) > 10:
        return True
    
    return False


def anonymize_conversation(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Anonymize sensitive information in conversations.
    
    Args:
        messages: List of messages
        
    Returns:
        Anonymized messages
    """
    anonymized = []
    
    # Patterns for sensitive info
    patterns = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    }
    
    for msg in messages:
        new_msg = msg.copy()
        content = new_msg["content"]
        
        # Replace sensitive patterns
        for info_type, pattern in patterns.items():
            content = re.sub(pattern, f"[{info_type.upper()}_REDACTED]", content)
        
        new_msg["content"] = content
        anonymized.append(new_msg)
    
    return anonymized


if __name__ == "__main__":
    # Test utilities
    test_messages = [
        {"role": "user", "content": "Hi, my name is John"},
        {"role": "assistant", "content": "Hello John! Nice to meet you."},
        {"role": "user", "content": "I prefer casual conversations and I'm interested in Python programming"},
        {"role": "assistant", "content": "Great! I'll keep our chat casual. Python is awesome!"}
    ]
    
    # Test summarization
    summary = summarize_conversation(test_messages)
    print(f"Summary: {summary}")
    
    # Test preference extraction
    preferences = extract_user_preferences(test_messages)
    print(f"\nExtracted preferences: {preferences}")
    
    # Test formatting
    formatted = format_chat_history(test_messages)
    print(f"\nFormatted history:\n{formatted}")