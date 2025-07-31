# KayGraph Deployment Guide

How to use KayGraph in your projects.

## Installation

```bash
# Using pip
pip install kaygraph

# Using uv (faster)
uv pip install kaygraph
```

That's it. KayGraph has ZERO dependencies.

## Basic Usage

```python
from kaygraph import Node, Graph

class MyNode(Node):
    def exec(self, data):
        return f"Processed: {data}"

graph = Graph(start=MyNode())
result = graph.run({"input": "hello"})
```

## In Production Applications

### FastAPI Example
```python
from fastapi import FastAPI
from kaygraph import Graph, Node

app = FastAPI()

class ProcessNode(Node):
    def exec(self, data):
        # Your logic here
        return {"result": data}

graph = Graph(start=ProcessNode())

@app.post("/process")
async def process(data: dict):
    return graph.run(data)
```

### Async Workflows
```python
from kaygraph import AsyncGraph, AsyncNode
import asyncio

class AsyncAPINode(AsyncNode):
    async def exec_async(self, data):
        # Non-blocking I/O
        await asyncio.sleep(0.1)
        return data

graph = AsyncGraph(start=AsyncAPINode())
result = await graph.run_async({"data": "async"})
```

## Deployment Options

### 1. Direct Python Application
```bash
# Your app using KayGraph
python app.py
```

### 2. Web Service (Gunicorn)
```bash
pip install kaygraph gunicorn
gunicorn app:app
```

### 3. Serverless (AWS Lambda)
```python
from kaygraph import Graph
import json

graph = Graph(start=YourNode())

def lambda_handler(event, context):
    result = graph.run(event)
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

## Environment Management

```bash
# Development
pip install -e .

# Production  
pip install kaygraph==0.1.4  # Pin version

# With requirements.txt
echo "kaygraph==0.1.4" >> requirements.txt
pip install -r requirements.txt
```

## That's It!

No Docker needed. No complex setup. Just:
1. Install KayGraph
2. Import and use
3. Deploy like any Python app

The beauty of ZERO dependencies.