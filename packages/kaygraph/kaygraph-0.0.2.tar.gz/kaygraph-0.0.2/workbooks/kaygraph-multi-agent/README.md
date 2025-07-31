# KayGraph Multi-Agent System

This workbook demonstrates how to build a multi-agent system using KayGraph where specialized agents collaborate asynchronously to complete complex tasks.

## What it does

The multi-agent system features:
- **Supervisor Agent**: Coordinates and delegates tasks
- **Research Agent**: Gathers information and analysis
- **Writer Agent**: Creates content based on research
- **Reviewer Agent**: Reviews and improves output
- **Message Queue**: Asynchronous communication between agents
- **Shared Workspace**: Collaborative data sharing

## How to run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure LLM integration (in `utils/agent_prompts.py`):
   - Replace mock responses with actual LLM calls
   - Or keep mocks for testing

3. Run with a task:
```bash
python main.py "Write a blog post about renewable energy"
```

4. Run demo mode:
```bash
python main.py --demo
```

## How it works

### Architecture

```
┌─────────────────┐
│   Supervisor    │ ← Coordinates all agents
└────────┬────────┘
         │
    ┌────┴────┬──────────┬────────┐
    ↓         ↓          ↓        ↓
┌────────┐ ┌────────┐ ┌────────┐ Message
│Research│ │ Writer │ │Reviewer│  Queue
└────────┘ └────────┘ └────────┘    ↕
    ↓         ↓          ↓      Workspace
    └─────────┴──────────┘
         Shared Data
```

### Key Components

1. **MultiAgentCoordinator**:
   - Runs all agents concurrently
   - Manages iteration cycles
   - Monitors task completion

2. **Message Queue**:
   - Async message passing
   - Agent-to-agent communication
   - Task assignments and completions

3. **Shared Workspace**:
   - Common data storage
   - Research findings
   - Draft content
   - Review feedback

4. **Agent Lifecycle**:
   - Wait for messages
   - Process assignments
   - Execute tasks
   - Share results

### Execution Flow

1. **Initialization**: Task is provided to the system
2. **Planning**: Supervisor creates delegation plan
3. **Research Phase**: Researcher gathers information
4. **Writing Phase**: Writer creates content using research
5. **Review Phase**: Reviewer evaluates and improves
6. **Completion**: Final output is assembled

### Features from KayGraph

- **AsyncNode**: All agents run asynchronously
- **AsyncGraph**: Coordinates async execution
- **Self-looping**: Coordinator iterates until complete
- **Message passing**: Through shared state

## Agent Behaviors

### Supervisor Agent
- Analyzes the main task
- Creates delegation plan
- Monitors progress
- Triggers next phases

### Research Agent
- Receives research assignments
- Gathers relevant information
- Provides structured findings
- Shares via workspace

### Writer Agent
- Uses research findings
- Creates structured content
- Follows style guidelines
- Produces drafts

### Reviewer Agent
- Evaluates content quality
- Checks accuracy
- Suggests improvements
- Approves final version

## Customization

### Add New Agent Types

```python
class FactCheckerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="factchecker",
            capabilities="Verify facts and citations"
        )
    
    async def exec_async(self, prep_res):
        # Implement fact checking logic
        pass
```

### Custom Communication Patterns

1. **Broadcast**: Send to all agents
2. **Pipeline**: Sequential processing
3. **Voting**: Consensus mechanisms
4. **Hierarchical**: Multi-level supervision

### Enhanced Workspace

Add features like:
- Version control for drafts
- Conflict resolution
- Access control
- Audit trails

## Example Output

```
🤖 Multi-Agent System Starting
📋 Task: Write a blog post about AI safety
============================================================

🔄 Agents working...

Multi-Agent Task Completion Report
=====================================

Original Task: Write a blog post about AI safety

Agent Contributions:
-------------------

Supervisor Agent:
Created delegation plan for research, writing, and review phases

Researcher Agent:
Research Findings:
1. Key Facts:
   - AI safety focuses on ensuring AI systems are beneficial
   - Major concerns include alignment and control
   - Current research explores various safety approaches

Writer Agent:
[Title: Navigating the Future: AI Safety Essentials]
Introduction: As AI becomes more powerful...
[Full article content]

Reviewer Agent:
Review Assessment:
Overall Rating: Good (8/10)
Strengths: Well-researched, clear structure
Recommendations: APPROVE with minor edits

Task Status: Completed Successfully

✅ Multi-agent task completed
📊 Execution Statistics:
   - Total iterations: 7
   - Agents involved: supervisor, researcher, writer, reviewer
```

## Advanced Patterns

### 1. Parallel Research
Multiple research agents investigate different aspects simultaneously

### 2. Iterative Refinement
Writer and reviewer collaborate through multiple rounds

### 3. Specialized Teams
Groups of agents for different domains (technical, creative, analytical)

### 4. Dynamic Agent Creation
Supervisor spawns new agents based on task requirements

## Performance Considerations

1. **Async Execution**: Agents work concurrently
2. **Message Batching**: Process multiple messages per iteration
3. **Workspace Optimization**: Efficient data structures
4. **Iteration Limits**: Prevent infinite loops
5. **Resource Management**: Control agent concurrency

## Debugging Tips

- Enable detailed logging for message flow
- Monitor workspace state changes
- Track iteration counts
- Visualize agent interactions
- Add checkpoints for long tasks