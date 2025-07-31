#!/usr/bin/env python3
"""
Finite State Machine nodes for KayGraph with Streamlit integration.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, ValidatedNode

logger = logging.getLogger(__name__)


@dataclass
class StateTransition:
    """Represents a state transition."""
    from_state: str
    to_state: str
    condition: Optional[Callable] = None
    action: Optional[Callable] = None
    timestamp: Optional[float] = None
    
    def can_transition(self, context: Dict[str, Any]) -> bool:
        """Check if transition is allowed."""
        if self.condition:
            return self.condition(context)
        return True


@dataclass
class State:
    """Represents a state in the FSM."""
    name: str
    description: str = ""
    on_enter: Optional[Callable] = None
    on_exit: Optional[Callable] = None
    data: Dict[str, Any] = field(default_factory=dict)
    is_final: bool = False
    timeout: Optional[int] = None  # seconds
    
    def enter(self, context: Dict[str, Any]):
        """Execute on_enter callback."""
        if self.on_enter:
            logger.info(f"🔵 Entering state: {self.name}")
            self.on_enter(context)
    
    def exit(self, context: Dict[str, Any]):
        """Execute on_exit callback."""
        if self.on_exit:
            logger.info(f"🔴 Exiting state: {self.name}")
            self.on_exit(context)


class FSMNode(ValidatedNode):
    """Base Finite State Machine node."""
    
    def __init__(self, 
                 states: List[str],
                 transitions: Dict[str, List[str]],
                 initial_state: str = None):
        super().__init__(node_id="fsm")
        
        # Initialize states
        self.states: Dict[str, State] = {}
        for state_name in states:
            self.states[state_name] = State(name=state_name)
        
        # Initialize transitions
        self.transitions: Dict[str, List[StateTransition]] = {}
        for from_state, to_states in transitions.items():
            self.transitions[from_state] = []
            for to_state in to_states:
                transition = StateTransition(from_state=from_state, to_state=to_state)
                self.transitions[from_state].append(transition)
        
        # Set initial state
        self.initial_state = initial_state or states[0]
        self.current_state = self.initial_state
        self.history: List[StateTransition] = []
        self.context: Dict[str, Any] = {}
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate FSM input."""
        if "action" in data and data["action"] not in ["transition", "reset", "get_state"]:
            raise ValueError(f"Invalid action: {data['action']}")
        return data
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare FSM operation."""
        return {
            "action": shared.get("fsm_action", "get_state"),
            "target_state": shared.get("target_state"),
            "context": shared.get("fsm_context", {})
        }
    
    def exec(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute FSM operation."""
        action = request["action"]
        self.context.update(request["context"])
        
        if action == "transition":
            return self._handle_transition(request["target_state"])
        elif action == "reset":
            return self._handle_reset()
        elif action == "get_state":
            return self._get_current_state()
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _handle_transition(self, target_state: str) -> Dict[str, Any]:
        """Handle state transition."""
        if target_state not in self.states:
            return {
                "success": False,
                "error": f"Unknown state: {target_state}",
                "current_state": self.current_state
            }
        
        # Check if transition is allowed
        if not self._can_transition_to(target_state):
            return {
                "success": False,
                "error": f"Cannot transition from {self.current_state} to {target_state}",
                "current_state": self.current_state,
                "allowed_transitions": self.get_allowed_transitions()
            }
        
        # Find the transition
        transition = self._find_transition(self.current_state, target_state)
        if transition and not transition.can_transition(self.context):
            return {
                "success": False,
                "error": "Transition condition not met",
                "current_state": self.current_state
            }
        
        # Execute transition
        old_state = self.current_state
        
        # Exit current state
        self.states[self.current_state].exit(self.context)
        
        # Execute transition action
        if transition and transition.action:
            transition.action(self.context)
        
        # Enter new state
        self.current_state = target_state
        self.states[self.current_state].enter(self.context)
        
        # Record in history
        completed_transition = StateTransition(
            from_state=old_state,
            to_state=target_state,
            timestamp=time.time()
        )
        self.history.append(completed_transition)
        
        logger.info(f"🔄 Transitioned from {old_state} to {target_state}")
        
        return {
            "success": True,
            "previous_state": old_state,
            "current_state": self.current_state,
            "allowed_transitions": self.get_allowed_transitions(),
            "is_final": self.states[self.current_state].is_final
        }
    
    def _handle_reset(self) -> Dict[str, Any]:
        """Reset FSM to initial state."""
        old_state = self.current_state
        self.current_state = self.initial_state
        self.history.clear()
        self.context.clear()
        
        logger.info(f"🔁 Reset FSM from {old_state} to {self.initial_state}")
        
        return {
            "success": True,
            "previous_state": old_state,
            "current_state": self.current_state,
            "allowed_transitions": self.get_allowed_transitions()
        }
    
    def _get_current_state(self) -> Dict[str, Any]:
        """Get current FSM state info."""
        return {
            "current_state": self.current_state,
            "state_data": self.states[self.current_state].data,
            "is_final": self.states[self.current_state].is_final,
            "allowed_transitions": self.get_allowed_transitions(),
            "history_length": len(self.history),
            "context": self.context
        }
    
    def _can_transition_to(self, target_state: str) -> bool:
        """Check if transition to target state is allowed."""
        if self.current_state not in self.transitions:
            return False
        
        for transition in self.transitions[self.current_state]:
            if transition.to_state == target_state:
                return True
        return False
    
    def _find_transition(self, from_state: str, to_state: str) -> Optional[StateTransition]:
        """Find specific transition."""
        if from_state not in self.transitions:
            return None
        
        for transition in self.transitions[from_state]:
            if transition.to_state == to_state:
                return transition
        return None
    
    def get_allowed_transitions(self) -> List[str]:
        """Get list of allowed transitions from current state."""
        if self.current_state not in self.transitions:
            return []
        
        allowed = []
        for transition in self.transitions[self.current_state]:
            if transition.can_transition(self.context):
                allowed.append(transition.to_state)
        
        return allowed
    
    def add_state_callback(self, state: str, on_enter: Callable = None, on_exit: Callable = None):
        """Add callbacks to a state."""
        if state in self.states:
            if on_enter:
                self.states[state].on_enter = on_enter
            if on_exit:
                self.states[state].on_exit = on_exit
    
    def add_transition_condition(self, from_state: str, to_state: str, condition: Callable):
        """Add condition to a transition."""
        transition = self._find_transition(from_state, to_state)
        if transition:
            transition.condition = condition
    
    def post(self, shared: Dict[str, Any], request: Dict, result: Dict[str, Any]) -> str:
        """Store FSM result."""
        shared["fsm_result"] = result
        shared["fsm_current_state"] = self.current_state
        shared["fsm_context"] = self.context
        
        # Determine next action based on state
        if result.get("is_final"):
            return "complete"
        elif result.get("error"):
            return "error"
        else:
            return "continue"


