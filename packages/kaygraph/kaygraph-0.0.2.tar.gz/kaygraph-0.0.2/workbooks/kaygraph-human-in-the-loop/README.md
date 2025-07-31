# KayGraph Human-in-the-Loop (HITL)

This example demonstrates how to build production-ready Human-in-the-Loop workflows using KayGraph. It shows various patterns for incorporating human feedback, approvals, and decisions into automated AI workflows.

## Features Demonstrated

1. **Human Approval Nodes**: Request and process human approvals
2. **Timeout Handling**: Automatic fallbacks when humans don't respond
3. **Multi-Channel Integration**: CLI, Web UI, and async queues
4. **Audit Trail**: Complete logging of human decisions
5. **Delegation Patterns**: Escalation and delegation workflows

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   AI Analysis   │────▶│ HumanApprovalNode│────▶│ Execute Action  │
│ (Generate Plan) │     │ (Request Review) │     │ (If Approved)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         │                       ▼                         │
         │              ┌──────────────────┐              │
         │              │ Timeout Handler  │              │
         │              │ (Fallback/Escalate)             │
         │              └──────────────────┘              │
         │                                                 │
         └─────────────────────────────────────────────────┘
                        (Retry with modifications)
```

## Usage

### CLI-Based HITL (Simple Approvals)
```bash
# Run interactive CLI approval workflow
python main_cli.py

# Run with auto-approve for testing
python main_cli.py --auto-approve

# Run with timeout (seconds)
python main_cli.py --timeout 30
```

### Web-Based HITL (Production)
```bash
# Start the FastAPI server
python main_web.py

# Access the UI at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Async Queue-Based HITL (Scale)
```bash
# Start the async processor
python main_async.py

# Submit tasks via API or queue
# Monitor at http://localhost:8001/tasks
```

## Examples

### 1. Document Approval Workflow
- AI generates a document
- Human reviews and can approve/reject/modify
- Approved documents are processed
- Rejected documents are revised by AI

### 2. Budget Authorization
- AI proposes budget allocations
- Requires human approval above thresholds
- Escalates to senior staff for large amounts
- Automatic approval for small amounts

### 3. Content Moderation
- AI flags potentially problematic content
- Human moderators review flagged items
- Decisions are logged for audit
- System learns from human feedback

## Key Concepts

### HumanApprovalNode Features
- **Timeout Configuration**: Set max wait time for human response
- **Fallback Actions**: Define what happens on timeout
- **Multiple Channels**: CLI, Web, Email, Slack, etc.
- **Context Preservation**: Full context passed to reviewers
- **Audit Logging**: Every decision is tracked

### Production Patterns
- **Escalation**: Route to different humans based on criteria
- **Delegation**: Allow humans to delegate to others
- **Batch Approvals**: Group similar requests
- **Priority Queues**: Urgent requests first
- **Load Balancing**: Distribute across team

## Integration Options

1. **CLI**: Simple command-line interface
2. **Web UI**: React/Vue frontend with FastAPI
3. **Slack/Teams**: Chat-based approvals
4. **Email**: Email with approval links
5. **Mobile**: Push notifications with actions