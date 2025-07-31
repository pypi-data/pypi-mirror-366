# KayGraph Production Extensions - Implementation Plan for Claude Code

This document provides a step-by-step implementation plan for adding production-ready extensions to KayGraph while maintaining its zero-dependency core.

## Overview

Transform KayGraph into a production-ready orchestration framework with optional extensions for:
- State persistence (Redis, PostgreSQL, S3)
- Scheduling (Cron-based with APScheduler)
- Web UI (FastAPI + React)
- Distributed execution (Celery, Ray)
- Observability (OpenTelemetry, Prometheus)

## Phase 1: Extension Architecture Setup

### Task 1.1: Restructure Core Library
Create the new directory structure while preserving existing functionality.

```bash
# Create new structure
mkdir -p kaygraph/core
mkdir -p kaygraph/ext/{base,persistence,scheduler,ui,distributed,observability}
mkdir -p kaygraph/plugins
mkdir -p kaygraph/utils

# Move existing files
mv kaygraph/*.py kaygraph/core/
```

**Files to create:**

1. `/kaygraph/core/__init__.py` - Re-export existing classes
2. `/kaygraph/__init__.py` - Import from core, maintain backward compatibility
3. `/kaygraph/ext/__init__.py` - Extension namespace
4. `/kaygraph/ext/base.py` - Base classes for extensions
5. `/kaygraph/utils/imports.py` - Lazy import utilities

### Task 1.2: Update setup.py
Create a new setup.py with extras_require for optional dependencies.

**File:** `/setup.py`
```python
setup(
    name="kaygraph",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],  # Core has zero dependencies
    extras_require={
        "scheduler": ["croniter>=1.3.0", "apscheduler>=3.10.0", "pytz>=2023.3"],
        "persistence": ["redis>=5.0.0", "psycopg2-binary>=2.9.0", "boto3>=1.28.0"],
        "ui": ["fastapi>=0.104.0", "uvicorn[standard]>=0.24.0", "aiofiles>=23.2.0"],
        "distributed": ["celery[redis]>=5.3.0", "ray[default]>=2.8.0"],
        "observability": ["opentelemetry-api>=1.20.0", "opentelemetry-sdk>=1.20.0", 
                         "opentelemetry-exporter-otlp>=1.20.0", "prometheus-client>=0.19.0"],
        "all": ["kaygraph[scheduler,persistence,ui,distributed,observability]"],
        "dev": ["pytest>=7.4.0", "pytest-asyncio>=0.21.0", "pytest-cov>=4.1.0",
                "black>=23.10.0", "mypy>=1.7.0", "ruff>=0.1.0"],
    }
)
```

### Task 1.3: Create Plugin System
Implement a plugin discovery and registration system.

**Files to create:**
1. `/kaygraph/plugins/registry.py` - Plugin registry implementation
2. `/kaygraph/plugins/base.py` - Base plugin class
3. `/kaygraph/config.py` - Configuration management

## Phase 2: Persistence Extension

### Task 2.1: Create Persistence Base Classes
Define the protocol for state backends.

**Files to create:**
1. `/kaygraph/ext/persistence/__init__.py` - Extension exports
2. `/kaygraph/ext/persistence/base.py` - StateBackend protocol
3. `/kaygraph/ext/persistence/types.py` - Type definitions

### Task 2.2: Implement Memory Backend
Create an in-memory backend for testing.

**File:** `/kaygraph/ext/persistence/backends/memory.py`

### Task 2.3: Implement Redis Backend
Add Redis-based persistence.

**Files to create:**
1. `/kaygraph/ext/persistence/backends/redis.py` - Redis implementation
2. `/kaygraph/ext/persistence/backends/config.py` - Backend configuration

### Task 2.4: Implement PostgreSQL Backend
Add PostgreSQL-based persistence.

**Files to create:**
1. `/kaygraph/ext/persistence/backends/postgres.py` - PostgreSQL implementation
2. `/kaygraph/ext/persistence/migrations/001_initial.sql` - Database schema

### Task 2.5: Implement S3 Backend
Add S3-based persistence for cloud deployments.

**File:** `/kaygraph/ext/persistence/backends/s3.py`

### Task 2.6: Create PersistentGraph Mixin
Add persistence capabilities to graphs.

**File:** `/kaygraph/ext/persistence/graph.py`

## Phase 3: Scheduler Extension

### Task 3.1: Create Scheduler Base
Define the scheduler interface.

