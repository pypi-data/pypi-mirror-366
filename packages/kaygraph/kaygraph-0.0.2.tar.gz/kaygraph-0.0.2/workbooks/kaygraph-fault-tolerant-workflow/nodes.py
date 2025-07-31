import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from kaygraph import Node
import logging

logging.basicConfig(level=logging.INFO)


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, name: str = "unnamed"):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(f"CircuitBreaker_{name}")
    
    def call(self, func, *args, **kwargs):
        """Call function with circuit breaker protection"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                self.logger.info(f"Circuit breaker {self.name}: Moving to HALF_OPEN")
            else:
                self.logger.warning(f"Circuit breaker {self.name}: OPEN - call blocked")
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time > self.timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.logger.info(f"Circuit breaker {self.name}: Reset to CLOSED")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.logger.warning(f"Circuit breaker {self.name}: Opened after {self.failure_count} failures")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class DataCollectorNode(Node):
    """Collects data with circuit breaker protection"""
    
    def __init__(self):
        super().__init__(max_retries=3, wait=1, node_id="data_collector")
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3, 
            timeout=30, 
            name="data_collection"
        )
        self.cache = {}
    
    def before_prep(self, shared: Dict[str, Any]):
        """Validate conditions before data collection"""
        self.logger.info("Checking data collection prerequisites...")
        
        # Check if we have cached data as fallback
        if not self.cache and self.params.get("require_cache_fallback", False):
            self.logger.warning("No cached data available for fallback")
        
        # Log circuit breaker status
        cb_stats = self.circuit_breaker.get_stats()
        self.logger.info(f"Circuit breaker status: {cb_stats['state']}")
    
    def after_exec(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any):
        """Post-execution validation and caching"""
        if exec_res and "data" in exec_res:
            # Cache successful results
            self.cache["last_successful_data"] = exec_res["data"]
            self.cache["cached_at"] = time.time()
            self.logger.info(f"Cached {len(exec_res['data'])} records for fallback")
    
    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Handle collection errors with fallback logic"""
        self.logger.error(f"Data collection failed: {error}")
        
        if isinstance(error, CircuitBreakerOpenError):
            # Circuit breaker is open, use cached data
            if self.cache.get("last_successful_data"):
                cached_data = self.cache["last_successful_data"]
                cached_time = self.cache.get("cached_at", 0)
                age_minutes = (time.time() - cached_time) / 60
                
                self.logger.info(f"Using cached data ({len(cached_data)} records, {age_minutes:.1f} min old)")
                
                # Store fallback data in shared context
                shared["data_collection_result"] = {
                    "data": cached_data,
                    "source": "cache_fallback",
                    "cache_age_minutes": age_minutes
                }
                shared["collection_status"] = "fallback_used"
                
                # Suppress the error since we handled it
                return True
        
        # For other errors, let them propagate (unless we have other fallback strategies)
        return False
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "data_source": self.params.get("data_source", "primary_api"),
            "batch_size": self.params.get("batch_size", 100)
        }
    
    def exec(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data with circuit breaker protection"""
        
        def collect_data():
            # Simulate data collection with potential failures
            if self.params.get("simulate_failure", False):
                failure_rate = self.params.get("failure_rate", 0.3)
                if random.random() < failure_rate:
                    raise ConnectionError("Simulated data collection failure")
            
            # Simulate collection time
            time.sleep(random.uniform(0.1, 0.5))
            
            # Generate mock data
            data = []
            for i in range(config["batch_size"]):
                record = {
                    "id": f"record_{i}_{int(time.time())}",
                    "value": random.randint(1, 1000),
                    "timestamp": datetime.now().isoformat(),
                    "source": config["data_source"]
                }
                data.append(record)
            
            return data
        
        # Use circuit breaker to call data collection
        try:
            collected_data = self.circuit_breaker.call(collect_data)
            
            return {
                "data": collected_data,
                "source": "primary",
                "collected_at": time.time(),
                "circuit_breaker_stats": self.circuit_breaker.get_stats()
            }
        
        except CircuitBreakerOpenError:
            # This will be handled by on_error hook
            raise
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        if "data_collection_result" not in shared:
            shared["data_collection_result"] = exec_res
            shared["collection_status"] = "success"
        
        # Determine next action based on collection status
        if shared.get("collection_status") == "fallback_used":
            return "circuit_open"
        else:
            return "success"


class ProcessingNode(Node):
    """Processes data with retry and fallback mechanisms"""
    
    def __init__(self):
        super().__init__(max_retries=5, wait=2, node_id="data_processor")
        self.processing_history = []
    
    def before_prep(self, shared: Dict[str, Any]):
        """Validate input data before processing"""
        collection_result = shared.get("data_collection_result", {})
        
        if not collection_result.get("data"):
            self.logger.warning("No data available for processing")
        
        data_source = collection_result.get("source", "unknown")
        self.logger.info(f"Processing data from source: {data_source}")
        
        # Log if we're processing fallback data
        if data_source == "cache_fallback":
            self.logger.info("Processing fallback data due to collection issues")
    
    def after_exec(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any):
        """Post-processing validation and history tracking"""
        # Track processing history
        self.processing_history.append({
            "timestamp": time.time(),
            "input_count": len(prep_res),
            "output_count": len(exec_res.get("processed_data", [])),
            "processing_time": exec_res.get("processing_time", 0),
            "retry_count": getattr(self, 'cur_retry', 0)
        })
        
        # Validate processing results
        if exec_res.get("processed_data"):
            success_rate = exec_res.get("success_rate", 0)
            if success_rate < 0.8:
                self.logger.warning(f"Low processing success rate: {success_rate:.2%}")
    
    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Handle processing errors with intelligent recovery"""
        self.logger.error(f"Processing failed on attempt {getattr(self, 'cur_retry', 0) + 1}: {error}")
        
        # If we've tried multiple times and it's a data issue, try partial processing
        if getattr(self, 'cur_retry', 0) >= 2:
            input_data = shared.get("data_collection_result", {}).get("data", [])
            
            if input_data:
                try:
                    # Attempt partial processing with smaller batch
                    partial_data = input_data[:len(input_data)//2]
                    self.logger.info(f"Attempting partial processing with {len(partial_data)} records")
                    
                    # Simple processing for recovery
                    processed_partial = []
                    for record in partial_data:
                        try:
                            processed_record = {
                                **record,
                                "processed": True,
                                "processing_mode": "partial_recovery",
                                "processed_at": time.time()
                            }
                            processed_partial.append(processed_record)
                        except:
                            continue
                    
                    if processed_partial:
                        # Store partial results
                        partial_result = {
                            "processed_data": processed_partial,
                            "processing_mode": "partial",
                            "success_rate": len(processed_partial) / len(partial_data),
                            "original_count": len(input_data),
                            "processed_count": len(processed_partial)
                        }
                        
                        shared["processing_result"] = partial_result
                        shared["processing_status"] = "partial_success"
                        
                        self.logger.info(f"Partial processing succeeded: {len(processed_partial)} records")
                        return True  # Suppress the error
                
                except Exception as recovery_error:
                    self.logger.error(f"Partial processing also failed: {recovery_error}")
        
        return False  # Let the error propagate
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        collection_result = shared.get("data_collection_result", {})
        return collection_result.get("data", [])
    
    def exec(self, input_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process data with potential failures and recovery"""
        start_time = time.time()
        processed_data = []
        failed_records = []
        
        # Simulate processing failures
        if self.params.get("simulate_failure", False):
            failure_rate = self.params.get("processing_failure_rate", 0.2)
            if random.random() < failure_rate:
                raise RuntimeError("Simulated processing failure")
        
        for record in input_data:
            try:
                # Simulate processing time
                time.sleep(random.uniform(0.01, 0.05))
                
                # Simulate occasional record-level failures
                if random.random() < 0.05:  # 5% record failure rate
                    failed_records.append(record["id"])
                    continue
                
                # Process the record
                processed_record = {
                    **record,
                    "processed": True,
                    "processing_time": time.time() - start_time,
                    "processed_value": record["value"] * 2,
                    "quality_score": random.uniform(0.7, 1.0)
                }
                processed_data.append(processed_record)
                
            except Exception as e:
                self.logger.warning(f"Failed to process record {record.get('id', 'unknown')}: {e}")
                failed_records.append(record.get("id", "unknown"))
        
        processing_time = time.time() - start_time
        success_rate = len(processed_data) / len(input_data) if input_data else 0
        
        return {
            "processed_data": processed_data,
            "failed_records": failed_records,
            "processing_time": processing_time,
            "success_rate": success_rate,
            "input_count": len(input_data),
            "output_count": len(processed_data)
        }
    
    def exec_fallback(self, prep_res: List[Dict[str, Any]], exc: Exception) -> Dict[str, Any]:
        """Fallback processing when main processing fails"""
        self.logger.info("Using fallback processing mode")
        
        # Simple fallback processing - just mark records as processed
        fallback_data = []
        for record in prep_res[:10]:  # Limit to first 10 for safety
            fallback_record = {
                **record,
                "processed": True,
                "processing_mode": "fallback",
                "processed_at": time.time()
            }
            fallback_data.append(fallback_record)
        
        return {
            "processed_data": fallback_data,
            "processing_mode": "fallback",
            "success_rate": 1.0,
            "fallback_reason": str(exc)
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        if "processing_result" not in shared:
            shared["processing_result"] = exec_res
            shared["processing_status"] = "success"
        
        # Determine next action based on processing results
        processing_mode = exec_res.get("processing_mode", "normal")
        success_rate = exec_res.get("success_rate", 0)
        
        if processing_mode == "partial":
            return "retry_exhausted"
        elif success_rate < 0.5:
            return "retry_exhausted"
        else:
            return "success"


class DeliveryNode(Node):
    """Delivers results with multiple channel support and failover"""
    
    def __init__(self):
        super().__init__(max_retries=3, wait=1, node_id="delivery")
        self.delivery_channels = ["primary", "secondary", "backup"]
        self.channel_health = {channel: "healthy" for channel in self.delivery_channels}
    
    def before_prep(self, shared: Dict[str, Any]):
        """Check delivery channel health before attempting delivery"""
        processing_result = shared.get("processing_result", {})
        
        data_count = len(processing_result.get("processed_data", []))
        self.logger.info(f"Preparing to deliver {data_count} processed records")
        
        # Check channel health
        healthy_channels = [ch for ch, health in self.channel_health.items() if health == "healthy"]
        self.logger.info(f"Healthy delivery channels: {healthy_channels}")
        
        if not healthy_channels:
            self.logger.warning("No healthy delivery channels available")
    
    def after_exec(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any):
        """Update channel health based on delivery results"""
        delivery_results = exec_res.get("delivery_results", [])
        
        for result in delivery_results:
            channel = result.get("channel")
            success = result.get("success", False)
            
            if channel and not success:
                # Mark channel as unhealthy after failure
                self.channel_health[channel] = "degraded"
                self.logger.warning(f"Marking channel {channel} as degraded")
            elif channel and success:
                # Restore channel health on success
                self.channel_health[channel] = "healthy"
    
    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Handle delivery failures with channel failover"""
        self.logger.error(f"Delivery failed: {error}")
        
        # Try alternate delivery method
        processing_result = shared.get("processing_result", {})
        processed_data = processing_result.get("processed_data", [])
        
        if processed_data:
            try:
                # Attempt local file delivery as ultimate fallback
                import json
                import tempfile
                
                fallback_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json.dump(processed_data, fallback_file, indent=2)
                fallback_file.close()
                
                fallback_result = {
                    "delivery_results": [{
                        "channel": "local_file",
                        "success": True,
                        "records_delivered": len(processed_data),
                        "delivery_location": fallback_file.name,
                        "delivery_method": "emergency_fallback"
                    }],
                    "total_delivered": len(processed_data),
                    "delivery_method": "emergency_fallback"
                }
                
                shared["delivery_result"] = fallback_result
                shared["delivery_status"] = "emergency_fallback"
                
                self.logger.info(f"Emergency fallback delivery to {fallback_file.name}")
                return True  # Suppress the error
                
            except Exception as fallback_error:
                self.logger.error(f"Emergency fallback also failed: {fallback_error}")
        
        return False
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        processing_result = shared.get("processing_result", {})
        return {
            "data": processing_result.get("processed_data", []),
            "processing_status": shared.get("processing_status", "unknown")
        }
    
    def exec(self, delivery_input: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver data with multi-channel support"""
        data_to_deliver = delivery_input["data"]
        
        if not data_to_deliver:
            return {"delivery_results": [], "total_delivered": 0}
        
        delivery_results = []
        healthy_channels = [ch for ch, health in self.channel_health.items() if health == "healthy"]
        
        if not healthy_channels:
            healthy_channels = ["backup"]  # Always try backup as last resort
        
        # Try delivery channels in order of preference
        for channel in healthy_channels:
            try:
                result = self._deliver_to_channel(channel, data_to_deliver)
                delivery_results.append(result)
                
                if result["success"]:
                    break  # Success, no need to try other channels
                    
            except Exception as e:
                self.logger.warning(f"Delivery to {channel} failed: {e}")
                delivery_results.append({
                    "channel": channel,
                    "success": False,
                    "error": str(e),
                    "records_attempted": len(data_to_deliver)
                })
        
        total_delivered = sum(r.get("records_delivered", 0) for r in delivery_results if r.get("success"))
        
        return {
            "delivery_results": delivery_results,
            "total_delivered": total_delivered,
            "channels_attempted": len(delivery_results)
        }
    
    def _deliver_to_channel(self, channel: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deliver data to a specific channel"""
        # Simulate delivery time
        time.sleep(random.uniform(0.2, 0.8))
        
        # Simulate channel-specific failure rates
        failure_rates = {
            "primary": 0.1,
            "secondary": 0.2,
            "backup": 0.05
        }
        
        if self.params.get("simulate_failure", False):
            failure_rate = failure_rates.get(channel, 0.3)
            if random.random() < failure_rate:
                raise ConnectionError(f"Simulated {channel} delivery failure")
        
        # Simulate successful delivery
        return {
            "channel": channel,
            "success": True,
            "records_delivered": len(data),
            "delivery_time": time.time(),
            "delivery_id": f"{channel}_{int(time.time())}"
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["delivery_result"] = exec_res
        
        total_delivered = exec_res.get("total_delivered", 0)
        input_count = len(prep_res.get("data", []))
        
        if total_delivered == 0:
            shared["delivery_status"] = "failed"
            return "delivery_failed"
        elif total_delivered < input_count:
            shared["delivery_status"] = "partial"
            return "delivery_failed"
        else:
            shared["delivery_status"] = "success"
            return "success"


class ErrorHandlerNode(Node):
    """Centralized error management and reporting"""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "collection_status": shared.get("collection_status", "unknown"),
            "processing_status": shared.get("processing_status", "unknown"),
            "delivery_status": shared.get("delivery_status", "unknown"),
            "errors_encountered": shared.get("errors_encountered", [])
        }
    
    def exec(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and categorize errors across the workflow"""
        
        error_summary = {
            "workflow_status": "success",
            "stage_statuses": status_data,
            "error_count": 0,
            "warnings": [],
            "recommendations": []
        }
        
        # Analyze each stage
        collection_status = status_data.get("collection_status", "unknown")
        processing_status = status_data.get("processing_status", "unknown")
        delivery_status = status_data.get("delivery_status", "unknown")
        
        # Check for issues
        if collection_status == "fallback_used":
            error_summary["warnings"].append("Data collection used fallback cache")
            error_summary["recommendations"].append("Check primary data source health")
        
        if processing_status == "partial_success":
            error_summary["warnings"].append("Processing completed with partial results")
            error_summary["recommendations"].append("Review processing logic for failures")
        
        if delivery_status in ["failed", "partial", "emergency_fallback"]:
            error_summary["error_count"] += 1
            error_summary["recommendations"].append("Check delivery channel health")
            
            if delivery_status == "emergency_fallback":
                error_summary["workflow_status"] = "degraded"
            else:
                error_summary["workflow_status"] = "failed"
        
        # Overall workflow assessment
        if error_summary["error_count"] > 0 or error_summary["warnings"]:
            if error_summary["workflow_status"] == "success":
                error_summary["workflow_status"] = "degraded"
        
        return error_summary
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["error_analysis"] = exec_res
        
        workflow_status = exec_res.get("workflow_status", "unknown")
        error_count = exec_res.get("error_count", 0)
        warning_count = len(exec_res.get("warnings", []))
        
        self.logger.info(f"Workflow completed with status: {workflow_status}")
        self.logger.info(f"Errors: {error_count}, Warnings: {warning_count}")
        
        # Log recommendations
        for rec in exec_res.get("recommendations", []):
            self.logger.info(f"Recommendation: {rec}")
        
        return None