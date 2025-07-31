"""
Guardrail utilities for topic filtering and content moderation.
"""

import re
from typing import List, Dict, Any, Set
import logging

logger = logging.getLogger(__name__)

# Travel-related topics
TRAVEL_TOPICS = [
    "destinations",
    "planning",
    "transportation",
    "accommodation",
    "activities",
    "budget",
    "safety",
    "documents",
    "packing",
    "weather",
    "culture",
    "food"
]

# Safety rules and filters
SAFETY_RULES = {
    "blocked_terms": [
        "violence", "illegal", "drugs", "weapons", "explicit"
    ],
    "sensitive_topics": [
        "politics", "religion", "medical_advice", "financial_advice"
    ],
    "max_length": 1000,
    "min_length": 1
}


class TopicClassifier:
    """Classify user input into topics."""
    
    def __init__(self, allowed_topics: List[str]):
        """
        Initialize classifier with allowed topics.
        
        Args:
            allowed_topics: List of allowed topic categories
        """
        self.allowed_topics = allowed_topics
        self.topic_keywords = self._build_topic_keywords()
    
    def _build_topic_keywords(self) -> Dict[str, Set[str]]:
        """Build keyword mappings for each topic."""
        keywords = {
            "destinations": {
                "destination", "place", "country", "city", "visit", "travel to",
                "where", "location", "explore", "recommend", "suggestion",
                "beach", "mountain", "island", "europe", "asia", "america"
            },
            "planning": {
                "plan", "itinerary", "schedule", "prepare", "organize",
                "trip", "journey", "vacation", "holiday", "tour",
                "how long", "when to", "best time"
            },
            "transportation": {
                "flight", "airplane", "train", "bus", "car", "rental",
                "transport", "airport", "station", "ticket", "booking",
                "drive", "fly", "transit", "connection"
            },
            "accommodation": {
                "hotel", "hostel", "airbnb", "stay", "accommodation",
                "room", "booking", "reservation", "lodge", "resort",
                "where to stay", "sleep", "bed"
            },
            "activities": {
                "activity", "things to do", "attractions", "sightseeing",
                "tour", "experience", "adventure", "museum", "park",
                "restaurant", "entertainment", "nightlife"
            },
            "budget": {
                "budget", "cost", "price", "expensive", "cheap", "affordable",
                "money", "spend", "save", "economy", "luxury", "fee"
            },
            "safety": {
                "safe", "safety", "secure", "dangerous", "risk", "caution",
                "health", "vaccine", "insurance", "emergency", "crime"
            },
            "documents": {
                "passport", "visa", "document", "permit", "requirement",
                "embassy", "consulate", "id", "paperwork", "entry"
            },
            "packing": {
                "pack", "packing", "luggage", "bag", "suitcase", "carry",
                "bring", "clothes", "gear", "essentials", "checklist"
            },
            "weather": {
                "weather", "climate", "temperature", "rain", "sun", "season",
                "hot", "cold", "forecast", "conditions"
            },
            "culture": {
                "culture", "customs", "tradition", "language", "etiquette",
                "local", "people", "behavior", "respect", "learn"
            },
            "food": {
                "food", "restaurant", "eat", "cuisine", "dish", "meal",
                "taste", "local food", "dietary", "vegetarian", "drink"
            }
        }
        
        # Add general travel keywords
        general_keywords = {
            "travel", "trip", "journey", "vacation", "holiday", "tour",
            "tourist", "traveler", "abroad", "overseas", "foreign"
        }
        
        # Add general keywords to all topics
        for topic in keywords:
            if topic in self.allowed_topics:
                keywords[topic].update(general_keywords)
        
        return keywords
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify text into topics.
        
        Args:
            text: User input text
            
        Returns:
            Classification result with topic and confidence
        """
        text_lower = text.lower()
        
        # Score each topic
        topic_scores = {}
        detected_keywords = {}
        
        for topic, keywords in self.topic_keywords.items():
            if topic not in self.allowed_topics:
                continue
            
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                if keyword in text_lower:
                    # Longer keywords get higher weight
                    weight = len(keyword.split())
                    score += weight
                    found_keywords.append(keyword)
            
            if score > 0:
                topic_scores[topic] = score
                detected_keywords[topic] = found_keywords
        
        # Determine primary topic
        if topic_scores:
            primary_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
            max_score = topic_scores[primary_topic]
            
            # Calculate confidence (0-1)
            confidence = min(max_score / 10.0, 1.0)
            
            # Check if it's travel-related
            is_on_topic = any(
                keyword in text_lower 
                for keyword in ["travel", "trip", "vacation", "visit", "tour"]
            ) or primary_topic in self.allowed_topics
            
            return {
                "primary_topic": primary_topic,
                "is_on_topic": is_on_topic,
                "confidence": confidence,
                "topic_scores": topic_scores,
                "detected_keywords": detected_keywords[primary_topic],
                "detected_topics": list(topic_scores.keys())
            }
        else:
            # No travel topics detected
            return {
                "primary_topic": "other",
                "is_on_topic": False,
                "confidence": 0.0,
                "topic_scores": {},
                "detected_keywords": [],
                "detected_topics": []
            }


class ContentModerator:
    """Moderate content for safety and appropriateness."""
    
    def __init__(self, safety_rules: Dict[str, Any]):
        """
        Initialize moderator with safety rules.
        
        Args:
            safety_rules: Dictionary of safety rules and filters
        """
        self.safety_rules = safety_rules
    
    def moderate(self, text: str) -> Dict[str, Any]:
        """
        Moderate text content.
        
        Args:
            text: Content to moderate
            
        Returns:
            Moderation result
        """
        result = {
            "is_safe": True,
            "flags": [],
            "severity": "none",
            "requires_disclaimer": False
        }
        
        text_lower = text.lower()
        
        # Check blocked terms
        for term in self.safety_rules.get("blocked_terms", []):
            if term in text_lower:
                result["is_safe"] = False
                result["flags"].append(f"blocked_term:{term}")
                result["severity"] = "high"
        
        # Check sensitive topics
        for topic in self.safety_rules.get("sensitive_topics", []):
            if topic in text_lower:
                result["requires_disclaimer"] = True
                result["flags"].append(f"sensitive_topic:{topic}")
                if result["severity"] == "none":
                    result["severity"] = "medium"
        
        # Check length limits
        if len(text) > self.safety_rules.get("max_length", 1000):
            result["flags"].append("too_long")
            result["severity"] = "low"
        
        if len(text) < self.safety_rules.get("min_length", 1):
            result["flags"].append("too_short")
            result["severity"] = "low"
        
        # Check for potential spam patterns
        if self._is_spam(text):
            result["is_safe"] = False
            result["flags"].append("spam_detected")
            result["severity"] = "high"
        
        logger.info(f"Moderation result: {result}")
        return result
    
    def _is_spam(self, text: str) -> bool:
        """Check for spam patterns."""
        spam_patterns = [
            r'(https?://\S+){3,}',  # Multiple URLs
            r'(.)\1{10,}',          # Repeated characters
            r'[A-Z\s]{20,}',        # All caps
            r'(\b\w+\b)(\s+\1){5,}' # Repeated words
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, text):
                return True
        
        return False


class ResponseFilter:
    """Filter and sanitize responses."""
    
    def filter_response(self, response: str) -> str:
        """
        Filter and format response.
        
        Args:
            response: Raw response text
            
        Returns:
            Filtered response
        """
        # Remove any accidental sensitive information
        filtered = self._remove_sensitive_info(response)
        
        # Ensure appropriate formatting
        filtered = self._format_response(filtered)
        
        # Add safety disclaimers if needed
        filtered = self._add_disclaimers(filtered)
        
        return filtered
    
    def _remove_sensitive_info(self, text: str) -> str:
        """Remove potentially sensitive information."""
        # Patterns to remove
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
        }
        
        filtered = text
        for info_type, pattern in patterns.items():
            filtered = re.sub(pattern, f'[{info_type.upper()}_REMOVED]', filtered)
        
        return filtered
    
    def _format_response(self, text: str) -> str:
        """Ensure proper formatting."""
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure ends with punctuation
        if text and text[-1] not in '.!?':
            text += '.'
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _add_disclaimers(self, text: str) -> str:
        """Add necessary disclaimers."""
        disclaimers = []
        
        # Check for specific content that needs disclaimers
        if "medical" in text.lower() or "health" in text.lower():
            disclaimers.append("💊 Health Notice: Consult healthcare professionals for medical advice.")
        
        if "legal" in text.lower() or "visa" in text.lower():
            disclaimers.append("⚖️ Legal Notice: Verify legal requirements with official sources.")
        
        if disclaimers:
            text = '\n\n'.join(disclaimers) + '\n\n' + text
        
        return text


def create_topic_filter(allowed_topics: List[str]) -> TopicClassifier:
    """Create a topic classifier with specified allowed topics."""
    return TopicClassifier(allowed_topics)


def create_content_moderator(custom_rules: Dict[str, Any] = None) -> ContentModerator:
    """Create a content moderator with custom or default rules."""
    rules = SAFETY_RULES.copy()
    if custom_rules:
        rules.update(custom_rules)
    return ContentModerator(rules)


if __name__ == "__main__":
    # Test topic classifier
    classifier = TopicClassifier(TRAVEL_TOPICS)
    
    test_queries = [
        "What are the best beaches in Thailand?",
        "How's the weather today?",
        "Tell me about Python programming",
        "I need help planning a trip to Paris",
        "What's the capital of France?"
    ]
    
    print("Topic Classification Tests:")
    for query in test_queries:
        result = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"Topic: {result['primary_topic']}, On-topic: {result['is_on_topic']}, "
              f"Confidence: {result['confidence']:.2f}")
    
    # Test content moderator
    moderator = ContentModerator(SAFETY_RULES)
    
    test_content = [
        "Tell me about travel insurance",
        "I need medical advice for my trip",
        "AAAAAAAAAAAAAAAAAAAAAAA",
        "Great travel tips!"
    ]
    
    print("\n\nContent Moderation Tests:")
    for content in test_content:
        result = moderator.moderate(content)
        print(f"\nContent: {content}")
        print(f"Safe: {result['is_safe']}, Flags: {result['flags']}")