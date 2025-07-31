# KayGraph FastAPI Background Tasks

This example demonstrates how to integrate KayGraph workflows with FastAPI background tasks, enabling asynchronous processing of long-running workflows while keeping your API responsive.

## Features

1. **Background Task Queue**: Process workflows asynchronously
2. **Progress Tracking**: Monitor task progress in real-time
3. **Task Management**: Start, stop, and query tasks
4. **Result Storage**: Retrieve results when ready
5. **WebSocket Updates**: Real-time progress notifications

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Run the server
python main.py

# Or with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   FastAPI       │────▶│  Task Queue     │────▶│  KayGraph       │
│   Endpoints     │     │  (Background)   │     │  Workflows      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ↑                       │                        │
         │                       ▼                        │
         │              ┌─────────────────┐              │
         └──────────────│  Task Storage   │◀─────────────┘
                        │  (Results/Status)│
                        └─────────────────┘
```

## API Endpoints

### Task Management
```bash
# Submit a new task
POST /tasks/
{
  "workflow": "data_processing",
  "params": {"input": "data"}
}

# Get task status
GET /tasks/{task_id}

# Get task result
GET /tasks/{task_id}/result

# Cancel a task
DELETE /tasks/{task_id}

# List all tasks
GET /tasks/
```

### Progress Tracking
```bash
# Get task progress
GET /tasks/{task_id}/progress

# Stream progress updates (SSE)
GET /tasks/{task_id}/stream

# WebSocket connection
WS /ws/{task_id}
```

## Usage Examples

### 1. Submit Long-Running Task
```python
import requests

# Submit task
response = requests.post("http://localhost:8000/tasks/", json={
    "workflow": "rag_indexing",
    "params": {
        "documents": ["doc1.pdf", "doc2.pdf"],
        "chunk_size": 500
    }
})

task_id = response.json()["task_id"]

# Check progress
progress = requests.get(f"http://localhost:8000/tasks/{task_id}/progress")
print(progress.json())
```

### 2. Monitor with WebSocket
```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/${taskId}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(`Progress: ${data.progress}% - ${data.message}`);
};
```

### 3. Server-Sent Events
```python
import sseclient

response = requests.get(
    f"http://localhost:8000/tasks/{task_id}/stream",
    stream=True
)

client = sseclient.SSEClient(response)
for event in client.events():
    print(f"Progress: {event.data}")
```

## Key Components

### 1. BackgroundTaskNode
Base node for background execution:
- Progress reporting
- Cancellation support
- Resource management
- Error handling

### 2. TaskQueueNode
Manages task queue:
- Priority scheduling
- Concurrency limits
- Task persistence
- Retry logic

### 3. TaskStorageNode
Handles task data:
- Status tracking
- Result storage
- Progress history
- Cleanup policies

### 4. ProgressReporterNode
Reports task progress:
- Percentage complete
- Step descriptions
- ETA calculations
- Performance metrics

## Workflow Examples

### 1. Data Processing Pipeline
```python
# Long-running data processing
- Load large dataset
- Validate and clean data
- Transform and enrich
- Generate reports
- Store results
```

### 2. ML Model Training
```python
# Background model training
- Prepare training data
- Initialize model
- Train with progress updates
- Evaluate performance
- Save model artifacts
```

### 3. Document Indexing
```python
# RAG indexing workflow
- Extract text from documents
- Chunk into passages
- Generate embeddings
- Build vector index
- Update search index
```

## Configuration

```python
# config.py
TASK_CONFIG = {
    "max_workers": 4,
    "task_timeout": 3600,  # 1 hour
    "result_ttl": 86400,   # 24 hours
    "max_queue_size": 100,
    "priority_levels": ["low", "normal", "high"],
    "storage_backend": "memory",  # or "redis", "database"
}
```

## Advanced Features

### 1. Task Chaining
```python
# Chain multiple tasks
task1 = submit_task("preprocess", data)
task2 = submit_task("analyze", depends_on=task1)
task3 = submit_task("report", depends_on=task2)
```

### 2. Scheduled Tasks
```python
# Schedule recurring tasks
schedule_task(
    workflow="daily_report",
    cron="0 9 * * *",  # 9 AM daily
    params={"type": "summary"}
)
```

### 3. Task Groups
```python
# Group related tasks
group = create_task_group("batch_processing")
for item in items:
    group.add_task("process_item", {"item": item})
group.execute()
```

### 4. Priority Queue
```python
# High priority tasks
submit_task(
    workflow="urgent_analysis",
    params=data,
    priority="high"
)
```

## Monitoring

### Dashboard
Access task dashboard at `http://localhost:8000/dashboard`

Features:
- Active tasks
- Queue status
- Performance metrics
- Error logs

### Metrics
```python
GET /metrics
{
  "tasks_pending": 5,
  "tasks_running": 2,
  "tasks_completed": 150,
  "avg_duration": 45.2,
  "error_rate": 0.02
}
```

## Error Handling

### Retry Logic
```python
@background_task(max_retries=3, retry_delay=60)
def process_with_retry(data):
    # Task will retry up to 3 times
    pass
```

### Dead Letter Queue
```python
# Failed tasks go to DLQ
failed_tasks = get_dead_letter_queue()
for task in failed_tasks:
    # Investigate or retry
    pass
```

## Deployment

### Production Setup
```bash
# With Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# With Docker
docker build -t kaygraph-api .
docker run -p 8000:8000 kaygraph-api

# With Kubernetes
kubectl apply -f k8s/deployment.yaml
```

### Scaling Considerations
- Use Redis for distributed task queue
- Deploy workers separately
- Implement health checks
- Set up monitoring

## Security

### Authentication
```python
# Add auth to endpoints
@app.post("/tasks/", dependencies=[Depends(verify_token)])
async def create_task(...):
    pass
```

### Rate Limiting
```python
# Limit task submissions
@app.post("/tasks/", dependencies=[Depends(rate_limit)])
async def create_task(...):
    pass
```

## Best Practices

1. **Idempotent Tasks**: Design tasks to be safely retried
2. **Progress Granularity**: Report progress at meaningful intervals
3. **Resource Limits**: Set memory and time limits
4. **Cleanup**: Remove old tasks and results
5. **Monitoring**: Track queue depth and processing times