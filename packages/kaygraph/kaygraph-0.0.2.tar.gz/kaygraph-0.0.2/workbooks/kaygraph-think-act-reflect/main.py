#!/usr/bin/env python3
"""
Main example for Think-Act-Reflect pattern in KayGraph.
"""

import argparse
import json
import logging
from pathlib import Path
import time

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph, Node
from tar_nodes import ThinkNode, ActNode, ReflectNode, MemoryNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TARController(Node):
    """Controller node that manages TAR iterations."""
    
    def __init__(self, max_iterations: int = 3):
        super().__init__(node_id="controller")
        self.max_iterations = max_iterations
        self.current_iteration = 0
    
    def prep(self, shared):
        """Check if we should continue iterating."""
        return {
            "iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "last_reflection": shared.get("reflection", {})
        }
    
    def exec(self, context):
        """Decide whether to continue."""
        self.current_iteration += 1
        
        # Check termination conditions
        if self.current_iteration >= self.max_iterations:
            return {"continue": False, "reason": "max_iterations_reached"}
        
        # Check if last iteration was successful
        reflection = context.get("last_reflection", {})
        if reflection.get("success", False):
            return {"continue": False, "reason": "success"}
        
        return {"continue": True, "reason": "iterate"}
    
    def post(self, shared, prep_res, decision):
        """Update shared context and determine next action."""
        shared["iteration"] = self.current_iteration
        shared["continue"] = decision["continue"]
        
        logger.info(f"🔄 Iteration {self.current_iteration}: {decision['reason']}")
        
        if decision["continue"]:
            return "think"  # Start next iteration
        else:
            return "complete"  # End the process


class CompletionNode(Node):
    """Final node that summarizes the TAR process."""
    
    def exec(self, shared):
        """Create final summary."""
        iterations = shared.get("iteration", 1)
        reflection = shared.get("reflection", {})
        memory_stats = shared.get("memory_stats", {})
        
        summary = {
            "task": shared.get("task"),
            "iterations": iterations,
            "final_success": reflection.get("success", False),
            "final_outcome": reflection.get("outcome", "No outcome"),
            "lessons_learned": reflection.get("lessons_learned", []),
            "next_steps": reflection.get("next_steps", []),
            "memories_created": memory_stats.get("total", 0),
            "execution_time": time.time() - shared.get("start_time", time.time())
        }
        
        return summary
    
    def post(self, shared, prep_res, summary):
        """Store and display final summary."""
        shared["summary"] = summary
        
        print("\n" + "="*60)
        print("🎯 THINK-ACT-REFLECT SUMMARY")
        print("="*60)
        print(f"Task: {summary['task']}")
        print(f"Iterations: {summary['iterations']}")
        print(f"Success: {'✅ Yes' if summary['final_success'] else '❌ No'}")
        print(f"Outcome: {summary['final_outcome']}")
        
        if summary['lessons_learned']:
            print(f"\n📚 Lessons Learned:")
            for lesson in summary['lessons_learned']:
                print(f"  • {lesson}")
        
        if summary['next_steps']:
            print(f"\n🚀 Next Steps:")
            for step in summary['next_steps']:
                print(f"  • {step}")
        
        print(f"\nExecution time: {summary['execution_time']:.2f}s")
        print("="*60)


def build_tar_graph(strategy="analytical", max_iterations=3, enable_memory=True):
    """Build the Think-Act-Reflect graph."""
    # Create nodes
    controller = TARController(max_iterations=max_iterations)
    think = ThinkNode(strategy=strategy)
    act = ActNode()
    reflect = ReflectNode()
    complete = CompletionNode(node_id="complete")
    
    # Create graph
    graph = Graph(start=controller)
    
    # Connect nodes
    controller - "think" >> think
    controller - "complete" >> complete
    
    think - "act" >> act
    think - "reflect" >> reflect  # Skip act if no action proposed
    
    act >> reflect
    
    # Add memory if enabled
    if enable_memory:
        memory = MemoryNode()
        reflect >> memory >> controller
    else:
        reflect >> controller
    
    return graph


def run_tar_agent(task, strategy="analytical", max_iterations=3, 
                  enable_memory=True, verbose=False):
    """Run the TAR agent on a task."""
    # Build the graph
    graph = build_tar_graph(
        strategy=strategy,
        max_iterations=max_iterations,
        enable_memory=enable_memory
    )
    
    # Prepare shared context
    shared_context = {
        "task": task,
        "current_state": {},
        "available_tools": ["search", "calculate", "analyze", "write", "experiment"],
        "constraints": {},
        "confidence": 0.5,  # Starting confidence
        "start_time": time.time()
    }
    
    # Run the graph
    logger.info(f"🚀 Starting TAR agent for task: {task}")
    graph.run(shared_context)
    
    # Export trace if verbose
    if verbose:
        trace_file = f"tar_trace_{int(time.time())}.json"
        with open(trace_file, 'w') as f:
            json.dump({
                "task": task,
                "strategy": strategy,
                "iterations": shared_context.get("iteration", 0),
                "thought_history": shared_context.get("thought_history", []),
                "reflection_history": shared_context.get("reflection_history", []),
                "summary": shared_context.get("summary", {})
            }, f, indent=2)
        logger.info(f"📄 Trace exported to: {trace_file}")
    
    return shared_context.get("summary", {})


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Think-Act-Reflect (TAR) agent"
    )
    
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="Task for the agent to complete"
    )
    
    parser.add_argument(
        "--strategy",
        choices=["analytical", "creative", "systematic"],
        default="analytical",
        help="Thinking strategy to use"
    )
    
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Maximum iterations"
    )
    
    parser.add_argument(
        "--enable-memory",
        action="store_true",
        default=True,
        help="Enable memory across iterations"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Export detailed trace"
    )
    
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Show example tasks and exit"
    )
    
    args = parser.parse_args()
    
    if args.examples:
        print("\n📝 Example TAR Tasks:")
        print("="*60)
        examples = [
            "Plan a trip to Paris for 5 days",
            "Debug why the server is running slowly",
            "Design a recommendation system",
            "Optimize this sorting algorithm",
            "Create a marketing strategy for a new product",
            "Solve the traveling salesman problem",
            "Write a blog post about AI safety"
        ]
        for example in examples:
            print(f"  • {example}")
        print("="*60)
        return
    
    # Run the agent
    summary = run_tar_agent(
        task=args.task,
        strategy=args.strategy,
        max_iterations=args.iterations,
        enable_memory=args.enable_memory,
        verbose=args.verbose
    )
    
    # Return appropriate exit code
    return 0 if summary.get("final_success", False) else 1


if __name__ == "__main__":
    exit(main())