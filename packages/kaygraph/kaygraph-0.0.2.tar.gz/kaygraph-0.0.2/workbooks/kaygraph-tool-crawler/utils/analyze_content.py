"""
Content analysis utilities for analyzing crawled web content.
"""

import re
from typing import Dict, List, Any
from collections import Counter


def analyze_page_content(page_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze a single page's content.
    
    Args:
        page_data: Page data with url, title, content
        
    Returns:
        Analysis results
    """
    content = page_data.get("content", "")
    
    # Extract key information
    analysis = {
        "url": page_data["url"],
        "title": page_data["title"],
        "word_count": page_data.get("word_count", len(content.split())),
        "topics": extract_topics(content),
        "key_points": extract_key_points(content),
        "sentiment": analyze_sentiment(content),
        "readability_score": calculate_readability(content),
        "has_contact_info": detect_contact_info(content),
        "has_pricing": detect_pricing_info(content),
        "summary": generate_summary(content)
    }
    
    return analysis


def extract_topics(content: str) -> List[str]:
    """Extract main topics from content."""
    # Simple keyword-based topic extraction
    topics = []
    
    topic_keywords = {
        "products": ["product", "widget", "catalog", "price", "stock"],
        "company": ["about", "founded", "mission", "team", "employees"],
        "blog": ["article", "post", "guide", "tips", "tutorial"],
        "technology": ["web", "crawling", "scalable", "architecture", "api"],
        "business": ["enterprise", "customer", "solution", "service"],
        "contact": ["contact", "email", "phone", "address", "support"]
    }
    
    content_lower = content.lower()
    word_freq = Counter(content_lower.split())
    
    for topic, keywords in topic_keywords.items():
        score = sum(word_freq.get(keyword, 0) for keyword in keywords)
        if score > 0:
            topics.append(topic)
    
    return topics[:3]  # Top 3 topics


def extract_key_points(content: str) -> List[str]:
    """Extract key points from content."""
    key_points = []
    
    # Look for bullet points or numbered lists
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        # Check for bullet points or numbered items
        if (line.startswith('-') or 
            line.startswith('•') or 
            re.match(r'^\d+\.', line) or
            line.startswith('*')):
            # Clean up the line
            point = re.sub(r'^[-•*\d.]\s*', '', line).strip()
            if len(point) > 10:  # Meaningful content
                key_points.append(point)
    
    # If no bullet points found, extract sentences with keywords
    if not key_points:
        sentences = re.split(r'[.!?]', content)
        important_keywords = ["key", "important", "main", "primary", "essential", "critical"]
        
        for sentence in sentences[:10]:  # Check first 10 sentences
            if any(keyword in sentence.lower() for keyword in important_keywords):
                key_points.append(sentence.strip())
    
    return key_points[:5]  # Top 5 points


def analyze_sentiment(content: str) -> str:
    """Simple sentiment analysis."""
    positive_words = ["excellent", "great", "good", "amazing", "wonderful", "best", 
                     "satisfied", "happy", "success", "award-winning", "leading"]
    negative_words = ["bad", "poor", "terrible", "worst", "dissatisfied", "unhappy", 
                     "failure", "problem", "issue", "complaint"]
    
    content_lower = content.lower()
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    if positive_count > negative_count * 2:
        return "positive"
    elif negative_count > positive_count * 2:
        return "negative"
    else:
        return "neutral"


def calculate_readability(content: str) -> float:
    """Calculate simple readability score (0-100)."""
    # Simple readability based on average word and sentence length
    sentences = re.split(r'[.!?]', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0.0
    
    words = content.split()
    if not words:
        return 0.0
    
    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Simple formula: shorter sentences and words = higher readability
    # Ideal sentence length: 15-20 words
    # Ideal word length: 4-5 characters
    sentence_score = max(0, 100 - abs(avg_sentence_length - 17.5) * 2)
    word_score = max(0, 100 - abs(avg_word_length - 4.5) * 10)
    
    return round((sentence_score + word_score) / 2, 1)


def detect_contact_info(content: str) -> bool:
    """Check if content contains contact information."""
    contact_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
        r'\bcontact\s+us\b',
        r'\bemail\b',
        r'\bphone\b',
        r'\baddress\b'
    ]
    
    content_lower = content.lower()
    return any(re.search(pattern, content_lower, re.IGNORECASE) for pattern in contact_patterns)


def detect_pricing_info(content: str) -> bool:
    """Check if content contains pricing information."""
    pricing_patterns = [
        r'\$\d+',  # Dollar amounts
        r'\bprice\b',
        r'\bcost\b',
        r'\bpricing\b',
        r'\bfee\b',
        r'\bsubscription\b'
    ]
    
    content_lower = content.lower()
    return any(re.search(pattern, content_lower, re.IGNORECASE) for pattern in pricing_patterns)


def generate_summary(content: str, max_length: int = 150) -> str:
    """Generate a brief summary of the content."""
    # Simple extractive summary - take first few sentences
    sentences = re.split(r'[.!?]', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return "No content available."
    
    summary = sentences[0]
    
    # Add more sentences if under max length
    for sentence in sentences[1:3]:
        if len(summary) + len(sentence) + 2 <= max_length:
            summary += ". " + sentence
        else:
            break
    
    if not summary.endswith('.'):
        summary += '.'
    
    return summary


def aggregate_analyses(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate multiple page analyses into overall insights.
    
    Args:
        analyses: List of individual page analyses
        
    Returns:
        Aggregated insights
    """
    if not analyses:
        return {}
    
    # Collect all topics
    all_topics = []
    for analysis in analyses:
        all_topics.extend(analysis.get("topics", []))
    
    topic_counts = Counter(all_topics)
    
    # Aggregate metrics
    total_words = sum(a.get("word_count", 0) for a in analyses)
    avg_readability = sum(a.get("readability_score", 0) for a in analyses) / len(analyses)
    
    # Count pages with specific features
    pages_with_contact = sum(1 for a in analyses if a.get("has_contact_info"))
    pages_with_pricing = sum(1 for a in analyses if a.get("has_pricing"))
    
    # Sentiment distribution
    sentiments = [a.get("sentiment", "neutral") for a in analyses]
    sentiment_counts = Counter(sentiments)
    
    return {
        "total_pages": len(analyses),
        "total_words": total_words,
        "avg_words_per_page": total_words / len(analyses),
        "avg_readability": round(avg_readability, 1),
        "main_topics": [topic for topic, _ in topic_counts.most_common(5)],
        "topic_distribution": dict(topic_counts),
        "sentiment_distribution": dict(sentiment_counts),
        "pages_with_contact_info": pages_with_contact,
        "pages_with_pricing_info": pages_with_pricing,
        "content_coverage": {
            "has_company_info": "company" in topic_counts,
            "has_product_info": "products" in topic_counts,
            "has_blog_content": "blog" in topic_counts,
            "has_contact_details": pages_with_contact > 0
        }
    }


if __name__ == "__main__":
    # Test content analysis
    test_page = {
        "url": "https://example.com/about",
        "title": "About Us - Example Site",
        "content": """About Our Company

Founded in 2020, we are a leading provider of excellent services.
Our mission is to deliver amazing products that satisfy our customers.

Key achievements:
- Award-winning customer service
- 99.9% uptime guarantee  
- Over 1000 satisfied clients
- Offices in 3 countries

Contact us at info@example.com or call 555-0123."""
    }
    
    print("Testing Content Analysis")
    print("=" * 50)
    
    analysis = analyze_page_content(test_page)
    
    print(f"\nAnalysis for: {analysis['title']}")
    print(f"Topics: {', '.join(analysis['topics'])}")
    print(f"Sentiment: {analysis['sentiment']}")
    print(f"Readability: {analysis['readability_score']}/100")
    print(f"Has contact info: {analysis['has_contact_info']}")
    print(f"Has pricing info: {analysis['has_pricing']}")
    print(f"\nKey points:")
    for point in analysis['key_points']:
        print(f"  - {point}")
    print(f"\nSummary: {analysis['summary']}")