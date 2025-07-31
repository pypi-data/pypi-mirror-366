"""
Chain-of-Thought nodes implementation using KayGraph.
"""

import yaml
import logging
from typing import Dict, Any, List, Optional
from kaygraph import Node, MetricsNode
from utils.call_llm import call_llm


class StartNode(Node):
    """Initialize the Chain-of-Thought process."""
    
    def exec(self, prep_res: Any) -> Dict[str, Any]:
        """Set up initial plan structure."""
        return {
            "plan": [
                {"description": "Understand the problem", "status": "Pending"},
                {"description": "Develop approach", "status": "Pending"},
                {"description": "Execute solution", "status": "Pending"},
                {"description": "Conclusion", "status": "Pending"}
            ]
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Dict[str, Any]) -> str:
        """Initialize shared state with the plan."""
        shared["thoughts"] = []
        shared["current_thought_number"] = 0
        shared["plan"] = exec_res["plan"]
        shared["solution"] = None
        self.logger.info("Chain-of-Thought process initialized")
        return "default"


class ChainOfThoughtNode(MetricsNode):
    """
    Self-looping node that implements the Chain-of-Thought reasoning.
    Uses KayGraph's MetricsNode for performance tracking.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(max_retries=2, wait=1, collect_metrics=True, *args, **kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for the next thought."""
        return {
            "problem": shared["problem"],
            "thoughts": shared["thoughts"],
            "current_thought_number": shared["current_thought_number"],
            "plan": shared.get("plan", [])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one step of chain-of-thought reasoning."""
        # Format previous thoughts
        previous_thoughts_str = self._format_previous_thoughts(prep_res["thoughts"])
        plan_str = self._format_plan(prep_res["plan"])
        
        # Construct the prompt
        prompt = f"""You are solving the following problem step by step:

{prep_res["problem"]}

Current hierarchical plan:
{plan_str}

Previous thoughts:
{previous_thoughts_str}

Instructions:
1. First, evaluate the previous thought (if any) - was the reasoning correct?
2. Execute the next "Pending" step in the plan
3. If a step is complex, break it into sub_steps
4. Update the plan with your progress
5. If you find an error, you can modify the plan

Respond in YAML format:
```yaml
evaluation: "Your evaluation of the previous thought"
plan:
  - description: "First step"
    status: "Done|Pending|Verification Needed"
    result: "Brief result if Done"
    mark: "Reason if Verification Needed"
    sub_steps:  # Optional, for complex steps
      - description: "Sub-step"
        status: "Done|Pending"
        result: "Result if done"
step_executed: "Which step you executed"
step_result: "Detailed result of the step"
next_thought_needed: true|false
```

If the "Conclusion" step is done, set next_thought_needed to false."""

        # Call LLM
        response = call_llm(prompt)
        
        # Parse YAML response
        try:
            # Extract YAML content between ```yaml and ```
            yaml_start = response.find("```yaml")
            yaml_end = response.find("```", yaml_start + 7)
            if yaml_start != -1 and yaml_end != -1:
                yaml_content = response[yaml_start + 7:yaml_end].strip()
            else:
                yaml_content = response.strip()
            
            parsed = yaml.safe_load(yaml_content)
            
            # Validate required fields
            required_fields = ["evaluation", "plan", "step_executed", "step_result", "next_thought_needed"]
            for field in required_fields:
                if field not in parsed:
                    raise ValueError(f"Missing required field: {field}")
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            # Return a fallback response
            return {
                "evaluation": "Error parsing response",
                "plan": prep_res["plan"],
                "step_executed": "Error",
                "step_result": f"Failed to parse LLM response: {str(e)}",
                "next_thought_needed": True
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Update shared state with the new thought."""
        # Create thought record
        thought = {
            "thought_number": prep_res["current_thought_number"] + 1,
            "evaluation": exec_res["evaluation"],
            "step_executed": exec_res["step_executed"],
            "step_result": exec_res["step_result"],
            "plan_after": exec_res["plan"]
        }
        
        # Update shared state
        shared["thoughts"].append(thought)
        shared["current_thought_number"] += 1
        shared["plan"] = exec_res["plan"]
        
        # Check if we're done
        if not exec_res["next_thought_needed"]:
            # Extract solution from the conclusion step
            for step in exec_res["plan"]:
                if step["description"] == "Conclusion" and step["status"] == "Done":
                    shared["solution"] = step.get("result", exec_res["step_result"])
                    break
            self.logger.info(f"Chain-of-Thought completed after {thought['thought_number']} thoughts")
            return "done"
        else:
            self.logger.info(f"Thought {thought['thought_number']} completed, continuing...")
            return "continue"
    
    def _format_previous_thoughts(self, thoughts: List[Dict[str, Any]]) -> str:
        """Format previous thoughts for the prompt."""
        if not thoughts:
            return "No previous thoughts."
        
        formatted = []
        for thought in thoughts[-3:]:  # Show last 3 thoughts
            formatted.append(f"""
Thought {thought['thought_number']}:
- Evaluation: {thought['evaluation']}
- Step executed: {thought['step_executed']}
- Result: {thought['step_result']}""")
        
        return "\n".join(formatted)
    
    def _format_plan(self, plan: List[Dict[str, Any]], indent: int = 0) -> str:
        """Format the hierarchical plan."""
        formatted = []
        for i, step in enumerate(plan):
            prefix = "  " * indent + f"{i+1}."
            status = f"[{step['status']}]"
            desc = step['description']
            
            line = f"{prefix} {status} {desc}"
            if step.get('result'):
                line += f" -> {step['result']}"
            elif step.get('mark'):
                line += f" (Note: {step['mark']})"
            
            formatted.append(line)
            
            # Format sub-steps if present
            if step.get('sub_steps'):
                formatted.append(self._format_plan(step['sub_steps'], indent + 1))
        
        return "\n".join(formatted)
    
    def exec_fallback(self, prep_res: Dict[str, Any], exc: Exception) -> Dict[str, Any]:
        """Fallback when exec fails."""
        self.logger.warning(f"Exec failed, using fallback: {exc}")
        return {
            "evaluation": "Previous execution failed",
            "plan": prep_res["plan"],
            "step_executed": "Error recovery",
            "step_result": f"Encountered error: {str(exc)}. Attempting to continue.",
            "next_thought_needed": True
        }


class EndNode(Node):
    """Finalize the Chain-of-Thought process."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare final results."""
        return {
            "solution": shared.get("solution", "No solution found"),
            "total_thoughts": shared["current_thought_number"],
            "metrics": None
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Format final output."""
        return f"""
Chain-of-Thought Reasoning Complete!

Total thoughts: {prep_res['total_thoughts']}

Final Solution:
{prep_res['solution']}
"""
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> None:
        """Log completion."""
        self.logger.info("Chain-of-Thought process ended successfully")
        print(exec_res)
        
        # If the previous node was a MetricsNode, show stats
        if shared.get("cot_node"):
            stats = shared["cot_node"].get_stats()
            if stats.get("total_executions"):
                print("\nPerformance Metrics:")
                print(f"- Total executions: {stats['total_executions']}")
                print(f"- Average time per thought: {stats['avg_execution_time']:.2f}s")
                print(f"- Total retries: {stats['total_retries']}")
        
        return None