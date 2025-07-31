import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import logging

from graph import create_api_processing_workflow, create_resilient_api_workflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KayGraph Production API",
    description="Production-ready API with KayGraph workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global workflow instances
api_workflow = None
resilient_workflow = None
metrics_collector = None

# Request/Response Models
class ProcessRequest(BaseModel):
    data: Any = Field(..., description="Data to process")
    processing_type: str = Field(..., description="Type of processing to perform")
    options: Optional[Dict[str, Any]] = Field(default={}, description="Processing options")
    callback_url: Optional[str] = Field(default=None, description="Callback URL for async processing")

class BatchProcessRequest(BaseModel):
    items: List[Any] = Field(..., description="List of items to process")
    batch_id: str = Field(..., description="Unique batch identifier")
    priority: Optional[int] = Field(default=5, ge=1, le=10, description="Processing priority (1-10)")
    timeout: Optional[int] = Field(default=30, description="Timeout in seconds")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    dependencies: Dict[str, str]
    metrics: Dict[str, Any]

class MetricsResponse(BaseModel):
    timestamp: str
    api_metrics: Dict[str, Any]
    workflow_metrics: Dict[str, Any]
    system_metrics: Dict[str, Any]


# Global metrics storage
api_metrics = {
    "requests_total": 0,
    "requests_successful": 0,
    "requests_failed": 0,
    "response_times": [],
    "start_time": time.time()
}


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect API metrics"""
    start_time = time.time()
    
    # Add correlation ID to request
    correlation_id = f"api_{int(time.time())}_{hash(str(request.url))}"
    request.state.correlation_id = correlation_id
    
    # Process request
    response = await call_next(request)
    
    # Collect metrics
    processing_time = time.time() - start_time
    api_metrics["requests_total"] += 1
    
    if response.status_code < 400:
        api_metrics["requests_successful"] += 1
    else:
        api_metrics["requests_failed"] += 1
    
    api_metrics["response_times"].append(processing_time)
    
    # Keep only recent response times (last 1000)
    if len(api_metrics["response_times"]) > 1000:
        api_metrics["response_times"] = api_metrics["response_times"][-1000:]
    
    # Add custom headers
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Processing-Time"] = str(round(processing_time * 1000, 2))
    response.headers["X-API-Version"] = "1.0.0"
    
    return response


@app.on_event("startup")
async def startup_event():
    """Initialize workflows and resources on startup"""
    global api_workflow, resilient_workflow
    
    logger.info("Starting KayGraph Production API...")
    
    # Initialize workflows
    api_workflow = create_api_processing_workflow()
    resilient_workflow = create_resilient_api_workflow()
    
    logger.info("API workflows initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Shutting down KayGraph Production API...")
    
    # Cleanup workflows if needed
    global api_workflow, resilient_workflow
    if api_workflow:
        # Perform any necessary cleanup
        pass
    
    logger.info("API shutdown complete")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    
    # Check system health
    current_time = datetime.now()
    uptime = time.time() - api_metrics["start_time"]
    
    # Check workflow health
    workflow_healthy = api_workflow is not None and resilient_workflow is not None
    
    # Check dependencies (simulated)
    dependencies = {
        "database": "healthy",
        "external_api": "healthy",
        "cache": "healthy",
        "workflow_engine": "healthy" if workflow_healthy else "unhealthy"
    }
    
    # Calculate metrics
    total_requests = api_metrics["requests_total"]
    success_rate = (api_metrics["requests_successful"] / total_requests) if total_requests > 0 else 1.0
    avg_response_time = sum(api_metrics["response_times"]) / len(api_metrics["response_times"]) if api_metrics["response_times"] else 0
    
    health_metrics = {
        "uptime_seconds": round(uptime, 2),
        "total_requests": total_requests,
        "success_rate": round(success_rate, 3),
        "avg_response_time_ms": round(avg_response_time * 1000, 2),
        "memory_usage": "normal",  # Simulated
        "cpu_usage": "normal"      # Simulated
    }
    
    # Determine overall status
    overall_status = "healthy"
    if success_rate < 0.95:
        overall_status = "degraded"
    if any(status != "healthy" for status in dependencies.values()):
        overall_status = "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=current_time.isoformat(),
        version="1.0.0",
        dependencies=dependencies,
        metrics=health_metrics
    )


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get comprehensive API and workflow metrics"""
    
    current_time = datetime.now()
    
    # API metrics
    total_requests = api_metrics["requests_total"]
    success_rate = (api_metrics["requests_successful"] / total_requests) if total_requests > 0 else 1.0
    error_rate = (api_metrics["requests_failed"] / total_requests) if total_requests > 0 else 0.0
    
    response_times = api_metrics["response_times"]
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 20 else avg_response_time
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = 0
    
    api_metrics_data = {
        "requests_total": total_requests,
        "requests_per_second": total_requests / (time.time() - api_metrics["start_time"]),
        "success_rate": round(success_rate, 3),
        "error_rate": round(error_rate, 3),
        "response_time_ms": {
            "avg": round(avg_response_time * 1000, 2),
            "min": round(min_response_time * 1000, 2),
            "max": round(max_response_time * 1000, 2),
            "p95": round(p95_response_time * 1000, 2)
        }
    }
    
    # Workflow metrics (simulated - in real implementation, get from workflow)
    workflow_metrics_data = {
        "workflows_executed": total_requests,
        "avg_workflow_time_ms": round(avg_response_time * 1000, 2),
        "validation_success_rate": 0.98,
        "processing_success_rate": round(success_rate, 3),
        "circuit_breaker_status": "closed"
    }
    
    # System metrics (simulated)
    system_metrics_data = {
        "cpu_percent": 45.2,
        "memory_percent": 62.8,
        "disk_usage_percent": 34.1,
        "active_connections": 12,
        "uptime_seconds": round(time.time() - api_metrics["start_time"], 2)
    }
    
    return MetricsResponse(
        timestamp=current_time.isoformat(),
        api_metrics=api_metrics_data,
        workflow_metrics=workflow_metrics_data,
        system_metrics=system_metrics_data
    )


