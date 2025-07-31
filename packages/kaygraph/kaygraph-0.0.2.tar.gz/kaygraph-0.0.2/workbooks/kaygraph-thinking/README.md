# KayGraph Chain-of-Thought Reasoning

This workbook demonstrates how to implement Chain-of-Thought (CoT) reasoning using KayGraph. It shows how to solve complex problems through structured, iterative thinking with self-evaluation.

## What it does

The Chain-of-Thought approach:
1. Breaks down complex problems into manageable steps
2. Maintains a hierarchical plan with status tracking
3. Evaluates previous reasoning before proceeding
4. Self-corrects when errors are found
5. Tracks progress through structured thoughts

## How to run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your LLM (edit `utils/call_llm.py`):
   - Add your API key and preferred LLM service
   - The example includes a placeholder implementation

3. Run with the default probability problem:
```bash
python main.py
```

4. Or provide your own problem:
```bash
python main.py "What is the optimal strategy for the Monty Hall problem? Prove it mathematically."
```

## How it works

### Graph Structure
```
StartNode → ChainOfThoughtNode ⟲ (self-loop)
                     ↓
                  EndNode
```

### Key Components

1. **StartNode**: Initializes the thinking process with a basic plan
2. **ChainOfThoughtNode**: 
   - Self-looping node that executes one thought per iteration
   - Uses structured YAML responses from the LLM
   - Updates the plan based on progress
   - Decides whether more thinking is needed
3. **EndNode**: Captures and displays the final solution

### Features Used from KayGraph

- **MetricsNode**: Tracks execution time and retry statistics
- **Retry mechanism**: Handles LLM failures gracefully
- **Enhanced logging**: Detailed execution traces
- **Node IDs**: Better tracking of execution flow

### Example Problems

Try these problems to see the Chain-of-Thought in action:

1. **Probability**: "A bag contains 3 red balls and 2 blue balls. If we draw 2 balls without replacement, what's the probability both are red?"

2. **Logic Puzzle**: "Three boxes are labeled 'Apples', 'Oranges', and 'Mixed'. Each label is wrong. You can pick one fruit from one box. How do you correctly label all boxes?"

3. **Algorithm Design**: "Design an efficient algorithm to find the kth largest element in an unsorted array. Analyze its time complexity."

## Customization

- Modify the initial plan structure in `StartNode`
- Adjust the prompt template in `ChainOfThoughtNode`
- Add domain-specific evaluation criteria
- Implement different termination conditions

## Performance

The example uses KayGraph's `MetricsNode` to track:
- Execution time per thought
- Number of retries needed
- Total thoughts generated

This helps optimize the reasoning process and identify bottlenecks.