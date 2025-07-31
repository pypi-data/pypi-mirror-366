#!/usr/bin/env python3
"""
Streamlit app for FSM visualization and interaction.
"""

import streamlit as st
import graphviz
import json
import time
from pathlib import Path
from datetime import datetime

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Graph
from fsm_nodes import (
    FSMNode, StreamlitFSMNode, WorkflowFSMNode, 
    FormStateMachine
)

# Page config
st.set_page_config(
    page_title="KayGraph FSM Demo",
    page_icon="🔄",
    layout="wide"
)

# Initialize session state
if 'fsm' not in st.session_state:
    st.session_state.fsm = None
if 'fsm_type' not in st.session_state:
    st.session_state.fsm_type = None
if 'shared_context' not in st.session_state:
    st.session_state.shared_context = {}


def create_fsm_diagram(fsm: StreamlitFSMNode) -> graphviz.Digraph:
    """Create Graphviz diagram from FSM."""
    dot = graphviz.Digraph(comment='FSM')
    dot.attr(rankdir='LR')
    
    diagram_data = fsm.get_diagram_data()
    
    # Add nodes
    for node in diagram_data['nodes']:
        style = node['style']
        shape = 'doublecircle' if node['is_final'] else 'circle'
        
        dot.node(
            node['id'], 
            node['label'],
            shape=shape,
            style='filled',
            fillcolor=style['fill'],
            color=style['stroke'],
            penwidth=style['stroke_width']
        )
    
    # Add edges
    for edge in diagram_data['edges']:
        style = edge['style']
        dot.edge(
            edge['from'], 
            edge['to'],
            color=style['stroke'],
            penwidth=style['stroke_width']
        )
    
    return dot


