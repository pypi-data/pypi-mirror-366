import random
import time
from typing import Any, Dict, List
from monitoring_nodes import MonitoringNode, MonitoringMetricsNode
import logging

logging.basicConfig(level=logging.INFO)


class DataSourceNode(MonitoringNode):
    """Generates synthetic data for processing"""
    
    def __init__(self):
        super().__init__(node_id="data_source", max_retries=2, wait=0.5)
    
    def prep(self, shared: Dict[str, Any]) -> int:
        # Get batch size from params
        return self.params.get("batch_size", 10)
    
    def exec(self, batch_size: int) -> List[Dict[str, Any]]:
        # Simulate data fetching with variable latency
        fetch_time = random.uniform(0.1, 0.3)
        time.sleep(fetch_time)
        
        # Generate synthetic data
        data = []
        for i in range(batch_size):
            record = {
                "id": f"record_{i}_{int(time.time() * 1000)}",
                "value": random.randint(1, 100),
                "category": random.choice(["A", "B", "C", "D"]),
                "priority": random.randint(1, 5),
                "timestamp": time.time()
            }
            data.append(record)
        
        self.logger.info(f"Generated {len(data)} records")
        return data
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["raw_data"] = exec_res
        shared["data_count"] = len(exec_res)
        return "validate"


