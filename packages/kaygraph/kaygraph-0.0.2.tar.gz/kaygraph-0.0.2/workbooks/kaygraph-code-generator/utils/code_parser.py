"""
Code requirements parser for natural language descriptions.

This module extracts specifications from natural language
descriptions of code requirements.
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RequirementsParser:
    """Parse natural language code descriptions into requirements."""
    
    def __init__(self):
        """Initialize parser with patterns and keywords."""
        # Code type patterns
        self.type_patterns = {
            "function": [
                r"(?:create|write|build|make)\s+(?:a\s+)?function",
                r"function\s+(?:to|that|for)",
                r"def\s+\w+",
                r"method\s+(?:to|that|for)"
            ],
            "class": [
                r"(?:create|write|build|make)\s+(?:a\s+)?class",
                r"class\s+(?:for|that)",
                r"object\s+(?:for|that)",
                r"model\s+(?:for|that)"
            ],
            "api": [
                r"(?:create|build)\s+(?:a\s+)?(?:rest\s+)?api",
                r"api\s+endpoint",
                r"web\s+service",
                r"http\s+endpoint"
            ],
            "script": [
                r"(?:create|write|build)\s+(?:a\s+)?script",
                r"cli\s+tool",
                r"command\s+line",
                r"automation\s+script"
            ],
            "component": [
                r"(?:create|build)\s+(?:a\s+)?component",
                r"react\s+component",
                r"vue\s+component",
                r"ui\s+component"
            ]
        }
        
        # Feature keywords
        self.feature_keywords = {
            "async": ["async", "asynchronous", "await", "concurrent", "parallel"],
            "database": ["database", "db", "sql", "query", "orm"],
            "auth": ["authentication", "auth", "login", "jwt", "oauth"],
            "validation": ["validate", "validation", "check", "verify"],
            "caching": ["cache", "caching", "memoize", "store"],
            "logging": ["log", "logging", "logger", "audit"],
            "error_handling": ["error", "exception", "try", "catch", "handle"],
            "testing": ["test", "testing", "unit test", "pytest", "jest"]
        }
        
        # Language indicators
        self.language_patterns = {
            "python": ["python", "py", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node", "react", "vue", "express"],
            "typescript": ["typescript", "ts", "angular"],
            "go": ["go", "golang", "gin"],
            "java": ["java", "spring", "springboot"],
            "csharp": ["c#", "csharp", "dotnet", ".net"],
            "ruby": ["ruby", "rails", "sinatra"]
        }
        
        # Common patterns
        self.name_pattern = r"(?:called|named)\s+['\"]?(\w+)['\"]?"
        self.param_pattern = r"(?:with|takes?|accepts?|parameters?|params?|arguments?|args?)\s+['\"]?(\w+(?:\s*,\s*\w+)*)['\"]?"
    
    def parse(self, description: str) -> Dict[str, Any]:
        """
        Parse code requirements from natural language.
        
        Args:
            description: Natural language description
            
        Returns:
            Dictionary with parsed requirements
        """
        description_lower = description.lower()
        logger.info(f"Parsing: '{description}'")
        
        result = {
            "original_description": description,
            "type": self._extract_type(description_lower),
            "name": self._extract_name(description),
            "language": self._extract_language(description_lower),
            "parameters": self._extract_parameters(description_lower),
            "features": self._extract_features(description_lower),
            "specifications": self._extract_specifications(description)
        }
        
        # Post-process based on type
        self._post_process(result, description_lower)
        
        return result
    
    def _extract_type(self, text: str) -> str:
        """Extract the code type (function, class, etc.)."""
        for code_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return code_type
        
        # Default to function
        return "function"
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract the name of the code entity."""
        # Look for explicit naming
        match = re.search(self.name_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Try to extract from context
        # "fibonacci calculator" -> "fibonacci_calculator"
        # "todo list manager" -> "TodoListManager"
        
        # Common patterns
        patterns = [
            (r"(?:function|class|api|script)\s+(?:to|for|that)\s+(\w+(?:\s+\w+)*)", "function"),
            (r"(\w+(?:\s+\w+)*)\s+(?:function|class|api|script)", "prefix"),
            (r"(?:create|build|write)\s+(?:a\s+)?(\w+(?:\s+\w+)*)", "verb")
        ]
        
        for pattern, style in patterns:
            match = re.search(pattern, text.lower())
            if match:
                name = match.group(1).strip()
                # Convert to appropriate case
                if "class" in text.lower():
                    # PascalCase for classes
                    return ''.join(word.capitalize() for word in name.split())
                else:
                    # snake_case for functions
                    return '_'.join(name.split())
        
        return None
    
    def _extract_language(self, text: str) -> str:
        """Extract the programming language."""
        for lang, indicators in self.language_patterns.items():
            for indicator in indicators:
                if indicator in text:
                    return lang
        
        # Default based on context
        if any(keyword in text for keyword in ["react", "component", "jsx"]):
            return "javascript"
        elif any(keyword in text for keyword in ["flask", "django", "pytest"]):
            return "python"
        
        # Default to Python
        return "python"
    
    def _extract_parameters(self, text: str) -> List[str]:
        """Extract function/method parameters."""
        params = []
        
        # Look for explicit parameter mentions
        match = re.search(self.param_pattern, text)
        if match:
            param_str = match.group(1)
            params = [p.strip() for p in param_str.split(',')]
        
        # Look for implicit parameters
        # "calculate fibonacci of n" -> parameter 'n'
        implicit_patterns = [
            r"(?:of|for|with)\s+(\w+)(?:\s+and\s+(\w+))?",
            r"given\s+(\w+)(?:\s+and\s+(\w+))?",
            r"from\s+(\w+)\s+to\s+(\w+)"
        ]
        
        for pattern in implicit_patterns:
            match = re.search(pattern, text)
            if match:
                for group in match.groups():
                    if group and group not in params:
                        params.append(group)
        
        return params
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract required features."""
        features = []
        
        for feature, keywords in self.feature_keywords.items():
            if any(keyword in text for keyword in keywords):
                features.append(feature)
        
        # Additional feature detection
        if "rate limit" in text or "throttle" in text:
            features.append("rate_limiting")
        
        if "scrape" in text or "extract" in text or "parse html" in text:
            features.append("web_scraping")
        
        if "real-time" in text or "websocket" in text:
            features.append("realtime")
        
        return features
    
    def _extract_specifications(self, text: str) -> Dict[str, Any]:
        """Extract specific requirements and constraints."""
        specs = {}
        
        # Numeric constraints
        number_pattern = r"(\d+)\s*(?:per|/)\s*(second|minute|hour|day)"
        match = re.search(number_pattern, text, re.IGNORECASE)
        if match:
            specs["rate_limit"] = {
                "count": int(match.group(1)),
                "period": match.group(2)
            }
        
        # Return type hints
        if "return" in text.lower():
            return_patterns = [
                r"returns?\s+(?:a\s+)?(\w+)",
                r"return\s+(?:a\s+)?(\w+)",
                r"gives?\s+(?:a\s+)?(\w+)"
            ]
            
            for pattern in return_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    specs["return_type"] = match.group(1)
                    break
        
        # Method specifications
        if "method" in text.lower():
            method_pattern = r"(?:with|has|includes?)\s+(\w+(?:\s*,\s*\w+)*)\s+methods?"
            match = re.search(method_pattern, text, re.IGNORECASE)
            if match:
                methods = match.group(1).split(',')
                specs["methods"] = [m.strip() for m in methods]
        
        return specs
    
    def _post_process(self, result: Dict[str, Any], text: str) -> None:
        """Post-process and enhance parsed requirements."""
        # Enhance based on type
        if result["type"] == "class":
            # Extract class-specific info
            if "todo" in text and "list" in text:
                result["name"] = result["name"] or "TodoList"
                if not result["specifications"].get("methods"):
                    result["specifications"]["methods"] = ["add", "remove", "complete", "list_all"]
            
            elif "rate limit" in text:
                result["name"] = result["name"] or "RateLimiter"
                if not result["specifications"].get("methods"):
                    result["specifications"]["methods"] = ["is_allowed", "reset", "get_remaining"]
        
        elif result["type"] == "function":
            # Enhance function specs
            if "fibonacci" in text:
                result["name"] = result["name"] or "fibonacci"
                result["parameters"] = result["parameters"] or ["n"]
                result["specifications"]["algorithm"] = "dynamic_programming"
            
            elif "scrape" in text or "scraper" in text:
                result["name"] = result["name"] or "scrape_website"
                result["parameters"] = result["parameters"] or ["url"]
                result["features"].append("web_scraping")
        
        # Add default names if missing
        if not result["name"]:
            if result["type"] == "class":
                result["name"] = "MyClass"
            elif result["type"] == "function":
                result["name"] = "my_function"
            elif result["type"] == "api":
                result["name"] = "api_endpoint"


# Convenience function
def parse_requirements(description: str) -> Dict[str, Any]:
    """Parse code requirements from description."""
    parser = RequirementsParser()
    return parser.parse(description)


if __name__ == "__main__":
    # Test the parser
    test_descriptions = [
        "Create a function to calculate fibonacci numbers",
        "Write a class for managing a todo list with add, remove, and complete methods",
        "Build a REST API endpoint for user authentication",
        "Create an async function that fetches data from multiple URLs",
        "Build a rate limiter class that limits API calls to 100 per minute",
        "Write a Python script to scrape article titles from a website"
    ]
    
    parser = RequirementsParser()
    
    for desc in test_descriptions:
        print(f"\nDescription: '{desc}'")
        result = parser.parse(desc)
        print(f"Type: {result['type']}")
        print(f"Name: {result['name']}")
        print(f"Language: {result['language']}")
        print(f"Parameters: {result['parameters']}")
        print(f"Features: {result['features']}")
        print(f"Specifications: {result['specifications']}")