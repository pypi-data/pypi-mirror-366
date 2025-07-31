import json
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from kaygraph import ValidatedNode, Node
import logging

logging.basicConfig(level=logging.INFO)


class DataLoaderNode(ValidatedNode):
    """Loads data with strict schema validation"""
    
    def __init__(self):
        super().__init__(max_retries=1, node_id="data_loader")
        self.required_fields = {"id", "timestamp", "value", "category", "metadata"}
        self.valid_categories = {"A", "B", "C", "D"}
    
    def validate_input(self, prep_res: Optional[str]) -> str:
        """Validate input file path"""
        if not prep_res:
            raise ValueError("No input file path provided")
        if not prep_res.endswith(('.json', '.csv')):
            raise ValueError(f"Unsupported file format: {prep_res}")
        return prep_res
    
    def validate_output(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate loaded records against schema"""
        if not records:
            raise ValueError("No records loaded")
        
        validation_errors = []
        valid_records = []
        
        for i, record in enumerate(records):
            try:
                # Check required fields
                missing_fields = self.required_fields - set(record.keys())
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                # Validate types
                if not isinstance(record["id"], str):
                    raise TypeError("'id' must be string")
                if not isinstance(record["value"], (int, float)):
                    raise TypeError("'value' must be numeric")
                if record["category"] not in self.valid_categories:
                    raise ValueError(f"Invalid category: {record['category']}")
                
                # Validate timestamp
                try:
                    datetime.fromisoformat(record["timestamp"])
                except:
                    raise ValueError(f"Invalid timestamp format: {record['timestamp']}")
                
                valid_records.append(record)
                
            except Exception as e:
                validation_errors.append({
                    "record_index": i,
                    "record_id": record.get("id", "unknown"),
                    "error": str(e)
                })
        
        # Log validation results
        self.logger.info(f"Schema validation: {len(valid_records)} valid, {len(validation_errors)} invalid")
        
        if validation_errors:
            self.logger.warning(f"Schema validation errors: {validation_errors[:5]}")  # Show first 5
        
        if not valid_records:
            raise ValueError("All records failed schema validation")
        
        return valid_records
    
    def prep(self, shared: Dict[str, Any]) -> Optional[str]:
        return self.params.get("input_file", "data.json")
    
    def exec(self, file_path: str) -> List[Dict[str, Any]]:
        """Simulate loading data from file"""
        # Generate synthetic data for demo
        records = []
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(100):
            # Sometimes generate invalid records to test validation
            if self.params.get("include_invalid", False) and random.random() < 0.1:
                # Invalid record
                record = {
                    "id": f"record_{i}",
                    "value": random.choice([-10, "invalid", None, 2000]),  # Invalid values
                    "category": random.choice(["A", "B", "C", "X"]),  # X is invalid
                    # Missing timestamp and metadata
                }
            else:
                # Valid record
                record = {
                    "id": f"record_{i}",
                    "timestamp": (base_time + timedelta(minutes=i*5)).isoformat(),
                    "value": random.uniform(0, 1000),
                    "category": random.choice(list(self.valid_categories)),
                    "metadata": {
                        "source": "sensor_" + str(random.randint(1, 5)),
                        "quality": random.uniform(0.5, 1.0)
                    }
                }
            records.append(record)
        
        return records
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["raw_records"] = exec_res
        shared["load_stats"] = {
            "total_loaded": len(exec_res),
            "timestamp": datetime.now().isoformat()
        }
        return "cleaned"


class DataCleanerNode(ValidatedNode):
    """Cleans data with quality validation"""
    
    def __init__(self):
        super().__init__(max_retries=2, wait=0.5, node_id="data_cleaner")
        self.quality_thresholds = {
            "min_quality_score": 0.6,
            "max_null_ratio": 0.1,
            "max_duplicate_ratio": 0.05
        }
    
    def validate_input(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate input records exist and have minimum quality"""
        if not records:
            raise ValueError("No records to clean")
        
        # Check for catastrophic data issues
        null_count = sum(1 for r in records if r.get("value") is None)
        null_ratio = null_count / len(records)
        
        if null_ratio > self.quality_thresholds["max_null_ratio"]:
            raise ValueError(f"Too many null values: {null_ratio:.2%} exceeds threshold")
        
        return records
    
    def validate_output(self, cleaned_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate cleaned data quality"""
        if not cleaned_records:
            raise ValueError("No records after cleaning")
        
        # Check duplicate ratio
        unique_ids = set(r["id"] for r in cleaned_records)
        duplicate_ratio = 1 - (len(unique_ids) / len(cleaned_records))
        
        if duplicate_ratio > self.quality_thresholds["max_duplicate_ratio"]:
            raise ValueError(f"Too many duplicates: {duplicate_ratio:.2%}")
        
        # Check quality scores
        low_quality_count = sum(1 for r in cleaned_records 
                               if r.get("metadata", {}).get("quality", 0) < self.quality_thresholds["min_quality_score"])
        
        if low_quality_count > len(cleaned_records) * 0.2:
            self.logger.warning(f"High number of low quality records: {low_quality_count}")
        
        return cleaned_records
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("raw_records", [])
    
    def exec(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and deduplicate records"""
        cleaned = []
        seen_ids = set()
        
        for record in records:
            # Skip duplicates
            if record["id"] in seen_ids:
                continue
            seen_ids.add(record["id"])
            
            # Clean the record
            cleaned_record = record.copy()
            
            # Normalize values
            if cleaned_record["value"] < 0:
                cleaned_record["value"] = 0
            elif cleaned_record["value"] > 1000:
                cleaned_record["value"] = 1000
            
            # Add cleaning metadata
            cleaned_record["cleaned_at"] = datetime.now().isoformat()
            cleaned_record["cleaning_actions"] = []
            
            if record["value"] != cleaned_record["value"]:
                cleaned_record["cleaning_actions"].append("normalized_value")
            
            cleaned.append(cleaned_record)
        
        return cleaned
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["cleaned_records"] = exec_res
        shared["cleaning_stats"] = {
            "input_count": len(prep_res),
            "output_count": len(exec_res),
            "removed_count": len(prep_res) - len(exec_res)
        }
        return "transformed"


class DataTransformerNode(ValidatedNode):
    """Transforms data with business rule validation"""
    
    def __init__(self):
        super().__init__(node_id="data_transformer")
        self.business_rules = {
            "category_value_limits": {
                "A": (0, 250),
                "B": (200, 500),
                "C": (450, 750),
                "D": (700, 1000)
            },
            "required_transformations": ["normalized_value", "risk_score", "trend"]
        }
    
    def validate_input(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate records are ready for transformation"""
        for record in records[:10]:  # Check first 10
            if "cleaned_at" not in record:
                raise ValueError("Records must be cleaned before transformation")
        return records
    
    def validate_output(self, transformed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate business rules are satisfied"""
        violations = []
        
        for record in transformed:
            # Check required transformations
            missing_fields = set(self.business_rules["required_transformations"]) - set(record.keys())
            if missing_fields:
                violations.append(f"Record {record['id']} missing transformations: {missing_fields}")
            
            # Check category-value constraints
            category = record["category"]
            value = record["value"]
            min_val, max_val = self.business_rules["category_value_limits"][category]
            
            if not (min_val <= value <= max_val):
                violations.append(
                    f"Record {record['id']}: value {value} violates category {category} "
                    f"limits [{min_val}, {max_val}]"
                )
            
            # Check risk score validity
            if "risk_score" in record:
                if not (0 <= record["risk_score"] <= 1):
                    violations.append(f"Record {record['id']}: invalid risk score {record['risk_score']}")
        
        if violations:
            # Log first few violations
            for violation in violations[:5]:
                self.logger.warning(f"Business rule violation: {violation}")
            
            if len(violations) > len(transformed) * 0.1:  # More than 10% violations
                raise ValueError(f"Too many business rule violations: {len(violations)}")
        
        return transformed
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("cleaned_records", [])
    
    def exec(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply business transformations"""
        transformed = []
        
        for i, record in enumerate(records):
            t_record = record.copy()
            
            # Normalize value to 0-1 range
            t_record["normalized_value"] = record["value"] / 1000.0
            
            # Calculate risk score based on category and value
            category = record["category"]
            value = record["value"]
            min_val, max_val = self.business_rules["category_value_limits"][category]
            
            # Risk increases as value approaches limits
            if value < min_val or value > max_val:
                risk = 1.0
            else:
                range_size = max_val - min_val
                distance_from_center = abs(value - (min_val + range_size/2))
                risk = (distance_from_center / (range_size/2)) * 0.8
            
            t_record["risk_score"] = round(risk, 3)
            
            # Calculate trend (simplified)
            if i > 0:
                prev_value = records[i-1]["value"]
                trend = "increasing" if value > prev_value else "decreasing"
            else:
                trend = "stable"
            t_record["trend"] = trend
            
            transformed.append(t_record)
        
        return transformed
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["transformed_records"] = exec_res
        shared["transformation_stats"] = {
            "total_transformed": len(exec_res),
            "high_risk_count": sum(1 for r in exec_res if r["risk_score"] > 0.7)
        }
        return "aggregated"


class DataAggregatorNode(ValidatedNode):
    """Aggregates data with statistical validation"""
    
    def __init__(self):
        super().__init__(node_id="data_aggregator")
        self.statistical_rules = {
            "min_sample_size": 10,
            "max_std_dev_ratio": 0.5,  # std dev should be < 50% of mean
            "required_aggregations": ["count", "mean", "std_dev", "min", "max"]
        }
    
    def validate_input(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate sufficient data for aggregation"""
        if len(records) < self.statistical_rules["min_sample_size"]:
            raise ValueError(f"Insufficient data: {len(records)} < {self.statistical_rules['min_sample_size']}")
        return records
    
    def validate_output(self, aggregations: Dict[str, Any]) -> Dict[str, Any]:
        """Validate statistical properties of aggregations"""
        # Check required aggregations exist
        missing = set(self.statistical_rules["required_aggregations"]) - set(aggregations.get("overall", {}).keys())
        if missing:
            raise ValueError(f"Missing required aggregations: {missing}")
        
        # Validate statistical sanity
        overall = aggregations["overall"]
        if overall["std_dev"] > overall["mean"] * self.statistical_rules["max_std_dev_ratio"]:
            self.logger.warning(f"High variance detected: std_dev={overall['std_dev']}, mean={overall['mean']}")
        
        # Check category balance
        by_category = aggregations.get("by_category", {})
        if by_category:
            counts = [cat["count"] for cat in by_category.values()]
            min_count, max_count = min(counts), max(counts)
            if max_count > min_count * 10:
                self.logger.warning("Highly imbalanced categories detected")
        
        return aggregations
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        return shared.get("transformed_records", [])
    
    def exec(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregations with multiple dimensions"""
        import statistics
        
        values = [r["value"] for r in records]
        
        # Overall statistics
        overall = {
            "count": len(records),
            "mean": round(statistics.mean(values), 2),
            "std_dev": round(statistics.stdev(values) if len(values) > 1 else 0, 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "median": round(statistics.median(values), 2)
        }
        
        # By category
        by_category = {}
        for category in ["A", "B", "C", "D"]:
            cat_records = [r for r in records if r["category"] == category]
            if cat_records:
                cat_values = [r["value"] for r in cat_records]
                by_category[category] = {
                    "count": len(cat_records),
                    "mean": round(statistics.mean(cat_values), 2),
                    "risk_mean": round(statistics.mean([r["risk_score"] for r in cat_records]), 3)
                }
        
        # Time-based aggregations
        by_hour = {}
        for record in records:
            hour = datetime.fromisoformat(record["timestamp"]).hour
            if hour not in by_hour:
                by_hour[hour] = []
            by_hour[hour].append(record["value"])
        
        hourly_stats = {}
        for hour, hour_values in by_hour.items():
            hourly_stats[hour] = {
                "count": len(hour_values),
                "mean": round(statistics.mean(hour_values), 2)
            }
        
        return {
            "overall": overall,
            "by_category": by_category,
            "by_hour": hourly_stats,
            "generated_at": datetime.now().isoformat()
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["aggregations"] = exec_res
        return "exported"


class DataExporterNode(ValidatedNode):
    """Exports data with output contract validation"""
    
    def __init__(self):
        super().__init__(node_id="data_exporter")
        self.output_contract = {
            "required_sections": ["summary", "details", "metadata"],
            "max_file_size_mb": 10,
            "supported_formats": ["json", "csv", "parquet"]
        }
    
    def validate_input(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data is ready for export"""
        if not export_data:
            raise ValueError("No data to export")
        return export_data
    
    def validate_output(self, export_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate export meets output contract"""
        # Check required sections
        missing_sections = set(self.output_contract["required_sections"]) - set(export_result.keys())
        if missing_sections:
            raise ValueError(f"Missing required export sections: {missing_sections}")
        
        # Check file size (simulated)
        estimated_size_mb = len(json.dumps(export_result)) / (1024 * 1024)
        if estimated_size_mb > self.output_contract["max_file_size_mb"]:
            raise ValueError(f"Export too large: {estimated_size_mb:.2f}MB > {self.output_contract['max_file_size_mb']}MB")
        
        # Validate metadata
        metadata = export_result.get("metadata", {})
        if "export_timestamp" not in metadata:
            raise ValueError("Export metadata missing timestamp")
        
        return export_result
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "aggregations": shared.get("aggregations", {}),
            "records": shared.get("transformed_records", [])[:10],  # Sample for export
            "stats": {
                "load": shared.get("load_stats", {}),
                "cleaning": shared.get("cleaning_stats", {}),
                "transformation": shared.get("transformation_stats", {})
            }
        }
    
    def exec(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for export"""
        return {
            "summary": {
                "total_records": export_data["stats"].get("load", {}).get("total_loaded", 0),
                "cleaned_records": export_data["stats"].get("cleaning", {}).get("output_count", 0),
                "high_risk_records": export_data["stats"].get("transformation", {}).get("high_risk_count", 0),
                "aggregations": export_data["aggregations"]
            },
            "details": {
                "sample_records": export_data["records"],
                "processing_stats": export_data["stats"]
            },
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "export_format": "json",
                "schema_version": "1.0",
                "validation_passed": True
            }
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["export_result"] = exec_res
        
        # Log final summary
        self.logger.info(f"Export completed: {exec_res['metadata']['export_timestamp']}")
        self.logger.info(f"Total records processed: {exec_res['summary']['total_records']}")
        
        return None  # End of pipeline


class ValidationErrorHandler(Node):
    """Handles validation errors gracefully"""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return shared.get("validation_errors", {})
    
    def exec(self, errors: Dict[str, Any]) -> Dict[str, Any]:
        """Log and categorize validation errors"""
        error_summary = {
            "total_errors": len(errors),
            "by_type": {},
            "by_node": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Categorize errors
        for error in errors.values():
            error_type = error.get("type", "unknown")
            node_id = error.get("node_id", "unknown")
            
            error_summary["by_type"][error_type] = error_summary["by_type"].get(error_type, 0) + 1
            error_summary["by_node"][node_id] = error_summary["by_node"].get(node_id, 0) + 1
        
        return error_summary
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["error_summary"] = exec_res
        self.logger.error(f"Validation error summary: {exec_res}")
        return None