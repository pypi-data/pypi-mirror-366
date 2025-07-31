#!/usr/bin/env python3
"""
Think-Act-Reflect (TAR) pattern nodes for KayGraph.
Implements cognitive architecture for reasoning agents.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, ValidatedNode

logger = logging.getLogger(__name__)


@dataclass
class Thought:
    """Represents a reasoning step."""
    content: str
    confidence: float
    reasoning_type: str  # analytical, creative, systematic
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "confidence": self.confidence,
            "reasoning_type": self.reasoning_type,
            "timestamp": self.timestamp
        }


@dataclass
class Action:
    """Represents an action to take."""
    name: str
    parameters: Dict[str, Any]
    expected_outcome: str
    risk_level: str  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "parameters": self.parameters,
            "expected_outcome": self.expected_outcome,
            "risk_level": self.risk_level
        }


@dataclass
class Reflection:
    """Represents a reflection on outcomes."""
    outcome: str
    success: bool
    lessons_learned: List[str]
    confidence_adjustment: float
    next_steps: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome": self.outcome,
            "success": self.success,
            "lessons_learned": self.lessons_learned,
            "confidence_adjustment": self.confidence_adjustment,
            "next_steps": self.next_steps
        }


class ThinkNode(ValidatedNode):
    """Node that analyzes situations and plans actions."""
    
    def __init__(self, 
                 strategy: str = "analytical",
                 max_depth: int = 5,
                 confidence_threshold: float = 0.7):
        super().__init__(node_id="think")
        self.strategy = strategy
        self.max_depth = max_depth
        self.confidence_threshold = confidence_threshold
        self.thought_history: List[Thought] = []
    
    def validate_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate thinking context."""
        required = ["task", "current_state"]
        for field in required:
            if field not in context:
                raise ValueError(f"Missing required field: {field}")
        return context
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for thinking."""
        return {
            "task": shared.get("task"),
            "current_state": shared.get("current_state", {}),
            "previous_thoughts": shared.get("thought_history", []),
            "available_tools": shared.get("available_tools", []),
            "constraints": shared.get("constraints", {})
        }
    
    def exec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute thinking process."""
        logger.info(f"🤔 Thinking about: {context['task']}")
        
        thoughts = []
        actions = []
        
        # Apply reasoning strategy
        if self.strategy == "analytical":
            thoughts, actions = self._analytical_thinking(context)
        elif self.strategy == "creative":
            thoughts, actions = self._creative_thinking(context)
        elif self.strategy == "systematic":
            thoughts, actions = self._systematic_thinking(context)
        else:
            thoughts, actions = self._default_thinking(context)
        
        # Filter by confidence
        confident_thoughts = [t for t in thoughts if t.confidence >= self.confidence_threshold]
        
        # Select best action
        best_action = self._select_best_action(actions, confident_thoughts)
        
        return {
            "thoughts": confident_thoughts,
            "proposed_action": best_action,
            "reasoning_chain": self._build_reasoning_chain(confident_thoughts),
            "confidence": self._calculate_overall_confidence(confident_thoughts)
        }
    
    def _analytical_thinking(self, context: Dict[str, Any]) -> tuple:
        """Analytical reasoning approach."""
        thoughts = []
        
        # Break down the problem
        thought = Thought(
            content=f"Breaking down task: {context['task']}",
            confidence=0.9,
            reasoning_type="analytical"
        )
        thoughts.append(thought)
        
        # Analyze current state
        if context['current_state']:
            thought = Thought(
                content=f"Current state analysis: {json.dumps(context['current_state'], indent=2)}",
                confidence=0.85,
                reasoning_type="analytical"
            )
            thoughts.append(thought)
        
        # Consider constraints
        if context['constraints']:
            thought = Thought(
                content=f"Constraints to consider: {context['constraints']}",
                confidence=0.8,
                reasoning_type="analytical"
            )
            thoughts.append(thought)
        
        # Generate actions based on analysis
        actions = []
        if "search" in context.get('available_tools', []):
            actions.append(Action(
                name="search",
                parameters={"query": context['task']},
                expected_outcome="Gather relevant information",
                risk_level="low"
            ))
        
        return thoughts, actions
    
    def _creative_thinking(self, context: Dict[str, Any]) -> tuple:
        """Creative reasoning approach."""
        thoughts = []
        
        # Lateral thinking
        thought = Thought(
            content=f"What if we approach '{context['task']}' from a different angle?",
            confidence=0.7,
            reasoning_type="creative"
        )
        thoughts.append(thought)
        
        # Generate creative solutions
        thought = Thought(
            content="Exploring unconventional solutions...",
            confidence=0.75,
            reasoning_type="creative"
        )
        thoughts.append(thought)
        
        actions = []
        # Creative actions might involve experimentation
        actions.append(Action(
            name="experiment",
            parameters={"approach": "novel", "task": context['task']},
            expected_outcome="Discover new possibilities",
            risk_level="medium"
        ))
        
        return thoughts, actions
    
    def _systematic_thinking(self, context: Dict[str, Any]) -> tuple:
        """Systematic step-by-step reasoning."""
        thoughts = []
        actions = []
        
        # Step-by-step approach
        steps = [
            "1. Define the problem clearly",
            "2. Gather all relevant information",
            "3. List possible solutions",
            "4. Evaluate each solution",
            "5. Select the best approach"
        ]
        
        for i, step in enumerate(steps):
            thought = Thought(
                content=f"{step} for task: {context['task']}",
                confidence=0.9 - (i * 0.05),  # Confidence decreases slightly with each step
                reasoning_type="systematic"
            )
            thoughts.append(thought)
        
        # Systematic action
        actions.append(Action(
            name="execute_plan",
            parameters={"steps": steps, "task": context['task']},
            expected_outcome="Complete task systematically",
            risk_level="low"
        ))
        
        return thoughts, actions
    
    def _default_thinking(self, context: Dict[str, Any]) -> tuple:
        """Default thinking when no specific strategy."""
        thoughts = [
            Thought(
                content=f"Considering task: {context['task']}",
                confidence=0.7,
                reasoning_type="default"
            )
        ]
        
        actions = [
            Action(
                name="process",
                parameters={"task": context['task']},
                expected_outcome="Complete the task",
                risk_level="medium"
            )
        ]
        
        return thoughts, actions
    
    def _select_best_action(self, actions: List[Action], thoughts: List[Thought]) -> Optional[Action]:
        """Select the best action based on thoughts."""
        if not actions:
            return None
        
        # Simple selection: prefer low-risk actions with high confidence thoughts
        best_action = min(actions, key=lambda a: (
            {"low": 0, "medium": 1, "high": 2}[a.risk_level],
            -len([t for t in thoughts if a.name in t.content.lower()])
        ))
        
        return best_action
    
    def _build_reasoning_chain(self, thoughts: List[Thought]) -> str:
        """Build a reasoning chain from thoughts."""
        chain = []
        for thought in thoughts:
            chain.append(f"[{thought.reasoning_type}] {thought.content}")
        return " → ".join(chain)
    
    def _calculate_overall_confidence(self, thoughts: List[Thought]) -> float:
        """Calculate overall confidence from thoughts."""
        if not thoughts:
            return 0.0
        return sum(t.confidence for t in thoughts) / len(thoughts)
    
    def post(self, shared: Dict[str, Any], context: Dict, result: Dict[str, Any]) -> str:
        """Store thinking results."""
        shared["thinking_result"] = result
        shared["proposed_action"] = result.get("proposed_action")
        
        # Update thought history
        self.thought_history.extend(result.get("thoughts", []))
        shared["thought_history"] = [t.to_dict() for t in self.thought_history[-10:]]  # Keep last 10
        
        logger.info(f"💭 Thinking complete. Confidence: {result.get('confidence', 0):.2f}")
        
        if result.get("proposed_action"):
            return "act"  # Proceed to action
        else:
            return "reflect"  # Skip to reflection if no action


