import argparse
import asyncio
import time
import logging
from typing import Dict, Any
import subprocess
import sys

from monitoring_nodes import MonitoringNode
from utils.monitoring import MonitoringConfig, MockBackend, HTTPBackend
from utils.redis_backend import RedisBackend, SyncRedisBackend
from graph import create_monitoring_workflow, create_parallel_monitoring_workflow

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_monitoring(backend_type: str = "mock", **kwargs) -> MonitoringConfig:
    """Setup monitoring configuration"""
    
    if backend_type == "mock":
        backend = MockBackend()
    elif backend_type == "redis":
        backend = RedisBackend(
            host=kwargs.get("redis_host", "localhost"),
            port=kwargs.get("redis_port", 6379)
        )
    elif backend_type == "http":
        backend = HTTPBackend(
            webhook_url=kwargs.get("webhook_url", "http://localhost:8000/webhook")
        )
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
    
    config = MonitoringConfig(
        backend=backend,
        enable_data_snapshots=kwargs.get("enable_snapshots", True),
        sample_rate=kwargs.get("sample_rate", 1.0),
        batch_size=kwargs.get("batch_size", 50),
        flush_interval=kwargs.get("flush_interval", 1.0)
    )
    
    # Configure monitoring for all nodes
    MonitoringNode.configure_monitoring(config)
    
    return config


