"""
LLM utility for the agent's reasoning and response generation.
"""

import json
from typing import List, Dict, Any, Optional


def call_llm(
    prompt: str,
    messages: Optional[List[Dict[str, str]]] = None,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 2048,
    temperature: float = 0.3,
    response_format: Optional[str] = None
) -> str:
    """
    Call the LLM API with the given prompt.
    
    Args:
        prompt: System prompt or instruction
        messages: Optional conversation history
        model: Model to use
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        response_format: Optional format hint (e.g., "json")
        
    Returns:
        The LLM's response text
    """
    # Placeholder implementation
    # Replace with actual LLM API call
    
    # Mock responses based on prompt patterns
    if "analyze the query" in prompt.lower():
        return json.dumps({
            "needs_search": True,
            "reasoning": "This query requires current information that I should search for.",
            "search_query": "latest information on the topic",
            "confidence": 0.9
        })
    
    elif "synthesize" in prompt.lower():
        return "Based on the search results, here's a comprehensive summary of the findings..."
    
    elif "generate a comprehensive answer" in prompt.lower():
        return "Based on my analysis and the available information, here's my response to your query..."
    
    else:
        return "I understand your query. Let me help you with that."


def analyze_query(query: str) -> Dict[str, Any]:
    """
    Analyze a query to determine if search is needed.
    
    Args:
        query: User's query
        
    Returns:
        Analysis results including whether search is needed
    """
    prompt = f"""Analyze the following query and determine if web search is needed:

Query: {query}

Consider:
1. Is this asking for current events or recent information?
2. Is this asking for facts that might have changed recently?
3. Can this be answered with general knowledge?
4. Would search results improve the answer quality?

Respond in JSON format:
{{
    "needs_search": true/false,
    "reasoning": "explanation",
    "search_query": "refined query if search needed",
    "confidence": 0.0-1.0
}}"""

    response = call_llm(prompt, response_format="json")
    
    try:
        return json.loads(response)
    except:
        # Fallback analysis
        return {
            "needs_search": True,
            "reasoning": "Unable to analyze, searching to be safe",
            "search_query": query,
            "confidence": 0.5
        }


if __name__ == "__main__":
    # Test the functions
    analysis = analyze_query("What is the weather today in New York?")
    print("Query analysis:", json.dumps(analysis, indent=2))
    
    response = call_llm("Generate a helpful response about Python programming")
    print("\nLLM Response:", response)