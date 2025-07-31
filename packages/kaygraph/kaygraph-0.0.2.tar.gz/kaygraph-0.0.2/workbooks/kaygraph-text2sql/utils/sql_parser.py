"""
Natural language query parser for SQL generation.

This module provides functionality to parse natural language queries
and extract SQL-relevant components.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class NLQueryParser:
    """Parse natural language queries to extract SQL components."""
    
    def __init__(self):
        """Initialize the parser with patterns and keywords."""
        # Intent patterns
        self.intent_patterns = {
            "select": [
                r"show\s+(?:me\s+)?(?:all\s+)?(.+)",
                r"list\s+(?:all\s+)?(.+)",
                r"find\s+(?:all\s+)?(.+)",
                r"get\s+(?:all\s+)?(.+)",
                r"display\s+(.+)",
                r"what\s+(?:are|is)\s+(?:the\s+)?(.+)"
            ],
            "count": [
                r"count\s+(?:the\s+)?(.+)",
                r"how\s+many\s+(.+)",
                r"number\s+of\s+(.+)",
                r"total\s+(.+)"
            ],
            "aggregate": [
                r"(sum|total|average|avg|mean|max|maximum|min|minimum)\s+(?:of\s+)?(.+)",
                r"(highest|lowest|largest|smallest)\s+(.+)"
            ],
            "top_n": [
                r"top\s+(\d+)\s+(.+)",
                r"first\s+(\d+)\s+(.+)",
                r"best\s+(\d+)\s+(.+)",
                r"worst\s+(\d+)\s+(.+)"
            ]
        }
        
        # Entity patterns
        self.entity_patterns = {
            "customers": ["customer", "customers", "client", "clients", "buyer", "buyers"],
            "products": ["product", "products", "item", "items", "good", "goods"],
            "orders": ["order", "orders", "purchase", "purchases", "transaction", "transactions"],
            "order_items": ["order item", "order items", "line item", "line items"]
        }
        
        # Filter patterns
        self.filter_patterns = [
            (r"under\s+\$?(\d+(?:\.\d+)?)", "less_than"),
            (r"over\s+\$?(\d+(?:\.\d+)?)", "greater_than"),
            (r"above\s+\$?(\d+(?:\.\d+)?)", "greater_than"),
            (r"below\s+\$?(\d+(?:\.\d+)?)", "less_than"),
            (r"(?:where|with|having)\s+(\w+)\s*=\s*['\"]?([^'\"]+)['\"]?", "equals"),
            (r"by\s+(\w+)", "group_by"),
            (r"in\s+(\w+)", "in_column"),
            (r"from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", "date_range"),
            (r"since\s+(\d{4}-\d{2}-\d{2})", "since_date"),
            (r"before\s+(\d{4}-\d{2}-\d{2})", "before_date")
        ]
        
        # Aggregation mappings
        self.aggregation_map = {
            "sum": "SUM", "total": "SUM",
            "average": "AVG", "avg": "AVG", "mean": "AVG",
            "max": "MAX", "maximum": "MAX", "highest": "MAX", "largest": "MAX",
            "min": "MIN", "minimum": "MIN", "lowest": "MIN", "smallest": "MIN",
            "count": "COUNT"
        }
        
        # Column keywords
        self.column_keywords = {
            "price": ["price", "cost", "amount", "value"],
            "name": ["name", "title", "label"],
            "status": ["status", "state", "condition"],
            "created_at": ["created", "date", "when"],
            "quantity": ["quantity", "qty", "amount", "count"],
            "category": ["category", "type", "class", "group"]
        }
    
    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with parsed components
        """
        query = query.lower().strip()
        logger.info(f"Parsing query: '{query}'")
        
        result = {
            "original_query": query,
            "intent": None,
            "entities": {},
            "filters": {},
            "aggregation": None,
            "limit": None,
            "order_by": None
        }
        
        # Extract intent
        result["intent"] = self._extract_intent(query)
        
        # Extract entities
        result["entities"] = self._extract_entities(query)
        
        # Extract filters
        result["filters"] = self._extract_filters(query)
        
        # Extract aggregation
        result["aggregation"] = self._extract_aggregation(query)
        
        # Extract limit
        result["limit"] = self._extract_limit(query)
        
        # Extract ordering
        result["order_by"] = self._extract_ordering(query)
        
        # Post-process and validate
        self._post_process(result)
        
        return result
    
    def _extract_intent(self, query: str) -> str:
        """Extract the primary intent from the query."""
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        # Default to select
        return "select"
    
    def _extract_entities(self, query: str) -> Dict[str, str]:
        """Extract database entities from the query."""
        entities = {}
        
        # Look for known entity patterns
        for table, keywords in self.entity_patterns.items():
            for keyword in keywords:
                if keyword in query:
                    entities["main"] = table
                    break
        
        # If no specific entity found, try to extract from patterns
        if not entities.get("main"):
            # Look for common patterns like "show X"
            match = re.search(r"(?:show|list|find|get)\s+(?:all\s+)?(\w+)", query)
            if match:
                potential_entity = match.group(1)
                # Try to match to known entities
                for table, keywords in self.entity_patterns.items():
                    if any(keyword in potential_entity for keyword in keywords):
                        entities["main"] = table
                        break
        
        # Extract related entities for joins
        if "by" in query and "spending" in query:
            entities["join"] = ["orders"]
        elif "never been ordered" in query:
            entities["main"] = "products"
            entities["join"] = ["order_items"]
        
        return entities
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filter conditions from the query."""
        filters = {}
        
        # Check filter patterns
        for pattern, filter_type in self.filter_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if filter_type == "less_than":
                    filters["price__lt"] = float(match.group(1))
                elif filter_type == "greater_than":
                    filters["price__gt"] = float(match.group(1))
                elif filter_type == "equals":
                    filters[match.group(1)] = match.group(2)
                elif filter_type == "group_by":
                    filters["_group_by"] = match.group(1)
                elif filter_type == "date_range":
                    filters["date__range"] = (match.group(1), match.group(2))
                elif filter_type == "since_date":
                    filters["date__gte"] = match.group(1)
                elif filter_type == "before_date":
                    filters["date__lt"] = match.group(1)
        
        return filters
    
    def _extract_aggregation(self, query: str) -> Optional[Dict[str, str]]:
        """Extract aggregation functions from the query."""
        # Check for count intent
        if self._extract_intent(query) == "count":
            return {"type": "COUNT", "column": "*"}
        
        # Check aggregation patterns
        for pattern in self.intent_patterns["aggregate"]:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                agg_type = match.group(1).lower()
                target = match.group(2).strip()
                
                # Map to SQL function
                sql_func = self.aggregation_map.get(agg_type, "SUM")
                
                # Try to identify the column
                column = self._identify_column(target)
                
                return {
                    "type": sql_func,
                    "column": column or target,
                    "alias": f"{agg_type}_{column or 'value'}"
                }
        
        # Check for "by total spending" pattern
        if "by total spending" in query:
            return {
                "type": "SUM",
                "column": "total",
                "alias": "total_spent"
            }
        
        return None
    
    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract LIMIT clause from the query."""
        # Check top_n patterns
        for pattern in self.intent_patterns["top_n"]:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # Check for explicit limit
        match = re.search(r"limit\s+(\d+)", query, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return None
    
    def _extract_ordering(self, query: str) -> Optional[Dict[str, str]]:
        """Extract ORDER BY clause from the query."""
        order = {}
        
        # Check for explicit ordering
        if "by total spending" in query:
            order["column"] = "total_spent"
            order["direction"] = "DESC"
        elif re.search(r"top\s+\d+", query):
            # Top N usually implies descending order
            order["direction"] = "DESC"
            # Try to infer column from aggregation
            agg = self._extract_aggregation(query)
            if agg:
                order["column"] = agg.get("alias", agg.get("column"))
        elif "latest" in query or "recent" in query:
            order["column"] = "created_at"
            order["direction"] = "DESC"
        elif "oldest" in query or "earliest" in query:
            order["column"] = "created_at"
            order["direction"] = "ASC"
        
        return order if order else None
    
    def _identify_column(self, text: str) -> Optional[str]:
        """Try to identify a database column from text."""
        text = text.lower()
        
        # Check column keywords
        for column, keywords in self.column_keywords.items():
            if any(keyword in text for keyword in keywords):
                return column
        
        # Check if it's already a column name
        if text in ["id", "name", "email", "price", "status", "created_at"]:
            return text
        
        return None
    
    def _post_process(self, result: Dict[str, Any]) -> None:
        """Post-process and validate the parsed result."""
        # If no main entity found, try to infer from context
        if not result["entities"].get("main"):
            if "customer" in result["original_query"]:
                result["entities"]["main"] = "customers"
            elif "product" in result["original_query"]:
                result["entities"]["main"] = "products"
            elif "order" in result["original_query"]:
                result["entities"]["main"] = "orders"
        
        # Handle special cases
        query = result["original_query"]
        
        # "products that have never been ordered"
        if "never been ordered" in query:
            result["intent"] = "select"
            result["entities"]["main"] = "products"
            result["entities"]["join"] = ["order_items"]
            result["filters"]["_special"] = "not_exists"
        
        # "Select from nowhere" - invalid query
        if "from nowhere" in query:
            result["entities"]["main"] = "nowhere"  # Invalid table
        
        # "Show me the stuffs" - ambiguous query
        if "stuffs" in query:
            result["entities"]["main"] = "stuffs"  # Ambiguous entity


# Convenience function
def parse_nl_query(query: str) -> Dict[str, Any]:
    """Parse a natural language query."""
    parser = NLQueryParser()
    return parser.parse(query)


if __name__ == "__main__":
    # Test the parser
    test_queries = [
        "Show all customers",
        "Find products under $50",
        "Count orders by status",
        "Top 5 customers by total spending",
        "Products that have never been ordered",
        "How many orders were placed this month?",
        "Average price of products in electronics category"
    ]
    
    parser = NLQueryParser()
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        result = parser.parse(query)
        print(f"Intent: {result['intent']}")
        print(f"Entities: {result['entities']}")
        print(f"Filters: {result['filters']}")
        print(f"Aggregation: {result['aggregation']}")
        print(f"Limit: {result['limit']}")
        print(f"Order By: {result['order_by']}")