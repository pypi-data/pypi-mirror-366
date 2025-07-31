"""
Task generation and validation utilities for supervisor example.
"""

import uuid
import time
from typing import Dict, Any, Tuple, List


def generate_research_task(topic: str, attempt: int) -> Dict[str, Any]:
    """
    Generate a research task for workers.
    
    Args:
        topic: Research topic
        attempt: Current attempt number
        
    Returns:
        Task dictionary
    """
    task_variations = [
        {
            "type": "comprehensive",
            "description": f"Conduct comprehensive research on {topic}",
            "requirements": [
                "Find at least 5 credible sources",
                "Identify key trends and developments",
                "Summarize main findings"
            ],
            "priority": "high"
        },
        {
            "type": "focused",
            "description": f"Research specific aspects of {topic}",
            "requirements": [
                "Focus on recent developments (last 2 years)",
                "Identify practical applications",
                "Highlight controversies or challenges"
            ],
            "priority": "medium"
        },
        {
            "type": "exploratory",
            "description": f"Explore future implications of {topic}",
            "requirements": [
                "Project future trends",
                "Identify potential risks and opportunities",
                "Consider societal impact"
            ],
            "priority": "medium"
        }
    ]
    
    # Select task type based on attempt
    task_template = task_variations[attempt % len(task_variations)]
    
    task = {
        "id": str(uuid.uuid4()),
        "topic": topic,
        "type": task_template["type"],
        "description": task_template["description"],
        "requirements": task_template["requirements"],
        "priority": task_template["priority"],
        "created_at": time.time(),
        "attempt_number": attempt,
        "timeout_seconds": 300,  # 5 minutes
        "quality_threshold": 0.7
    }
    
    return task


def validate_research_result(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a research result from a worker.
    
    Args:
        result: Worker's research result
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    required_fields = ["status", "worker", "task_id", "data"]
    for field in required_fields:
        if field not in result:
            issues.append(f"Missing required field: {field}")
    
    # If status is not success, it's invalid
    if result.get("status") != "success":
        issues.append(f"Result status is not success: {result.get('status')}")
        return False, issues
    
    # Validate data structure
    data = result.get("data", {})
    
    # Check for facts
    facts = data.get("facts", [])
    if not facts:
        issues.append("No facts provided")
    elif len(facts) < 2:
        issues.append(f"Insufficient facts: {len(facts)} (minimum 2 required)")
    
    # Check for sources
    sources = data.get("sources", [])
    if not sources:
        issues.append("No sources provided")
    
    # Check confidence score
    confidence = result.get("confidence", 0)
    if confidence < 0.5:
        issues.append(f"Low confidence score: {confidence}")
    elif confidence > 1.0:
        issues.append(f"Invalid confidence score: {confidence} (must be <= 1.0)")
    
    # Check timestamp
    if "timestamp" not in data:
        issues.append("Missing timestamp")
    else:
        # Check if timestamp is recent (within last hour)
        current_time = time.time()
        if current_time - data["timestamp"] > 3600:
            issues.append("Result timestamp is too old (> 1 hour)")
    
    # Overall validation
    is_valid = len(issues) == 0
    
    return is_valid, issues


def score_research_quality(result: Dict[str, Any]) -> float:
    """
    Score the quality of a research result.
    
    Args:
        result: Research result to score
        
    Returns:
        Quality score between 0 and 1
    """
    if result.get("status") != "success":
        return 0.0
    
    score = 0.0
    data = result.get("data", {})
    
    # Score based on number of facts (max 0.3)
    facts = data.get("facts", [])
    fact_score = min(len(facts) / 5.0, 1.0) * 0.3
    score += fact_score
    
    # Score based on number of sources (max 0.2)
    sources = data.get("sources", [])
    source_score = min(len(sources) / 3.0, 1.0) * 0.2
    score += source_score
    
    # Score based on confidence (max 0.3)
    confidence = result.get("confidence", 0)
    confidence_score = confidence * 0.3
    score += confidence_score
    
    # Score based on detail/length (max 0.2)
    total_length = sum(len(str(fact)) for fact in facts)
    detail_score = min(total_length / 200.0, 1.0) * 0.2
    score += detail_score
    
    return min(score, 1.0)


def merge_research_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple research results into a consolidated result.
    
    Args:
        results: List of research results to merge
        
    Returns:
        Merged result
    """
    if not results:
        return {}
    
    # Start with the highest quality result
    sorted_results = sorted(results, key=score_research_quality, reverse=True)
    best_result = sorted_results[0].copy()
    
    # Merge additional facts and sources from other results
    all_facts = set()
    all_sources = set()
    
    for result in results:
        data = result.get("data", {})
        all_facts.update(data.get("facts", []))
        all_sources.update(data.get("sources", []))
    
    # Update the merged result
    best_result["data"]["facts"] = list(all_facts)
    best_result["data"]["sources"] = list(all_sources)
    best_result["merged_from"] = len(results)
    best_result["confidence"] = sum(r.get("confidence", 0) for r in results) / len(results)
    
    return best_result


if __name__ == "__main__":
    # Test task generation
    task = generate_research_task("AI Ethics", 1)
    print("Generated task:", task)
    
    # Test validation
    test_result = {
        "status": "success",
        "worker": "worker1",
        "task_id": "123",
        "confidence": 0.8,
        "data": {
            "facts": ["Fact 1", "Fact 2", "Fact 3"],
            "sources": ["source1.com", "source2.org"],
            "timestamp": time.time()
        }
    }
    
    is_valid, issues = validate_research_result(test_result)
    print(f"\nValidation: {is_valid}")
    if issues:
        print("Issues:", issues)
    
    # Test quality scoring
    score = score_research_quality(test_result)
    print(f"\nQuality score: {score:.2f}")