class ActNode(Node):
    """Node that executes planned actions."""
    
    def __init__(self, available_tools: Optional[List[str]] = None):
        super().__init__(node_id="act", max_retries=3, wait=1)
        self.available_tools = available_tools or ["search", "calculate", "analyze", "write"]
    
    def prep(self, shared: Dict[str, Any]) -> Optional[Action]:
        """Get the action to execute."""
        action_dict = shared.get("proposed_action")
        if not action_dict:
            return None
        
        # Convert dict to Action if needed
        if isinstance(action_dict, dict):
            return Action(**action_dict)
        return action_dict
    
    def exec(self, action: Optional[Action]) -> Dict[str, Any]:
        """Execute the planned action."""
        if not action:
            logger.warning("No action to execute")
            return {"status": "no_action", "result": None}
        
        logger.info(f"🎯 Executing action: {action.name}")
        
        # Simulate action execution based on type
        if action.name == "search":
            result = self._execute_search(action.parameters)
        elif action.name == "calculate":
            result = self._execute_calculate(action.parameters)
        elif action.name == "analyze":
            result = self._execute_analyze(action.parameters)
        elif action.name == "write":
            result = self._execute_write(action.parameters)
        elif action.name == "experiment":
            result = self._execute_experiment(action.parameters)
        else:
            result = self._execute_generic(action)
        
        return {
            "status": "completed",
            "action": action.to_dict(),
            "result": result,
            "execution_time": time.time()
        }
    
    def _execute_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search action."""
        query = params.get("query", "")
        logger.info(f"🔍 Searching for: {query}")
        
        # Simulate search results
        return {
            "query": query,
            "results": [
                {"title": f"Result 1 for {query}", "relevance": 0.9},
                {"title": f"Result 2 for {query}", "relevance": 0.7},
                {"title": f"Result 3 for {query}", "relevance": 0.5}
            ],
            "total": 3
        }
    
    def _execute_calculate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calculation action."""
        expression = params.get("expression", "")
        logger.info(f"🧮 Calculating: {expression}")
        
        try:
            # Simple evaluation (in production, use safe math parser)
            result = eval(expression)
            return {"expression": expression, "result": result, "error": None}
        except Exception as e:
            return {"expression": expression, "result": None, "error": str(e)}
    
    def _execute_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis action."""
        data = params.get("data", {})
        logger.info(f"📊 Analyzing data...")
        
        # Simulate analysis
        return {
            "data_points": len(str(data)),
            "patterns_found": ["pattern1", "pattern2"],
            "insights": ["Data shows increasing trend", "Anomaly detected at point 5"]
        }
    
    def _execute_write(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute write action."""
        content = params.get("content", "")
        filename = params.get("filename", "output.txt")
        
        logger.info(f"✍️ Writing to {filename}")
        
        # Simulate writing
        return {
            "filename": filename,
            "bytes_written": len(content),
            "status": "success"
        }
    
    def _execute_experiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute experimental action."""
        approach = params.get("approach", "standard")
        logger.info(f"🧪 Experimenting with {approach} approach")
        
        # Simulate experiment
        import random
        success = random.random() > 0.3  # 70% success rate
        
        return {
            "approach": approach,
            "success": success,
            "findings": "Interesting results" if success else "Experiment failed",
            "data": {"metric1": random.random(), "metric2": random.random()}
        }
    
    def _execute_generic(self, action: Action) -> Dict[str, Any]:
        """Execute generic action."""
        logger.info(f"⚡ Executing generic action: {action.name}")
        return {
            "action": action.name,
            "parameters": action.parameters,
            "status": "completed"
        }
    
    def exec_fallback(self, action: Optional[Action], exc: Exception) -> Dict[str, Any]:
        """Fallback when action fails."""
        logger.error(f"Action failed: {exc}")
        return {
            "status": "failed",
            "action": action.to_dict() if action else None,
            "error": str(exc),
            "fallback": True
        }
    
    def post(self, shared: Dict[str, Any], action: Optional[Action], result: Dict[str, Any]) -> None:
        """Store action results."""
        shared["action_result"] = result
        shared["last_action"] = action.to_dict() if action else None
        
        status = result.get("status", "unknown")
        logger.info(f"✅ Action {status}")


class ReflectNode(ValidatedNode):
    """Node that reflects on outcomes and learns."""
    
    def __init__(self, learning_rate: float = 0.1):
        super().__init__(node_id="reflect")
        self.learning_rate = learning_rate
        self.reflection_history: List[Reflection] = []
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare reflection context."""
        return {
            "task": shared.get("task"),
            "thinking_result": shared.get("thinking_result", {}),
            "action_result": shared.get("action_result", {}),
            "previous_reflections": shared.get("reflection_history", [])
        }
    
    def exec(self, context: Dict[str, Any]) -> Reflection:
        """Reflect on the outcomes."""
        logger.info("🪞 Reflecting on outcomes...")
        
        # Analyze what happened
        action_result = context.get("action_result", {})
        thinking_result = context.get("thinking_result", {})
        
        # Determine success
        success = self._evaluate_success(action_result, thinking_result)
        
        # Extract lessons
        lessons = self._extract_lessons(action_result, thinking_result, success)
        
        # Calculate confidence adjustment
        confidence_adj = self._calculate_confidence_adjustment(success, thinking_result)
        
        # Determine next steps
        next_steps = self._determine_next_steps(success, lessons, context)
        
        reflection = Reflection(
            outcome=self._summarize_outcome(action_result),
            success=success,
            lessons_learned=lessons,
            confidence_adjustment=confidence_adj,
            next_steps=next_steps
        )
        
        return reflection
    
    def _evaluate_success(self, action_result: Dict, thinking_result: Dict) -> bool:
        """Evaluate if the action was successful."""
        # Check action status
        if action_result.get("status") == "failed":
            return False
        
        # Check if action matched expected outcome
        action = action_result.get("action", {})
        expected = action.get("expected_outcome", "")
        
        # Simple success check
        return action_result.get("status") == "completed"
    
    def _extract_lessons(self, action_result: Dict, thinking_result: Dict, success: bool) -> List[str]:
        """Extract lessons from the experience."""
        lessons = []
        
        if success:
            lessons.append(f"The {thinking_result.get('reasoning_chain', 'approach')} was effective")
            
            # Learn from what worked
            if action_result.get("result"):
                lessons.append("Action produced expected results")
        else:
            lessons.append("The approach needs adjustment")
            
            # Learn from failure
            if action_result.get("error"):
                lessons.append(f"Error encountered: {action_result['error']}")
            
            if action_result.get("fallback"):
                lessons.append("Action required fallback mechanism")
        
        # Learn from confidence levels
        confidence = thinking_result.get("confidence", 0)
        if confidence > 0.9 and not success:
            lessons.append("High confidence doesn't guarantee success")
        elif confidence < 0.5 and success:
            lessons.append("Low confidence actions can still succeed")
        
        return lessons
    
    def _calculate_confidence_adjustment(self, success: bool, thinking_result: Dict) -> float:
        """Calculate how to adjust confidence based on outcome."""
        current_confidence = thinking_result.get("confidence", 0.5)
        
        if success:
            # Increase confidence, but not too much
            adjustment = self.learning_rate * (1 - current_confidence)
        else:
            # Decrease confidence
            adjustment = -self.learning_rate * current_confidence
        
        return adjustment
    
    def _determine_next_steps(self, success: bool, lessons: List[str], context: Dict) -> List[str]:
        """Determine what to do next."""
        next_steps = []
        
        if success:
            next_steps.append("Continue with current approach")
            next_steps.append("Consider optimizing successful strategy")
        else:
            next_steps.append("Revise approach based on lessons learned")
            next_steps.append("Consider alternative strategies")
            
            # Specific suggestions based on failure type
            if "timeout" in str(context.get("action_result", {})):
                next_steps.append("Increase timeout or use async approach")
            if "permission" in str(context.get("action_result", {})):
                next_steps.append("Check permissions and access rights")
        
        # Always consider iteration
        next_steps.append("Apply lessons to next iteration")
        
        return next_steps
    
    def _summarize_outcome(self, action_result: Dict) -> str:
        """Create a summary of what happened."""
        status = action_result.get("status", "unknown")
        action_name = action_result.get("action", {}).get("name", "unknown")
        
        if status == "completed":
            result = action_result.get("result", {})
            return f"Successfully executed {action_name} with result: {result}"
        elif status == "failed":
            error = action_result.get("error", "unknown error")
            return f"Failed to execute {action_name}: {error}"
        else:
            return f"Action {action_name} ended with status: {status}"
    
    def post(self, shared: Dict[str, Any], context: Dict, reflection: Reflection) -> str:
        """Store reflection results."""
        shared["reflection"] = reflection.to_dict()
        
        # Update reflection history
        self.reflection_history.append(reflection)
        shared["reflection_history"] = [r.to_dict() for r in self.reflection_history[-5:]]
        
        # Update confidence based on reflection
        if "confidence" in shared:
            shared["confidence"] += reflection.confidence_adjustment
            shared["confidence"] = max(0.1, min(1.0, shared["confidence"]))  # Clamp between 0.1 and 1.0
        
        logger.info(f"💡 Reflection complete. Success: {reflection.success}")
        logger.info(f"📝 Lessons learned: {', '.join(reflection.lessons_learned)}")
        
        # Determine if we should iterate
        if reflection.success or len(self.reflection_history) >= 3:
            return "complete"
        else:
            return "iterate"  # Go back to thinking


