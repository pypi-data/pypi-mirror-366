from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from typing import List, Dict, Any
import uvicorn
from datetime import datetime

app = FastAPI()

# Store active websocket connections
active_connections: List[WebSocket] = []

# Shared metrics storage
metrics_store = {"latest": {}, "history": []}


async def send_metrics_update(metrics: Dict[str, Any]):
    """Send metrics update to all connected clients"""
    if not metrics:
        return
        
    message = json.dumps({
        "type": "metrics_update",
        "data": metrics,
        "timestamp": datetime.now().isoformat()
    })
    
    # Send to all connected clients
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
    await websocket.accept()
    active_connections.append(websocket)
    
    # Send initial metrics
    if metrics_store["latest"]:
        await websocket.send_text(json.dumps({
            "type": "initial_metrics",
            "data": metrics_store["latest"],
            "history": metrics_store["history"][-50:]  # Last 50 entries
        }))
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.get("/")
async def get():
    return HTMLResponse(content=dashboard_html, status_code=200)


@app.get("/api/metrics")
async def get_metrics():
    """REST endpoint for current metrics"""
    return {
        "latest": metrics_store["latest"],
        "history_count": len(metrics_store["history"])
    }


# Dashboard HTML
dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>KayGraph Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            margin: -20px -20px 20px -20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-card h3 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            margin: 10px 0;
        }
        .metric-label {
            color: #7f8c8d;
            font-size: 14px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-good { background-color: #27ae60; }
        .status-warning { background-color: #f39c12; }
        .status-error { background-color: #e74c3c; }
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 20px;
            background: #27ae60;
            color: white;
            font-size: 12px;
        }
        .connection-status.disconnected {
            background: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>KayGraph Metrics Dashboard</h1>
        <p>Real-time monitoring of graph execution metrics</p>
    </div>
    
    <div class="connection-status" id="connectionStatus">Connected</div>
    
    <div class="metrics-grid" id="metricsGrid">
        <!-- Metric cards will be inserted here -->
    </div>
    
    <div class="chart-container">
        <h3>Success Rate Over Time</h3>
        <canvas id="successRateChart"></canvas>
    </div>
    
    <div class="chart-container">
        <h3>Execution Times by Node</h3>
        <canvas id="executionTimeChart"></canvas>
    </div>

    <script>
        // WebSocket connection
        const ws = new WebSocket('ws://localhost:8000/ws');
        const connectionStatus = document.getElementById('connectionStatus');
        const metricsGrid = document.getElementById('metricsGrid');
        
        // Chart setup
        const successRateCtx = document.getElementById('successRateChart').getContext('2d');
        const executionTimeCtx = document.getElementById('executionTimeChart').getContext('2d');
        
        const successRateChart = new Chart(successRateCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
        
        const executionTimeChart = new Chart(executionTimeCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Average Execution Time (s)',
                    data: [],
                    backgroundColor: '#3498db'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // WebSocket handlers
        ws.onopen = () => {
            connectionStatus.textContent = 'Connected';
            connectionStatus.classList.remove('disconnected');
        };
        
        ws.onclose = () => {
            connectionStatus.textContent = 'Disconnected';
            connectionStatus.classList.add('disconnected');
        };
        
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            
            if (message.type === 'metrics_update' || message.type === 'initial_metrics') {
                updateMetrics(message.data);
            }
            
            if (message.type === 'initial_metrics' && message.history) {
                // Update charts with historical data
                updateCharts(message.history);
            }
        };
        
        function updateMetrics(data) {
            if (!data.nodes) return;
            
            metricsGrid.innerHTML = '';
            
            // Create metric cards for each node
            Object.entries(data.nodes).forEach(([nodeId, metrics]) => {
                const card = createMetricCard(nodeId, metrics);
                metricsGrid.appendChild(card);
            });
            
            // Update charts
            updateExecutionTimeChart(data.nodes);
        }
        
        function createMetricCard(nodeId, metrics) {
            const card = document.createElement('div');
            card.className = 'metric-card';
            
            const statusClass = metrics.success_rate > 0.9 ? 'status-good' : 
                               metrics.success_rate > 0.7 ? 'status-warning' : 'status-error';
            
            card.innerHTML = `
                <h3><span class="status-indicator ${statusClass}"></span>${nodeId}</h3>
                <div class="metric-value">${(metrics.success_rate * 100).toFixed(1)}%</div>
                <div class="metric-label">Success Rate</div>
                <hr style="margin: 15px 0; border: none; border-top: 1px solid #ecf0f1;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <div class="metric-value" style="font-size: 18px;">${metrics.total_executions}</div>
                        <div class="metric-label">Executions</div>
                    </div>
                    <div>
                        <div class="metric-value" style="font-size: 18px;">${metrics.total_retries}</div>
                        <div class="metric-label">Retries</div>
                    </div>
                </div>
                <hr style="margin: 15px 0; border: none; border-top: 1px solid #ecf0f1;">
                <div>
                    <div class="metric-label">Execution Time</div>
                    <div style="font-size: 14px;">
                        Avg: ${metrics.avg_execution_time}s<br>
                        Min: ${metrics.min_execution_time}s<br>
                        Max: ${metrics.max_execution_time}s
                    </div>
                </div>
            `;
            
            return card;
        }
        
        function updateExecutionTimeChart(nodes) {
            const labels = Object.keys(nodes);
            const data = labels.map(nodeId => nodes[nodeId].avg_execution_time);
            
            executionTimeChart.data.labels = labels;
            executionTimeChart.data.datasets[0].data = data;
            executionTimeChart.update();
        }
        
        function updateCharts(history) {
            // Prepare data for success rate chart
            const nodeIds = new Set();
            history.forEach(entry => {
                if (entry.metrics) {
                    Object.keys(entry.metrics).forEach(nodeId => nodeIds.add(nodeId));
                }
            });
            
            // Create datasets for each node
            const datasets = Array.from(nodeIds).map(nodeId => ({
                label: nodeId,
                data: [],
                borderColor: getColorForNode(nodeId),
                fill: false
            }));
            
            // Fill data
            const labels = [];
            history.forEach((entry, index) => {
                labels.push(index);
                datasets.forEach(dataset => {
                    const nodeId = dataset.label;
                    const metrics = entry.metrics && entry.metrics[nodeId];
                    dataset.data.push(metrics ? metrics.success_rate : null);
                });
            });
            
            successRateChart.data.labels = labels;
            successRateChart.data.datasets = datasets;
            successRateChart.update();
        }
        
        function getColorForNode(nodeId) {
            const colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6'];
            const index = Array.from(nodeId).reduce((acc, char) => acc + char.charCodeAt(0), 0);
            return colors[index % colors.length];
        }
    </script>
</body>
</html>
"""


def update_metrics_store(metrics: Dict[str, Any]):
    """Update the metrics store with new data"""
    metrics_store["latest"] = metrics
    metrics_store["history"].append({
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics
    })
    # Keep only last 1000 entries
    metrics_store["history"] = metrics_store["history"][-1000:]


async def start_dashboard(host: str = "0.0.0.0", port: int = 8000):
    """Start the dashboard server"""
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()