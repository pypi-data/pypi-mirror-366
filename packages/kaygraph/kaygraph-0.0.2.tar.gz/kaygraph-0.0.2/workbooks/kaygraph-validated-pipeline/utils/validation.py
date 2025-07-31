"""
Utility functions for data validation in the pipeline.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Callable


class ValidationRule:
    """Represents a single validation rule"""
    
    def __init__(self, name: str, validator: Callable, error_message: str, severity: str = "error"):
        self.name = name
        self.validator = validator
        self.error_message = error_message
        self.severity = severity  # "error", "warning", "info"
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """Validate a value and return (is_valid, message)"""
        try:
            is_valid = self.validator(value)
            return is_valid, "" if is_valid else self.error_message
        except Exception as e:
            return False, f"{self.error_message}: {str(e)}"


class SchemaValidator:
    """Validates data against a defined schema"""
    
    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}
    
    def add_field_rule(self, field: str, rule: ValidationRule):
        """Add a validation rule for a specific field"""
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append(rule)
    
    def validate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single record"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        for field, rules in self.rules.items():
            value = record.get(field)
            
            for rule in rules:
                is_valid, message = rule.validate(value)
                
                if not is_valid:
                    if rule.severity == "error":
                        result["is_valid"] = False
                        result["errors"].append(f"{field}: {message}")
                    elif rule.severity == "warning":
                        result["warnings"].append(f"{field}: {message}")
        
        return result
    
    def validate_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate multiple records"""
        results = {
            "total_records": len(records),
            "valid_records": 0,
            "invalid_records": 0,
            "warnings": 0,
            "validation_details": []
        }
        
        for i, record in enumerate(records):
            validation = self.validate_record(record)
            
            if validation["is_valid"]:
                results["valid_records"] += 1
            else:
                results["invalid_records"] += 1
            
            if validation["warnings"]:
                results["warnings"] += len(validation["warnings"])
            
            # Store details for first 10 invalid records
            if not validation["is_valid"] and len(results["validation_details"]) < 10:
                results["validation_details"].append({
                    "record_index": i,
                    "record_id": record.get("id", f"record_{i}"),
                    "errors": validation["errors"],
                    "warnings": validation["warnings"]
                })
        
        return results


def create_data_schema() -> SchemaValidator:
    """Create the standard data validation schema"""
    validator = SchemaValidator()
    
    # ID validation
    validator.add_field_rule("id", ValidationRule(
        "required_id",
        lambda x: x is not None and isinstance(x, str) and len(x) > 0,
        "ID is required and must be non-empty string"
    ))
    
    validator.add_field_rule("id", ValidationRule(
        "id_format",
        lambda x: isinstance(x, str) and re.match(r'^[a-zA-Z0-9_-]+$', x),
        "ID must contain only alphanumeric characters, underscores, and hyphens"
    ))
    
    # Timestamp validation
    validator.add_field_rule("timestamp", ValidationRule(
        "required_timestamp",
        lambda x: x is not None,
        "Timestamp is required"
    ))
    
    validator.add_field_rule("timestamp", ValidationRule(
        "valid_timestamp",
        lambda x: isinstance(x, str) and datetime.fromisoformat(x),
        "Timestamp must be valid ISO format"
    ))
    
    # Value validation
    validator.add_field_rule("value", ValidationRule(
        "required_value",
        lambda x: x is not None,
        "Value is required"
    ))
    
    validator.add_field_rule("value", ValidationRule(
        "numeric_value",
        lambda x: isinstance(x, (int, float)),
        "Value must be numeric"
    ))
    
    validator.add_field_rule("value", ValidationRule(
        "positive_value",
        lambda x: isinstance(x, (int, float)) and x >= 0,
        "Value must be non-negative"
    ))
    
    # Category validation
    validator.add_field_rule("category", ValidationRule(
        "required_category",
        lambda x: x is not None,
        "Category is required"
    ))
    
    validator.add_field_rule("category", ValidationRule(
        "valid_category",
        lambda x: isinstance(x, str) and x in {"A", "B", "C", "D"},
        "Category must be one of: A, B, C, D"
    ))
    
    # Metadata validation
    validator.add_field_rule("metadata", ValidationRule(
        "required_metadata",
        lambda x: x is not None and isinstance(x, dict),
        "Metadata is required and must be a dictionary"
    ))
    
    validator.add_field_rule("metadata", ValidationRule(
        "metadata_quality",
        lambda x: isinstance(x, dict) and "quality" in x and isinstance(x["quality"], (int, float)),
        "Metadata must contain numeric quality field"
    ))
    
    return validator