class MemoryNode(Node):
    """Node that manages agent memory across iterations."""
    
    def __init__(self, capacity: int = 1000):
        super().__init__(node_id="memory")
        self.capacity = capacity
        self.memories: List[Dict[str, Any]] = []
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare memory context."""
        return {
            "current_task": shared.get("task"),
            "thought_history": shared.get("thought_history", []),
            "action_result": shared.get("action_result"),
            "reflection": shared.get("reflection")
        }
    
    def exec(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store and retrieve memories."""
        # Store current experience
        if context.get("reflection"):
            memory = {
                "task": context["current_task"],
                "thoughts": context.get("thought_history", []),
                "action": context.get("action_result", {}).get("action"),
                "outcome": context.get("reflection", {}).get("outcome"),
                "lessons": context.get("reflection", {}).get("lessons_learned", []),
                "timestamp": time.time()
            }
            
            self._store_memory(memory)
        
        # Retrieve relevant memories
        relevant_memories = self._retrieve_relevant_memories(context["current_task"])
        
        return {
            "stored": True,
            "total_memories": len(self.memories),
            "relevant_memories": relevant_memories
        }
    
    def _store_memory(self, memory: Dict[str, Any]):
        """Store a memory, managing capacity."""
        self.memories.append(memory)
        
        # Remove oldest memories if over capacity
        if len(self.memories) > self.capacity:
            self.memories = self.memories[-self.capacity:]
    
    def _retrieve_relevant_memories(self, task: str, max_memories: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories relevant to current task."""
        if not task or not self.memories:
            return []
        
        # Simple relevance: memories with similar tasks
        relevant = []
        task_words = set(task.lower().split())
        
        for memory in reversed(self.memories):  # Recent memories first
            memory_task = memory.get("task", "")
            memory_words = set(memory_task.lower().split())
            
            # Calculate similarity
            similarity = len(task_words & memory_words) / max(len(task_words), 1)
            
            if similarity > 0.3:  # Threshold for relevance
                relevant.append({
                    "memory": memory,
                    "similarity": similarity
                })
        
        # Sort by similarity and return top memories
        relevant.sort(key=lambda x: x["similarity"], reverse=True)
        return [r["memory"] for r in relevant[:max_memories]]
    
    def post(self, shared: Dict[str, Any], context: Dict, result: Dict[str, Any]) -> None:
        """Update shared context with memory insights."""
        shared["memory_stats"] = {
            "total": result["total_memories"],
            "relevant": len(result["relevant_memories"])
        }
        
        # Add relevant memories to context for next iteration
        if result["relevant_memories"]:
            shared["past_experiences"] = result["relevant_memories"]
            logger.info(f"🧠 Retrieved {len(result['relevant_memories'])} relevant memories")


if __name__ == "__main__":
    # Test TAR nodes
    import asyncio
    
    # Test think node
    think_node = ThinkNode(strategy="analytical")
    shared = {
        "task": "Write a Python function to sort a list",
        "current_state": {"language": "Python", "complexity": "medium"},
        "available_tools": ["search", "write", "analyze"]
    }
    
    result = think_node.run(shared)
    print(f"Thinking result: {json.dumps(shared.get('thinking_result', {}), indent=2)}")
    
    # Test act node
    if shared.get("proposed_action"):
        act_node = ActNode()
        act_node.run(shared)
        print(f"\nAction result: {json.dumps(shared.get('action_result', {}), indent=2)}")
    
    # Test reflect node
    reflect_node = ReflectNode()
    reflect_node.run(shared)
    print(f"\nReflection: {json.dumps(shared.get('reflection', {}), indent=2)}")