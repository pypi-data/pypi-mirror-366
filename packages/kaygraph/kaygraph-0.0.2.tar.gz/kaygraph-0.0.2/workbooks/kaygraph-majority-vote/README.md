# KayGraph Majority Vote

This example demonstrates how to implement majority vote patterns for LLM consensus using KayGraph. It shows how to query multiple LLMs, aggregate their responses, and achieve higher accuracy through ensemble methods.

## Features Demonstrated

1. **Multi-LLM Querying**: Query multiple LLM providers in parallel
2. **Response Aggregation**: Combine responses using various voting strategies
3. **Confidence Scoring**: Calculate consensus confidence levels
4. **Fallback Handling**: Deal with LLM failures gracefully
5. **Cost Optimization**: Smart routing based on query complexity

## Voting Strategies

### 1. Simple Majority
- Most common response wins
- Equal weight for all models
- Good for factual questions

### 2. Weighted Voting
- Models have different weights based on expertise
- GPT-4 might have higher weight for reasoning
- Claude for analysis tasks

### 3. Confidence-Based
- Each model provides confidence score
- Weighted by confidence levels
- More nuanced decisions

### 4. Hierarchical Consensus
- Tier 1: Fast, cheap models filter
- Tier 2: Expensive models for close calls
- Cost-effective approach

## Architecture

```
┌─────────────────┐
│ Query Router    │
│ (Complexity     │
│  Analysis)      │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Simple  │ Complex
    ▼         ▼
┌─────────┐ ┌─────────────────────────────┐
│ Single  │ │     Parallel LLM Queries    │
│  LLM    │ ├─────────┬─────────┬─────────┤
└─────────┘ │ GPT-4   │ Claude  │ Gemini  │
            └─────────┴─────────┴─────────┘
                      │
                      ▼
            ┌─────────────────┐
            │ Vote Aggregator │
            │ (Consensus)     │
            └─────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │ Result with     │
            │ Confidence      │
            └─────────────────┘
```

## Usage

### Basic Majority Vote
```bash
# Simple majority vote with 3 LLMs
python main.py --query "What is the capital of France?"

# Use more models for higher confidence
python main.py --query "Explain quantum entanglement" --models 5
```

### Advanced Options
```bash
# Weighted voting with custom weights
python main.py --strategy weighted --weights "gpt4:0.4,claude:0.3,gemini:0.3"

# Confidence-based voting
python main.py --strategy confidence --min-confidence 0.7

# Hierarchical consensus for cost optimization
python main.py --strategy hierarchical --budget 0.50
```

## Examples

### 1. Fact Checking
Use multiple models to verify factual claims with high confidence.

### 2. Creative Writing
Combine different models' creative outputs for richer content.

### 3. Code Generation
Ensure code correctness through multi-model validation.

### 4. Decision Making
Get balanced perspectives on complex decisions.

## Configuration

```python
# Model pool configuration
MODELS = {
    "gpt-4": {
        "provider": "openai",
        "cost_per_1k": 0.03,
        "strengths": ["reasoning", "coding"],
        "latency": "medium"
    },
    "claude-3": {
        "provider": "anthropic", 
        "cost_per_1k": 0.025,
        "strengths": ["analysis", "writing"],
        "latency": "medium"
    },
    "gemini-pro": {
        "provider": "google",
        "cost_per_1k": 0.02,
        "strengths": ["factual", "multilingual"],
        "latency": "fast"
    }
}
```

## Best Practices

1. **Query Routing**: Use simple models for straightforward queries
2. **Timeout Handling**: Set appropriate timeouts for each model
3. **Cache Results**: Cache consensus results for repeated queries
4. **Monitor Disagreements**: Log cases where models strongly disagree
5. **Cost Tracking**: Monitor costs across different models