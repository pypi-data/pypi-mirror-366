import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from .redis_backend import RedisBackend

logger = logging.getLogger(__name__)

app = FastAPI()

# Store active websocket connections
active_connections: List[WebSocket] = []

# Redis backend for monitoring
redis_backend: RedisBackend = None

# Cache for dashboard data
dashboard_cache = {
    "events": [],
    "metrics": {},
    "active_nodes": set(),
    "active_workflows": set(),
    "network_graph": {"nodes": [], "edges": []}
}


async def initialize_redis(host: str = "localhost", port: int = 6379):
    """Initialize Redis connection"""
    global redis_backend
    redis_backend = RedisBackend(host=host, port=port)
    await redis_backend.connect()
    
    # Start monitoring Redis events
    asyncio.create_task(monitor_redis_events())


async def monitor_redis_events():
    """Monitor Redis for new events"""
    try:
        # Subscribe to all events
        pubsub = await redis_backend.subscribe_to_events()
        
        while True:
            try:
                # Get message with timeout
                message = await asyncio.wait_for(
                    pubsub.get_message(ignore_subscribe_messages=True),
                    timeout=0.1
                )
                
                if message and message["type"] == "message":
                    event_json = message["data"]
                    if isinstance(event_json, bytes):
                        event_json = event_json.decode()
                    
                    event = json.loads(event_json)
                    await process_event(event)
                    
            except asyncio.TimeoutError:
                # Update metrics periodically
                await update_metrics()
                
            except Exception as e:
                logger.error(f"Error monitoring Redis: {e}")
                await asyncio.sleep(1)
                
    except Exception as e:
        logger.error(f"Redis monitoring failed: {e}")


async def process_event(event: Dict[str, Any]):
    """Process incoming monitoring event"""
    # Add to events cache (keep last 1000)
    dashboard_cache["events"].append(event)
    if len(dashboard_cache["events"]) > 1000:
        dashboard_cache["events"] = dashboard_cache["events"][-1000:]
    
    # Update network graph
    update_network_graph(event)
    
    # Send to all connected clients
    await broadcast_event(event)


async def update_metrics():
    """Update dashboard metrics from Redis"""
    try:
        metrics = await redis_backend.get_metrics()
        active_nodes = await redis_backend.get_active_nodes()
        active_workflows = await redis_backend.get_active_workflows()
        
        dashboard_cache["metrics"] = metrics
        dashboard_cache["active_nodes"] = active_nodes
        dashboard_cache["active_workflows"] = active_workflows
        
        # Broadcast metrics update
        await broadcast_metrics()
        
    except Exception as e:
        logger.error(f"Failed to update metrics: {e}")


def update_network_graph(event: Dict[str, Any]):
    """Update network graph based on event"""
    nodes = dashboard_cache["network_graph"]["nodes"]
    edges = dashboard_cache["network_graph"]["edges"]
    
    node_id = event.get("node_id")
    node_type = event.get("node_type")
    event_name = event.get("event_name")
    
    # Add node if not exists
    node_exists = any(n["id"] == node_id for n in nodes)
    if not node_exists and node_id:
        nodes.append({
            "id": node_id,
            "label": node_type,
            "status": "idle",
            "metrics": {}
        })
    
    # Update node status based on event
    for node in nodes:
        if node["id"] == node_id:
            if event_name == "node_started":
                node["status"] = "running"
            elif event_name == "node_completed":
                node["status"] = "completed"
            elif event_name in ["node_failed", "exec_failed"]:
                node["status"] = "error"
            
            # Update node metrics
            if event["event_type"] == "metric":
                node["metrics"].update(event.get("data", {}))
    
    # Add edges based on workflow progression
    if event_name == "node_completed":
        next_action = event.get("data", {}).get("next_action")
        if next_action and next_action != "None":
            # This is simplified - in real implementation would track actual transitions
            edge_id = f"{node_id}->{next_action}"
            if not any(e["id"] == edge_id for e in edges):
                edges.append({
                    "id": edge_id,
                    "source": node_id,
                    "target": next_action,
                    "label": next_action
                })


