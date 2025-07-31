"""
Chat with guardrails example using KayGraph.

Demonstrates a chatbot that only responds to specific topics
(e.g., travel-related queries) and politely redirects off-topic questions.
"""

import logging
from typing import Dict, Any, List, Optional
from kaygraph import Node, Graph, ValidatedNode
from utils.guardrails import (
    TopicClassifier, ContentModerator, ResponseFilter,
    TRAVEL_TOPICS, SAFETY_RULES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class InputValidationNode(ValidatedNode):
    """Validate and sanitize user input."""
    
    def validate_input(self, prep_res):
        """Ensure input is safe and valid."""
        user_input = prep_res.strip()
        
        # Check for empty input
        if not user_input:
            raise ValueError("Please provide a question or topic.")
        
        # Check length limits
        if len(user_input) > 500:
            raise ValueError("Input too long. Please keep questions under 500 characters.")
        
        # Basic safety checks
        dangerous_patterns = ["<script", "javascript:", "eval(", "exec("]
        for pattern in dangerous_patterns:
            if pattern.lower() in user_input.lower():
                raise ValueError("Invalid input detected.")
        
        return user_input
    
    def prep(self, shared):
        """Get user input."""
        return shared.get("user_input", "")
    
    def exec(self, validated_input):
        """Process validated input."""
        return {
            "original": validated_input,
            "sanitized": validated_input.strip(),
            "length": len(validated_input)
        }
    
    def post(self, shared, prep_res, exec_res):
        """Store validated input."""
        shared["validated_input"] = exec_res
        return "default"


class TopicClassificationNode(Node):
    """Classify if the input is on-topic (travel-related)."""
    
    def __init__(self, allowed_topics: List[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classifier = TopicClassifier(allowed_topics or TRAVEL_TOPICS)
    
    def prep(self, shared):
        """Get validated input."""
        return shared.get("validated_input", {}).get("sanitized", "")
    
    def exec(self, user_input):
        """Classify the topic."""
        classification = self.classifier.classify(user_input)
        
        self.logger.info(f"Topic classification: {classification['primary_topic']} "
                        f"(confidence: {classification['confidence']:.2f})")
        
        return classification
    
    def post(self, shared, prep_res, exec_res):
        """Route based on classification."""
        shared["topic_classification"] = exec_res
        
        if exec_res["is_on_topic"]:
            return "on_topic"
        else:
            return "off_topic"


class ContentModerationNode(Node):
    """Check content for safety and appropriateness."""
    
    def __init__(self, safety_rules: Dict[str, Any] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moderator = ContentModerator(safety_rules or SAFETY_RULES)
    
    def prep(self, shared):
        """Get input for moderation."""
        return {
            "input": shared.get("validated_input", {}).get("sanitized", ""),
            "classification": shared.get("topic_classification", {})
        }
    
    def exec(self, context):
        """Moderate content."""
        moderation_result = self.moderator.moderate(context["input"])
        
        # Additional checks based on classification
        if context["classification"].get("detected_topics"):
            for topic in context["classification"]["detected_topics"]:
                if topic in ["politics", "religion", "medical_advice"]:
                    moderation_result["requires_disclaimer"] = True
                    moderation_result["disclaimer_type"] = topic
        
        self.logger.info(f"Moderation result: safe={moderation_result['is_safe']}, "
                        f"flags={moderation_result.get('flags', [])}")
        
        return moderation_result
    
    def post(self, shared, prep_res, exec_res):
        """Store moderation result and route."""
        shared["moderation_result"] = exec_res
        
        if not exec_res["is_safe"]:
            return "unsafe"
        elif exec_res.get("requires_disclaimer"):
            return "disclaimer"
        else:
            return "safe"


class OnTopicResponseNode(Node):
    """Generate response for on-topic (travel) queries."""
    
    def prep(self, shared):
        """Prepare context for response generation."""
        return {
            "query": shared.get("validated_input", {}).get("sanitized", ""),
            "topic": shared.get("topic_classification", {}).get("primary_topic", "travel"),
            "subtopics": shared.get("topic_classification", {}).get("detected_topics", [])
        }
    
    def exec(self, context):
        """Generate travel-related response."""
        query = context["query"]
        topic = context["topic"]
        
        # Mock response generation (replace with actual LLM)
        responses = {
            "destinations": f"Great question about travel destinations! Based on your interest in '{query}', I can help you explore amazing places to visit, from tropical beaches to mountain adventures.",
            "planning": f"I'd be happy to help with your travel planning! For '{query}', key considerations include timing, budget, and required documents.",
            "transportation": f"Transportation is crucial for travel! Regarding '{query}', I can provide information about flights, trains, car rentals, and local transport options.",
            "accommodation": f"Finding the right place to stay is important! For '{query}', consider options ranging from hotels to vacation rentals to hostels.",
            "activities": f"There are so many exciting activities for travelers! Based on '{query}', I can suggest adventures, cultural experiences, and must-see attractions.",
            "general": f"I'm here to help with your travel questions! Regarding '{query}', let me provide some helpful travel information and tips."
        }
        
        response = responses.get(topic, responses["general"])
        
        # Add specific tips based on subtopics
        if "budget" in context["subtopics"]:
            response += "\n\n💰 Budget tip: Consider traveling during shoulder season for better deals!"
        if "safety" in context["subtopics"]:
            response += "\n\n🛡️ Safety tip: Always register with your embassy when traveling abroad."
        
        return response
    
    def post(self, shared, prep_res, exec_res):
        """Store response."""
        shared["response"] = exec_res
        return "default"


class OffTopicRedirectNode(Node):
    """Generate polite redirect for off-topic queries."""
    
    def prep(self, shared):
        """Get context for redirect."""
        return {
            "query": shared.get("validated_input", {}).get("sanitized", ""),
            "detected_topic": shared.get("topic_classification", {}).get("primary_topic", "other")
        }
    
    def exec(self, context):
        """Generate redirect message."""
        redirects = [
            "I appreciate your question, but I'm specifically designed to help with travel-related topics. Is there anything about travel destinations, planning, or tips I can help you with?",
            "While that's an interesting topic, I'm a travel-focused assistant. I'd be happy to help you plan a trip, find destinations, or answer travel questions!",
            "I'm specialized in travel assistance. Although I can't help with that particular topic, I'd love to help you discover amazing places to visit or plan your next adventure!",
            f"I notice you're asking about {context['detected_topic']}, but I'm specifically trained for travel topics. How about I help you plan an exciting trip instead?"
        ]
        
        # Select appropriate redirect
        import random
        response = random.choice(redirects)
        
        # Add travel suggestions
        response += "\n\n✈️ Here are some travel topics I can help with:\n"
        response += "• Finding the perfect destination\n"
        response += "• Travel planning and itineraries\n"
        response += "• Budget travel tips\n"
        response += "• Transportation options\n"
        response += "• Accommodation recommendations"
        
        return response
    
    def post(self, shared, prep_res, exec_res):
        """Store redirect response."""
        shared["response"] = exec_res
        return "default"


class SafetyResponseNode(Node):
    """Generate safety-aware responses."""
    
    def prep(self, shared):
        """Get moderation context."""
        return {
            "moderation": shared.get("moderation_result", {}),
            "query": shared.get("validated_input", {}).get("sanitized", "")
        }
    
    def exec(self, context):
        """Generate appropriate safety response."""
        moderation = context["moderation"]
        
        if not moderation.get("is_safe"):
            response = "I apologize, but I cannot provide a response to that query. "
            response += "Please feel free to ask me about travel destinations, planning, or tips!"
        
        elif moderation.get("requires_disclaimer"):
            disclaimer_type = moderation.get("disclaimer_type", "general")
            
            disclaimers = {
                "medical_advice": "⚕️ Health Notice: While I can share general travel health tips, please consult healthcare professionals for medical advice specific to your travel plans.",
                "politics": "🌍 Note: Travel conditions can vary. Please check current government travel advisories for the most up-to-date information.",
                "safety": "⚠️ Safety Notice: Conditions can change. Always verify current safety information through official channels before traveling."
            }
            
            response = disclaimers.get(disclaimer_type, disclaimers["safety"])
            response += f"\n\nRegarding your travel question about '{context['query']}', here's what I can share..."
        
        else:
            response = "Let me help you with that travel query!"
        
        return response
    
    def post(self, shared, prep_res, exec_res):
        """Store safety response."""
        shared["response"] = exec_res
        return "default"


class ResponseFilterNode(Node):
    """Final filtering and formatting of responses."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter = ResponseFilter()
    
    def prep(self, shared):
        """Get response to filter."""
        return shared.get("response", "")
    
    def exec(self, response):
        """Apply final filters and formatting."""
        # Apply response filters
        filtered = self.filter.filter_response(response)
        
        # Add friendly footer
        if "travel" in response.lower():
            filtered += "\n\n🌟 Happy travels! Feel free to ask more travel questions!"
        
        return filtered
    
    def post(self, shared, prep_res, exec_res):
        """Store final response."""
        shared["final_response"] = exec_res
        print(f"\n🤖 Travel Assistant: {exec_res}")
        return None


def create_guardrail_chat_graph():
    """Create a chat graph with topic guardrails."""
    # Create nodes
    input_validation = InputValidationNode(node_id="input_validation")
    topic_classifier = TopicClassificationNode(
        allowed_topics=TRAVEL_TOPICS,
        node_id="topic_classifier"
    )
    content_moderator = ContentModerationNode(node_id="content_moderator")
    on_topic_response = OnTopicResponseNode(node_id="on_topic_response")
    off_topic_redirect = OffTopicRedirectNode(node_id="off_topic_redirect")
    safety_response = SafetyResponseNode(node_id="safety_response")
    response_filter = ResponseFilterNode(node_id="response_filter")
    
    # Connect validation and classification
    input_validation >> topic_classifier
    
    # Topic-based routing
    topic_classifier >> ("on_topic", content_moderator)
    topic_classifier >> ("off_topic", off_topic_redirect)
    
    # Moderation routing
    content_moderator >> ("safe", on_topic_response)
    content_moderator >> ("unsafe", safety_response)
    content_moderator >> ("disclaimer", safety_response)
    
    # All paths lead to response filter
    on_topic_response >> response_filter
    off_topic_redirect >> response_filter
    safety_response >> response_filter
    
    # Create graph
    return Graph(start=input_validation)


def main():
    """Run the guardrail chat example."""
    print("🌍 Travel Assistant with Guardrails")
    print("=" * 50)
    print("I'm a specialized travel assistant! Ask me about:")
    print("• Destinations and places to visit")
    print("• Travel planning and itineraries")
    print("• Transportation and accommodation")
    print("• Travel tips and activities")
    print("\nType 'exit' to quit")
    print("=" * 50)
    
    # Create graph
    graph = create_guardrail_chat_graph()
    
    # Chat loop
    while True:
        user_input = input("\n✈️ You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\n🌟 Thank you for using Travel Assistant! Safe travels!")
            break
        
        # Process input
        shared = {"user_input": user_input}
        
        try:
            graph.run(shared)
            
            # Show classification info in debug mode
            if shared.get("topic_classification"):
                classification = shared["topic_classification"]
                print(f"\n[Debug - Topic: {classification['primary_topic']}, "
                      f"On-topic: {classification['is_on_topic']}]")
        
        except ValueError as e:
            print(f"\n⚠️ Input Error: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logging.error(f"Chat error: {e}", exc_info=True)


if __name__ == "__main__":
    main()