"""
Mock LLM providers for majority vote example.
In production, these would call actual LLM APIs.
"""

import time
import random
from typing import Dict, Any


# Mock responses for different models
MOCK_RESPONSES = {
    "factual": {
        "What is the capital of France?": "Paris is the capital of France.",
        "When was Python created?": "Python was created in 1991 by Guido van Rossum.",
        "What is 2+2?": "2+2 equals 4.",
    },
    "analytical": {
        "explain": "This is a complex topic that requires careful analysis. The key factors include: 1) Historical context, 2) Current implications, and 3) Future considerations.",
        "analyze": "Based on comprehensive analysis, we can identify several important patterns and relationships in the data.",
        "compare": "When comparing these elements, we observe both similarities and differences across multiple dimensions.",
    },
    "creative": {
        "write": "In the realm of creative expression, we find infinite possibilities for crafting unique narratives.",
        "imagine": "Imagine a world where boundaries dissolve and innovation knows no limits.",
        "design": "The design process involves iterative refinement and creative problem-solving.",
    }
}


def query_llm_mock(query: str, model: str = "gpt-3.5", temperature: float = 0.7) -> Dict[str, Any]:
    """
    Mock LLM query function.
    In production, this would call OpenAI, Anthropic, Google, etc.
    """
    
    # Simulate API latency
    latency = random.uniform(0.5, 2.0)
    time.sleep(latency)
    
    # Determine response based on query type
    query_lower = query.lower()
    
    # Check for factual questions
    for question, answer in MOCK_RESPONSES["factual"].items():
        if question.lower() in query_lower:
            response = answer
            confidence = random.uniform(0.85, 0.98)
            break
    else:
        # Check for analytical queries
        for keyword in ["explain", "analyze", "compare"]:
            if keyword in query_lower:
                response = MOCK_RESPONSES["analytical"][keyword]
                confidence = random.uniform(0.70, 0.90)
                break
        else:
            # Check for creative queries
            for keyword in ["write", "imagine", "design"]:
                if keyword in query_lower:
                    response = MOCK_RESPONSES["creative"][keyword]
                    confidence = random.uniform(0.60, 0.85)
                    break
            else:
                # Default response with model-specific variations
                base_response = f"Based on the query '{query}', "
                
                if "gpt" in model:
                    response = base_response + "I would say that this requires careful consideration of multiple factors."
                elif "claude" in model:
                    response = base_response + "let me provide a thoughtful analysis of the key aspects involved."
                elif "gemini" in model:
                    response = base_response + "here's a comprehensive perspective on this topic."
                else:
                    response = base_response + "this is an interesting question that touches on several important points."
                
                confidence = random.uniform(0.65, 0.85)
    
    # Add model-specific variations
    if temperature > 0.8:
        # Higher temperature = more variation
        if random.random() < 0.3:
            response = response[:-1] + " Additionally, " + random.choice([
                "we should consider alternative perspectives.",
                "there are nuanced aspects to explore.",
                "this connects to broader themes.",
            ])
    
    # Simulate occasional differences between models
    if model in ["gpt-3.5", "claude-2"] and random.random() < 0.1:
        # 10% chance of slight variation for cheaper models
        response += " (Note: This is a simplified explanation.)"
        confidence *= 0.9
    
    return {
        "text": response,
        "model": model,
        "confidence": confidence,
        "tokens_used": len(response.split()),
        "latency": latency,
        "temperature": temperature
    }


def get_model_capabilities(model: str) -> Dict[str, Any]:
    """Get model capabilities and metadata."""
    model_info = {
        "gpt-4": {
            "strengths": ["reasoning", "coding", "analysis"],
            "max_tokens": 8192,
            "cost_per_1k": 0.03,
            "latency": "medium",
            "accuracy": 0.95
        },
        "gpt-3.5": {
            "strengths": ["general", "fast"],
            "max_tokens": 4096,
            "cost_per_1k": 0.002,
            "latency": "fast",
            "accuracy": 0.85
        },
        "claude-3": {
            "strengths": ["analysis", "writing", "safety"],
            "max_tokens": 100000,
            "cost_per_1k": 0.025,
            "latency": "medium",
            "accuracy": 0.93
        },
        "claude-2": {
            "strengths": ["writing", "summary"],
            "max_tokens": 100000,
            "cost_per_1k": 0.01,
            "latency": "fast",
            "accuracy": 0.88
        },
        "gemini-pro": {
            "strengths": ["multimodal", "factual", "coding"],
            "max_tokens": 32768,
            "cost_per_1k": 0.02,
            "latency": "fast",
            "accuracy": 0.92
        },
        "gemini-1.5": {
            "strengths": ["general", "efficient"],
            "max_tokens": 8192,
            "cost_per_1k": 0.005,
            "latency": "very_fast",
            "accuracy": 0.83
        }
    }
    
    return model_info.get(model, {
        "strengths": ["general"],
        "max_tokens": 4096,
        "cost_per_1k": 0.01,
        "latency": "medium",
        "accuracy": 0.80
    })