**Files to create:**
1. `/kaygraph/ext/scheduler/__init__.py` - Extension exports
2. `/kaygraph/ext/scheduler/base.py` - Scheduler interface
3. `/kaygraph/ext/scheduler/config.py` - Scheduler configuration

### Task 3.2: Implement Core Scheduler
Build the main scheduler using APScheduler.

**Files to create:**
1. `/kaygraph/ext/scheduler/scheduler.py` - Main scheduler implementation
2. `/kaygraph/ext/scheduler/jobs.py` - Job management
3. `/kaygraph/ext/scheduler/stores.py` - Job stores

### Task 3.3: Add Schedule Decorators
Create decorators for easy scheduling.

**File:** `/kaygraph/ext/scheduler/decorators.py`

### Task 3.4: Implement Scheduler CLI
Add CLI commands for scheduler management.

**File:** `/kaygraph/ext/scheduler/cli.py`

## Phase 4: UI Extension

### Task 4.1: Create FastAPI Backend
Build the API server for the UI.

**Files to create:**
1. `/kaygraph/ext/ui/__init__.py` - Extension exports
2. `/kaygraph/ext/ui/api/app.py` - FastAPI application
3. `/kaygraph/ext/ui/api/routes/graphs.py` - Graph endpoints
4. `/kaygraph/ext/ui/api/routes/runs.py` - Run endpoints
5. `/kaygraph/ext/ui/api/routes/metrics.py` - Metrics endpoints
6. `/kaygraph/ext/ui/api/websocket.py` - WebSocket support

### Task 4.2: Create React Frontend
Build the web UI.

**Files to create:**
1. `/kaygraph/ext/ui/frontend/package.json` - Frontend dependencies
2. `/kaygraph/ext/ui/frontend/src/App.tsx` - Main application
3. `/kaygraph/ext/ui/frontend/src/api/client.ts` - API client
4. `/kaygraph/ext/ui/frontend/src/components/GraphList.tsx` - Graph listing
5. `/kaygraph/ext/ui/frontend/src/components/RunMonitor.tsx` - Run monitoring
6. `/kaygraph/ext/ui/frontend/src/hooks/useWebSocket.ts` - WebSocket hook

### Task 4.3: Build System Integration
Set up build process for frontend.

**Files to create:**
1. `/kaygraph/ext/ui/frontend/vite.config.ts` - Vite configuration
2. `/kaygraph/ext/ui/build.py` - Build script

## Phase 5: Distributed Extension

### Task 5.1: Create Executor Base
Define the executor interface.

**Files to create:**
1. `/kaygraph/ext/distributed/__init__.py` - Extension exports
2. `/kaygraph/ext/distributed/base.py` - Executor protocol
3. `/kaygraph/ext/distributed/serialization.py` - Node serialization

### Task 5.2: Implement Local Executor
Default single-process executor.

**File:** `/kaygraph/ext/distributed/executors/local.py`

### Task 5.3: Implement Celery Executor
Add Celery-based distributed execution.

**Files to create:**
1. `/kaygraph/ext/distributed/executors/celery.py` - Celery executor
2. `/kaygraph/ext/distributed/executors/celery_tasks.py` - Task definitions

### Task 5.4: Implement Ray Executor
Add Ray-based distributed execution.

**File:** `/kaygraph/ext/distributed/executors/ray.py`

### Task 5.5: Add Distributed Decorators
Create decorators for distributed nodes.

**File:** `/kaygraph/ext/distributed/decorators.py`

## Phase 6: Observability Extension

### Task 6.1: Create Tracing Support
Add OpenTelemetry integration.

**Files to create:**
1. `/kaygraph/ext/observability/__init__.py` - Extension exports
2. `/kaygraph/ext/observability/tracing.py` - Tracing setup
3. `/kaygraph/ext/observability/instrumentation.py` - Auto-instrumentation

### Task 6.2: Add Metrics Collection
Implement Prometheus metrics.

**Files to create:**
1. `/kaygraph/ext/observability/metrics.py` - Metric definitions
2. `/kaygraph/ext/observability/collectors.py` - Custom collectors

### Task 6.3: Create Observability Decorators
Add decorators for easy instrumentation.

**File:** `/kaygraph/ext/observability/decorators.py`

## Phase 7: Testing Infrastructure

### Task 7.1: Create Test Fixtures
Build reusable test components.

**Files to create:**
1. `/tests/conftest.py` - Pytest configuration
2. `/tests/fixtures/graphs.py` - Test graphs
3. `/tests/fixtures/backends.py` - Test backends
4. `/tests/utils.py` - Test utilities