def run_monitoring_demo(
    backend_type: str = "mock",
    batch_size: int = 20,
    iterations: int = 5,
    parallel: bool = False,
    **kwargs
):
    """Run the monitoring demo"""
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║         KayGraph Real-time Monitoring Demo                ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This demo shows real-time monitoring capabilities:       ║
    ║  • Non-blocking event dispatching                        ║
    ║  • Multiple backend support (Redis, HTTP, Mock)          ║
    ║  • Performance metrics with <1% overhead                 ║
    ║  • Live dashboard visualization                          ║
    ║  • Comprehensive error tracking                          ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Configuration:
    • Backend: {backend_type}
    • Batch size: {batch_size} records per iteration
    • Iterations: {iterations}
    • Parallel processing: {'Enabled' if parallel else 'Disabled'}
    • Data snapshots: {'Enabled' if kwargs.get('enable_snapshots', True) else 'Disabled'}
    • Sample rate: {kwargs.get('sample_rate', 1.0) * 100:.0f}%
    """)
    
    # Setup monitoring
    config = setup_monitoring(backend_type, **kwargs)
    
    # Create workflow
    if parallel:
        logger.info("Creating parallel monitoring workflow")
        workflow = create_parallel_monitoring_workflow()
    else:
        logger.info("Creating sequential monitoring workflow")
        workflow = create_monitoring_workflow()
    
    # Run iterations
    total_start = time.time()
    results = []
    
    for i in range(iterations):
        print(f"\n🔄 Iteration {i + 1}/{iterations}")
        print("=" * 50)
        
        iteration_start = time.time()
        
        # Create shared context
        shared = {"iteration": i + 1}
        
        # Set workflow parameters
        workflow.set_params({"batch_size": batch_size})
        
        try:
            # Run workflow
            result = workflow.run(shared)
            
            iteration_time = time.time() - iteration_start
            
            # Collect results
            iteration_result = {
                "iteration": i + 1,
                "success": True,
                "duration": iteration_time,
                "records_processed": shared.get("data_count", 0),
                "valid_records": len(shared.get("valid_data", [])),
                "invalid_records": len(shared.get("invalid_data", [])),
                "storage_id": shared.get("storage_result", {}).get("storage_id")
            }
            
            results.append(iteration_result)
            
            print(f"✅ Iteration completed in {iteration_time:.2f}s")
            print(f"   • Records generated: {iteration_result['records_processed']}")
            print(f"   • Valid records: {iteration_result['valid_records']}")
            print(f"   • Invalid records: {iteration_result['invalid_records']}")
            if iteration_result['storage_id']:
                print(f"   • Storage ID: {iteration_result['storage_id']}")
            
        except Exception as e:
            logger.error(f"Iteration {i + 1} failed: {e}")
            results.append({
                "iteration": i + 1,
                "success": False,
                "error": str(e)
            })
        
        # Small delay between iterations
        if i < iterations - 1:
            time.sleep(0.5)
    
    total_time = time.time() - total_start
    
    # Print summary
    print(f"\n📊 Monitoring Demo Summary")
    print("=" * 50)
    print(f"Total execution time: {total_time:.2f}s")
    print(f"Average iteration time: {total_time / iterations:.2f}s")
    
    successful = sum(1 for r in results if r.get("success", False))
    print(f"Success rate: {successful}/{iterations} ({successful/iterations*100:.1f}%)")
    
    total_records = sum(r.get("records_processed", 0) for r in results if r.get("success", False))
    print(f"Total records processed: {total_records}")
    
    if backend_type == "mock":
        # Show mock backend statistics
        mock_backend = config.backend
        print(f"\n📈 Mock Backend Statistics:")
        print(f"Total events captured: {len(mock_backend.get_events())}")
        
        event_types = {}
        for event in mock_backend.get_events():
            event_type = event.event_type
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print("Event breakdown:")
        for event_type, count in sorted(event_types.items()):
            print(f"  • {event_type}: {count}")
    
    elif backend_type == "redis":
        # Show Redis statistics
        print(f"\n📈 Redis Backend Statistics:")
        try:
            sync_redis = SyncRedisBackend()
            metrics = sync_redis.get_metrics()
            
            print("Event counts:")
            for event_type, count in metrics.items():
                if event_type not in ["active_nodes", "active_workflows"]:
                    print(f"  • {event_type}: {count}")
            
            print(f"\nActive nodes: {metrics.get('active_nodes', 0)}")
            
        except Exception as e:
            print(f"Could not retrieve Redis metrics: {e}")
    
    # Show dispatcher statistics
    if hasattr(MonitoringNode, '_event_dispatcher') and MonitoringNode._event_dispatcher:
        dispatcher_stats = MonitoringNode._event_dispatcher.get_stats()
        print(f"\n🚀 Event Dispatcher Statistics:")
        print(f"  • Queue size: {dispatcher_stats['queue_size']}")
        print(f"  • Circuit breaker: {'Open' if dispatcher_stats['circuit_open'] else 'Closed'}")
        print(f"  • Backend connected: {dispatcher_stats['backend_connected']}")
    
    print(f"\n✨ Monitoring demo completed!")
    
    # Cleanup
    MonitoringNode.disable_monitoring()
    
    return results


def run_dashboard_server():
    """Run the monitoring dashboard in a subprocess"""
    print("Starting monitoring dashboard on http://localhost:8080")
    print("Press Ctrl+C to stop...")
    
    try:
        subprocess.run([sys.executable, "-m", "utils.dashboard"], check=True)
    except KeyboardInterrupt:
        print("\nDashboard stopped")


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="KayGraph Real-time Monitoring Demo")
    
    parser.add_argument(
        "--backend",
        choices=["mock", "redis", "http"],
        default="mock",
        help="Monitoring backend to use"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Number of records per batch"
    )
    
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of workflow iterations"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel processing workflow"
    )
    
    parser.add_argument(
        "--sample-rate",
        type=float,
        default=1.0,
        help="Event sampling rate (0.0-1.0)"
    )
    
    parser.add_argument(
        "--no-snapshots",
        action="store_true",
        help="Disable data snapshots in events"
    )
    
    parser.add_argument(
        "--redis-host",
        default="localhost",
        help="Redis host (for Redis backend)"
    )
    
    parser.add_argument(
        "--redis-port",
        type=int,
        default=6379,
        help="Redis port (for Redis backend)"
    )
    
    parser.add_argument(
        "--webhook-url",
        default="http://localhost:8000/webhook",
        help="Webhook URL (for HTTP backend)"
    )
    
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Run the monitoring dashboard"
    )
    
    args = parser.parse_args()
    
    if args.dashboard:
        run_dashboard_server()
    else:
        # Run the monitoring demo
        run_monitoring_demo(
            backend_type=args.backend,
            batch_size=args.batch_size,
            iterations=args.iterations,
            parallel=args.parallel,
            sample_rate=args.sample_rate,
            enable_snapshots=not args.no_snapshots,
            redis_host=args.redis_host,
            redis_port=args.redis_port,
            webhook_url=args.webhook_url
        )


if __name__ == "__main__":
    main()