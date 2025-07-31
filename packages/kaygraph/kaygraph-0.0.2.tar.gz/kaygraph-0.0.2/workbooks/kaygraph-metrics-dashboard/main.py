import asyncio
import threading
import time
from typing import Dict, Any
from graph import create_metrics_graph, create_metrics_aggregation_graph
from utils.dashboard import start_dashboard, update_metrics_store, send_metrics_update
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def run_workflow_continuously(shared: Dict[str, Any], interval: float = 5.0):
    """Run the workflow continuously and update metrics"""
    
    # Create graphs
    main_graph = create_metrics_graph()
    metrics_graph = create_metrics_aggregation_graph()
    
    while True:
        try:
            # Run main workflow
            logger.info("Starting new workflow iteration...")
            main_graph.set_params({"batch_size": 20})
            main_graph.run(shared)
            
            # Aggregate metrics
            metrics_graph.run(shared)
            
            # Update dashboard
            if "dashboard_metrics" in shared:
                update_metrics_store(shared["dashboard_metrics"])
                await send_metrics_update(shared["dashboard_metrics"])
            
            # Log summary
            if "storage_result" in shared:
                result = shared["storage_result"]
                logger.info(f"Workflow completed: {result['records_stored']} records stored in {result['storage_time']:.2f}s")
            
        except Exception as e:
            logger.error(f"Workflow error: {e}")
        
        # Wait before next iteration
        await asyncio.sleep(interval)


async def main():
    """Main entry point"""
    
    # Initialize shared context
    shared = {
        "metrics_history": [],
        "config": {
            "batch_size": 20,
            "workflow_interval": 5.0
        }
    }
    
    # Start dashboard server in background
    dashboard_task = asyncio.create_task(start_dashboard(host="localhost", port=8000))
    
    # Give dashboard time to start
    await asyncio.sleep(2)
    
    logger.info("Dashboard running at http://localhost:8000")
    logger.info("Starting continuous workflow execution...")
    
    # Run workflow continuously
    try:
        await run_workflow_continuously(shared, interval=5.0)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        dashboard_task.cancel()


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          KayGraph Metrics Dashboard Example               ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This example demonstrates:                               ║
    ║  • MetricsNode automatic metrics collection               ║
    ║  • Real-time performance monitoring                       ║
    ║  • Production-ready observability patterns                ║
    ║  • Complex graph execution tracking                       ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Starting dashboard server...
    Open http://localhost:8000 in your browser to view metrics.
    Press Ctrl+C to stop.
    """)
    
    asyncio.run(main())