async def broadcast_event(event: Dict[str, Any]):
    """Broadcast event to all connected clients"""
    message = json.dumps({
        "type": "event",
        "data": event,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    await broadcast_message(message)


async def broadcast_metrics():
    """Broadcast metrics update to all clients"""
    message = json.dumps({
        "type": "metrics",
        "data": {
            "metrics": dashboard_cache["metrics"],
            "active_nodes": list(dashboard_cache["active_nodes"]),
            "active_workflows": list(dashboard_cache["active_workflows"]),
            "network_graph": dashboard_cache["network_graph"]
        },
        "timestamp": datetime.utcnow().isoformat()
    })
    
    await broadcast_message(message)


async def broadcast_message(message: str):
    """Send message to all connected WebSocket clients"""
    disconnected = []
    
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    # Send initial state
    initial_state = {
        "type": "initial",
        "data": {
            "events": dashboard_cache["events"][-100:],  # Last 100 events
            "metrics": dashboard_cache["metrics"],
            "active_nodes": list(dashboard_cache["active_nodes"]),
            "active_workflows": list(dashboard_cache["active_workflows"]),
            "network_graph": dashboard_cache["network_graph"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await websocket.send_text(json.dumps(initial_state))
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Handle client commands
            try:
                command = json.loads(data)
                if command.get("type") == "get_workflow_events":
                    workflow_id = command.get("workflow_id")
                    if workflow_id:
                        events = await redis_backend.get_events_by_workflow(workflow_id)
                        await websocket.send_text(json.dumps({
                            "type": "workflow_events",
                            "workflow_id": workflow_id,
                            "events": events
                        }))
            except:
                pass
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.get("/")
async def get_dashboard():
    """Serve dashboard HTML"""
    return HTMLResponse(content=dashboard_html, status_code=200)


@app.get("/api/metrics")
async def get_metrics():
    """REST endpoint for current metrics"""
    await update_metrics()
    return {
        "metrics": dashboard_cache["metrics"],
        "active_nodes": list(dashboard_cache["active_nodes"]),
        "active_workflows": list(dashboard_cache["active_workflows"]),
        "event_count": len(dashboard_cache["events"])
    }


@app.get("/api/events")
async def get_events(limit: int = 100):
    """REST endpoint for recent events"""
    return {
        "events": dashboard_cache["events"][-limit:],
        "total": len(dashboard_cache["events"])
    }


@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection on startup"""
    await initialize_redis()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if redis_backend:
        await redis_backend.disconnect()


# Dashboard HTML with real-time visualization
dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>KayGraph Real-time Monitoring</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: auto 400px auto;
            gap: 20px;
            padding: 20px;
            height: calc(100vh - 80px);
        }
        .card {
            background: #2a2a2a;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            grid-column: 1 / -1;
        }
        .metric-card {
            background: #3a3a3a;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            border: 1px solid #4a4a4a;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: #667eea;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin: 5px 0;
        }
        .metric-label {
            color: #b0b0b0;
            font-size: 12px;
            text-transform: uppercase;
        }
        #network-graph {
            height: 100%;
            border: 1px solid #4a4a4a;
            border-radius: 8px;
        }
        #events-log {
            height: 100%;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .event-item {
            padding: 8px;
            border-bottom: 1px solid #3a3a3a;
            transition: background-color 0.3s;
        }
        .event-item:hover {
            background-color: #3a3a3a;
        }
        .event-lifecycle { border-left: 3px solid #4CAF50; }
        .event-data { border-left: 3px solid #2196F3; }
        .event-error { border-left: 3px solid #f44336; }
        .event-metric { border-left: 3px solid #FF9800; }
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            z-index: 1000;
        }
        .status-connected {
            background: #4CAF50;
            color: white;
        }
        .status-disconnected {
            background: #f44336;
            color: white;
        }
        .active-list {
            max-height: 200px;
            overflow-y: auto;
        }
        .active-item {
            padding: 5px 10px;
            margin: 2px 0;
            background: #3a3a3a;
            border-radius: 4px;
            font-size: 14px;
        }
        h3 {
            margin-top: 0;
            color: #667eea;
            border-bottom: 2px solid #4a4a4a;
            padding-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>KayGraph Real-time Monitoring Dashboard</h1>
        <p>Monitor your workflow execution in real-time</p>
    </div>
    
    <div class="connection-status" id="connection-status">
        Connecting...
    </div>
    
    <div class="container">
        <!-- Metrics Cards -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Events</div>
                <div class="metric-value" id="total-events">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Active Nodes</div>
                <div class="metric-value" id="active-nodes">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Active Workflows</div>
                <div class="metric-value" id="active-workflows">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value" id="success-rate">0%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Errors</div>
                <div class="metric-value" id="error-count">0</div>
            </div>
        </div>
        
        <!-- Network Graph -->
        <div class="card">
            <h3>Workflow Network</h3>
            <div id="network-graph"></div>
        </div>
        
        <!-- Events Log -->
        <div class="card">
            <h3>Live Events</h3>
            <div id="events-log"></div>
        </div>
        
        <!-- Active Items -->
        <div class="card" style="grid-column: 1;">
            <h3>Active Nodes</h3>
            <div class="active-list" id="active-nodes-list"></div>
        </div>
        
        <div class="card" style="grid-column: 2;">
            <h3>Active Workflows</h3>
            <div class="active-list" id="active-workflows-list"></div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let network = null;
        let nodes = new vis.DataSet();
        let edges = new vis.DataSet();
        let eventCount = 0;
        
        function connect() {
            ws = new WebSocket('ws://localhost:8080/ws');
            
            ws.onopen = function() {
                console.log('Connected to monitoring server');
                updateConnectionStatus(true);
            };
            
            ws.onclose = function() {
                console.log('Disconnected from monitoring server');
                updateConnectionStatus(false);
                // Reconnect after 3 seconds
                setTimeout(connect, 3000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                handleMessage(message);
            };
        }
        
        function handleMessage(message) {
            switch(message.type) {
                case 'initial':
                    initializeDashboard(message.data);
                    break;
                case 'event':
                    handleEvent(message.data);
                    break;
                case 'metrics':
                    updateMetrics(message.data);
                    break;
            }
        }
        
        function initializeDashboard(data) {
            // Initialize network graph
            initializeNetwork();
            
            // Load initial events
            data.events.forEach(event => addEventToLog(event));
            
            // Update metrics
            updateMetrics(data);
            
            // Update network graph
            if (data.network_graph) {
                updateNetworkGraph(data.network_graph);
            }
        }
        
        function initializeNetwork() {
            const container = document.getElementById('network-graph');
            const data = { nodes: nodes, edges: edges };
            const options = {
                physics: {
                    enabled: true,
                    barnesHut: {
                        gravitationalConstant: -2000,
                        centralGravity: 0.3,
                        springLength: 120
                    }
                },
                nodes: {
                    shape: 'box',
                    font: { color: '#ffffff' },
                    borderWidth: 2
                },
                edges: {
                    arrows: 'to',
                    color: { color: '#667eea', highlight: '#764ba2' },
                    font: { color: '#ffffff' }
                }
            };
            
            network = new vis.Network(container, data, options);
        }
        
        function handleEvent(event) {
            addEventToLog(event);
            updateNodeStatus(event);
            eventCount++;
            document.getElementById('total-events').textContent = eventCount;
        }
        
        function addEventToLog(event) {
            const log = document.getElementById('events-log');
            const eventDiv = document.createElement('div');
            eventDiv.className = `event-item event-${event.event_type}`;
            
            const time = new Date(event.timestamp).toLocaleTimeString();
            eventDiv.innerHTML = `
                <strong>${time}</strong> 
                [${event.node_id}] 
                ${event.event_name}
                ${event.data.error ? ' - ' + event.data.error : ''}
            `;
            
            log.insertBefore(eventDiv, log.firstChild);
            
            // Keep only last 100 events in UI
            while (log.children.length > 100) {
                log.removeChild(log.lastChild);
            }
        }
        
        function updateNodeStatus(event) {
            const nodeId = event.node_id;
            const existingNode = nodes.get(nodeId);
            
            let color = '#4a4a4a';  // Default gray
            if (event.event_name === 'node_started') {
                color = '#2196F3';  // Blue for running
            } else if (event.event_name === 'node_completed') {
                color = '#4CAF50';  // Green for completed
            } else if (event.event_type === 'error') {
                color = '#f44336';  // Red for error
            }
            
            if (existingNode) {
                nodes.update({ id: nodeId, color: { background: color } });
            } else {
                nodes.add({
                    id: nodeId,
                    label: event.node_type,
                    color: { background: color, border: '#667eea' }
                });
            }
            
            // Add edge if there's a next action
            if (event.data.next_action && event.data.next_action !== 'None') {
                const edgeId = `${nodeId}-${event.data.next_action}`;
                if (!edges.get(edgeId)) {
                    edges.add({
                        id: edgeId,
                        from: nodeId,
                        to: event.data.next_action,
                        label: event.data.next_action
                    });
                }
            }
        }
        
        function updateMetrics(data) {
            // Update metric cards
            document.getElementById('active-nodes').textContent = 
                data.active_nodes ? data.active_nodes.length : 0;
            document.getElementById('active-workflows').textContent = 
                data.active_workflows ? data.active_workflows.length : 0;
            
            if (data.metrics) {
                const total = Object.values(data.metrics).reduce((a, b) => a + b, 0);
                const errors = data.metrics.error || 0;
                const successRate = total > 0 ? ((total - errors) / total * 100).toFixed(1) : 100;
                
                document.getElementById('error-count').textContent = errors;
                document.getElementById('success-rate').textContent = successRate + '%';
            }
            
            // Update active lists
            updateActiveList('active-nodes-list', data.active_nodes || []);
            updateActiveList('active-workflows-list', data.active_workflows || []);
            
            // Update network graph
            if (data.network_graph) {
                updateNetworkGraph(data.network_graph);
            }
        }
        
        function updateActiveList(elementId, items) {
            const list = document.getElementById(elementId);
            list.innerHTML = '';
            
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'active-item';
                div.textContent = item;
                list.appendChild(div);
            });
        }
        
        function updateNetworkGraph(graphData) {
            // Update nodes
            graphData.nodes.forEach(node => {
                const existing = nodes.get(node.id);
                if (!existing) {
                    nodes.add({
                        id: node.id,
                        label: node.label,
                        color: getNodeColor(node.status)
                    });
                } else {
                    nodes.update({
                        id: node.id,
                        color: getNodeColor(node.status)
                    });
                }
            });
            
            // Update edges
            graphData.edges.forEach(edge => {
                if (!edges.get(edge.id)) {
                    edges.add(edge);
                }
            });
        }
        
        function getNodeColor(status) {
            const colors = {
                idle: { background: '#4a4a4a', border: '#667eea' },
                running: { background: '#2196F3', border: '#667eea' },
                completed: { background: '#4CAF50', border: '#667eea' },
                error: { background: '#f44336', border: '#667eea' }
            };
            return colors[status] || colors.idle;
        }
        
        function updateConnectionStatus(connected) {
            const status = document.getElementById('connection-status');
            if (connected) {
                status.textContent = 'Connected';
                status.className = 'connection-status status-connected';
            } else {
                status.textContent = 'Disconnected';
                status.className = 'connection-status status-disconnected';
            }
        }
        
        // Initialize connection
        connect();
    </script>
</body>
</html>
"""


def run_dashboard(host: str = "0.0.0.0", port: int = 8080):
    """Run the monitoring dashboard"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_dashboard()