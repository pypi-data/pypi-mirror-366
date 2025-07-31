"""
Chain-of-Thought reasoning example using KayGraph.

This example demonstrates how to solve complex problems using structured
step-by-step reasoning with self-evaluation and plan updates.
"""

import sys
import logging
from graph import create_chain_of_thought_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Default problem
DEFAULT_PROBLEM = """
We have a standard 6-sided die. We want to roll it repeatedly until we get the sequence
"3, 4, 5" in consecutive rolls. What is the expected number of rolls needed?

For example:
- Rolling "1, 3, 4, 5" would take 4 rolls
- Rolling "3, 4, 2, 3, 4, 5" would take 6 rolls
- Rolling "3, 4, 4, 5" would not work (we need consecutive 3,4,5)

Solve this step by step using Markov chain analysis.
"""


def main():
    """Run the Chain-of-Thought reasoning example."""
    # Get problem from command line or use default
    if len(sys.argv) > 1:
        problem = " ".join(sys.argv[1:])
    else:
        problem = DEFAULT_PROBLEM.strip()
    
    print("Chain-of-Thought Reasoning with KayGraph")
    print("=" * 50)
    print(f"Problem: {problem}")
    print("=" * 50)
    print()
    
    # Create the graph
    graph, cot_node = create_chain_of_thought_graph()
    
    # Initialize shared state
    shared = {
        "problem": problem,
        "cot_node": cot_node  # Store reference for metrics
    }
    
    try:
        # Run the graph
        final_action = graph.run(shared)
        print(f"\nGraph execution completed with final action: {final_action}")
        
    except Exception as e:
        logging.error(f"Error during execution: {e}")
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())