def validate_business_rules(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate business rules across records"""
    violations = []
    
    # Rule 1: No duplicate IDs
    ids = [r.get("id") for r in records]
    duplicates = [id for id in set(ids) if ids.count(id) > 1]
    if duplicates:
        violations.append(f"Duplicate IDs found: {duplicates[:5]}")
    
    # Rule 2: Category distribution should be balanced
    categories = [r.get("category") for r in records if r.get("category")]
    if categories:
        from collections import Counter
        cat_counts = Counter(categories)
        max_count = max(cat_counts.values())
        min_count = min(cat_counts.values())
        
        if max_count > min_count * 5:  # More than 5x difference
            violations.append(f"Unbalanced categories: {dict(cat_counts)}")
    
    # Rule 3: Temporal ordering
    timestamps = []
    for r in records:
        if r.get("timestamp"):
            try:
                timestamps.append(datetime.fromisoformat(r["timestamp"]))
            except:
                pass
    
    if len(timestamps) > 1:
        if timestamps != sorted(timestamps):
            violations.append("Records are not in chronological order")
    
    # Rule 4: Value ranges by category
    category_limits = {
        "A": (0, 250),
        "B": (200, 500),
        "C": (450, 750),
        "D": (700, 1000)
    }
    
    for record in records[:20]:  # Check first 20
        category = record.get("category")
        value = record.get("value")
        
        if category and value is not None and category in category_limits:
            min_val, max_val = category_limits[category]
            if not (min_val <= value <= max_val):
                violations.append(
                    f"Value {value} outside expected range for category {category}: [{min_val}, {max_val}]"
                )
    
    return {
        "total_violations": len(violations),
        "violations": violations[:10],  # First 10
        "passed": len(violations) == 0
    }


def validate_statistical_properties(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate statistical properties of the data"""
    import statistics
    
    if not records:
        return {"error": "No records to validate"}
    
    # Extract numeric values
    values = [r.get("value") for r in records if isinstance(r.get("value"), (int, float))]
    
    if not values:
        return {"error": "No valid numeric values found"}
    
    # Calculate statistics
    stats = {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
        "min": min(values),
        "max": max(values)
    }
    
    # Statistical validation rules
    validations = []
    
    # Check for outliers (values more than 3 standard deviations from mean)
    if stats["std_dev"] > 0:
        outliers = [v for v in values if abs(v - stats["mean"]) > 3 * stats["std_dev"]]
        if outliers:
            validations.append(f"Found {len(outliers)} outliers (>3σ from mean)")
    
    # Check for unusual distribution
    if stats["std_dev"] > stats["mean"] * 0.5:
        validations.append("High variance detected (std dev > 50% of mean)")
    
    # Check for reasonable range
    if stats["max"] - stats["min"] > 1000:
        validations.append("Very wide value range detected")
    
    return {
        "statistics": stats,
        "validations": validations,
        "passed": len(validations) == 0
    }


def generate_validation_report(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a comprehensive validation report"""
    
    # Schema validation
    schema_validator = create_data_schema()
    schema_results = schema_validator.validate_records(records)
    
    # Business rule validation
    business_results = validate_business_rules(records)
    
    # Statistical validation
    statistical_results = validate_statistical_properties(records)
    
    # Overall summary
    total_errors = schema_results["invalid_records"] + business_results["total_violations"]
    total_warnings = schema_results["warnings"]
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_records": len(records),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "overall_valid": total_errors == 0
        },
        "schema_validation": schema_results,
        "business_rules": business_results,
        "statistical_analysis": statistical_results
    }
    
    return report


if __name__ == "__main__":
    # Test the validation utilities
    
    # Sample valid record
    valid_record = {
        "id": "test_001",
        "timestamp": datetime.now().isoformat(),
        "value": 150.5,
        "category": "A",
        "metadata": {
            "source": "sensor_1",
            "quality": 0.95
        }
    }
    
    # Sample invalid record
    invalid_record = {
        "id": "",  # Empty ID
        "timestamp": "invalid-date",  # Invalid timestamp
        "value": -50,  # Negative value
        "category": "X",  # Invalid category
        "metadata": "not a dict"  # Wrong type
    }
    
    # Test schema validation
    validator = create_data_schema()
    
    print("Testing valid record:")
    result = validator.validate_record(valid_record)
    print(f"Valid: {result['is_valid']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    
    print("\nTesting invalid record:")
    result = validator.validate_record(invalid_record)
    print(f"Valid: {result['is_valid']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    
    print("\nGenerating full report:")
    report = generate_validation_report([valid_record, invalid_record])
    print(f"Total records: {report['summary']['total_records']}")
    print(f"Total errors: {report['summary']['total_errors']}")
    print(f"Overall valid: {report['summary']['overall_valid']}")