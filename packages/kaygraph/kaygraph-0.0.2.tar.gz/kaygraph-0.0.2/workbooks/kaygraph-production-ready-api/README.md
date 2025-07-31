# KayGraph Production-Ready API

This example demonstrates how KayGraph enhances FastAPI applications with production-grade features like request validation, comprehensive metrics, error handling, resource management, and monitoring. It builds upon PocketFlow's FastAPI examples but adds enterprise-level capabilities.

## Features Demonstrated

1. **Request Validation**: Comprehensive input validation using ValidatedNode
2. **Performance Monitoring**: Real-time API metrics collection with MetricsNode
3. **Error Handling**: Robust error recovery and circuit breaker patterns
4. **Resource Management**: Automatic database and external service connection management
5. **Health Monitoring**: Advanced health checks and system monitoring

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ FastAPI Server  │────▶│ Request Handler  │────▶│ Response Builder│
│ (HTTP Layer)    │     │ (ValidatedNode + │     │ (MetricsNode +  │
│                 │     │  Circuit Breaker)│     │  Validation)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
   [Rate Limiting]        [Resource Pool]           [Metrics Export]
                                                           │
                          ┌──────────────────┐             │
                          │ Health Monitor   │◀────────────┘
                          │ (System Status)  │
                          └──────────────────┘
```

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the production API server
python main.py

# Run with custom configuration
python main.py --host 0.0.0.0 --port 8000 --workers 4

# Enable debug mode
python main.py --debug

# Test the API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/metrics
curl -X POST http://localhost:8000/api/v1/process -H "Content-Type: application/json" -d '{"data": "test"}'
```

## API Endpoints

### Core Endpoints
- `GET /health` - Comprehensive health check
- `GET /metrics` - Prometheus-compatible metrics
- `GET /api/v1/status` - System status and performance
- `POST /api/v1/process` - Main processing endpoint

### Management Endpoints
- `GET /admin/workers` - Worker pool status
- `POST /admin/circuit-breaker/reset` - Reset circuit breakers
- `GET /admin/logs` - Recent application logs

## Key Concepts

### Production Features
- Request/response validation with detailed error messages
- Comprehensive metrics collection and export
- Circuit breaker protection for external services
- Resource pooling with health monitoring
- Structured logging with correlation IDs

### Enterprise Patterns
- Graceful shutdown with cleanup
- Health checks with dependency validation
- Performance monitoring and alerting
- Rate limiting and throttling
- Security headers and validation

## Monitoring Integration

The API provides multiple monitoring interfaces:
- Prometheus metrics endpoint
- Health check endpoint with dependency status
- Real-time performance dashboards
- Structured logging for centralized collection