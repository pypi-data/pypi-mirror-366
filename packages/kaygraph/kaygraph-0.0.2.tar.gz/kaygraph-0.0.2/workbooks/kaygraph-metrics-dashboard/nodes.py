import random
import time
import json
from typing import Any, Dict, List
from kaygraph import MetricsNode, Node
import logging

logging.basicConfig(level=logging.INFO)

class DataIngestionNode(MetricsNode):
    """Simulates data ingestion with variable performance"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=3, wait=0.5, node_id="ingestion")
        
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        batch_size = self.params.get("batch_size", 10)
        # Generate synthetic data batch
        return [
            {
                "id": f"record_{i}_{int(time.time())}",
                "value": random.randint(1, 100),
                "timestamp": time.time()
            }
            for i in range(batch_size)
        ]
    
    def exec(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Simulate variable ingestion time
        processing_time = random.uniform(0.1, 0.5)
        time.sleep(processing_time)
        
        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Simulated ingestion failure")
        
        return data_batch
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["ingested_data"] = exec_res
        shared["ingestion_metrics"] = self.get_stats()
        return "validated"


class DataValidationNode(MetricsNode):
    """Validates data with detailed metrics tracking"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=2, wait=0.2, node_id="validation")
        
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("ingested_data", [])
    
    def exec(self, data_batch: List[Dict[str, Any]]) -> tuple:
        valid_records = []
        invalid_records = []
        
        for record in data_batch:
            # Simulate validation logic
            time.sleep(0.01)  # Validation overhead
            
            if record["value"] > 10:  # Simple validation rule
                valid_records.append(record)
            else:
                invalid_records.append(record)
        
        # Simulate occasional validation errors
        if random.random() < 0.05:  # 5% error rate
            raise ValueError("Validation service temporarily unavailable")
        
        return valid_records, invalid_records
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        valid_records, invalid_records = exec_res
        shared["valid_data"] = valid_records
        shared["invalid_data"] = invalid_records
        shared["validation_metrics"] = self.get_stats()
        
        # Log validation results
        self.logger.info(f"Validated {len(valid_records)} records, rejected {len(invalid_records)}")
        
        return "processed"


class DataProcessingNode(MetricsNode):
    """Heavy processing with performance tracking"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=3, wait=1.0, node_id="processing")
        
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("valid_data", [])
    
    def exec(self, valid_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed_data = []
        
        for record in valid_data:
            # Simulate CPU-intensive processing
            processing_time = random.uniform(0.05, 0.2)
            time.sleep(processing_time)
            
            # Simulate processing that might fail
            if random.random() < 0.08:  # 8% failure rate
                raise RuntimeError(f"Processing failed for record {record['id']}")
            
            # Transform the data
            processed_record = {
                **record,
                "processed_value": record["value"] * 2,
                "processing_time": processing_time
            }
            processed_data.append(processed_record)
        
        return processed_data
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["processed_data"] = exec_res
        shared["processing_metrics"] = self.get_stats()
        return "enriched"


class DataEnrichmentNode(MetricsNode):
    """Enriches data with external service calls"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=5, wait=2.0, node_id="enrichment")
        
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("processed_data", [])
    
    def exec(self, processed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enriched_data = []
        
        for record in processed_data:
            # Simulate external API call
            api_latency = random.uniform(0.1, 0.5)
            time.sleep(api_latency)
            
            # Simulate API failures
            if random.random() < 0.15:  # 15% failure rate (higher for external services)
                raise ConnectionError("External enrichment service unavailable")
            
            # Enrich the record
            enriched_record = {
                **record,
                "enrichment": {
                    "category": random.choice(["A", "B", "C"]),
                    "score": random.uniform(0.0, 1.0),
                    "api_latency": api_latency
                }
            }
            enriched_data.append(enriched_record)
        
        return enriched_data
    
    def exec_fallback(self, prep_res: List[Dict[str, Any]], exc: Exception) -> List[Dict[str, Any]]:
        # Graceful degradation - return data without enrichment
        self.logger.warning(f"Enrichment failed, returning unenriched data: {exc}")
        return [{**record, "enrichment": None} for record in prep_res]
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["enriched_data"] = exec_res
        shared["enrichment_metrics"] = self.get_stats()
        return "stored"


class DataStorageNode(MetricsNode):
    """Simulates data storage operations"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=3, wait=0.5, node_id="storage")
        
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("enriched_data", [])
    
    def exec(self, enriched_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Simulate batch storage operation
        storage_time = random.uniform(0.2, 0.8)
        time.sleep(storage_time)
        
        # Simulate storage failures
        if random.random() < 0.05:  # 5% failure rate
            raise IOError("Storage system temporarily unavailable")
        
        return {
            "records_stored": len(enriched_data),
            "storage_time": storage_time,
            "timestamp": time.time()
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["storage_result"] = exec_res
        shared["storage_metrics"] = self.get_stats()
        
        # Collect all metrics for dashboard
        self._collect_graph_metrics(shared)
        
        return None  # End of graph
    
    def _collect_graph_metrics(self, shared: Dict[str, Any]):
        """Aggregate metrics from all nodes"""
        all_metrics = {
            "ingestion": shared.get("ingestion_metrics", {}),
            "validation": shared.get("validation_metrics", {}),
            "processing": shared.get("processing_metrics", {}),
            "enrichment": shared.get("enrichment_metrics", {}),
            "storage": shared.get("storage_metrics", {})
        }
        
        # Store in metrics history
        if "metrics_history" not in shared:
            shared["metrics_history"] = []
        
        shared["metrics_history"].append({
            "timestamp": time.time(),
            "metrics": all_metrics
        })
        
        # Keep only last 100 entries
        shared["metrics_history"] = shared["metrics_history"][-100:]


class MetricsAggregatorNode(Node):
    """Aggregates and formats metrics for dashboard display"""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return shared.get("metrics_history", [])
    
    def exec(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not metrics_history:
            return {}
        
        # Get latest metrics
        latest = metrics_history[-1]["metrics"]
        
        # Calculate aggregate statistics
        aggregated = {
            "timestamp": time.time(),
            "nodes": {}
        }
        
        for node_id, metrics in latest.items():
            if metrics and "total_executions" in metrics:
                aggregated["nodes"][node_id] = {
                    "total_executions": metrics["total_executions"],
                    "success_rate": metrics["success_rate"],
                    "avg_execution_time": round(metrics["avg_execution_time"], 3),
                    "min_execution_time": round(metrics["min_execution_time"], 3),
                    "max_execution_time": round(metrics["max_execution_time"], 3),
                    "total_retries": metrics["total_retries"]
                }
        
        # Calculate graph-wide metrics
        total_nodes = len(aggregated["nodes"])
        if total_nodes > 0:
            aggregated["graph_metrics"] = {
                "avg_success_rate": sum(n["success_rate"] for n in aggregated["nodes"].values()) / total_nodes,
                "total_executions": sum(n["total_executions"] for n in aggregated["nodes"].values()),
                "total_retries": sum(n["total_retries"] for n in aggregated["nodes"].values())
            }
        
        return aggregated
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["dashboard_metrics"] = exec_res
        return None