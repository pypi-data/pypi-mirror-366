import argparse
import logging
from typing import Dict, Any
from graph import create_streaming_llm_workflow, create_resilient_streaming_workflow

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_streaming_demo(
    prompt: str = None,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 150,
    enable_guardrails: bool = True,
    simulate_failures: bool = False,
    monitor_performance: bool = False,
    use_resilient_workflow: bool = False
):
    """Run the streaming LLM demo with KayGraph enhancements"""
    
    # Default prompt if none provided
    if not prompt:
        prompt = "Explain the concept of machine learning in simple terms and provide a practical example."
    
    # Initialize shared context
    shared: Dict[str, Any] = {
        "config": {
            "enable_guardrails": enable_guardrails,
            "simulate_failures": simulate_failures,
            "monitor_performance": monitor_performance
        }
    }
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║         KayGraph Enhanced Streaming LLM Demo             ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This demo shows KayGraph's enhancements to streaming:    ║
    ║  • Real-time metrics collection during streaming         ║
    ║  • Token-by-token validation and safety checks           ║
    ║  • Circuit breaker protection for LLM APIs               ║
    ║  • Graceful error recovery and fallback responses        ║
    ║  • Performance monitoring and optimization               ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Configuration:
    • Model: {model}
    • Temperature: {temperature}
    • Max tokens: {max_tokens}
    • Guardrails: {'Enabled' if enable_guardrails else 'Disabled'}
    • Failure simulation: {'Yes' if simulate_failures else 'No'}
    • Performance monitoring: {'Yes' if monitor_performance else 'No'}
    
    Prompt: "{prompt[:100]}{'...' if len(prompt) > 100 else ''}"
    """)
    
    # Create appropriate workflow
    if use_resilient_workflow:
        workflow = create_resilient_streaming_workflow()
        print("Using resilient streaming workflow with error handling...")
    else:
        workflow = create_streaming_llm_workflow()
        print("Using standard enhanced streaming workflow...")
    
    # Configure workflow parameters
    workflow.set_params({
        "prompt": prompt,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "enable_guardrails": enable_guardrails,
        "simulate_failure": simulate_failures
    })
    
    try:
        logger.info("Starting enhanced streaming LLM workflow...")
        
        # Run the workflow
        result = workflow.run(shared)
        
        # Display comprehensive results
        display_streaming_results(shared)
        
        if monitor_performance:
            display_performance_analysis(shared)
        
        # Show the enhanced features
        display_kaygraph_enhancements(shared)
        
        logger.info("Streaming workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Streaming workflow failed: {e}")
        print(f"\n❌ Streaming failed: {e}")
        print("KayGraph's error handling prevented system crashes and provided diagnostics!")
        
        # Show partial results
        if shared:
            print(f"\n📊 Partial results before failure:")
            display_partial_streaming_results(shared)


def display_streaming_results(shared: Dict[str, Any]):
    """Display the streaming results with KayGraph enhancements"""
    
    print(f"\n📊 Streaming Results:")
    print("=" * 60)
    
    # Prompt processing results
    processed_prompt = shared.get("processed_prompt", {})
    print(f"📝 Prompt Processing:")
    print(f"  Original length: {len(processed_prompt.get('original_prompt', ''))}")
    print(f"  Optimized length: {len(processed_prompt.get('prompt', ''))}")
    print(f"  Model: {processed_prompt.get('model', 'unknown')}")
    print(f"  Temperature: {processed_prompt.get('temperature', 'unknown')}")
    print(f"  Max tokens: {processed_prompt.get('max_tokens', 'unknown')}")
    
    # Streaming performance
    streaming_result = shared.get("streaming_result", {})
    streaming_metrics = streaming_result.get("streaming_metrics", {})
    
    print(f"\n⚡ Streaming Performance:")
    print(f"  Success: {'✅ Yes' if streaming_result.get('success', False) else '❌ No'}")
    print(f"  Total tokens: {streaming_metrics.get('total_tokens', 0)}")
    print(f"  Streaming time: {streaming_metrics.get('elapsed_time', 0):.2f}s")
    print(f"  Tokens/second: {streaming_metrics.get('tokens_per_second', 0):.1f}")
    print(f"  Recent rate: {streaming_metrics.get('recent_tokens_per_second', 0):.1f} tokens/sec")
    
    if streaming_metrics.get("error_count", 0) > 0:
        print(f"  ⚠️ Errors during streaming: {streaming_metrics['error_count']}")
    
    # Response validation and safety
    response_result = shared.get("response_result", {})
    quality_metrics = response_result.get("quality_metrics", {})
    safety_summary = response_result.get("safety_summary", {})
    
    print(f"\n🛡️ Response Validation & Safety:")
    print(f"  Total tokens processed: {quality_metrics.get('total_tokens', 0)}")
    print(f"  Validated tokens: {quality_metrics.get('validated_tokens', 0)}")
    print(f"  Filter rate: {quality_metrics.get('filter_rate', 0):.1%}")
    print(f"  Avg safety score: {quality_metrics.get('avg_safety_score', 0):.3f}")
    print(f"  Safety violations: {safety_summary.get('total_violations', 0)}")
    
    if response_result.get("filtered_tokens"):
        filtered_count = len(response_result["filtered_tokens"])
        print(f"  🚫 Filtered tokens: {filtered_count}")
    
    # Final response
    validated_response = response_result.get("validated_response", "")
    print(f"\n💬 Generated Response:")
    print(f"  Length: {len(validated_response)} characters")
    if validated_response:
        # Show first 200 characters
        preview = validated_response[:200]
        if len(validated_response) > 200:
            preview += "..."
        print(f"  Preview: \"{preview}\"")
    
    # Overall summary
    final_summary = shared.get("final_summary", {})
    if final_summary:
        performance_score = final_summary.get("performance_score", 0)
        print(f"\n📈 Overall Performance Score: {performance_score:.3f}/1.000")


def display_performance_analysis(shared: Dict[str, Any]):
    """Display detailed performance analysis"""
    
    final_summary = shared.get("final_summary", {})
    
    print(f"\n🔍 Performance Analysis:")
    print("=" * 60)
    
    streaming_performance = final_summary.get("streaming_performance", {})
    quality_metrics = final_summary.get("quality_metrics", {})
    
    # Performance breakdown
    print(f"📊 Performance Breakdown:")
    
    # Streaming metrics
    tokens_per_second = streaming_performance.get("tokens_per_second", 0)
    if tokens_per_second > 8:
        print(f"  Streaming Speed: ✅ Excellent ({tokens_per_second:.1f} tokens/sec)")
    elif tokens_per_second > 5:
        print(f"  Streaming Speed: ⚠️ Good ({tokens_per_second:.1f} tokens/sec)")
    else:
        print(f"  Streaming Speed: ❌ Poor ({tokens_per_second:.1f} tokens/sec)")
    
    # Safety performance
    safety_score = quality_metrics.get("avg_safety_score", 0)
    if safety_score > 0.9:
        print(f"  Safety Quality: ✅ Excellent ({safety_score:.3f})")
    elif safety_score > 0.7:
        print(f"  Safety Quality: ⚠️ Good ({safety_score:.3f})")
    else:
        print(f"  Safety Quality: ❌ Poor ({safety_score:.3f})")
    
    # Filter efficiency
    filter_rate = quality_metrics.get("filter_rate", 0)
    if filter_rate < 0.05:
        print(f"  Filter Efficiency: ✅ Excellent ({filter_rate:.1%} filtered)")
    elif filter_rate < 0.15:
        print(f"  Filter Efficiency: ⚠️ Good ({filter_rate:.1%} filtered)")
    else:
        print(f"  Filter Efficiency: ❌ High filtering ({filter_rate:.1%} filtered)")
    
    # Recommendations
    print(f"\n💡 Performance Recommendations:")
    
    if tokens_per_second < 5:
        print(f"  • Consider reducing max_tokens or using a faster model")
    
    if filter_rate > 0.1:
        print(f"  • Review prompt content - high filter rate detected")
    
    if safety_score < 0.8:
        print(f"  • Enable stricter safety guardrails")
    
    error_count = streaming_performance.get("error_count", 0)
    if error_count > 0:
        print(f"  • Investigate streaming errors - {error_count} errors occurred")


def display_kaygraph_enhancements(shared: Dict[str, Any]):
    """Display KayGraph-specific enhancements over basic streaming"""
    
    print(f"\n🚀 KayGraph Enhancements Demonstrated:")
    print("=" * 60)
    
    enhancements_shown = []
    
    # Metrics collection
    streaming_result = shared.get("streaming_result", {})
    if streaming_result.get("streaming_metrics"):
        enhancements_shown.append("✅ Real-time streaming metrics collection")
    
    # Validation
    response_result = shared.get("response_result", {})
    if response_result.get("quality_metrics"):
        enhancements_shown.append("✅ Token-by-token validation during streaming")
    
    # Safety guardrails
    safety_summary = response_result.get("safety_summary", {})
    if safety_summary:
        enhancements_shown.append("✅ Real-time content safety guardrails")
    
    # Circuit breaker
    if streaming_result.get("source") == "cache_fallback":
        enhancements_shown.append("✅ Circuit breaker with cached fallback")
    
    # Error handling
    if streaming_result.get("success", True) or response_result:
        enhancements_shown.append("✅ Robust error handling and recovery")
    
    # Performance analysis
    final_summary = shared.get("final_summary", {})
    if final_summary.get("performance_score") is not None:
        enhancements_shown.append("✅ Comprehensive performance scoring")
    
    # Prompt optimization
    processed_prompt = shared.get("processed_prompt", {})
    if processed_prompt.get("original_prompt") != processed_prompt.get("prompt"):
        enhancements_shown.append("✅ Automatic prompt optimization")
    
    for enhancement in enhancements_shown:
        print(f"  {enhancement}")
    
    print(f"\n🆚 Comparison with Basic Streaming:")
    print(f"  Basic Streaming: Just token generation")
    print(f"  KayGraph Enhanced: Production-ready with metrics, safety, and reliability")
    
    # Show metric advantages
    streaming_metrics = streaming_result.get("streaming_metrics", {})
    if streaming_metrics:
        print(f"\n📈 Metrics Advantage:")
        print(f"  • Real-time performance monitoring")
        print(f"  • Streaming quality assessment")
        print(f"  • Automatic performance optimization")
        print(f"  • Historical performance tracking")


def display_partial_streaming_results(shared: Dict[str, Any]):
    """Display partial results when streaming fails"""
    
    for key, value in shared.items():
        if not key.startswith("_") and not key.startswith("config"):
            if key == "streaming_result":
                metrics = value.get("streaming_metrics", {})
                print(f"  {key}: {metrics.get('total_tokens', 0)} tokens streamed")
            elif key == "response_result":
                tokens = len(value.get("validated_tokens", []))
                print(f"  {key}: {tokens} tokens validated")
            elif isinstance(value, dict) and "session_id" in value:
                print(f"  {key}: Session {value['session_id']}")
            elif isinstance(value, str):
                print(f"  {key}: {value}")


def main():
    """Main entry point with command line options"""
    
    parser = argparse.ArgumentParser(description="KayGraph Enhanced Streaming LLM Demo")
    parser.add_argument(
        "--prompt",
        type=str,
        help="Custom prompt to use for streaming"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        help="LLM model to simulate"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for generation"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=150,
        help="Maximum tokens to generate"
    )
    parser.add_argument(
        "--disable-guardrails",
        action="store_true",
        help="Disable safety guardrails"
    )
    parser.add_argument(
        "--simulate-failures",
        action="store_true",
        help="Simulate streaming failures for testing"
    )
    parser.add_argument(
        "--monitor-performance",
        action="store_true",
        help="Enable detailed performance monitoring"
    )
    parser.add_argument(
        "--use-resilient-workflow",
        action="store_true",
        help="Use resilient workflow with advanced error handling"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the demo
    run_streaming_demo(
        prompt=args.prompt,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        enable_guardrails=not args.disable_guardrails,
        simulate_failures=args.simulate_failures,
        monitor_performance=args.monitor_performance,
        use_resilient_workflow=args.use_resilient_workflow
    )


if __name__ == "__main__":
    main()