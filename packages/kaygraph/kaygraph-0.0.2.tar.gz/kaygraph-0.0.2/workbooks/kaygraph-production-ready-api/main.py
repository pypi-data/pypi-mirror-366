import argparse
import asyncio
import json
import logging
import uvicorn
from typing import Dict, Any

from api_server import create_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_api_demo(
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 1,
    debug: bool = False,
    simulate_failures: bool = False
):
    """Run the production-ready API demo"""
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║        KayGraph Production-Ready API Demo                 ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  This demo shows KayGraph's enterprise API features:     ║
    ║  • Comprehensive request/response validation             ║
    ║  • Real-time metrics collection and monitoring          ║
    ║  • Circuit breaker protection for external services     ║
    ║  • Robust error handling with graceful degradation      ║
    ║  • Resource management with automatic cleanup           ║
    ║  • Production-ready monitoring and health checks        ║
    ╚═══════════════════════════════════════════════════════════╝
    
    API Configuration:
    • Host: {host}
    • Port: {port}
    • Workers: {workers}
    • Debug mode: {'Enabled' if debug else 'Disabled'}
    • Failure simulation: {'Enabled' if simulate_failures else 'Disabled'}
    
    Available Endpoints:
    • GET  /health                    - Health check with dependencies
    • GET  /metrics                   - Comprehensive API metrics
    • GET  /api/v1/status            - System status and performance
    • POST /api/v1/process           - Main processing endpoint
    • POST /api/v1/batch-process     - Batch processing endpoint
    • GET  /docs                     - Interactive API documentation
    
    Starting server...
    """)
    
    # Create FastAPI app
    app = create_app()
    
    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        workers=workers,
        log_level="debug" if debug else "info",
        reload=debug,
        access_log=True
    )
    
    # Start server
    server = uvicorn.Server(config)
    
    try:
        logger.info(f"Starting KayGraph Production API on {host}:{port}")
        server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down API server...")
    except Exception as e:
        logger.error(f"Server error: {e}")


async def run_api_tests():
    """Run API tests to demonstrate functionality"""
    
    print(f"\n🧪 Running API Tests:")
    print("=" * 50)
    
    import aiohttp
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        
        # Test health endpoint
        print("1. Testing health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Health check: {data['status']}")
                    print(f"   Dependencies: {', '.join(data['dependencies'].keys())}")
                else:
                    print(f"   ❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
        
        # Test metrics endpoint
        print("\n2. Testing metrics endpoint...")
        try:
            async with session.get(f"{base_url}/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    api_metrics = data['api_metrics']
                    print(f"   ✅ Metrics: {api_metrics['requests_total']} total requests")
                    print(f"   Success rate: {api_metrics['success_rate']:.1%}")
                else:
                    print(f"   ❌ Metrics failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Metrics error: {e}")
        
        # Test text analysis processing
        print("\n3. Testing text analysis processing...")
        try:
            payload = {
                "data": "This is a great example of KayGraph's amazing capabilities!",
                "processing_type": "text_analysis",
                "options": {}
            }
            
            async with session.post(f"{base_url}/api/v1/process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data['data']
                    print(f"   ✅ Text analysis: {result['sentiment']} sentiment")
                    print(f"   Confidence: {result['confidence']:.3f}")
                    print(f"   Keywords: {', '.join(result['keywords'][:3])}")
                else:
                    print(f"   ❌ Text analysis failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Text analysis error: {e}")
        
        # Test data transformation
        print("\n4. Testing data transformation...")
        try:
            payload = {
                "data": {"name": "JOHN DOE", "email": "JOHN@EXAMPLE.COM", "age": 30},
                "processing_type": "data_transformation",
                "options": {"transformation": "normalize"}
            }
            
            async with session.post(f"{base_url}/api/v1/process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data['data']
                    print(f"   ✅ Data transformation: {result['transformation_applied']}")
                    print(f"   Transformed: {result['transformed_data']}")
                else:
                    print(f"   ❌ Data transformation failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Data transformation error: {e}")
        
        # Test ML inference
        print("\n5. Testing ML inference...")
        try:
            payload = {
                "data": [1.2, 3.4, 2.1, 4.5, 3.2],
                "processing_type": "ml_inference",
                "options": {"model": "classification"}
            }
            
            async with session.post(f"{base_url}/api/v1/process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data['data']
                    print(f"   ✅ ML inference: {result['predicted_class']}")
                    print(f"   Confidence: {result['confidence']:.3f}")
                else:
                    print(f"   ❌ ML inference failed: {response.status}")
        except Exception as e:
            print(f"   ❌ ML inference error: {e}")
        
        # Test batch processing
        print("\n6. Testing batch processing...")
        try:
            payload = {
                "items": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "batch_id": "test_batch_001",
                "priority": 7
            }
            
            async with session.post(f"{base_url}/api/v1/batch-process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    batch_id = data['metadata']['batch_id']
                    batch_size = data['metadata']['batch_size']
                    print(f"   ✅ Batch processing: {batch_id}")
                    print(f"   Batch size: {batch_size} items")
                else:
                    print(f"   ❌ Batch processing failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Batch processing error: {e}")
        
        # Test invalid request (validation)
        print("\n7. Testing request validation...")
        try:
            payload = {
                "data": "test",
                "processing_type": "invalid_type"  # Invalid type
            }
            
            async with session.post(f"{base_url}/api/v1/process", json=payload) as response:
                if response.status == 400:
                    data = await response.json()
                    print(f"   ✅ Validation correctly rejected invalid request")
                    print(f"   Error: {data['error']['message']}")
                else:
                    print(f"   ❌ Validation should have failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Validation test error: {e}")
        
        # Final metrics check
        print("\n8. Final metrics check...")
        try:
            async with session.get(f"{base_url}/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    api_metrics = data['api_metrics']
                    print(f"   ✅ Final metrics: {api_metrics['requests_total']} total requests")
                    print(f"   Success rate: {api_metrics['success_rate']:.1%}")
                    print(f"   Avg response time: {api_metrics['response_time_ms']['avg']:.1f}ms")
                else:
                    print(f"   ❌ Final metrics failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Final metrics error: {e}")
    
    print(f"\n🎉 API tests completed!")
    print(f"\n🔍 KayGraph Production Features Demonstrated:")
    print(f"  ✅ Comprehensive request validation with detailed error messages")
    print(f"  ✅ Real-time metrics collection and monitoring")
    print(f"  ✅ Multiple processing types with business logic validation")
    print(f"  ✅ Structured error responses with correlation IDs")
    print(f"  ✅ Health checks with dependency monitoring")
    print(f"  ✅ Performance tracking and response time monitoring")
    print(f"  ✅ Batch processing capabilities")
    print(f"  ✅ Production-ready API patterns and best practices")


def main():
    """Main entry point with command line options"""
    
    parser = argparse.ArgumentParser(description="KayGraph Production-Ready API Demo")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with auto-reload"
    )
    parser.add_argument(
        "--simulate-failures",
        action="store_true",
        help="Simulate random processing failures for testing"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run API tests instead of starting server"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run tests if requested
    if args.test:
        print("Running API tests...")
        print("Make sure the API server is running on localhost:8000")
        asyncio.run(run_api_tests())
        return
    
    # Run the server
    run_api_demo(
        host=args.host,
        port=args.port,
        workers=args.workers,
        debug=args.debug,
        simulate_failures=args.simulate_failures
    )


if __name__ == "__main__":
    main()