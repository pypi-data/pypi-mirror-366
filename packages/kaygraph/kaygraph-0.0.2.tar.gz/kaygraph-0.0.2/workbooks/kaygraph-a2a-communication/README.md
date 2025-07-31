# KayGraph Agent-to-Agent (A2A) Communication

This example demonstrates how to build complex multi-agent systems where agents communicate and collaborate through KayGraph's messaging infrastructure.

## Features

1. **Message Passing**: Agents exchange typed messages
2. **Agent Registry**: Dynamic agent discovery and registration
3. **Communication Protocols**: Request-response, publish-subscribe, broadcast
4. **Coordination Patterns**: Leader election, consensus, task delegation
5. **Fault Tolerance**: Message retry, agent health monitoring

## Quick Start

```bash
# Run the multi-agent system
python main.py

# Run with specific configuration
python main.py --agents 5 --protocol consensus
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Agent A      │◀───▶│  Message Bus    │◀───▶│    Agent B      │
│  (Specialist)   │     │   & Registry    │     │  (Coordinator)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                       │                        ▲
         │                       ▼                        │
         │              ┌─────────────────┐              │
         └──────────────│    Agent C      │──────────────┘
                        │   (Worker)       │
                        └─────────────────┘
```

## Agent Types

### 1. Coordinator Agent
Manages overall workflow and delegates tasks:
```python
class CoordinatorAgent(A2AAgent):
    def handle_message(self, message):
        if message.type == "task_request":
            # Delegate to appropriate specialist
            specialist = self.find_specialist(message.task_type)
            self.send_message(specialist, message)
```

### 2. Specialist Agent
Handles specific types of tasks:
```python
class SpecialistAgent(A2AAgent):
    expertise = ["data_analysis", "nlp_processing"]
    
    def can_handle(self, task_type):
        return task_type in self.expertise
```

### 3. Worker Agent
Executes assigned tasks:
```python
class WorkerAgent(A2AAgent):
    def handle_message(self, message):
        if message.type == "work_assignment":
            result = self.execute_task(message.task)
            self.reply(message.sender, result)
```

### 4. Monitor Agent
Observes system health and performance:
```python
class MonitorAgent(A2AAgent):
    def periodic_check(self):
        for agent in self.registry.get_all_agents():
            health = self.check_health(agent)
            if not health.is_healthy:
                self.broadcast("agent_unhealthy", agent)
```

## Communication Patterns

### 1. Request-Response
```python
# Agent A requests help from Agent B
response = await agent_a.request(
    agent_b, 
    "analyze_data",
    {"data": [1, 2, 3]},
    timeout=30
)
```

### 2. Publish-Subscribe
```python
# Agent publishes to a topic
agent.publish("market_data", {
    "symbol": "AAPL",
    "price": 150.00
})

# Other agents subscribe
agent.subscribe("market_data", handle_market_update)
```

### 3. Broadcast
```python
# Agent broadcasts to all
agent.broadcast("system_alert", {
    "level": "warning",
    "message": "High memory usage"
})
```

### 4. Direct Messaging
```python
# Send direct message
agent.send_message("agent_b", {
    "type": "private_info",
    "content": "confidential data"
})
```

## Coordination Examples

### 1. Task Distribution
```python
# Coordinator distributes tasks among workers
tasks = split_workload(big_task)
for i, task in enumerate(tasks):
    worker = workers[i % len(workers)]
    coordinator.assign_task(worker, task)
```

### 2. Consensus Building
```python
# Agents vote on a decision
proposal = "increase_processing_capacity"
votes = await coordinator.collect_votes(proposal, timeout=60)
decision = majority_decision(votes)
```

### 3. Leader Election
```python
# Agents elect a leader using Raft-like algorithm
if current_leader_timeout():
    candidate = agent.become_candidate()
    votes = await candidate.request_votes()
    if votes > num_agents // 2:
        agent.become_leader()
```

### 4. Hierarchical Delegation
```python
# Multi-level task delegation
CEO → Managers → TeamLeads → Workers
```

## Message Format

```python
class Message:
    sender: str          # Agent ID
    recipient: str       # Agent ID or "broadcast"
    message_id: str      # Unique ID
    correlation_id: str  # For request-response
    timestamp: datetime
    type: str           # Message type
    payload: Dict       # Message content
    priority: int       # 0-10
    ttl: int           # Time to live
```

## Agent Lifecycle

1. **Registration**: Agent registers with the system
2. **Discovery**: Agent discovers other agents
3. **Communication**: Agent exchanges messages
4. **Coordination**: Agent participates in workflows
5. **Deregistration**: Agent leaves the system

## Advanced Features

### 1. Message Persistence
```python
# Store important messages
message_store.save(message)

# Replay messages after restart
for msg in message_store.get_unprocessed():
    agent.handle_message(msg)
```

### 2. Circuit Breaker
```python
# Prevent cascading failures
if agent_b.failure_rate > 0.5:
    circuit_breaker.open()
    # Route to backup agent
    agent_c.handle_message(message)
```

### 3. Load Balancing
```python
# Distribute load among agents
least_loaded = min(workers, key=lambda w: w.current_load)
coordinator.assign_task(least_loaded, task)
```

### 4. Message Routing
```python
# Smart routing based on capabilities
router = MessageRouter()
router.add_rule("nlp_*", specialist_agents["nlp"])
router.add_rule("data_*", specialist_agents["data"])
```

## Configuration

```python
A2A_CONFIG = {
    "message_bus": {
        "type": "in_memory",  # or "redis", "rabbitmq"
        "max_queue_size": 10000,
        "message_ttl": 3600
    },
    "registry": {
        "heartbeat_interval": 30,
        "agent_timeout": 120
    },
    "coordination": {
        "consensus_timeout": 60,
        "leader_election_interval": 300
    }
}
```

## Monitoring & Debugging

### 1. Message Tracing
```python
# Trace message flow
tracer.start_trace(message_id)
# ... message flows through agents
trace = tracer.get_trace(message_id)
print(trace.path)  # [agent_a, agent_b, agent_c]
```

### 2. Performance Metrics
```python
metrics = {
    "messages_sent": counter,
    "messages_received": counter,
    "avg_response_time": histogram,
    "active_agents": gauge
}
```

### 3. Health Checks
```python
@app.get("/health")
def health_check():
    return {
        "agents": registry.get_agent_count(),
        "healthy_agents": registry.get_healthy_count(),
        "message_queue_size": message_bus.size(),
        "uptime": system.uptime()
    }
```

## Use Cases

### 1. Distributed Data Processing
Multiple agents process different parts of a dataset in parallel.

### 2. Multi-Stage Pipeline
Agents form a pipeline where each handles a specific transformation.

### 3. Collaborative Decision Making
Agents with different expertise contribute to complex decisions.

### 4. Fault-Tolerant System
Agents monitor each other and take over failed agent's tasks.

### 5. Dynamic Scaling
System spawns new agents based on workload.

## Best Practices

1. **Message Design**: Keep messages small and focused
2. **Idempotency**: Ensure message handlers are idempotent
3. **Timeouts**: Always set reasonable timeouts
4. **Error Handling**: Implement proper retry and fallback
5. **Monitoring**: Track all agent communications
6. **Security**: Encrypt sensitive messages
7. **Testing**: Test agent failures and network partitions