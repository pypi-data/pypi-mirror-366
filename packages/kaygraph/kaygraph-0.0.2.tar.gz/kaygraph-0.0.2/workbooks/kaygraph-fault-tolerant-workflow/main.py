import argparse
import logging
import random
from typing import Dict, Any
from graph import create_fault_tolerant_workflow, create_resilient_workflow_with_fallbacks

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_fault_tolerance_demo(
    simulate_failures: bool = False,
    failure_type: str = "random",
    enable_circuit_breaker: bool = False,
    test_recovery: bool = False
):
    """Run the fault tolerance demo with various failure scenarios"""
    
    # Initialize shared context
    shared: Dict[str, Any] = {
        "config": {
            "simulate_failures": simulate_failures,
            "failure_type": failure_type,
            "enable_circuit_breaker": enable_circuit_breaker,
            "test_recovery": test_recovery
        },
        "errors_encountered": []
    }
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║       KayGraph Fault-Tolerant Workflow Demo              ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This demo shows:                                         ║
    ║  • Execution hooks (before_prep, after_exec, on_error)   ║
    ║  • Circuit breaker patterns                               ║
    ║  • Graceful degradation and fallback strategies          ║
    ║  • Multi-channel delivery with failover                  ║
    ║  • Intelligent error recovery                             ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Running workflow with:
    • Failure simulation: {'Yes' if simulate_failures else 'No'}
    • Failure type: {failure_type}
    • Circuit breaker: {'Enabled' if enable_circuit_breaker else 'Disabled'}
    • Recovery testing: {'Yes' if test_recovery else 'No'}
    """)
    
    # Create appropriate workflow
    if test_recovery:
        workflow = create_resilient_workflow_with_fallbacks()
        print("Using resilient workflow with explicit fallback paths...")
    else:
        workflow = create_fault_tolerant_workflow()
        print("Using standard fault-tolerant workflow...")
    
    # Configure failure parameters based on type
    failure_params = configure_failure_simulation(failure_type, simulate_failures)
    workflow.set_params(failure_params)
    
    try:
        logger.info("Starting fault-tolerant workflow execution...")
        
        # Run the workflow
        result = workflow.run(shared)
        
        # Display comprehensive results
        display_workflow_results(shared)
        display_fault_tolerance_analysis(shared)
        
        # Determine overall success
        error_analysis = shared.get("error_analysis", {})
        workflow_status = error_analysis.get("workflow_status", "unknown")
        
        if workflow_status == "success":
            print(f"\n✅ Workflow completed successfully!")
        elif workflow_status == "degraded":
            print(f"\n⚠️ Workflow completed with degraded performance but delivered results!")
        else:
            print(f"\n❌ Workflow failed but demonstrated robust error handling!")
        
        logger.info(f"Workflow finished with status: {workflow_status}")
        
    except Exception as e:
        logger.error(f"Workflow failed with unhandled exception: {e}")
        print(f"\n💥 Workflow failed with unhandled exception: {e}")
        print("This demonstrates the limits of fault tolerance - some errors cannot be recovered from.")
        
        # Show partial results if any
        if shared:
            print(f"\n📊 Partial results before failure:")
            display_partial_results(shared)


def configure_failure_simulation(failure_type: str, simulate: bool) -> Dict[str, Any]:
    """Configure failure simulation parameters based on type"""
    
    if not simulate:
        return {
            "simulate_failure": False,
            "batch_size": 50
        }
    
    base_params = {
        "simulate_failure": True,
        "batch_size": 30
    }
    
    if failure_type == "network":
        return {
            **base_params,
            "failure_rate": 0.4,
            "processing_failure_rate": 0.1,
            "enable_circuit_breaker": True
        }
    elif failure_type == "processing":
        return {
            **base_params,
            "failure_rate": 0.1,
            "processing_failure_rate": 0.5,
            "enable_circuit_breaker": False
        }
    elif failure_type == "storage":
        return {
            **base_params,
            "failure_rate": 0.1,
            "processing_failure_rate": 0.1,
            "delivery_failure_rate": 0.6
        }
    else:  # random failures
        return {
            **base_params,
            "failure_rate": random.uniform(0.2, 0.4),
            "processing_failure_rate": random.uniform(0.1, 0.3),
            "enable_circuit_breaker": random.choice([True, False])
        }


def display_workflow_results(shared: Dict[str, Any]):
    """Display detailed workflow execution results"""
    
    print(f"\n📊 Workflow Execution Results:")
    print("=" * 60)
    
    # Data collection results
    collection_result = shared.get("data_collection_result", {})
    collection_status = shared.get("collection_status", "unknown")
    
    print(f"📥 Data Collection:")
    print(f"  Status: {collection_status.upper()}")
    print(f"  Source: {collection_result.get('source', 'unknown')}")
    print(f"  Records collected: {len(collection_result.get('data', []))}")
    
    if collection_result.get("circuit_breaker_stats"):
        cb_stats = collection_result["circuit_breaker_stats"]
        print(f"  Circuit breaker: {cb_stats['state']} (failures: {cb_stats['failure_count']})")
    
    if collection_status == "fallback_used":
        cache_age = collection_result.get("cache_age_minutes", 0)
        print(f"  ⚠️ Used cached data ({cache_age:.1f} minutes old)")
    
    # Processing results
    processing_result = shared.get("processing_result", {})
    processing_status = shared.get("processing_status", "unknown")
    
    print(f"\n⚙️ Data Processing:")
    print(f"  Status: {processing_status.upper()}")
    print(f"  Input records: {processing_result.get('input_count', 0)}")
    print(f"  Processed records: {processing_result.get('output_count', 0)}")
    print(f"  Success rate: {processing_result.get('success_rate', 0):.1%}")
    
    processing_mode = processing_result.get("processing_mode", "normal")
    if processing_mode != "normal":
        print(f"  ⚠️ Processing mode: {processing_mode}")
    
    if processing_result.get("failed_records"):
        failed_count = len(processing_result["failed_records"])
        print(f"  Failed records: {failed_count}")
    
    # Delivery results
    delivery_result = shared.get("delivery_result", {})
    delivery_status = shared.get("delivery_status", "unknown")
    
    print(f"\n📤 Data Delivery:")
    print(f"  Status: {delivery_status.upper()}")
    print(f"  Records delivered: {delivery_result.get('total_delivered', 0)}")
    print(f"  Channels attempted: {delivery_result.get('channels_attempted', 0)}")
    
    delivery_results = delivery_result.get("delivery_results", [])
    for result in delivery_results:
        channel = result.get("channel", "unknown")
        success = "✅" if result.get("success", False) else "❌"
        records = result.get("records_delivered", result.get("records_attempted", 0))
        print(f"    {channel}: {success} ({records} records)")
        
        if result.get("delivery_method") == "emergency_fallback":
            print(f"      🚨 Emergency fallback to: {result.get('delivery_location', 'unknown')}")


def display_fault_tolerance_analysis(shared: Dict[str, Any]):
    """Display fault tolerance analysis and patterns demonstrated"""
    
    error_analysis = shared.get("error_analysis", {})
    
    print(f"\n🛡️ Fault Tolerance Analysis:")
    print("=" * 60)
    
    workflow_status = error_analysis.get("workflow_status", "unknown")
    error_count = error_analysis.get("error_count", 0)
    warnings = error_analysis.get("warnings", [])
    
    print(f"Overall Status: {workflow_status.upper()}")
    print(f"Errors Handled: {error_count}")
    print(f"Warnings Generated: {len(warnings)}")
    
    # Show warnings
    if warnings:
        print(f"\n⚠️ Warnings:")
        for warning in warnings:
            print(f"  • {warning}")
    
    # Show recommendations
    recommendations = error_analysis.get("recommendations", [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
    
    # Analyze fault tolerance patterns used
    print(f"\n🔧 Fault Tolerance Patterns Demonstrated:")
    
    # Circuit breaker
    collection_result = shared.get("data_collection_result", {})
    if collection_result.get("circuit_breaker_stats"):
        cb_stats = collection_result["circuit_breaker_stats"]
        print(f"  ✅ Circuit Breaker: {cb_stats['state']} state")
    
    # Fallback strategies
    collection_status = shared.get("collection_status", "")
    if collection_status == "fallback_used":
        print(f"  ✅ Data Fallback: Used cached data when primary source failed")
    
    processing_result = shared.get("processing_result", {})
    if processing_result.get("processing_mode") in ["partial", "fallback"]:
        print(f"  ✅ Processing Fallback: {processing_result['processing_mode']} mode")
    
    # Multi-channel delivery
    delivery_result = shared.get("delivery_result", {})
    if delivery_result.get("channels_attempted", 0) > 1:
        print(f"  ✅ Channel Failover: Attempted {delivery_result['channels_attempted']} delivery channels")
    
    # Emergency fallback
    delivery_results = delivery_result.get("delivery_results", [])
    for result in delivery_results:
        if result.get("delivery_method") == "emergency_fallback":
            print(f"  ✅ Emergency Fallback: Local file delivery when all channels failed")
    
    # Error recovery
    if shared.get("processing_status") == "partial_success":
        print(f"  ✅ Error Recovery: Partial processing after retry exhaustion")
    
    # Graceful degradation
    if workflow_status == "degraded":
        print(f"  ✅ Graceful Degradation: Workflow completed despite issues")


def display_partial_results(shared: Dict[str, Any]):
    """Display partial results when workflow fails"""
    
    stages_completed = []
    
    if "data_collection_result" in shared:
        stages_completed.append("Data Collection")
    if "processing_result" in shared:
        stages_completed.append("Data Processing")
    if "delivery_result" in shared:
        stages_completed.append("Data Delivery")
    if "error_analysis" in shared:
        stages_completed.append("Error Analysis")
    
    print(f"  Completed stages: {', '.join(stages_completed)}")
    
    for key, value in shared.items():
        if not key.startswith("_") and not key.startswith("config"):
            if isinstance(value, dict) and "data" in value:
                data_count = len(value["data"]) if isinstance(value["data"], list) else "unknown"
                print(f"  {key}: {data_count} records")
            elif isinstance(value, str):
                print(f"  {key}: {value}")


def demonstrate_circuit_breaker():
    """Demonstrate circuit breaker behavior in isolation"""
    
    print(f"\n🔧 Circuit Breaker Demonstration:")
    print("=" * 50)
    
    from nodes import CircuitBreaker
    
    # Create circuit breaker with low threshold for demo
    cb = CircuitBreaker(failure_threshold=3, timeout=5, name="demo")
    
    def failing_service():
        if random.random() < 0.8:  # 80% failure rate
            raise ConnectionError("Service unavailable")
        return "Success!"
    
    print("Calling failing service repeatedly...")
    
    for i in range(10):
        try:
            result = cb.call(failing_service)
            print(f"  Call {i+1}: ✅ {result}")
        except Exception as e:
            print(f"  Call {i+1}: ❌ {e}")
        
        # Show circuit breaker state
        stats = cb.get_stats()
        print(f"    Circuit state: {stats['state']} (failures: {stats['failure_count']})")
        
        if stats['state'] == 'OPEN':
            print("    🚨 Circuit breaker opened - protecting system from further failures")
            break


def main():
    """Main entry point with command line options"""
    
    parser = argparse.ArgumentParser(description="KayGraph Fault-Tolerant Workflow Demo")
    parser.add_argument(
        "--simulate-failures",
        action="store_true",
        help="Simulate various types of failures"
    )
    parser.add_argument(
        "--failure-type",
        choices=["network", "processing", "storage", "random"],
        default="random",
        help="Type of failures to simulate"
    )
    parser.add_argument(
        "--enable-circuit-breaker",
        action="store_true",
        help="Enable circuit breaker pattern"
    )
    parser.add_argument(
        "--test-recovery",
        action="store_true",
        help="Test recovery patterns with explicit fallback paths"
    )
    parser.add_argument(
        "--demo-circuit-breaker",
        action="store_true",
        help="Demonstrate circuit breaker behavior in isolation"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run circuit breaker demo if requested
    if args.demo_circuit_breaker:
        demonstrate_circuit_breaker()
        return
    
    # Run the main demo
    run_fault_tolerance_demo(
        simulate_failures=args.simulate_failures,
        failure_type=args.failure_type,
        enable_circuit_breaker=args.enable_circuit_breaker,
        test_recovery=args.test_recovery
    )


if __name__ == "__main__":
    main()