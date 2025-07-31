"""
Document generation utilities for HITL example.
Simulates AI document generation.
"""

import uuid
from datetime import datetime
import random


def generate_document(topic: str) -> dict:
    """
    Generate a mock document for demonstration.
    In production, this would use an LLM.
    """
    
    # Generate document ID
    doc_id = str(uuid.uuid4())[:8]
    
    # Create sections based on topic
    if "financial" in topic.lower() or "quarterly" in topic.lower():
        sections = {
            "Executive Summary": "This quarter showed strong performance across all key metrics...",
            "Financial Highlights": "Revenue: $45.2M (+15% YoY), Profit: $12.1M (+22% YoY)...",
            "Market Analysis": "Market conditions remain favorable with growing demand...",
            "Risk Assessment": "Key risks include supply chain disruptions and inflation...",
            "Future Outlook": "We expect continued growth in Q1 2025..."
        }
        metadata = {
            "department": "Finance",
            "report_type": "Quarterly",
            "sensitivity": "Confidential"
        }
    elif "marketing" in topic.lower():
        sections = {
            "Campaign Overview": "Q4 marketing campaigns achieved 125% of target ROI...",
            "Channel Performance": "Digital channels outperformed traditional by 3x...",
            "Customer Insights": "Customer satisfaction increased to 92%...",
            "Competitive Analysis": "We maintained market leadership position...",
            "Q1 2025 Strategy": "Focus on personalization and AI-driven campaigns..."
        }
        metadata = {
            "department": "Marketing",
            "report_type": "Performance",
            "sensitivity": "Internal"
        }
    else:
        sections = {
            "Introduction": f"This document provides comprehensive analysis of {topic}...",
            "Current State": "Analysis of the current situation reveals...",
            "Key Findings": "Our research has identified several important trends...",
            "Recommendations": "Based on our analysis, we recommend...",
            "Conclusion": "In summary, the outlook remains positive..."
        }
        metadata = {
            "department": "General",
            "report_type": "Analysis",
            "sensitivity": "Public"
        }
    
    # Calculate word count (mock)
    word_count = random.randint(3000, 8000)
    
    # Generate summary
    summary = f"Comprehensive analysis of {topic} covering key metrics, trends, and strategic recommendations for stakeholders."
    
    return {
        "id": doc_id,
        "title": topic,
        "summary": summary,
        "sections": sections,
        "word_count": word_count,
        "metadata": metadata,
        "created_at": datetime.utcnow().isoformat(),
        "author": "AI Document Generator v2.0",
        "revision": {
            "number": 0,
            "feedback": None
        }
    }


def revise_document_with_feedback(document: dict, feedback: str, modifications: dict) -> dict:
    """
    Revise document based on human feedback.
    In production, this would use an LLM to incorporate feedback.
    """
    revised = document.copy()
    
    # Apply direct modifications
    for key, value in modifications.items():
        if key in revised:
            revised[key] = value
    
    # Simulate AI revision based on feedback
    if "clarity" in feedback.lower():
        revised["summary"] = f"[Clarified] {revised['summary']}"
    
    if "data" in feedback.lower() or "numbers" in feedback.lower():
        # Add more data to sections
        for section in revised["sections"]:
            revised["sections"][section] += " [Additional data points added]"
    
    if "shorten" in feedback.lower() or "concise" in feedback.lower():
        revised["word_count"] = int(revised["word_count"] * 0.8)
    
    # Update revision info
    revised["revision"]["number"] += 1
    revised["revision"]["feedback"] = feedback
    revised["revised_at"] = datetime.utcnow().isoformat()
    
    return revised