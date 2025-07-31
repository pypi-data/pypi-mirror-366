# KayGraph Streamlit FSM Integration

This example demonstrates how to build interactive finite state machine (FSM) workflows with Streamlit UI, enabling visual workflow management and real-time state tracking.

## What is FSM + Streamlit?

Finite State Machines (FSM) combined with Streamlit provide:
- **Visual State Management**: See current state and possible transitions
- **Interactive Workflows**: User-driven state transitions
- **Real-time Updates**: Live workflow progress
- **Form Integration**: Collect inputs at each state
- **State Persistence**: Maintain workflow state across sessions

## Features

1. **Visual FSM Designer**: Draw and modify state machines
2. **Interactive Execution**: Click to transition between states
3. **State Visualization**: See current state highlighted
4. **Form Builder**: Dynamic forms based on state
5. **Progress Tracking**: Visual progress indicators
6. **History View**: See all state transitions

## Quick Start

```bash
# Install dependencies
pip install streamlit graphviz plotly

# Run the app
streamlit run app.py

# Or with specific port
streamlit run app.py --server.port 8080
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Streamlit UI   │────▶│   FSM Engine    │────▶│  KayGraph Node  │
│  (Frontend)     │     │  (State Logic)  │     │  (Execution)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                        Session State
```

## Example Workflows

### 1. Order Processing FSM
```
Start → Order Placed → Payment Processing → Payment Confirmed → Shipping → Delivered
                ↓                   ↓
           Order Cancelled    Payment Failed → Retry Payment
```

### 2. Document Approval FSM
```
Draft → Review → Approve → Publish
   ↑       ↓         ↓
   └── Revise ← Reject
```

### 3. User Onboarding FSM
```
Welcome → Profile Setup → Preferences → Tutorial → Active User
              ↓                            ↓
           Incomplete ←──────────────── Skip Tutorial
```

## Key Components

### 1. FSMNode
Base node for state machine logic:
- Define states and transitions
- Validate state changes
- Execute state actions

### 2. StreamlitFSMNode
Streamlit-specific FSM node:
- Render state diagram
- Handle UI interactions
- Update display in real-time

### 3. StateVisualizerNode
Visualize FSM state:
- Graphviz diagrams
- Interactive state maps
- Transition animations

### 4. FormStateNode
Dynamic form handling:
- State-specific forms
- Input validation
- Data persistence

## Usage Examples

### Basic FSM
```python
# Define states
states = ["start", "processing", "complete", "error"]

# Define transitions
transitions = {
    "start": ["processing", "error"],
    "processing": ["complete", "error"],
    "error": ["start"],
    "complete": []
}

# Create FSM
fsm = FSMNode(states=states, transitions=transitions, initial="start")
```

### Streamlit Integration
```python
import streamlit as st

# Initialize FSM in session state
if 'fsm' not in st.session_state:
    st.session_state.fsm = create_fsm()

# Display current state
st.write(f"Current State: {st.session_state.fsm.current_state}")

# Show available transitions
for next_state in st.session_state.fsm.get_transitions():
    if st.button(f"Go to {next_state}"):
        st.session_state.fsm.transition_to(next_state)
        st.rerun()
```

## Advanced Features

### 1. State Actions
```python
@fsm.on_enter("processing")
def start_processing(data):
    # Execute when entering processing state
    return process_data(data)

@fsm.on_exit("processing")
def cleanup_processing():
    # Cleanup when leaving processing state
    pass
```

### 2. Guards
```python
@fsm.guard("processing", "complete")
def can_complete(data):
    # Only allow transition if condition met
    return data.get("validated", False)
```

### 3. State Persistence
```python
# Save FSM state
fsm.save_state("workflow_123.json")

# Load FSM state
fsm.load_state("workflow_123.json")
```

## UI Components

### 1. State Diagram
- Interactive SVG diagram
- Current state highlighting
- Clickable transitions
- Zoom and pan support

### 2. Control Panel
- Transition buttons
- State information
- History timeline
- Debug console

### 3. Data Forms
- Dynamic form generation
- Multi-step wizards
- Validation feedback
- File uploads

## Configuration

```python
config = {
    "ui": {
        "theme": "light",
        "diagram_engine": "graphviz",  # or "plotly"
        "auto_refresh": True,
        "refresh_interval": 1000  # ms
    },
    "fsm": {
        "save_history": True,
        "max_history": 100,
        "allow_manual_override": False,
        "strict_transitions": True
    },
    "visualization": {
        "node_colors": {
            "active": "#4CAF50",
            "available": "#2196F3",
            "blocked": "#f44336",
            "complete": "#9E9E9E"
        }
    }
}
```

## Best Practices

1. **State Naming**: Use clear, action-oriented state names
2. **Transition Logic**: Keep transition conditions simple
3. **Error States**: Always include error handling states
4. **User Feedback**: Show clear status messages
5. **State Persistence**: Save state for long workflows

## Common Patterns

### 1. Retry Pattern
```python
fsm.add_retry_loop("processing", "error", max_retries=3)
```

### 2. Timeout Pattern
```python
fsm.add_timeout("waiting_approval", timeout=3600, timeout_state="expired")
```

### 3. Parallel States
```python
fsm.add_parallel_states(["upload", "validate", "process"])
```

## Deployment

### Local Development
```bash
streamlit run app.py --server.headless false
```

### Production
```bash
# With authentication
streamlit run app.py \
  --server.enableCORS false \
  --server.enableXsrfProtection true
```

### Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## Troubleshooting

- **State not updating**: Check session state persistence
- **Diagram not showing**: Verify graphviz installation
- **Slow transitions**: Optimize state action functions
- **Lost state**: Enable state persistence in config