### Task 7.2: Unit Tests for Extensions
Test each extension in isolation.

**Files to create:**
1. `/tests/test_persistence.py` - Persistence tests
2. `/tests/test_scheduler.py` - Scheduler tests
3. `/tests/test_distributed.py` - Distributed tests
4. `/tests/test_observability.py` - Observability tests

### Task 7.3: Integration Tests
Test extensions working together.

**Files to create:**
1. `/tests/integration/test_scheduled_persistent.py`
2. `/tests/integration/test_distributed_observability.py`
3. `/tests/integration/test_ui_api.py`

## Phase 8: Documentation

### Task 8.1: Extension Guides
Create user guides for each extension.

**Files to create:**
1. `/docs/extensions/persistence.md` - Persistence guide
2. `/docs/extensions/scheduler.md` - Scheduler guide
3. `/docs/extensions/ui.md` - UI guide
4. `/docs/extensions/distributed.md` - Distributed guide
5. `/docs/extensions/observability.md` - Observability guide

### Task 8.2: API Documentation
Generate API docs from code.

**Files to create:**
1. `/docs/conf.py` - Sphinx configuration
2. `/docs/api/index.rst` - API index
3. `/docs/Makefile` - Documentation build

### Task 8.3: Migration Guide
Help users adopt extensions.

**File:** `/docs/migration/from_basic_to_production.md`

## Phase 9: Example Applications

### Task 9.1: ML Pipeline Example
Show ML workflow orchestration.

**Files to create:**
1. `/examples/ml_pipeline/pipeline.py` - Main pipeline
2. `/examples/ml_pipeline/nodes.py` - ML nodes
3. `/examples/ml_pipeline/README.md` - Documentation

### Task 9.2: Data Processing Example
Show ETL workflow.

**Files to create:**
1. `/examples/data_etl/etl.py` - ETL pipeline
2. `/examples/data_etl/transformers.py` - Data transformers
3. `/examples/data_etl/README.md` - Documentation

### Task 9.3: Web Scraping Example
Show distributed web scraping.

**Files to create:**
1. `/examples/web_scraper/scraper.py` - Scraping pipeline
2. `/examples/web_scraper/distributed.py` - Distributed setup
3. `/examples/web_scraper/README.md` - Documentation

## Phase 10: Deployment Tools

### Task 10.1: Docker Support
Create Docker images.

**Files to create:**
1. `/docker/Dockerfile` - Main image
2. `/docker/Dockerfile.scheduler` - Scheduler image
3. `/docker/Dockerfile.worker` - Worker image
4. `/docker/docker-compose.yml` - Local development

### Task 10.2: Kubernetes Manifests
Create K8s deployment files.

**Files to create:**
1. `/k8s/namespace.yaml` - Namespace
2. `/k8s/scheduler.yaml` - Scheduler deployment
3. `/k8s/worker.yaml` - Worker deployment
4. `/k8s/ui.yaml` - UI deployment
5. `/k8s/configmap.yaml` - Configuration

### Task 10.3: Helm Chart
Create Helm chart for easy deployment.

**Files to create:**
1. `/helm/kaygraph/Chart.yaml` - Chart metadata
2. `/helm/kaygraph/values.yaml` - Default values
3. `/helm/kaygraph/templates/deployment.yaml` - Deployments

## Implementation Instructions for Claude Code

1. **Start with Phase 1** - Set up the extension architecture without breaking existing code
2. **Test after each phase** - Ensure backward compatibility is maintained
3. **Use type hints** - Add comprehensive type hints for better IDE support
4. **Add logging** - Use Python's logging module throughout
5. **Follow patterns** - Maintain consistency with existing KayGraph patterns
6. **Document as you go** - Add docstrings and comments
7. **Create examples** - Add usage examples for each new feature

## Success Criteria

- [ ] Core KayGraph still works with zero dependencies
- [ ] Each extension can be installed independently
- [ ] All extensions have comprehensive tests
- [ ] Documentation is complete and accurate
- [ ] Examples demonstrate real-world usage
- [ ] Performance overhead is minimal (<5%)
- [ ] Backward compatibility is maintained

## Notes for Implementation

- Prioritize code quality over speed
- Make small, focused commits
- Test edge cases thoroughly
- Consider security implications
- Plan for horizontal scaling
- Design for cloud-native deployment

Start with Phase 1 and proceed systematically through each phase!