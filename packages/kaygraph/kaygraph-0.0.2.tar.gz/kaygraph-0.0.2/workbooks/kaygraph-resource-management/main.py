import argparse
import logging
import random
import time
from typing import Dict, Any
from graph import create_resource_managed_workflow, create_monitored_workflow

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_resource_demo(simulate_failures: bool = False, monitor_resources: bool = False):
    """Run the resource management demo"""
    
    # Initialize shared context
    shared: Dict[str, Any] = {
        "config": {
            "simulate_failures": simulate_failures,
            "monitor_resources": monitor_resources
        }
    }
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║        KayGraph Resource Management Demo                  ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This demo shows:                                         ║
    ║  • Context manager support for resource cleanup          ║
    ║  • Database connection pooling                            ║
    ║  • File handle management                                 ║
    ║  • HTTP session reuse                                     ║
    ║  • Automatic cleanup on success/failure                   ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Running workflow with {'failure simulation' if simulate_failures else 'normal operation'}...
    """)
    
    # Create the workflow
    if monitor_resources:
        main_workflow, monitor_workflow = create_monitored_workflow()
    else:
        main_workflow = create_resource_managed_workflow()
        monitor_workflow = None
    
    # Configure workflow parameters
    main_workflow.set_params({
        "query": "SELECT * FROM sample_table ORDER BY id LIMIT 25",
        "batch_size": 5
    })
    
    try:
        logger.info("Starting resource-managed workflow...")
        
        # Simulate resource failures if requested
        if simulate_failures:
            # Randomly decide what type of failure to simulate
            failure_type = random.choice(["database", "file", "network"])
            logger.warning(f"Simulating {failure_type} failure for demonstration")
            shared["config"]["failure_type"] = failure_type
        
        # Run the main workflow using context manager
        with main_workflow:
            result = main_workflow.run(shared)
        
        # Run resource monitoring if requested
        if monitor_resources and monitor_workflow:
            logger.info("Running resource monitoring...")
            monitor_result = monitor_workflow.run(shared)
            display_resource_monitoring(shared)
        
        # Display results
        display_workflow_results(shared)
        
        logger.info("Workflow completed successfully with proper resource cleanup!")
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        print(f"\n❌ Workflow failed: {e}")
        print("Notice how KayGraph's context manager ensured resource cleanup even on failure!")
        
        # Show partial results if any
        if shared:
            print(f"\n📊 Partial results before failure:")
            for key, value in shared.items():
                if not key.startswith("_") and not key.startswith("config"):
                    if isinstance(value, (list, dict)):
                        print(f"  {key}: {type(value).__name__} with {len(value)} items")
                    else:
                        print(f"  {key}: {value}")


def display_workflow_results(shared: Dict[str, Any]):
    """Display the results of the workflow execution"""
    
    print(f"\n📊 Workflow Execution Results:")
    print("=" * 50)
    
    # Database results
    if "database_results" in shared:
        db_results = shared["database_results"]
        print(f"🗄️ Database Reading:")
        print(f"  Records read: {len(db_results.get('data', []))}")
        print(f"  Connection ID: {db_results.get('connection_stats', {}).get('connection_id', 'unknown')}")
        print(f"  Queries executed: {db_results.get('connection_stats', {}).get('queries_executed', 0)}")
    
    # File processing results
    if "file_results" in shared:
        file_results = shared["file_results"]
        stats = file_results.get("processing_stats", {})
        print(f"📁 File Processing:")
        print(f"  Records processed: {stats.get('records_processed', 0)}")
        print(f"  Input file size: {stats.get('input_size_bytes', 0)} bytes")
        print(f"  Output file size: {stats.get('output_size_bytes', 0)} bytes")
        print(f"  Temp files created: {len([f for f in [file_results.get('input_file'), file_results.get('output_file')] if f])}")
    
    # Upload results
    if "upload_results" in shared:
        upload_results = shared["upload_results"]
        print(f"🌐 API Upload:")
        print(f"  Total batches: {upload_results.get('total_batches', 0)}")
        print(f"  Successful uploads: {upload_results.get('successful_uploads', 0)}")
        print(f"  Failed uploads: {upload_results.get('failed_uploads', 0)}")
        
        # Show session reuse
        if "upload_results" in upload_results:
            sessions_used = set()
            for result in upload_results["upload_results"]:
                if "session_id" in result:
                    sessions_used.add(result["session_id"])
            print(f"  HTTP sessions used: {len(sessions_used)} (demonstrates session reuse)")
    
    # Notification results
    if "notification_result" in shared:
        notif_result = shared["notification_result"]
        print(f"📧 Notifications:")
        print(f"  Notification sent: {'✅ Yes' if notif_result.get('notification_sent', False) else '❌ No'}")
        if notif_result.get("notification_result"):
            result = notif_result["notification_result"]
            print(f"  Message ID: {result.get('message_id', 'unknown')}")
            print(f"  Status: {result.get('status', 'unknown')}")


def display_resource_monitoring(shared: Dict[str, Any]):
    """Display resource monitoring information"""
    
    if "resource_stats" not in shared:
        return
    
    stats = shared["resource_stats"]
    
    print(f"\n🔍 Resource Monitoring:")
    print("=" * 50)
    
    print(f"📊 Overall Status: {stats.get('status', 'unknown').upper()}")
    
    # Database stats
    if "database" in stats:
        db = stats["database"]
        print(f"🗄️ Database Connections:")
        print(f"  Active: {db.get('active_connections', 0)}/{db.get('max_connections', 0)}")
        print(f"  Total created: {db.get('total_created', 0)}")
    
    # HTTP stats
    if "http" in stats:
        http = stats["http"]
        print(f"🌐 HTTP Sessions:")
        print(f"  Active: {http.get('active_sessions', 0)}/{http.get('max_sessions', 0)}")
        print(f"  Total created: {http.get('total_created', 0)}")
    
    # Temp files
    temp_files = stats.get("temp_files", 0)
    print(f"📁 Temporary Files: {temp_files}")
    
    # Warnings
    if "warnings" in stats:
        print(f"⚠️ Resource Warnings:")
        for warning in stats["warnings"]:
            print(f"  • {warning}")
    
    print(f"\n✅ All resources properly managed and cleaned up!")


def demonstrate_context_manager():
    """Demonstrate context manager behavior with exceptions"""
    
    print(f"\n🔧 Demonstrating Context Manager Cleanup:")
    print("=" * 50)
    
    from nodes import DatabaseReaderNode
    
    # Test normal operation
    print("1. Normal operation with cleanup:")
    try:
        with DatabaseReaderNode() as node:
            print("   Node created and resources setup")
            # Normal processing would happen here
            time.sleep(0.1)
            print("   Processing completed")
        print("   ✅ Resources automatically cleaned up")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with exception
    print("\n2. Operation with exception - cleanup still happens:")
    try:
        with DatabaseReaderNode() as node:
            print("   Node created and resources setup")
            # Simulate an error
            raise ValueError("Simulated processing error")
    except ValueError as e:
        print(f"   ❌ Error occurred: {e}")
        print("   ✅ Resources still cleaned up automatically!")
    
    print("\nThis demonstrates KayGraph's robust resource management! 🎉")


def main():
    """Main entry point with command line options"""
    
    parser = argparse.ArgumentParser(description="KayGraph Resource Management Demo")
    parser.add_argument(
        "--simulate-failures",
        action="store_true",
        help="Simulate resource failures to demonstrate cleanup"
    )
    parser.add_argument(
        "--monitor-resources",
        action="store_true",
        help="Enable resource monitoring and display statistics"
    )
    parser.add_argument(
        "--demo-context-manager",
        action="store_true",
        help="Demonstrate context manager behavior"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run context manager demo if requested
    if args.demo_context_manager:
        demonstrate_context_manager()
        return
    
    # Run the main demo
    run_resource_demo(
        simulate_failures=args.simulate_failures,
        monitor_resources=args.monitor_resources
    )


if __name__ == "__main__":
    main()