@app.post("/api/v1/process")
async def process_request(request: ProcessRequest, http_request: Request):
    """Main processing endpoint using KayGraph workflow"""
    
    correlation_id = getattr(http_request.state, 'correlation_id', 'unknown')
    
    try:
        # Prepare request data for workflow
        request_data = {
            "request_id": correlation_id,
            "type": "process",
            "data": request.data,
            "processing_type": request.processing_type,
            "options": request.options or {},
            "callback_url": request.callback_url,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create shared context for workflow
        shared = {"request_data": request_data}
        
        # Execute workflow
        result = api_workflow.run(shared)
        
        # Get API response from workflow
        api_response = shared.get("api_response", {})
        
        if not api_response:
            raise HTTPException(status_code=500, detail="Workflow did not produce response")
        
        # Return response with appropriate status code
        status_code = 200 if api_response.get("status") == "success" else 400
        
        return JSONResponse(
            content=api_response,
            status_code=status_code
        )
        
    except Exception as e:
        logger.error(f"Request processing failed: {e}")
        
        error_response = {
            "request_id": correlation_id,
            "status": "error",
            "data": {},
            "error": {
                "type": "internal_error",
                "message": str(e),
                "code": "INT_001"
            },
            "metadata": {
                "request_id": correlation_id,
                "processed_at": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }
        }
        
        return JSONResponse(
            content=error_response,
            status_code=500
        )


@app.post("/api/v1/batch-process")
async def batch_process_request(request: BatchProcessRequest, http_request: Request):
    """Batch processing endpoint"""
    
    correlation_id = getattr(http_request.state, 'correlation_id', 'unknown')
    
    try:
        # Prepare batch request data
        request_data = {
            "request_id": correlation_id,
            "type": "batch_process",
            "items": request.items,
            "batch_id": request.batch_id,
            "priority": request.priority,
            "timeout": request.timeout,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create shared context for workflow
        shared = {"request_data": request_data}
        
        # Execute resilient workflow for batch processing
        result = resilient_workflow.run(shared)
        
        # Get API response from workflow
        api_response = shared.get("api_response", {})
        
        if not api_response:
            raise HTTPException(status_code=500, detail="Batch workflow did not produce response")
        
        # Add batch-specific metadata
        if "metadata" in api_response:
            api_response["metadata"]["batch_id"] = request.batch_id
            api_response["metadata"]["batch_size"] = len(request.items)
        
        status_code = 200 if api_response.get("status") == "success" else 400
        
        return JSONResponse(
            content=api_response,
            status_code=status_code
        )
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        
        error_response = {
            "request_id": correlation_id,
            "batch_id": request.batch_id,
            "status": "error",
            "data": {},
            "error": {
                "type": "batch_error",
                "message": str(e),
                "code": "BAT_001"
            },
            "metadata": {
                "request_id": correlation_id,
                "batch_id": request.batch_id,
                "processed_at": datetime.now().isoformat(),
                "api_version": "1.0.0"
            }
        }
        
        return JSONResponse(
            content=error_response,
            status_code=500
        )


@app.get("/api/v1/status")
async def get_status():
    """Get current API status and performance"""
    
    total_requests = api_metrics["requests_total"]
    success_rate = (api_metrics["requests_successful"] / total_requests) if total_requests > 0 else 1.0
    
    response_times = api_metrics["response_times"][-100:]  # Last 100 requests
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        "status": "operational",
        "version": "1.0.0",
        "uptime_seconds": round(time.time() - api_metrics["start_time"], 2),
        "performance": {
            "total_requests": total_requests,
            "success_rate": round(success_rate, 3),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "requests_per_second": round(total_requests / (time.time() - api_metrics["start_time"]), 2)
        },
        "features": {
            "request_validation": True,
            "metrics_collection": True,
            "circuit_breaker": True,
            "fault_tolerance": True,
            "resource_management": True
        }
    }


@app.get("/admin/reset-metrics")
async def reset_metrics():
    """Reset API metrics (admin endpoint)"""
    
    global api_metrics
    api_metrics = {
        "requests_total": 0,
        "requests_successful": 0,
        "requests_failed": 0,
        "response_times": [],
        "start_time": time.time()
    }
    
    return {"message": "Metrics reset successfully", "timestamp": datetime.now().isoformat()}


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "type": "not_found",
                "message": f"Endpoint {request.url.path} not found",
                "code": "NOT_001"
            },
            "request_id": getattr(request.state, 'correlation_id', 'unknown'),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "internal_error",
                "message": "Internal server error",
                "code": "INT_002"
            },
            "request_id": getattr(request.state, 'correlation_id', 'unknown'),
            "timestamp": datetime.now().isoformat()
        }
    )


def create_app():
    """Factory function to create the FastAPI app"""
    return app


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        log_level="info"
    )