class DataValidationNode(MonitoringNode):
    """Validates data with configurable rules"""
    
    def __init__(self):
        super().__init__(node_id="data_validator", max_retries=3, wait=0.2)
        self.validation_rules = {
            "min_value": 10,
            "max_value": 90,
            "valid_categories": ["A", "B", "C"],
            "max_priority": 4
        }
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("raw_data", [])
    
    def exec(self, data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        valid_records = []
        invalid_records = []
        
        for record in data:
            # Simulate validation processing
            time.sleep(0.01)
            
            # Apply validation rules
            is_valid = True
            reasons = []
            
            if record["value"] < self.validation_rules["min_value"]:
                is_valid = False
                reasons.append(f"Value {record['value']} below minimum")
            
            if record["value"] > self.validation_rules["max_value"]:
                is_valid = False
                reasons.append(f"Value {record['value']} above maximum")
            
            if record["category"] not in self.validation_rules["valid_categories"]:
                is_valid = False
                reasons.append(f"Invalid category: {record['category']}")
            
            if record["priority"] > self.validation_rules["max_priority"]:
                is_valid = False
                reasons.append(f"Priority {record['priority']} too high")
            
            if is_valid:
                valid_records.append(record)
            else:
                record["validation_errors"] = reasons
                invalid_records.append(record)
        
        # Simulate occasional validation service errors
        if random.random() < 0.05:  # 5% error rate
            raise ValueError("Validation service temporarily unavailable")
        
        return {
            "valid": valid_records,
            "invalid": invalid_records
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["valid_data"] = exec_res["valid"]
        shared["invalid_data"] = exec_res["invalid"]
        shared["validation_stats"] = {
            "total": len(prep_res),
            "valid": len(exec_res["valid"]),
            "invalid": len(exec_res["invalid"]),
            "validation_rate": len(exec_res["valid"]) / len(prep_res) if prep_res else 0
        }
        
        self.logger.info(f"Validation complete: {len(exec_res['valid'])} valid, {len(exec_res['invalid'])} invalid")
        
        # Route based on validation results
        if len(exec_res["valid"]) > 0:
            return "process"
        else:
            return "no_valid_data"


class DataProcessingNode(MonitoringMetricsNode):
    """Heavy processing with metrics collection"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=2, wait=1.0, node_id="data_processor")
        self.processing_cache = {}
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("valid_data", [])
    
    def exec(self, valid_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed_records = []
        
        for record in valid_data:
            # Check cache
            cache_key = f"{record['category']}_{record['value']}"
            if cache_key in self.processing_cache:
                result = self.processing_cache[cache_key].copy()
                result["id"] = record["id"]
                result["from_cache"] = True
                processed_records.append(result)
                continue
            
            # Simulate CPU-intensive processing
            processing_time = random.uniform(0.05, 0.2)
            time.sleep(processing_time)
            
            # Simulate processing that might fail
            if random.random() < 0.08:  # 8% failure rate
                raise RuntimeError(f"Processing failed for record {record['id']}")
            
            # Process the record
            processed = {
                "id": record["id"],
                "original_value": record["value"],
                "processed_value": record["value"] * 2 + random.randint(-5, 5),
                "category": record["category"],
                "priority": record["priority"],
                "processing_time": processing_time,
                "score": random.uniform(0.0, 1.0),
                "from_cache": False
            }
            
            # Cache the result
            self.processing_cache[cache_key] = processed.copy()
            processed_records.append(processed)
        
        return processed_records
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["processed_data"] = exec_res
        shared["processing_stats"] = self.get_stats()
        
        # Log cache stats
        cache_hits = sum(1 for r in exec_res if r.get("from_cache", False))
        self.logger.info(f"Processed {len(exec_res)} records, {cache_hits} from cache")
        
        return "aggregate"


class DataAggregationNode(MonitoringNode):
    """Aggregates processed data by category"""
    
    def __init__(self):
        super().__init__(node_id="data_aggregator", max_retries=1, wait=0.5)
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("processed_data", [])
    
    def exec(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Aggregate by category
        aggregates = {}
        
        for record in processed_data:
            category = record["category"]
            if category not in aggregates:
                aggregates[category] = {
                    "count": 0,
                    "sum_value": 0,
                    "sum_processed": 0,
                    "max_value": float('-inf'),
                    "min_value": float('inf'),
                    "avg_score": 0,
                    "total_processing_time": 0
                }
            
            agg = aggregates[category]
            agg["count"] += 1
            agg["sum_value"] += record["original_value"]
            agg["sum_processed"] += record["processed_value"]
            agg["max_value"] = max(agg["max_value"], record["original_value"])
            agg["min_value"] = min(agg["min_value"], record["original_value"])
            agg["avg_score"] += record["score"]
            agg["total_processing_time"] += record["processing_time"]
        
        # Calculate averages
        for category, agg in aggregates.items():
            if agg["count"] > 0:
                agg["avg_value"] = agg["sum_value"] / agg["count"]
                agg["avg_processed"] = agg["sum_processed"] / agg["count"]
                agg["avg_score"] = agg["avg_score"] / agg["count"]
                agg["avg_processing_time"] = agg["total_processing_time"] / agg["count"]
        
        return {
            "aggregates": aggregates,
            "total_records": len(processed_data),
            "categories": list(aggregates.keys())
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["aggregation_results"] = exec_res
        
        # Log summary
        self.logger.info(f"Aggregated {exec_res['total_records']} records into {len(exec_res['categories'])} categories")
        
        return "store"


class DataStorageNode(MonitoringNode):
    """Simulates storing results with external service calls"""
    
    def __init__(self):
        super().__init__(node_id="data_storage", max_retries=5, wait=2.0)
        self.storage_attempts = 0
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "aggregates": shared.get("aggregation_results", {}),
            "processed_data": shared.get("processed_data", []),
            "validation_stats": shared.get("validation_stats", {}),
            "processing_stats": shared.get("processing_stats", {})
        }
    
    def exec(self, storage_data: Dict[str, Any]) -> Dict[str, Any]:
        self.storage_attempts += 1
        
        # Simulate external storage API call
        api_latency = random.uniform(0.2, 0.8)
        time.sleep(api_latency)
        
        # Simulate storage failures (higher rate for first attempts)
        failure_rate = 0.3 if self.storage_attempts == 1 else 0.1
        if random.random() < failure_rate:
            raise ConnectionError("Storage service temporarily unavailable")
        
        # Simulate successful storage
        storage_result = {
            "storage_id": f"storage_{int(time.time() * 1000)}",
            "records_stored": storage_data["aggregates"].get("total_records", 0),
            "categories_stored": len(storage_data["aggregates"].get("categories", [])),
            "storage_latency": api_latency,
            "storage_timestamp": time.time()
        }
        
        return storage_result
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["storage_result"] = exec_res
        
        self.logger.info(f"Storage complete: {exec_res['records_stored']} records stored with ID {exec_res['storage_id']}")
        
        return None  # End of workflow


class ErrorHandlerNode(MonitoringNode):
    """Handles workflow errors and provides fallback"""
    
    def __init__(self):
        super().__init__(node_id="error_handler", max_retries=1, wait=0.1)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "error_context": shared.get("error_context", {}),
            "partial_results": {
                "valid_data": shared.get("valid_data", []),
                "invalid_data": shared.get("invalid_data", []),
                "processed_data": shared.get("processed_data", [])
            }
        }
    
    def exec(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        # Log error context
        self.logger.error(f"Handling workflow error: {error_data.get('error_context', {})}")
        
        # Provide fallback result
        return {
            "status": "error_handled",
            "partial_results_available": any(error_data["partial_results"].values()),
            "recovery_action": "stored_partial_results",
            "timestamp": time.time()
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["error_handling_result"] = exec_res
        return None  # End error path