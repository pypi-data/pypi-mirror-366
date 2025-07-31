# KayGraph Think-Act-Reflect Pattern

This example demonstrates the Think-Act-Reflect (TAR) pattern, a cognitive architecture for AI agents that promotes reasoning, action execution, and learning from outcomes.

## What is Think-Act-Reflect?

The TAR pattern is a three-phase cognitive loop:

1. **Think**: Analyze the situation, understand context, and plan actions
2. **Act**: Execute the planned actions in the environment
3. **Reflect**: Evaluate the outcomes, learn from results, and adjust strategy

This pattern enables agents to:
- Make deliberate, reasoned decisions
- Execute actions based on planning
- Learn from experience and improve over time
- Handle complex, multi-step problems

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Think    │────▶│     Act     │────▶│   Reflect   │
│  (Analyze)  │     │  (Execute)  │     │ (Evaluate)  │
└─────────────┘     └─────────────┘     └─────────────┘
       ▲                                          │
       └──────────────────────────────────────────┘
                    (Feedback Loop)
```

## Usage

### Basic TAR Agent
```bash
# Run a simple TAR agent
python main.py --task "Plan a trip to Paris"

# With verbose reasoning
python main.py --task "Solve this puzzle" --verbose

# With multiple iterations
python main.py --task "Optimize this code" --iterations 3
```

### Advanced Features
```bash
# Enable memory across iterations
python main.py --task "Learn to play chess" --enable-memory

# Use different reasoning strategies
python main.py --task "Debug this error" --strategy analytical

# Export reasoning trace
python main.py --task "Design a system" --export-trace trace.json
```

## Key Components

### 1. ThinkNode
- Analyzes the current situation
- Considers available information
- Generates action plans
- Uses reasoning strategies

### 2. ActNode
- Executes planned actions
- Interacts with tools/APIs
- Handles action failures
- Collects execution data

### 3. ReflectNode
- Evaluates action outcomes
- Identifies successes/failures
- Extracts lessons learned
- Updates agent knowledge

### 4. MemoryNode
- Stores experiences
- Retrieves relevant past experiences
- Enables learning across iterations
- Maintains context

## Example Scenarios

### 1. Problem Solving
```python
# Agent solving a coding problem
Think: "Need to implement a sorting algorithm. Quick sort is efficient..."
Act: "Implement quick sort with pivot selection"
Reflect: "Implementation works but fails on already sorted arrays. Need optimization..."
```

### 2. Task Planning
```python
# Agent planning a project
Think: "Project needs frontend, backend, and database. Start with API design..."
Act: "Create API specification and database schema"
Reflect: "API design revealed missing requirements. Need to revisit with stakeholder..."
```

### 3. Learning from Mistakes
```python
# Agent learning from errors
Think: "Previous attempt failed due to timeout. Need async approach..."
Act: "Implement with async/await pattern"
Reflect: "Async solved timeout but introduced race condition. Need synchronization..."
```

## Configuration

Create `config.json`:
```json
{
  "reasoning": {
    "max_depth": 5,
    "strategies": ["analytical", "creative", "systematic"],
    "confidence_threshold": 0.7
  },
  "actions": {
    "timeout": 30,
    "max_retries": 3,
    "available_tools": ["search", "calculate", "code", "analyze"]
  },
  "reflection": {
    "metrics": ["success_rate", "efficiency", "quality"],
    "learning_rate": 0.1
  },
  "memory": {
    "capacity": 1000,
    "retention_days": 30
  }
}
```

## Integration with Other Patterns

The TAR pattern works well with:
- **Multi-Agent**: Multiple agents can share reflections
- **Supervisor**: Supervisor can guide the thinking process
- **RAG**: Retrieve relevant experiences during thinking
- **Human-in-the-Loop**: Human feedback during reflection

## Best Practices

1. **Clear Objectives**: Define what success looks like
2. **Structured Thinking**: Use frameworks for analysis
3. **Actionable Plans**: Ensure thoughts lead to concrete actions
4. **Honest Reflection**: Don't skip learning from failures
5. **Iterative Improvement**: Use reflections in next iteration

## Comparison with Other Patterns

| Pattern | Focus | Strength |
|---------|-------|----------|
| TAR | Reasoning + Learning | Adaptive problem solving |
| ReAct | Reasoning + Acting | Simpler, no reflection |
| Chain-of-Thought | Reasoning only | Good for analysis |
| Trial-and-Error | Acting only | Fast but no planning |

## Advanced Usage

### Custom Reasoning Strategies
```python
class ScientificThinkNode(ThinkNode):
    def think(self, context):
        # Hypothesis formation
        hypothesis = self.form_hypothesis(context)
        # Experiment design
        experiment = self.design_experiment(hypothesis)
        return {"hypothesis": hypothesis, "experiment": experiment}
```

### Multi-Level Reflection
```python
class DeepReflectNode(ReflectNode):
    def reflect(self, outcome):
        # Immediate reflection
        tactical = self.reflect_tactical(outcome)
        # Strategic reflection
        strategic = self.reflect_strategic(tactical)
        # Meta-reflection
        meta = self.reflect_on_reflection_process(strategic)
        return {"tactical": tactical, "strategic": strategic, "meta": meta}
```

## Metrics and Monitoring

Track TAR performance:
- **Thinking Time**: How long analysis takes
- **Action Success Rate**: How often actions succeed
- **Learning Curve**: Improvement over iterations
- **Reflection Quality**: Depth of insights gained