def render_fsm_controls(fsm: StreamlitFSMNode):
    """Render FSM control buttons."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Get allowed transitions
        allowed = fsm.get_allowed_transitions()
        
        if allowed:
            st.write("**Available Transitions:**")
            for state in allowed:
                if st.button(f"Go to {state}", key=f"trans_{state}"):
                    shared = {
                        "fsm_action": "transition",
                        "target_state": state,
                        "fsm_context": st.session_state.shared_context
                    }
                    result = fsm.run(shared)
                    
                    if result.get("success"):
                        st.success(f"✅ Transitioned to {state}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Transition failed')}")
        else:
            st.info("No transitions available from current state")
    
    with col2:
        if st.button("🔄 Reset FSM"):
            shared = {"fsm_action": "reset"}
            fsm.run(shared)
            st.session_state.shared_context = {}
            st.rerun()
    
    with col3:
        if st.button("🔃 Refresh"):
            st.rerun()


def render_fsm_info(fsm: StreamlitFSMNode):
    """Render FSM information."""
    shared = {"fsm_action": "get_state"}
    state_info = fsm.run(shared)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Current State", state_info['current_state'])
        progress = fsm.get_progress()
        st.progress(progress)
        st.caption(f"Progress: {progress*100:.0f}%")
    
    with col2:
        st.metric("Transitions Made", state_info['history_length'])
        if state_info.get('is_final'):
            st.success("✅ Final state reached")


def render_workflow_demo():
    """Render workflow FSM demo."""
    st.header("📄 Document Workflow FSM")
    
    if st.session_state.fsm is None or st.session_state.fsm_type != 'workflow':
        st.session_state.fsm = WorkflowFSMNode()
        st.session_state.fsm_type = 'workflow'
    
    fsm = st.session_state.fsm
    
    # Info section
    render_fsm_info(fsm)
    
    # Diagram
    st.subheader("State Diagram")
    diagram = create_fsm_diagram(fsm)
    st.graphviz_chart(diagram.source)
    
    # Controls
    st.subheader("Controls")
    render_fsm_controls(fsm)
    
    # Context
    if st.checkbox("Show Context"):
        st.json(fsm.context)
    
    # History
    if st.checkbox("Show History"):
        timeline = fsm.get_history_timeline()
        if timeline:
            st.subheader("Transition History")
            for entry in timeline:
                st.write(f"{entry['timestamp']}: {entry['from']} → {entry['to']}")


def render_form_demo():
    """Render multi-step form FSM demo."""
    st.header("📝 Multi-Step Form FSM")
    
    if st.session_state.fsm is None or st.session_state.fsm_type != 'form':
        form_steps = ["personal_info", "contact", "preferences", "review"]
        st.session_state.fsm = FormStateMachine(form_steps)
        st.session_state.fsm_type = 'form'
    
    fsm = st.session_state.fsm
    
    # Get current state
    shared = {"fsm_action": "get_state"}
    state_info = fsm.run(shared)
    current_state = state_info['current_state']
    
    # Progress bar
    progress = fsm.get_progress()
    st.progress(progress)
    st.caption(f"Step {int(progress * len(fsm.states))} of {len(fsm.states)}")
    
    # Render form based on current state
    if current_state == "personal_info":
        st.subheader("Step 1: Personal Information")
        with st.form("personal_info_form"):
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            
            if st.form_submit_button("Next"):
                fsm.save_step_data("personal_info", {"name": name, "age": age})
                shared = {
                    "fsm_action": "transition",
                    "target_state": "contact",
                    "fsm_context": fsm.context
                }
                result = fsm.run(shared)
                if result.get("success"):
                    st.rerun()
    
    elif current_state == "contact":
        st.subheader("Step 2: Contact Information")
        with st.form("contact_form"):
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Previous"):
                    shared = {"fsm_action": "transition", "target_state": "personal_info"}
                    fsm.run(shared)
                    st.rerun()
            with col2:
                if st.form_submit_button("Next"):
                    fsm.save_step_data("contact", {"email": email, "phone": phone})
                    shared = {
                        "fsm_action": "transition",
                        "target_state": "preferences",
                        "fsm_context": fsm.context
                    }
                    result = fsm.run(shared)
                    if result.get("success"):
                        st.rerun()
    
    elif current_state == "preferences":
        st.subheader("Step 3: Preferences")
        with st.form("preferences_form"):
            notifications = st.checkbox("Email notifications")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Previous"):
                    shared = {"fsm_action": "transition", "target_state": "contact"}
                    fsm.run(shared)
                    st.rerun()
            with col2:
                if st.form_submit_button("Next"):
                    fsm.save_step_data("preferences", {
                        "notifications": notifications,
                        "theme": theme
                    })
                    shared = {
                        "fsm_action": "transition",
                        "target_state": "review",
                        "fsm_context": fsm.context
                    }
                    result = fsm.run(shared)
                    if result.get("success"):
                        st.rerun()
    
    elif current_state == "review":
        st.subheader("Step 4: Review & Submit")
        
        # Show all collected data
        form_data = fsm.get_all_form_data()
        st.json(form_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Previous"):
                shared = {"fsm_action": "transition", "target_state": "preferences"}
                fsm.run(shared)
                st.rerun()
        with col2:
            if st.button("Cancel"):
                shared = {"fsm_action": "transition", "target_state": "cancelled"}
                fsm.run(shared)
                st.rerun()
        with col3:
            if st.button("Submit", type="primary"):
                shared = {"fsm_action": "transition", "target_state": "complete"}
                fsm.run(shared)
                st.rerun()
    
    elif current_state == "complete":
        st.success("✅ Form submitted successfully!")
        st.balloons()
        if st.button("Start New Form"):
            shared = {"fsm_action": "reset"}
            fsm.run(shared)
            st.rerun()
    
    elif current_state == "cancelled":
        st.warning("❌ Form cancelled")
        if st.button("Start Again"):
            shared = {"fsm_action": "reset"}
            fsm.run(shared)
            st.rerun()
    
    # Show diagram
    with st.expander("View State Diagram"):
        diagram = create_fsm_diagram(fsm)
        st.graphviz_chart(diagram.source)


def render_custom_demo():
    """Render custom FSM builder."""
    st.header("🛠️ Custom FSM Builder")
    
    with st.form("custom_fsm_form"):
        st.subheader("Define States")
        states_input = st.text_area(
            "States (one per line)",
            value="start\nprocessing\ncomplete\nerror",
            height=100
        )
        
        st.subheader("Define Transitions")
        st.caption("Format: from_state -> to_state1, to_state2")
        transitions_input = st.text_area(
            "Transitions",
            value="start -> processing, error\nprocessing -> complete, error\nerror -> start",
            height=100
        )
        
        if st.form_submit_button("Create FSM"):
            # Parse states
            states = [s.strip() for s in states_input.strip().split('\n') if s.strip()]
            
            # Parse transitions
            transitions = {}
            for line in transitions_input.strip().split('\n'):
                if '->' in line:
                    from_state, to_states = line.split('->')
                    from_state = from_state.strip()
                    to_states = [s.strip() for s in to_states.split(',')]
                    transitions[from_state] = to_states
            
            # Create FSM
            try:
                st.session_state.fsm = StreamlitFSMNode(
                    states=states,
                    transitions=transitions,
                    initial_state=states[0]
                )
                st.session_state.fsm_type = 'custom'
                st.success("✅ Custom FSM created!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating FSM: {e}")
    
    # If custom FSM exists, show it
    if st.session_state.fsm and st.session_state.fsm_type == 'custom':
        st.divider()
        render_fsm_info(st.session_state.fsm)
        
        diagram = create_fsm_diagram(st.session_state.fsm)
        st.graphviz_chart(diagram.source)
        
        render_fsm_controls(st.session_state.fsm)


def main():
    """Main Streamlit app."""
    st.title("🔄 KayGraph FSM with Streamlit")
    st.caption("Interactive Finite State Machine demonstrations")
    
    # Sidebar
    with st.sidebar:
        st.header("FSM Demos")
        demo_type = st.radio(
            "Select Demo",
            ["Workflow", "Multi-Step Form", "Custom FSM"]
        )
        
        st.divider()
        
        # Info
        st.info(
            "FSMs help manage complex workflows with clear states "
            "and transitions. Perfect for forms, approval processes, "
            "and state-driven applications."
        )
    
    # Main content
    if demo_type == "Workflow":
        render_workflow_demo()
    elif demo_type == "Multi-Step Form":
        render_form_demo()
    elif demo_type == "Custom FSM":
        render_custom_demo()


if __name__ == "__main__":
    main()