class StreamlitFSMNode(FSMNode):
    """Streamlit-specific FSM node with UI helpers."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui_config = {
            "show_diagram": True,
            "show_history": True,
            "show_context": False,
            "auto_refresh": True
        }
    
    def get_diagram_data(self) -> Dict[str, Any]:
        """Get data for diagram visualization."""
        nodes = []
        edges = []
        
        # Create nodes
        for state_name, state in self.states.items():
            node = {
                "id": state_name,
                "label": state_name,
                "description": state.description,
                "is_current": state_name == self.current_state,
                "is_final": state.is_final,
                "style": self._get_node_style(state_name)
            }
            nodes.append(node)
        
        # Create edges
        for from_state, transitions in self.transitions.items():
            for transition in transitions:
                edge = {
                    "from": from_state,
                    "to": transition.to_state,
                    "label": "",
                    "style": self._get_edge_style(from_state, transition.to_state)
                }
                edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "current_state": self.current_state,
            "layout": "hierarchical"
        }
    
    def _get_node_style(self, state: str) -> Dict[str, str]:
        """Get node styling based on state."""
        if state == self.current_state:
            return {"fill": "#4CAF50", "stroke": "#2E7D32", "stroke_width": "3"}
        elif state in self.get_allowed_transitions():
            return {"fill": "#2196F3", "stroke": "#1565C0", "stroke_width": "2"}
        elif self.states[state].is_final:
            return {"fill": "#9E9E9E", "stroke": "#616161", "stroke_width": "2"}
        else:
            return {"fill": "#E0E0E0", "stroke": "#9E9E9E", "stroke_width": "1"}
    
    def _get_edge_style(self, from_state: str, to_state: str) -> Dict[str, str]:
        """Get edge styling based on states."""
        if from_state == self.current_state and to_state in self.get_allowed_transitions():
            return {"stroke": "#2196F3", "stroke_width": "2", "arrow_size": "10"}
        else:
            return {"stroke": "#BDBDBD", "stroke_width": "1", "arrow_size": "8"}
    
    def get_history_timeline(self) -> List[Dict[str, Any]]:
        """Get history in timeline format."""
        timeline = []
        
        for i, transition in enumerate(self.history):
            entry = {
                "index": i,
                "from": transition.from_state,
                "to": transition.to_state,
                "timestamp": datetime.fromtimestamp(transition.timestamp).strftime("%H:%M:%S"),
                "duration": 0
            }
            
            # Calculate duration to next transition
            if i < len(self.history) - 1:
                entry["duration"] = self.history[i + 1].timestamp - transition.timestamp
            
            timeline.append(entry)
        
        return timeline
    
    def get_progress(self) -> float:
        """Calculate progress through FSM (0.0 to 1.0)."""
        if not self.states:
            return 0.0
        
        # Simple progress: how many unique states visited
        visited_states = set([t.from_state for t in self.history])
        visited_states.add(self.current_state)
        
        return len(visited_states) / len(self.states)


class WorkflowFSMNode(StreamlitFSMNode):
    """FSM node specifically for workflow management."""
    
    def __init__(self):
        # Define workflow states
        states = ["draft", "review", "approved", "published", "archived"]
        
        # Define transitions
        transitions = {
            "draft": ["review", "archived"],
            "review": ["approved", "draft", "archived"],
            "approved": ["published", "review", "archived"],
            "published": ["archived"],
            "archived": []
        }
        
        super().__init__(states=states, transitions=transitions, initial_state="draft")
        
        # Add descriptions
        self.states["draft"].description = "Initial draft state"
        self.states["review"].description = "Under review"
        self.states["approved"].description = "Approved for publication"
        self.states["published"].description = "Published and live"
        self.states["archived"].description = "Archived (final state)"
        self.states["archived"].is_final = True
        
        # Add callbacks
        self.add_state_callback("published", on_enter=self._on_publish)
        self.add_state_callback("review", on_enter=self._on_review)
    
    def _on_publish(self, context: Dict[str, Any]):
        """Called when entering published state."""
        context["published_at"] = datetime.now().isoformat()
        logger.info("📢 Workflow published!")
    
    def _on_review(self, context: Dict[str, Any]):
        """Called when entering review state."""
        context["review_started_at"] = datetime.now().isoformat()
        context["review_count"] = context.get("review_count", 0) + 1
        logger.info(f"👀 Review #{context['review_count']} started")


class FormStateMachine(StreamlitFSMNode):
    """FSM for multi-step forms."""
    
    def __init__(self, form_steps: List[str]):
        # Create states from form steps
        states = form_steps + ["complete", "cancelled"]
        
        # Create transitions (linear with ability to go back)
        transitions = {}
        for i, step in enumerate(form_steps):
            transitions[step] = []
            if i > 0:
                transitions[step].append(form_steps[i-1])  # Previous
            if i < len(form_steps) - 1:
                transitions[step].append(form_steps[i+1])  # Next
            else:
                transitions[step].append("complete")  # Final step
            transitions[step].append("cancelled")  # Can always cancel
        
        transitions["complete"] = []
        transitions["cancelled"] = []
        
        super().__init__(states=states, transitions=transitions, initial_state=form_steps[0])
        
        # Mark final states
        self.states["complete"].is_final = True
        self.states["cancelled"].is_final = True
        
        # Add validation
        for i, step in enumerate(form_steps[:-1]):
            next_step = form_steps[i+1]
            self.add_transition_condition(
                step, 
                next_step,
                lambda ctx, s=step: self._validate_step(ctx, s)
            )
    
    def _validate_step(self, context: Dict[str, Any], step: str) -> bool:
        """Validate form step data."""
        step_data = context.get(f"{step}_data", {})
        
        # Add your validation logic here
        if not step_data:
            logger.warning(f"❌ No data for step: {step}")
            return False
        
        return True
    
    def save_step_data(self, step: str, data: Dict[str, Any]):
        """Save data for a form step."""
        self.context[f"{step}_data"] = data
        self.states[step].data = data
        logger.info(f"💾 Saved data for step: {step}")
    
    def get_all_form_data(self) -> Dict[str, Any]:
        """Get all collected form data."""
        form_data = {}
        for key, value in self.context.items():
            if key.endswith("_data"):
                step_name = key.replace("_data", "")
                form_data[step_name] = value
        return form_data


if __name__ == "__main__":
    # Test FSM nodes
    
    # Test basic FSM
    fsm = FSMNode(
        states=["idle", "running", "paused", "stopped"],
        transitions={
            "idle": ["running"],
            "running": ["paused", "stopped"],
            "paused": ["running", "stopped"],
            "stopped": []
        },
        initial_state="idle"
    )
    
    shared = {"fsm_action": "get_state"}
    result = fsm.run(shared)
    print(f"Initial state: {result}")
    
    # Test transition
    shared = {"fsm_action": "transition", "target_state": "running"}
    result = fsm.run(shared)
    print(f"After transition: {result}")
    
    # Test workflow FSM
    workflow = WorkflowFSMNode()
    shared = {"fsm_action": "transition", "target_state": "review"}
    result = workflow.run(shared)
    print(f"\nWorkflow state: {result}")
    
    # Test form FSM
    form = FormStateMachine(["personal_info", "contact", "preferences", "review"])
    form.save_step_data("personal_info", {"name": "John", "age": 30})
    
    shared = {"fsm_action": "transition", "target_state": "contact"}
    result = form.run(shared)
    print(f"\nForm state: {result}")
    print(f"Form data: {form.get_all_form_data()}")