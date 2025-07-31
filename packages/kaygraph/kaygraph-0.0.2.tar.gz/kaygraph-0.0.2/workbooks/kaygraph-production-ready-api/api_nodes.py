import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from kaygraph import ValidatedNode, MetricsNode, Node
import logging

logging.basicConfig(level=logging.INFO)


class RequestValidatorNode(ValidatedNode):
    """Validates incoming API requests with comprehensive checks"""
    
    def __init__(self):
        super().__init__(node_id="request_validator")
        self.request_schemas = {
            "process": {
                "required_fields": ["data", "processing_type"],
                "optional_fields": ["options", "callback_url"],
                "data_types": {
                    "data": (str, dict, list),
                    "processing_type": str,
                    "options": dict,
                    "callback_url": str
                }
            },
            "batch_process": {
                "required_fields": ["items", "batch_id"],
                "optional_fields": ["priority", "timeout"],
                "data_types": {
                    "items": list,
                    "batch_id": str,
                    "priority": int,
                    "timeout": int
                }
            }
        }
    
    def validate_input(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the incoming request structure"""
        if not request_data:
            raise ValueError("Empty request data")
        
        # Check for required metadata
        if "request_id" not in request_data:
            request_data["request_id"] = str(uuid.uuid4())
        
        if "timestamp" not in request_data:
            request_data["timestamp"] = datetime.now().isoformat()
        
        # Validate request type
        request_type = request_data.get("type", "process")
        if request_type not in self.request_schemas:
            raise ValueError(f"Unknown request type: {request_type}")
        
        return request_data
    
    def validate_output(self, validated_request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the processed request meets all requirements"""
        required_output_fields = ["request_id", "type", "data", "validation_passed", "correlation_id"]
        
        for field in required_output_fields:
            if field not in validated_request:
                raise ValueError(f"Missing required output field: {field}")
        
        if not validated_request.get("validation_passed", False):
            raise ValueError("Request validation failed")
        
        return validated_request
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return shared.get("request_data", {})
    
    def exec(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive request validation"""
        
        # Extract request details
        request_type = request_data.get("type", "process")
        schema = self.request_schemas[request_type]
        
        # Validate required fields
        missing_fields = []
        for field in schema["required_fields"]:
            if field not in request_data:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Validate data types
        type_errors = []
        for field, expected_type in schema["data_types"].items():
            if field in request_data:
                actual_value = request_data[field]
                if not isinstance(actual_value, expected_type):
                    type_errors.append(f"{field}: expected {expected_type}, got {type(actual_value)}")
        
        if type_errors:
            raise ValueError(f"Type validation errors: {type_errors}")
        
        # Business logic validation
        validation_errors = self._validate_business_rules(request_data, request_type)
        if validation_errors:
            raise ValueError(f"Business validation errors: {validation_errors}")
        
        # Add validation metadata
        validated_request = request_data.copy()
        validated_request.update({
            "validation_passed": True,
            "validation_timestamp": datetime.now().isoformat(),
            "correlation_id": f"req_{int(time.time())}_{request_data['request_id'][:8]}",
            "validated_fields": list(schema["required_fields"]) + list(schema["optional_fields"])
        })
        
        return validated_request
    
    def _validate_business_rules(self, request_data: Dict[str, Any], request_type: str) -> List[str]:
        """Validate business-specific rules"""
        errors = []
        
        if request_type == "process":
            # Validate processing type
            processing_type = request_data.get("processing_type", "")
            valid_types = ["text_analysis", "data_transformation", "ml_inference", "aggregation"]
            if processing_type not in valid_types:
                errors.append(f"Invalid processing_type: {processing_type}, must be one of {valid_types}")
            
            # Validate data size
            data = request_data.get("data", "")
            if isinstance(data, str) and len(data) > 10000:
                errors.append("Data size exceeds 10KB limit")
            elif isinstance(data, (list, dict)) and len(json.dumps(data)) > 10000:
                errors.append("Data size exceeds 10KB limit")
            
            # Validate callback URL if provided
            callback_url = request_data.get("callback_url")
            if callback_url and not callback_url.startswith(("http://", "https://")):
                errors.append("Invalid callback_url format")
        
        elif request_type == "batch_process":
            # Validate batch constraints
            items = request_data.get("items", [])
            if len(items) > 100:
                errors.append("Batch size exceeds 100 items limit")
            
            if len(items) == 0:
                errors.append("Batch cannot be empty")
            
            # Validate priority
            priority = request_data.get("priority", 5)
            if not (1 <= priority <= 10):
                errors.append("Priority must be between 1 and 10")
        
        return errors
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["validated_request"] = exec_res
        
        correlation_id = exec_res.get("correlation_id", "unknown")
        self.logger.info(f"Request validated successfully: {correlation_id}")
        
        return "validated"


class ProcessorNode(MetricsNode):
    """Main business logic processor with comprehensive metrics"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=3, wait=1, node_id="processor")
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_open = False
        self.last_failure_time = None
        self.processing_cache = {}
    
    def before_prep(self, shared: Dict[str, Any]):
        """Check circuit breaker and resource availability"""
        # Check circuit breaker
        if self.circuit_breaker_open:
            if self.last_failure_time and (time.time() - self.last_failure_time) > 60:
                self.circuit_breaker_open = False
                self.circuit_breaker_failures = 0
                self.logger.info("Circuit breaker reset")
            else:
                raise RuntimeError("Circuit breaker is open - service temporarily unavailable")
        
        # Log processing start
        validated_request = shared.get("validated_request", {})
        correlation_id = validated_request.get("correlation_id", "unknown")
        self.logger.info(f"Starting processing for request: {correlation_id}")
    
    def after_exec(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any):
        """Post-processing validation and caching"""
        if exec_res.get("success", False):
            # Reset circuit breaker on success
            self.circuit_breaker_failures = 0
            self.circuit_breaker_open = False
            
            # Cache successful results for similar requests
            cache_key = self._generate_cache_key(prep_res)
            if cache_key:
                self.processing_cache[cache_key] = {
                    "result": exec_res,
                    "cached_at": time.time(),
                    "ttl": 300  # 5 minutes
                }
                
                # Cleanup old cache entries
                self._cleanup_cache()
        else:
            self._handle_processing_failure()
    
    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Handle processing errors with fallback strategies"""
        self.logger.error(f"Processing failed: {error}")
        self._handle_processing_failure()
        
        # Try to provide cached or fallback response
        validated_request = shared.get("validated_request", {})
        fallback_result = self._get_fallback_response(validated_request)
        
        if fallback_result:
            shared["processing_result"] = fallback_result
            return True  # Suppress the error
        
        return False
    
    def _handle_processing_failure(self):
        """Handle processing failure for circuit breaker"""
        self.circuit_breaker_failures += 1
        self.last_failure_time = time.time()
        
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.circuit_breaker_open = True
            self.logger.warning("Circuit breaker opened due to repeated failures")
    
    def _generate_cache_key(self, request_data: Dict[str, Any]) -> Optional[str]:
        """Generate cache key for request"""
        try:
            processing_type = request_data.get("processing_type", "")
            data_str = str(request_data.get("data", ""))[:100]  # First 100 chars
            return f"{processing_type}:{hash(data_str)}"
        except:
            return None
    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.processing_cache.items():
            if current_time - entry["cached_at"] > entry["ttl"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.processing_cache[key]
    
    def _get_fallback_response(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get fallback response for failed processing"""
        processing_type = request_data.get("processing_type", "")
        
        # Check cache first
        cache_key = self._generate_cache_key(request_data)
        if cache_key and cache_key in self.processing_cache:
            cached_entry = self.processing_cache[cache_key]
            if time.time() - cached_entry["cached_at"] < cached_entry["ttl"]:
                result = cached_entry["result"].copy()
                result["source"] = "cache_fallback"
                return result
        
        # Provide default fallback based on processing type
        if processing_type == "text_analysis":
            return {
                "result": {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "keywords": [],
                    "summary": "Analysis unavailable - using fallback"
                },
                "success": True,
                "source": "fallback",
                "processing_time": 0.001
            }
        elif processing_type == "data_transformation":
            return {
                "result": {
                    "transformed_data": request_data.get("data", {}),
                    "transformation_applied": "identity",
                    "note": "Transformation unavailable - returning original data"
                },
                "success": True,
                "source": "fallback",
                "processing_time": 0.001
            }
        
        return None
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return shared.get("validated_request", {})
    
    def exec(self, validated_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute main business logic processing"""
        start_time = time.time()
        
        processing_type = validated_request.get("processing_type", "")
        data = validated_request.get("data", {})
        options = validated_request.get("options", {})
        
        # Simulate processing failures for testing
        if self.params.get("simulate_failure", False):
            if time.time() % 10 < 2:  # 20% failure rate
                raise RuntimeError("Simulated processing failure")
        
        # Route to appropriate processing method
        try:
            if processing_type == "text_analysis":
                result = self._process_text_analysis(data, options)
            elif processing_type == "data_transformation":
                result = self._process_data_transformation(data, options)
            elif processing_type == "ml_inference":
                result = self._process_ml_inference(data, options)
            elif processing_type == "aggregation":
                result = self._process_aggregation(data, options)
            else:
                raise ValueError(f"Unsupported processing type: {processing_type}")
            
            processing_time = time.time() - start_time
            
            return {
                "result": result,
                "success": True,
                "processing_type": processing_type,
                "processing_time": processing_time,
                "correlation_id": validated_request.get("correlation_id", "unknown"),
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "result": {},
                "success": False,
                "error": str(e),
                "processing_type": processing_type,
                "processing_time": processing_time,
                "correlation_id": validated_request.get("correlation_id", "unknown")
            }
    
    def _process_text_analysis(self, data: Any, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process text analysis requests"""
        text = str(data)
        
        # Simulate processing time
        time.sleep(0.1 + len(text) * 0.0001)
        
        # Simple sentiment analysis simulation
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        # Extract keywords (simple word frequency)
        words = text_lower.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only words longer than 3 chars
                word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "keywords": [word for word, freq in keywords],
            "word_count": len(words),
            "character_count": len(text)
        }
    
    def _process_data_transformation(self, data: Any, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process data transformation requests"""
        transformation_type = options.get("transformation", "normalize")
        
        time.sleep(0.05)  # Simulate processing
        
        if isinstance(data, dict):
            if transformation_type == "normalize":
                # Normalize string values to lowercase
                transformed = {}
                for key, value in data.items():
                    if isinstance(value, str):
                        transformed[key] = value.lower().strip()
                    else:
                        transformed[key] = value
            elif transformation_type == "aggregate":
                # Aggregate numeric values
                numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
                transformed = {
                    "sum": sum(numeric_values),
                    "avg": sum(numeric_values) / len(numeric_values) if numeric_values else 0,
                    "count": len(numeric_values),
                    "original_keys": list(data.keys())
                }
            else:
                transformed = data
        elif isinstance(data, list):
            if transformation_type == "normalize":
                transformed = [item.lower() if isinstance(item, str) else item for item in data]
            elif transformation_type == "aggregate":
                numeric_items = [item for item in data if isinstance(item, (int, float))]
                transformed = {
                    "sum": sum(numeric_items),
                    "avg": sum(numeric_items) / len(numeric_items) if numeric_items else 0,
                    "count": len(numeric_items),
                    "total_items": len(data)
                }
            else:
                transformed = data
        else:
            transformed = data
        
        return {
            "transformed_data": transformed,
            "transformation_applied": transformation_type,
            "original_type": type(data).__name__,
            "transformed_type": type(transformed).__name__
        }
    
    def _process_ml_inference(self, data: Any, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process ML inference requests"""
        model_type = options.get("model", "classification")
        
        time.sleep(0.2)  # Simulate model inference time
        
        if model_type == "classification":
            # Simulate classification
            classes = ["category_a", "category_b", "category_c"]
            predicted_class = classes[hash(str(data)) % len(classes)]
            confidence = 0.7 + (hash(str(data)) % 30) / 100
            
            return {
                "predicted_class": predicted_class,
                "confidence": round(confidence, 3),
                "model_type": model_type,
                "classes": classes
            }
        elif model_type == "regression":
            # Simulate regression
            predicted_value = (hash(str(data)) % 1000) / 10.0
            
            return {
                "predicted_value": round(predicted_value, 2),
                "model_type": model_type,
                "confidence_interval": [predicted_value - 5, predicted_value + 5]
            }
        else:
            return {
                "error": f"Unsupported model type: {model_type}",
                "supported_models": ["classification", "regression"]
            }
    
    def _process_aggregation(self, data: Any, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process data aggregation requests"""
        operation = options.get("operation", "sum")
        
        time.sleep(0.03)
        
        if isinstance(data, list):
            numeric_data = [item for item in data if isinstance(item, (int, float))]
            
            if operation == "sum":
                result = sum(numeric_data)
            elif operation == "avg":
                result = sum(numeric_data) / len(numeric_data) if numeric_data else 0
            elif operation == "min":
                result = min(numeric_data) if numeric_data else None
            elif operation == "max":
                result = max(numeric_data) if numeric_data else None
            elif operation == "count":
                result = len(numeric_data)
            else:
                result = None
            
            return {
                "operation": operation,
                "result": result,
                "input_count": len(data),
                "numeric_count": len(numeric_data)
            }
        else:
            return {
                "error": "Aggregation requires list input",
                "input_type": type(data).__name__
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["processing_result"] = exec_res
        
        success = exec_res.get("success", False)
        correlation_id = exec_res.get("correlation_id", "unknown")
        processing_time = exec_res.get("processing_time", 0)
        
        if success:
            self.logger.info(f"Processing completed successfully: {correlation_id} in {processing_time:.3f}s")
            return "processed"
        else:
            self.logger.warning(f"Processing failed: {correlation_id}")
            return "process_failed"


class ResponseBuilderNode(ValidatedNode):
    """Builds API responses with validation and formatting"""
    
    def __init__(self):
        super().__init__(node_id="response_builder")
    
    def validate_input(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processing result"""
        if not processing_result:
            raise ValueError("No processing result provided")
        
        required_fields = ["correlation_id", "success", "processing_time"]
        for field in required_fields:
            if field not in processing_result:
                raise ValueError(f"Missing required field in processing result: {field}")
        
        return processing_result
    
    def validate_output(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate final API response"""
        required_response_fields = ["request_id", "status", "data", "metadata"]
        
        for field in required_response_fields:
            if field not in api_response:
                raise ValueError(f"Missing required response field: {field}")
        
        # Validate status is valid
        valid_statuses = ["success", "error", "partial"]
        if api_response.get("status") not in valid_statuses:
            raise ValueError(f"Invalid status: {api_response.get('status')}")
        
        return api_response
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "validated_request": shared.get("validated_request", {}),
            "processing_result": shared.get("processing_result", {})
        }
    
    def exec(self, response_input: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive API response"""
        validated_request = response_input.get("validated_request", {})
        processing_result = response_input.get("processing_result", {})
        
        # Extract key information
        request_id = validated_request.get("request_id", "unknown")
        correlation_id = processing_result.get("correlation_id", "unknown")
        success = processing_result.get("success", False)
        processing_time = processing_result.get("processing_time", 0)
        
        # Build response data
        if success:
            status = "success"
            data = processing_result.get("result", {})
            error = None
        else:
            status = "error"
            data = {}
            error = {
                "type": "processing_error",
                "message": processing_result.get("error", "Unknown error"),
                "code": "PROC_001"
            }
        
        # Build comprehensive metadata
        metadata = {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "processing_time_ms": round(processing_time * 1000, 2),
            "processed_at": datetime.now().isoformat(),
            "processing_type": processing_result.get("processing_type", "unknown"),
            "api_version": "1.0",
            "source": processing_result.get("source", "primary")
        }
        
        # Add performance metadata
        if processing_time > 0:
            if processing_time < 0.1:
                performance_rating = "excellent"
            elif processing_time < 0.5:
                performance_rating = "good"
            elif processing_time < 2.0:
                performance_rating = "acceptable"
            else:
                performance_rating = "slow"
            
            metadata["performance_rating"] = performance_rating
        
        # Build final response
        api_response = {
            "request_id": request_id,
            "status": status,
            "data": data,
            "metadata": metadata
        }
        
        if error:
            api_response["error"] = error
        
        return api_response
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["api_response"] = exec_res
        
        status = exec_res.get("status", "unknown")
        request_id = exec_res.get("request_id", "unknown")
        
        self.logger.info(f"API response built: {request_id} with status {status}")
        
        return None  # End of processing workflow