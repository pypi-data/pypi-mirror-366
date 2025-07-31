"""
Agent nodes implementation using KayGraph.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from kaygraph import Node, ValidatedNode
from utils.call_llm import call_llm, analyze_query
from utils.search_web import search_web, extract_key_points


class QueryNode(ValidatedNode):
    """Process and validate user query."""
    
    def validate_input(self, prep_res: str) -> str:
        """Validate the query is not empty."""
        if not prep_res or not prep_res.strip():
            raise ValueError("Query cannot be empty")
        return prep_res.strip()
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get query from shared state."""
        return shared.get("query", "")
    
    def exec(self, prep_res: str) -> str:
        """Process the query."""
        self.logger.info(f"Processing query: {prep_res}")
        return prep_res
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Store processed query."""
        shared["query"] = exec_res
        return "default"


class ThinkNode(Node):
    """Analyze query and decide on action plan."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(max_retries=2, wait=1, *args, **kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get query for analysis."""
        return shared["query"]
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Analyze query to determine if search is needed."""
        analysis = analyze_query(prep_res)
        
        self.logger.info(f"Query analysis: needs_search={analysis['needs_search']}, "
                        f"confidence={analysis['confidence']}")
        
        return analysis
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> str:
        """Store analysis results and determine next action."""
        shared["thought_process"] = exec_res["reasoning"]
        shared["needs_search"] = exec_res["needs_search"]
        
        if exec_res["needs_search"]:
            shared["search_query"] = exec_res.get("search_query", prep_res)
            return "search"
        else:
            return "answer"
    
    def exec_fallback(self, prep_res: str, exc: Exception) -> Dict[str, Any]:
        """Fallback to search on analysis failure."""
        self.logger.warning(f"Analysis failed: {exc}. Defaulting to search.")
        return {
            "needs_search": True,
            "reasoning": "Analysis failed, searching to provide best answer",
            "search_query": prep_res,
            "confidence": 0.5
        }


class SearchNode(Node):
    """Perform web search for information."""
    
    def __init__(self, max_results: int = 5, *args, **kwargs):
        super().__init__(max_retries=2, wait=2, *args, **kwargs)
        self.max_results = max_results
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get search query."""
        return shared.get("search_query", shared["query"])
    
    def exec(self, prep_res: str) -> List[Dict[str, Any]]:
        """Execute web search."""
        results = search_web(prep_res, max_results=self.max_results)
        self.logger.info(f"Found {len(results)} search results")
        return results
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: List[Dict]) -> str:
        """Store search results."""
        shared["search_results"] = exec_res
        return "default"
    
    def exec_fallback(self, prep_res: str, exc: Exception) -> List[Dict]:
        """Return empty results on search failure."""
        self.logger.error(f"Search failed: {exc}")
        return []


class SynthesizeNode(Node):
    """Process and synthesize search results."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare search results and query context."""
        return {
            "query": shared["query"],
            "search_results": shared.get("search_results", [])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Synthesize information from search results."""
        if not prep_res["search_results"]:
            return "No search results found to synthesize."
        
        # Extract key points
        key_points = extract_key_points(prep_res["search_results"])
        
        # Create synthesis prompt
        prompt = f"""Synthesize the following search results to answer the query: {prep_res['query']}

Key information found:
{chr(10).join(f'- {point}' for point in key_points)}

Provide a concise synthesis that directly addresses the query."""

        synthesis = call_llm(prompt)
        return synthesis
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> str:
        """Store synthesized information."""
        shared["synthesized_info"] = exec_res
        self.logger.info("Search results synthesized")
        return "default"


class AnswerNode(Node):
    """Generate final answer combining all available information."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all context for answer generation."""
        return {
            "query": shared["query"],
            "thought_process": shared.get("thought_process", ""),
            "needs_search": shared.get("needs_search", False),
            "synthesized_info": shared.get("synthesized_info", ""),
            "search_results": shared.get("search_results", [])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Generate comprehensive answer."""
        # Build context for answer
        context_parts = []
        
        if prep_res["needs_search"] and prep_res["synthesized_info"]:
            context_parts.append(f"Based on search results: {prep_res['synthesized_info']}")
        
        if prep_res["search_results"]:
            context_parts.append(f"Found {len(prep_res['search_results'])} relevant sources")
        
        # Generate answer prompt
        prompt = f"""Generate a comprehensive answer to the query: {prep_res['query']}

Thought process: {prep_res['thought_process']}

{chr(10).join(context_parts)}

Provide a helpful, accurate, and well-structured response."""

        answer = call_llm(prompt, temperature=0.7)
        return answer
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> str:
        """Store final answer."""
        shared["final_answer"] = exec_res
        
        # Log summary
        self.logger.info(f"Generated answer for query: {prep_res['query'][:50]}...")
        if prep_res["needs_search"]:
            self.logger.info(f"Used {len(prep_res['search_results'])} search results")
        
        return "default"